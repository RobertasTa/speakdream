# The shared synthesis recipe for Reginutė through the piper-tts wheel.
#
# It exists because the raw model output is not what a listener should get.
# Two problems were found by ear and then measured: piper's
# `normalize_audio=True` raises the peak to 1.0 and clips this voice, and
# without inserted pauses only 11 % of the audio is silence instead of the
# 32 % a person actually leaves between phrases.
#
# The recipe:
#   1. text -> cleanup (quotes, brackets, ellipses) -> optional expander;
#   2. split at every punctuation mark into fragments;
#   3. fragment -> phonemes (phonemize_lithuanian) -> model, NO normalization;
#   4. trim the model's trailing silence (-45 dB) and insert our own pauses:
#      comma 0.25 s, . ! ? 0.45 s, colon 0.20 s, line 0.15 s, end 0.7 s.
#      The pause lengths come from measuring a corpus of annotated Lithuanian
#      speech, not from taste.
#
# Used by demo_piper_wheel.py and wyoming_reginute.py.
import re
import unicodedata
from dataclasses import replace
from typing import Iterable, Optional

import numpy as np
from piper import PiperVoice, SynthesisConfig

_KABUTES = re.compile(r'[„“”"«»]')
# Splitting at commas was tried both ways, by ear. Splitting always makes
# one-word fragments, and VITS stretches those (a single "Labas" ran 0.72 s).
# Never splitting made the whole text speed up instead - 159 -> 178 words per
# minute, where the original speaker reads 149. MIN_ZODZIU is the compromise:
# with 0 we split at every comma, as the reference recipe does; raise it to
# keep short clauses together, letting the model handle the comma itself (it
# has the comma in its phoneme map and learned the pause from the speaker).
# The hyphen marks the edges of a spelled-out abbreviation (0.10 s).
_ZENKLAI = re.compile(r"([.,!?:;–-])")
_ZENKLAI_BE_KABLELIO = re.compile(r"([.!?:;–-])")
SILPNI = ","            # split here only if both sides are long enough
MIN_ZODZIU = 0          # 0 = split at every comma
TRUMPAS = 20            # phoneme count: below this the model stretches
ILGAS = 30              # from here up, a fragment's rate is taken as reference
TIKSLINIS_MS = 41.0     # ms per phoneme (measured on long fragments)

# "It speaks in waves" - a listener's description, then measured across
# fragments of one text: short sentences ran at 50 ms per phoneme, long ones
# at 38. A third of a difference, heard as unevenness.
# Fix: every fragment is re-synthesized (up to twice) until it lands on one
# rate. Spread afterwards: 38-50 -> 45-51 ms per phoneme.
# The target is tied to length_scale so that it stays a meaningful control:
# at 1.30 it works out to 48 ms per phoneme.
MS_UZ_TEMPO_VIENETA = 36.9
LYGINIMO_PAKLAIDA = 0.06    # within 6 % - leave it alone
LYGINIMO_BANDYMAI = 2

# One target for every fragment turned out to be wrong: there have to be two.
# Measured across the 5121 recordings of the original speaker, ms per phoneme:
#     long (30+ phonemes) 37.8 · medium (15-29) 46.3 · short (<15) 63.6
# She speaks a short fragment 68 % SLOWER than a long one. The comment above
# assumed the opposite ("a person throws a short phrase away faster") - that
# assumption came from intuition rather than from the data, and for this
# speaker it is simply false.
# The existing 36.9 x 1.25 = 46.1 matches the MEDIUM reference (46.3) to a
# tenth, so it was right - only it was being applied to short fragments too.
# The audible result: single spoken numbers came out at 0.75-0.86x her rate
# and sounded thin, because the voice has no time to open up.
# Do NOT switch the levelling off: without it a short fragment runs 1.80x
# slower than she does, because the model barely saw any (93 short fragments
# against 4963). Medium and long are left alone - they were approved by ear.
TRUMPI_FON = 15             # phonemes: below this a different target applies
MS_TRUMPIEMS_UZ_VIENETA = 50.9
# 50.9 comes from dividing her 63.6 by the length_scale that was default at
# the time (1.25). The default is now 1.30, so the real target for short
# fragments is 50.9 x 1.30 = 66.2 ms rather than 63.6.
# The constant is deliberately NOT recalculated to 48.9: it was the 66.2 ms
# result that a listener heard through a speaker and approved. A number
# confirmed by ear is not changed for the sake of tidier arithmetic.

# Spelled-out abbreviations were first split into separate fragments with
# pauses between the letters. Measured with an ASR model listening to 24
# files, that made recognition WORSE:
#     letters mid-sentence (as in training) 8/11   <- kept
#     pauses between letters                6/11
#     slower + pauses                       7/11
# But ASR measures what a machine recovers, and a speaker talks to a person.
# By ear, letters run together read as one word, so the abbreviation is kept
# as a single fragment and spoken slower instead - the hyphens around it mark
# where it starts and ends.
# Slowing abbreviations down came back, for the same reason the ASR result
# above was set aside: that measurement asked what a machine recovers, and
# this one was chosen by listening. Three rates were compared - 1.0, 1.15 and
# 1.30, with the abbreviation as one fragment and no pauses inside it - and
# 1.15 was picked. Together with the expander change (letters joined by
# spaces, hyphens only on the outside) it gives both things that were asked
# for: the letters do not rattle out one by one, and they do not rush.
SANTRUMPOS_LETUMAS = 1.15


def valyk_teksta(t: str) -> str:
    t = _KABUTES.sub(" ", t)
    t = re.sub(r"\(\s*\.\.\.\s*\)", " ", t)
    t = re.sub(r"[()\[\]]", " ", t)
    t = t.replace("…", ".")
    t = re.sub(r"\.{2,}", ".", t)
    t = re.sub(r"([.,:;!?])\s*(?=[.,:;!?])", "", t)
    t = re.sub(r"[ \t]+", " ", t)
    return t


def nukirpk_tyla(a: np.ndarray, sr: int, slenkstis_db: float = -45.0,
                 pradzios_db: float = -70.0, pradzios_atsarga: int = 3) -> np.ndarray:
    """Nukerpa gabalo tylą. ⭐ 09-03: PRIEKIUI slenkstis ŽEMESNIS.

    Robertas perklausė Reginutę dviem atpažintuvais ir abu iš „Rašykite"
    padarė „Ašykite". Priežastis pamatuota: modelis kiekvieną gabalą pradeda
    120–200 ms beveik tylos, o po to garsas KYLA palaipsniui — „R" pradžia
    eina per −83, −76, −73, −71, −65, −58 dB. Kirpimas ties −45 dB tą kilimą
    nurėždavo, ir pirmasis priebalsis dingdavo. Todėl priekiui imam −70 dB su
    3 langų (30 ms) atsarga, o galui paliekam −45 dB (uodegos tyla nereikalinga).
    """
    lango = int(sr * 0.01)
    n = len(a) // lango
    if n == 0:
        return a
    rms = 20 * np.log10(np.sqrt(np.mean(a[:n * lango].reshape(n, lango) ** 2, axis=1)) + 1e-12)
    garsus = np.where(rms > slenkstis_db)[0]
    if len(garsus) == 0:
        return a
    tylus = np.where(rms > pradzios_db)[0]
    if not len(tylus):
        tylus = garsus
    pradzia = max(0, tylus[0] - pradzios_atsarga)
    # The same low threshold was tried at the END too, because an ASR model
    # kept dropping final consonants. It made things worse (9/11 -> 7/11) and
    # a human listener confirmed the endings were fine in the audio - the
    # recognizer was wrong, not the synthesis. The end keeps -45 dB, where
    # there really is nothing but trailing silence.
    return a[pradzia * lango: min(n, garsus[-1] + 2) * lango]


class ReginuteSynth:
    def __init__(self, voice: PiperVoice, phonemizer, length_scale: float = 1.30,
                 kablelis: float = 0.25, taskas: float = 0.45,
                 expand_text=None, min_zodziu: int = MIN_ZODZIU,
                 santrumpu_letumas: float = SANTRUMPOS_LETUMAS,
                 kableli_skaidyti: bool = False, lyginti_greiti: bool = True) -> None:
        # Let the model keep its own rhythm. With our pauses the same text ran
        # 22.6 s; without them, 7.9 s - three times shorter. Most of that time
        # was not speech but our 0.45 s after a full stop and 0.25 s after a
        # comma. The comma is now left to the model, which has it in its
        # phoneme map and learned the pause from the speaker; we only add what
        # the model cannot do by itself.
        self.voice = voice
        self.kableli_skaidyti = kableli_skaidyti
        self.min_zodziu = min_zodziu
        self.santrumpu_letumas = santrumpu_letumas
        self.length_scale = length_scale
        self.lyginti_greiti = lyginti_greiti
        self.tikslinis_ms = (MS_UZ_TEMPO_VIENETA * length_scale
                             if lyginti_greiti else TIKSLINIS_MS)
        self._etalonas = []
        self.phonemizer = phonemizer
        self.expand_text = expand_text
        self.sr = voice.config.sample_rate
        self.syn = SynthesisConfig(length_scale=length_scale, noise_scale=0.667,
                                   noise_w_scale=0.8, normalize_audio=False)
        self.pauze = {".": taskas, "!": taskas, "?": taskas, ":": 0.20, ";": 0.20,
                      ",": kablelis, "–": kablelis,
                      # the hyphen marks the edges of an abbreviation
                      "-": 0.10}
        self.kablelis = kablelis
        self.zurnalas = []   # (fragment, duration s, RMS dB) - for measuring

    def _tyla(self, s: float) -> np.ndarray:
        return np.zeros(int(self.sr * s), dtype=np.float32)

    def _sintezuok(self, fonemos, length_scale: float) -> np.ndarray:
        ids = self.voice.phonemes_to_ids(fonemos)
        syn = replace(self.syn, length_scale=length_scale)
        a = self.voice.phoneme_ids_to_audio(ids, syn)
        if isinstance(a, tuple):
            a = a[0]
        return nukirpk_tyla(np.asarray(a, dtype=np.float32), self.sr)

    def _fragmentas(self, frag: str, santrumpa: bool = False) -> Optional[np.ndarray]:
        ipa = self.phonemizer.phonemize_sentence(frag)
        if not ipa:
            return None
        fonemos = list(unicodedata.normalize("NFD", ipa))
        if santrumpa:
            # An abbreviation must not be sped up. It is short (13 characters),
            # so the rate correction below treated it as a "stretched"
            # fragment and squeezed three letters into 0.64 s. A letter is not
            # a word: you cannot guess it from context, so it has to be SLOWER
            # than speech, not faster. The correction is skipped and the
            # fragment is slowed instead.
            a = self._sintezuok(fonemos, self.length_scale * self.santrumpu_letumas)
            if len(a):
                self.zurnalas.append((frag, len(a) / self.sr, 0.0))
            return a
        # Rate levelling, applied to EVERY fragment so the waviness goes away
        ls = self.length_scale
        a = self._sintezuok(fonemos, ls)
        if self.lyginti_greiti:
            # short fragments have their own target (see MS_TRUMPIEMS_UZ_VIENETA)
            tikslas = (MS_TRUMPIEMS_UZ_VIENETA * self.length_scale
                       if len(fonemos) < TRUMPI_FON else self.tikslinis_ms)
            for _ in range(LYGINIMO_BANDYMAI):
                ms = 1000 * len(a) / self.sr / len(fonemos)
                if abs(ms - tikslas) < tikslas * LYGINIMO_PAKLAIDA:
                    break
                ls = max(0.6, min(2.0, ls * tikslas / ms))
                a = self._sintezuok(fonemos, ls)
            if len(a):
                self.zurnalas.append((frag, len(a) / self.sr,
                                      20 * float(np.log10(np.sqrt(np.mean(a ** 2)) + 1e-12))))
            return a

        # Fallback path (levelling off): a single word came out so long it was
        # nearly spelled out. Measured: long fragments settle at ~41 ms per
        # phoneme, while short ones are stretched - one word 100 ms, two
        # letters 87, another word 66. The reason is the training input: its
        # median length was 47 characters, so a 7-character fragment is
        # outside the model's experience and the duration predictor gives it
        # too much time. Corrected only as far as needed, by re-synthesizing
        # with a proportionally smaller length_scale (one extra pass, RTF
        # 0.03). The 0.6 floor keeps speech from collapsing.
        if len(a) and len(fonemos) < TRUMPAS:
            greitis = 1000 * len(a) / self.sr / len(fonemos)      # ms fonemai
            if greitis > self.tikslinis_ms * 1.15:
                ls = max(self.length_scale * 0.6,
                         self.length_scale * self.tikslinis_ms / greitis)
                a = self._sintezuok(fonemos, ls)
        elif len(fonemos) >= ILGAS and len(a):
            # long fragments set this text's reference rate (running average)
            self._etalonas = (self._etalonas +
                              [1000 * len(a) / self.sr / len(fonemos)])[-5:]
            self.tikslinis_ms = float(np.median(self._etalonas))

        if len(a):
            self.zurnalas.append((frag, len(a) / self.sr,
                                  20 * float(np.log10(np.sqrt(np.mean(a ** 2)) + 1e-12))))
        return a

    def fragmentai(self, eil: str):
        """Eilutė -> [(tekstas, skyrybos ženklas po jo)], kableliai sujungti,
        kai bet kuri pusė trumpesnė nei min_zodziu žodžių (0 = skaidyti visada,
        kaip kadrų sintezuok_zinias)."""
        MIN_ZODZIU = self.min_zodziu
        dalys = (_ZENKLAI if self.kableli_skaidyti else _ZENKLAI_BE_KABLELIO).split(eil)
        poros = []
        for i in range(0, len(dalys), 2):
            frag = dalys[i].strip()
            zenklas = dalys[i + 1] if i + 1 < len(dalys) else ""
            if frag or zenklas:
                poros.append((frag, zenklas))
        out, cur = [], ""
        for k, (frag, zenklas) in enumerate(poros):
            cur = (cur + " " + frag).strip()
            if zenklas in SILPNI and zenklas:
                kitas = poros[k + 1][0] if k + 1 < len(poros) else ""
                if len(cur.split()) >= MIN_ZODZIU and len(kitas.split()) >= MIN_ZODZIU:
                    out.append((cur, zenklas))
                    cur = ""
                else:
                    cur += zenklas          # kablelis lieka modeliui
            else:
                out.append((cur, zenklas))
                cur = ""
        if cur:
            out.append((cur, ""))
        return out

    def _balso_lygis(self, a: np.ndarray) -> float:
        """Įgarsintų 10 ms kadrų RMS mediana, dB (tyla neskaičiuojama)."""
        lango = int(self.sr * 0.01)
        n = len(a) // lango
        if n == 0:
            return -99.0
        rms = 20 * np.log10(np.sqrt(np.mean(a[:n * lango].reshape(n, lango) ** 2, axis=1)) + 1e-12)
        garsus = rms[rms > -45]
        return float(np.median(garsus)) if len(garsus) else -99.0

    @staticmethod
    def _pikas_db(a: np.ndarray) -> float:
        return float(20 * np.log10(np.abs(a).max() + 1e-12))

    def _islygink_santrumpa(self, a: np.ndarray, zodziu_pikai) -> np.ndarray:
        """09-03 Roberto ausis: „trumpiniai nutyla, sunkiai įklausomi".
        Išmatuota: raidžių gabalų VIDURKIS toks pat kaip žodžių (−18 dB), bet
        PIKAI 2–4 dB žemesni (−6…−8 prieš −3…−4) — raidės tariamos plokščiau,
        o ausis girdi pikus. Keliam santrumpos piką iki gretimų ŽODŽIŲ gabalų
        pikų medianos, ne daugiau +4 dB, pikas ne aukščiau −1 dB."""
        if not zodziu_pikai:
            return a
        skirtumas = float(np.median(zodziu_pikai)) - self._pikas_db(a)
        if skirtumas <= 0.3:
            return a
        gain = 10 ** (min(skirtumas, 4.0) / 20)
        pikas = float(np.abs(a).max()) or 1.0
        gain = min(gain, 0.89 / pikas)
        return (a * gain).astype(np.float32)

    def gabalai(self, tekstas: str) -> Iterable[np.ndarray]:
        """Garso gabalai eilės tvarka (kalba ir pauzės) — srautui."""
        t = valyk_teksta(tekstas)
        if self.expand_text is not None:
            t = self.expand_text(t)
        zodziu_pikai = []           # žodžių gabalų pikai, dB (paskutiniai 6)
        for eil in t.splitlines():
            poros = self.fragmentai(eil)
            for i, (frag, zenklas) in enumerate(poros):
                pries = poros[i - 1][1] if i > 0 else ""
                santrumpa = (pries == "-" or zenklas == "-")
                if frag:
                    a = self._fragmentas(frag, santrumpa=santrumpa)
                    if a is not None and len(a):
                        if santrumpa:
                            a = self._islygink_santrumpa(a, zodziu_pikai)
                        else:
                            zodziu_pikai = (zodziu_pikai + [self._pikas_db(a)])[-6:]
                        yield a
                if zenklas:
                    yield self._tyla(self.pauze.get(zenklas, self.kablelis))
            yield self._tyla(0.15)
        yield self._tyla(0.7)

    def synthesize(self, tekstas: str) -> np.ndarray:
        return np.concatenate(list(self.gabalai(tekstas)) or [self._tyla(0.1)])


def i_int16(a: np.ndarray) -> bytes:
    return (np.clip(a, -1.0, 1.0) * 32767).astype(np.int16).tobytes()

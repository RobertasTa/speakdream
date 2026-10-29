# -*- coding: utf-8 -*-
"""NAUJOS AUSYS SEKRETOREI (2026-10-29): LT_ausys lietuviams, GigaAM v3 rusams.

Paimta iš Diktuoklės 0.2 (`DIKTUOKLE programa\\diktuokle\\ausys.py`, `modeliai.py`,
`parsisiuntimas.py`, 2026-10-25) — ten jos pamatuotos ir jau veikia žmonėms. Kopija, o ne
importas: programos savarankiškos (Roberto taisyklė 09-19 — „negali skolintis viena iš kitos").

Kodėl jos, o ne Whisper — Diktuoklės matavimai tame pačiame kompiuteryje
(`_darbal\\lt_ausys_palyginimas\\REZULTATAI.md` ten):

  LT  Roberto komandos   WER 17,9 %  (Paprika 23,2 %)
      ilgas diktavimas   WER 10,2 %  (Paprika 31,8 % — numeta pabaigas)
      procesoriuje 0,05 s komandai; skyrybą ir didžiąsias deda PATI.
  RU  FLEURS             WER  4,6 %  (large-v3 3,9 %), procesoriuje 0,11 s vietoj 7,2 s.

Abi sukasi PROCESORIUJE — vaizdo plokštės joms nereikia. Variklis `onnx-asr` (MIT).
Kodėl kol kas TIK sekretorei: vertėjo režime kalbą sprendžia ausų ginčas pagal Whisper
`avg_logprob` (`ausys.kas_ir_kuria_kalba`), o šios ausys tokio įverčio neduoda.

⚠️ ILGI GABALAI. Abi mokytos ant trumpų įrašų (≤ 20 s), o mūsų mikrofonas atiduoda iki 30 s
(`garsas.ILGIAUSIAS_GABALAS`). Todėl ilgesni kerpami TYLOS VIDURYJE; karpo Silero VAD, kuris
jau guli faster-whisper pakete. Jis atsako ir į klausimą, ar kalbos IŠ VISO buvo: tyloje
LT_ausys be jo prirašė 6 310 simbolių šiukšlių, su juo — 101 (Diktuoklės matavimas).
"""
import os

import numpy as np

# Langinėje programoje sys.stderr gali būti None — tqdm juosta tada nuverčia
# `snapshot_download` (Diktuoklės 2026-09-11 pamoka).
os.environ.setdefault('HF_HUB_DISABLE_PROGRESS_BARS', '1')

SR = 16000
MAX_S = 20                  # Diktuoklės spike: gabalai 9–21 s, nė vieno nukirsto žodžio

# Iš HF imam TIK int8 failus: lt-ausys repo turi ir fp32 (2,5 GB), gigaam — dar penkis
# variantus. Failų sąrašas = tai, ko onnx-asr 0.12.0 ieško (patikrinta Diktuoklėje 10-25).
# Dydžiai — HF API 2026-10-25, apvalinti į didesnę pusę.
ONNX_MODELIAI = {
    'lt_ausys': {
        'repo': 'RobertasTa/lt-ausys',
        'tipas': 'nemo-conformer-tdt',
        'failai': ['config.json', 'vocab.txt', 'encoder-model.int8.onnx',
                   'decoder_joint-model.int8.onnx'],
        'mb': 960,
    },
    'gigaam': {
        'repo': 'istupakov/gigaam-v3-onnx',
        'tipas': 'gigaam-v3-e2e-rnnt',
        'failai': ['config.json', 'v3_e2e_rnnt_vocab.txt', 'v3_e2e_rnnt_encoder.int8.onnx',
                   'v3_e2e_rnnt_decoder.int8.onnx', 'v3_e2e_rnnt_joint.int8.onnx'],
        'mb': 230,
    },
}


def _katalogas(raktas):
    from nustatymai import KATALOGAS
    return os.path.join(KATALOGAS, 'modeliai', raktas)


def onnx_kelias(raktas):
    """Katalogas, kuriame guli VISI modelio failai, arba None. Tikrinam kiekvieną failą:
    nutrūkęs parsisiuntimas palieka pusę katalogo."""
    k = _katalogas(raktas)
    if all(os.path.isfile(os.path.join(k, f)) for f in ONNX_MODELIAI[raktas]['failai']):
        return k
    return None


def parsisiusk(raktas):
    """Tik reikalingi failai į mūsų katalogą. → katalogas."""
    from huggingface_hub import snapshot_download
    m = ONNX_MODELIAI[raktas]
    vieta = _katalogas(raktas)
    os.makedirs(vieta, exist_ok=True)
    snapshot_download(m['repo'], local_dir=vieta, allow_patterns=m['failai'])
    return vieta


def gabalai(garsas):
    """[] — kalbos nėra; kitaip [(pradžia, pabaiga)] imtimis, kiekvienas ≤ ~MAX_S.

    Ilgas įrašas kerpamas tarp kalbos gabalų, tylos viduryje, o pradžia ir galas lieka
    kaip buvo (0 ir len) — kad nieko nenukirptume."""
    from faster_whisper.vad import VadOptions, get_speech_timestamps
    kalba = get_speech_timestamps(garsas, VadOptions(
        min_silence_duration_ms=300, speech_pad_ms=200, max_speech_duration_s=MAX_S))
    if not kalba:
        return []
    if len(garsas) <= MAX_S * SR:
        return [(0, len(garsas))]
    ribos, pr = [], 0
    for a, b in zip(kalba, kalba[1:]):
        if b['end'] - pr > MAX_S * SR:      # kitas gabalas nebetilptų — kerpam čia
            kirpti = (a['end'] + b['start']) // 2
            ribos.append((pr, kirpti))
            pr = kirpti
    ribos.append((pr, len(garsas)))
    return ribos


class OnnxAusys:
    """Vienas onnx-asr modelis iš katalogo (be tinklo — failus jau padėjo `parsisiusk`)."""

    def __init__(self, raktas, katalogas, gijos=0):
        import onnx_asr
        import onnxruntime as rt
        so = rt.SessionOptions()
        if gijos:
            so.intra_op_num_threads = gijos      # 0 — onnxruntime pats (fiziniai branduoliai)
        self.modelis = onnx_asr.load_model(ONNX_MODELIAI[raktas]['tipas'], katalogas,
                                           quantization='int8', sess_options=so)
        # Pirmas atpažinimas visada lėtesnis — tegu jis įvyksta ruošiantis, ne kalbant.
        self.modelis.recognize(np.zeros(SR, dtype=np.float32), sample_rate=SR)

    def atpazink(self, garsas):
        """float32, 16 kHz, mono → tekstas ('' — kalbos nebuvo)."""
        tekstas = ''
        for a, b in gabalai(garsas):
            d = self.modelis.recognize(garsas[a:b], sample_rate=SR).strip()
            if not d:
                continue
            # Ausys kiekvieną gabalą pradeda didžiąja — joms atrodo, kad tai sakinio pradžia.
            # Diktuoklėje 10-25: „močiutė var Virdavo" — kirpta per pauzę sakinio viduryje.
            # Jei ankstesnis gabalas sakinio NEBAIGĖ, mažinam. Visas didžiąsias („LDSP") paliekam.
            if tekstas and tekstas[-1] not in '.?!…' and d[:1].isupper() \
                    and not d.split()[0].isupper():
                d = d[0].lower() + d[1:]
            tekstas = '%s %s' % (tekstas, d) if tekstas else d
        return _tarpai(tekstas)


def _tarpai(tekstas):
    """LT_ausys kartais sulipdo ženklus. Diktuoklė 10-25: „spintą.„Kur", „kamuolys?“– paklausė";
    SpeakDream 10-29 (09-23 įrašas): „garsą„Jūsų" — prilipo ir prie RAIDĖS, tad čia platesnė
    taisyklė nei Diktuoklėje: prieš atidarančias kabutes „ tarpas po bet kokio ženklo.
    Brūkšnys, po kurio tarpas, gauna tarpą ir prieš; „1–2" neliečiamas."""
    import re
    tekstas = re.sub(r'(?<=\S)„', ' „', tekstas)
    return re.sub(r'(?<=\S)([–—])(?=\s)', r' \1', tekstas)

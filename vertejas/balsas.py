# -*- coding: utf-8 -*-
"""BALSAS: Piper (09-12).

Roberto sprendimas: programa statoma ant Piper, o ne ant savo įskiepių — kai Reginutė pateks
į `rhasspy/piper-voices`, ji atsiras pati, per tą patį kelią kaip visi kiti balsai.
Todėl balsų paieška eina TA TVARKA:
  1. oficialus Piper katalogas (`voices.json`, 176 balsai);
  2. jei tos kalbos ten nėra — mūsų pridėtas balsas (šiandien: lietuvių).

⚠️ Lietuvių kalbai kol kas DU skirtumai, abu laikini (išnyks sulietus PR #296):
  * `PiperVoice.load` neužsikrauna su mūsų konfigūracija (`phoneme_type: lithuanian`), todėl
    naudojam json kopiją su `espeak` ir fonemizuojam patys;
  * žalia modelio išvestis skamba blogai — imamas TAS PATS receptas, kuriuo Reginutė buvo
    išmokyta kalbėti (`lietuviskai/synth_reginute.py`): pauzės pagal skyrybą, tempo lyginimas,
    be normalizavimo (ji kirpdavo šio balso viršūnes).
"""
import json
import os
import sys

import numpy as np

CIA = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, CIA)
from piper import PiperVoice, SynthesisConfig

# ⛔ 2026-09-23: iki šiol čia stovėjo kietas kelias `D:\_Balsas Lietuviksas\...` — Reginutė
# veikė TIK Roberto kompe. Modelis imamas iš Piper katalogo (tas pats failas, SHA256
# 0417C4EF…86EE, PR #103), o konfigas — MŪSŲ `espeak` kopija (katalogo neužsikrauna).
REGINUTE_MODELIS = 'lt/lt_LT/reginute1/medium/lt_LT-reginute1-medium.onnx'
REGINUTE_JSON = os.path.join(CIA, 'balsai', 'lt_LT-reginute1-medium.onnx.json')
INGUTE_MODELIS = os.path.join(CIA, 'balsai', 'lt_LT-ingute-medium.onnx')
INGUTE_JSON = os.path.join(CIA, 'balsai', 'lt_LT-ingute-medium.onnx.json')
# v1.0.0 — tik Reginutė (Roberto sprendimas 09-23: Ingutė ateis su savo publikavimu, kartu
# nauja programos versija). Grąžinti Ingutę = įrašyti ją atgal į šiuos tris žodynus.
MUSU_BALSAI = {'lt': [('lt_LT-reginute1-medium', 'reginutė (medium)')]}
MUSU_FAILAI = {'lt_LT-reginute1-medium': (REGINUTE_MODELIS, REGINUTE_JSON)}
NUMATYTI = {'lt': 'lt_LT-reginute1-medium', 'ru': 'ru_RU-ruslan-medium',
            'en': 'en_US-lessac-medium', 'de': 'de_DE-thorsten-medium'}
# Ingutės tempas: aklas pasirinkimas iš trijų (1,00 / 1,15 / 1,30). Buvęs 1,30 buvo
# paveldėtas iš Reginutės konfigo ir Ingutei niekada nederintas, tad tai pagreitinimas.
INGUTE_LS = 1.15

# ⭐ BALSŲ GARSUMO SULYGINIMAS — pamatuota 2026-09-18 (`_matavimas\47_balsu_garsumas.py`).
#
# Robertas per kolonėlę: *„Ingutė kalba gerokai garsiau už Ruslaną, čia kažkaip reiktų
# suvienodinti."* Pamatavus integruotą LUFS (ITU-R BS.1770, K-svertimas — žr. `OKF_Garsumas`)
# paaiškėjo, kad iš modelio TRYS balsai praktiškai sutampa (−24,35 / −24,62 / −24,80 LUFS),
# o du išsiskiria: Reginutė +5,79 dB ir Lessac +4,23 dB.
#
# ⛔ Iš to matyti 09-16 klaida: Ingutė tada buvo sulyginta su REGINUTE, o pati Reginutė —
# su niekuo. Etalonu tapo garsiausias sąrašo balsas, ir Ingutė (kuri buvo normali) pakelta
# ×1,97 virš visų. Matas irgi buvo netinkamas — dBFS nežino, kad ausis vyrišką ir moterišką
# balsą prie tos pačios energijos girdi skirtingai.
#
# Tikslas — visų balsų MEDIANA (−24,35 LUFS), ne vieno balso lygis: taip nė vienas keistuolis
# netempia kitų ir neatsiranda naujo atsitiktinio etalono.
STIPRINIMAI = {
    'lt_LT-ingute-medium': 1.05,
    'lt_LT-reginute1-medium': 0.51,
    'ru_RU-ruslan-medium': 1.00,
    'en_US-lessac-medium': 0.61,
    'de_DE-thorsten-medium': 1.03,
}


RIBA = 250          # simbolių viena sinteze; ilgesnis tekstas pjaunamas ties sakinio pabaiga


def _dalyk(tekstas: str):
    """Ilgą tekstą — į gabalus iki RIBA simbolių, pjaunant TIK ties sakinio pabaiga.

    ⚠️ Ne grožio sumetimais: VITS dėmesio atmintis auga su sekos ilgiu kvadratiškai. 09-16
    namų kolonėlės serveryje (1 GB RAM) ilgas asistento atsakymas viena seka tarnybą pakišo
    OOM killer'iui. Čia atminties daugiau, bet skylė ta pati, tad ir apsauga ta pati.

    Trumpas tekstas grįžta vienas ir nepaliestas — toks, koks buvo aklai patvirtintas.
    """
    import re
    t = (tekstas or '').strip()
    if len(t) <= RIBA:
        return [t]
    dalys, dabar = [], ''
    for s in [x for x in re.split(r'(?<=[.!?…])\s+', t) if x.strip()]:
        if dabar and len(dabar) + 1 + len(s) > RIBA:
            dalys.append(dabar)
            dabar = s
        else:
            dabar = ('%s %s' % (dabar, s)).strip()
    if dabar:
        dalys.append(dabar)
    return dalys or [t]


def katalogas():
    """{kalbos kodas: [(raktas, rodomas vardas)]} iš Piper katalogo + mūsų pridėti balsai."""
    sarasas = {}
    try:
        from huggingface_hub import hf_hub_download
        d = json.load(open(hf_hub_download('rhasspy/piper-voices', 'voices.json'), encoding='utf-8'))
        for raktas, x in d.items():
            sarasas.setdefault(x['language']['family'], []).append(
                (raktas, '%s (%s)' % (x['name'], x['quality'])))
    except Exception:
        pass
    for kalba, musu in MUSU_BALSAI.items():
        jau = [r for r, _ in sarasas.get(kalba, [])]
        for raktas, pav in reversed(musu):
            if raktas not in jau:
                sarasas.setdefault(kalba, []).insert(0, (raktas, pav))
    return sarasas


def parsiusk(raktas: str):
    """Balso failai iš Piper katalogo (kešuojami). Mūsų balsams — vietinis kelias."""
    from huggingface_hub import hf_hub_download
    if raktas in MUSU_FAILAI:
        modelis, konfig = MUSU_FAILAI[raktas]
        if not os.path.isabs(modelis):
            modelis = hf_hub_download('rhasspy/piper-voices', modelis)
        return modelis, konfig
    kalba, vardas, kokybe = raktas.split('-')[0], raktas.split('-')[1], raktas.split('-')[2]
    seima = kalba.split('_')[0]
    kelias = '%s/%s/%s/%s/%s.onnx' % (seima, kalba, vardas, kokybe, raktas)
    m = hf_hub_download('rhasspy/piper-voices', kelias)
    hf_hub_download('rhasspy/piper-voices', kelias + '.json')
    return m, None


class Balsas:
    """Vienas balsas vienai kalbai."""

    def __init__(self, raktas: str, kalba: str):
        self.raktas = raktas
        self.kalba = kalba
        modelis, konfig = parsiusk(raktas)
        self.voice = PiperVoice.load(modelis, konfig) if konfig else PiperVoice.load(modelis)
        self.daznis = self.voice.config.sample_rate
        self._reginute = None
        self._fonemizatorius = None
        # Sulyginimas galioja VISIEMS mūsų siūlomiems balsams, ne tik lietuviškiems.
        # Piper kataloge yra 176 balsai; jų nematavom, tad jiems lieka 1,0.
        self.stiprinimas = STIPRINIMAI.get(raktas, 1.0)
        # Reginutės receptas savo numatytąjį tempą turi 1,30 (išmatuotas ant diktorės įrašų);
        # kitų balsų Piper numatytasis — 1,0. Nuo šio skaičiaus ir skaičiuojam vartotojo greitį.
        self.bazinis_ls = 1.0
        if kalba == 'lt' and raktas in MUSU_FAILAI:
            from lietuviskai.phonemize_lithuanian import LithuanianPhonemizer
            lt = os.path.join(CIA, 'lietuviskai')
            self._fonemizatorius = LithuanianPhonemizer(
                dictionary_path=os.path.join(lt, 'lt_kirciai.tsv'),
                letters_path=os.path.join(lt, 'lt_raides.tsv'),
                vocatives_path=os.path.join(lt, 'lt_kreipiniai.tsv'))
            if raktas == 'lt_LT-ingute-medium':
                # Ingutei recepto NETAIKOM. Aklas palyginimas 09-16: su receptu ji skamba
                # prasčiau nei be jo — receptas derintas Reginutės tempui (tikslinis ms
                # vienai fonemai susietas su jos `length_scale` 1,30), o Ingutė kalba 1,15.
                # Roberto verdiktas išklausius abu: „vo kitas reikalas, dabar tikrai Ingutė".
                self.bazinis_ls = INGUTE_LS
            else:
                from lietuviskai.synth_reginute import ReginuteSynth
                self._reginute = ReginuteSynth(self.voice, self._fonemizatorius)
                self.bazinis_ls = self._reginute.length_scale
                self.daznis = self._reginute.sr

    def sakyk(self, tekstas: str, greitis: float = 1.0, garsas: float = 1.0) -> np.ndarray:
        """`greitis`: 1,0 — balso numatytasis tempas; mažiau nei 1 — lėčiau, daugiau — greičiau.

        Robertas 09-12 19:10: „Ruslanas labai greitai kalba… gal tą greitintuvą į GUI galima
        būtų įmontuoti prie kiekvienos iš kalbų — gal kas supranta gerai greitesnę šneką,
        o kitam gali prireikti sulėtinti." Piper tam turi `length_scale`: didesnis = lėčiau,
        todėl mūsų „greitis" verčiamas atvirkščiai.
        """
        tekstas = (tekstas or '').strip()
        if not tekstas:
            return np.zeros(0, dtype='float32')
        mastelis = self.bazinis_ls / max(0.3, greitis)
        # ⛔ Stiprinimas taikomas ČIA — vienoje vietoje visiems trims keliams. Iki 09-18 jis
        # gyveno tik `_musu_fonemomis`, tad Reginutė ir bendrasis Piper kelias jo nematė:
        # sulyginti visų balsų tada nebūtų buvę įmanoma, kad ir kokį skaičių įrašytum.
        if self._reginute is not None:
            g = self._reginute_greiciu(mastelis).synthesize(tekstas)
            return self._sulygink(np.asarray(g, dtype='float32'), garsas)
        if self._fonemizatorius is not None:
            return self._sulygink(self._musu_fonemomis(tekstas, mastelis), garsas)
        gabalai = [np.frombuffer(x.audio_int16_bytes, dtype='int16')
                   for x in self.voice.synthesize(
                       tekstas, SynthesisConfig(length_scale=mastelis, normalize_audio=False))]
        if not gabalai:
            return np.zeros(0, dtype='float32')
        return self._sulygink(np.concatenate(gabalai).astype('float32') / 32768.0, garsas)

    def _sulygink(self, bangos: np.ndarray, garsas: float = 1.0) -> np.ndarray:
        """Balso sulyginimas × vartotojo slankiklis, su apsauga nuo kirpimo.

        Du daugikliai, du skirtingi dalykai: `stiprinimas` suveda visus balsus į vieną lygį
        (pamatuota 09-18), `garsas` yra žmogaus pasirinkimas šitam kambariui.

        Kirpimas skamba blogiau nei per tylus balsas, todėl viršūnė niekada neperžengia 0,95.
        """
        daugiklis = self.stiprinimas * (garsas or 1.0)
        if daugiklis == 1.0 or not bangos.size:
            return bangos
        bangos = bangos * daugiklis
        pikas = float(np.max(np.abs(bangos)))
        if pikas > 0.95:
            bangos = bangos * (0.95 / pikas)
        return bangos

    def _musu_fonemomis(self, tekstas: str, mastelis: float) -> np.ndarray:
        """Lietuviškas balsas BE recepto: fonemas paduodam patys.

        Reikia todėl, kad šio `piper` `PhonemeType` lietuvių kalbos dar neturi (ESPEAK, TEXT,
        PINYIN, HEBREW, JAPANESE, THAI) — ⚠️ o konfige palikus `espeak`, `voice.synthesize(tekstas)`
        fonemizuotų per espeak ir **apeitų visą mūsų kirčiavimą**: nei kirčių žodyno, nei
        priegaidžių, nei kreipinių taisyklės. 09-16 taip ir nutiko, ir tai buvo girdėti iškart.
        Išnyks, kai išeis Piper leidimas su PR #296 — tada užteks `phoneme_type: lithuanian`.
        """
        import re
        import unicodedata
        syn = SynthesisConfig(length_scale=mastelis, noise_scale=0.667,
                              noise_w_scale=0.8, normalize_audio=False)
        dalys = []
        for dalis in _dalyk(tekstas):
            ipa = self._fonemizatorius.phonemize_sentence(dalis)
            if not ipa:
                continue
            ids = self.voice.phonemes_to_ids(list(unicodedata.normalize('NFD', ipa)))
            g = self.voice.phoneme_ids_to_audio(ids, syn)
            if isinstance(g, tuple):
                g = g[0]
            dalys.append(np.asarray(g, dtype='float32'))
        if not dalys:
            return np.zeros(0, dtype='float32')
        # Stiprinimą taiko `sakyk` per `_sulygink` — čia jo nebekartojam, kitaip balsas
        # būtų pakeltas du kartus.
        return np.concatenate(dalys) if len(dalys) > 1 else dalys[0]

    def _reginute_greiciu(self, mastelis: float):
        """Reginutės recepte tempo lyginimas susietas su `length_scale`, todėl greičiui
        pakeisti kuriamas naujas receptas — modelis lieka tas pats, tad tai pigu."""
        if abs(mastelis - self._reginute.length_scale) < 0.01:
            return self._reginute
        from lietuviskai.synth_reginute import ReginuteSynth
        self._reginute = ReginuteSynth(self.voice, self._fonemizatorius, length_scale=mastelis)
        return self._reginute


class Balsai:
    """Du balsai — po vieną kiekvienai pusei; keičiami neperkraunant programos."""

    def __init__(self):
        self._balsai = {}

    def nustatyk(self, kalba: str, raktas: str, pranesk=None):
        if not raktas:
            self._balsai.pop(kalba, None)
            return None
        esamas = self._balsai.get(kalba)
        if esamas is not None and esamas.raktas == raktas:
            return esamas
        if pranesk:
            pranesk('Kraunu balsą (%s)…' % kalba)
        self._balsai[kalba] = Balsas(raktas, kalba)
        return self._balsai[kalba]

    def sakyk(self, kalba: str, tekstas: str, greitis: float = 1.0, garsas: float = 1.0):
        """`garsas` — vartotojo slankiklis (09-18), ATSKIRAS nuo balsų sulyginimo.

        Sulyginimas (`STIPRINIMAI`) yra tai, kas paverčia visus balsus vienodai garsiais;
        šitas daugiklis — kiek žmogus nori garsiau ar tyliau ŠITAM kambariui. Todėl jie
        dauginami, o ne vienas kitą pakeičia.
        """
        b = self._balsai.get(kalba)
        if b is None:
            return np.zeros(0, dtype='float32'), 22050
        return b.sakyk(tekstas, greitis, garsas), b.daznis

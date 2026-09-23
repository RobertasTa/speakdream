# -*- coding: utf-8 -*-
"""AUSYS: kas pasakyta ir KURIA KALBA (09-12).

Sprendimas iš matavimų (`_matavimas\\AUSYS_KALBA.md`):
  * Whisper kalbos detektorius (`detect_language`) trumpiems gabalams NETINKA — ties 1 s jis
    teisingas 13 % atvejų (blogiau nei moneta), ties 2 s — 49 %. Priežastis: jam paduodamas
    30 s langas, o 1 s garso jam beveik tyla.
  * Veikia kitaip: gabalą klauso ABI ausys, laimi ta, kurios pasitikėjimas (`avg_logprob`)
    didesnis. Ant viso gabalo iki pauzės — **98,5 %**, ir skirtumas didelis (pvz. lietuviškoms
    −0,02 prieš rusiškoms −0,78), tad sprendimas tvirtas.
  * Kaina — dvi transkripcijos vietoj vienos: pamatuota 1,04 s vienam gabalui.

Modeliai: lietuvių — Paprika (mūsų, kol `wyoming-faster-whisper` PR #122 nesulietas);
kitos kalbos — faster-whisper `medium` (ru WER 6,94 %, geriau nei mūsų pačių Paprika lietuviškai;
`large-v3` duotų 4,33 %, bet atimtų 3 GB iš plokštės).
"""
import os

import numpy as np

# Modelių aprašai rodomi LANGE, tad verčiami. `K`, o ne `kalba` — pastarasis čia yra
# funkcijų parametro vardas (`ausu_sarasas(kalba)`) ir modulį užgožtų.
import kalba as K

def _cuda_katalogai():
    """Kur paimti cuBLAS ir cuDNN, kurių reikia `ctranslate2` (ausims).

    ⛔ Iki 2026-09-19 čia stovėjo `%LOCALAPPDATA%\\Diktuokle\\cuda` — bibliotekos buvo
    pasiskolinamos iš KITOS mūsų programos. Kūrimo metu tai buvo protinga (netraukėm 1,6 GB
    antrą kartą), bet dovanai — siena: kas neturi Diktuoklės, tas neturi ir CUDA, o ausys
    kviečiamos su `device='cuda'`. Roberto sprendimas: *„jeigu Diktuoklė turi CUDA, tai turi
    turėti ir Vertėjas — atskiros programos, negali skolintis viena iš kitos."*

    ⭐ Ir mokėti už tai neteko: **torch jau atsineša visus vienuolika reikalingų DLL**
    (`cublas64_12`, `cublasLt64_12` ir visas `cudnn*_9` rinkinys, `torch\\lib`, 2026-09-19
    pamatuota). Vertėjas torch'ą tempia dėl Marian modelių, tad CUDA jame jau yra —
    nei parsisiųsti, nei pakuoti nieko papildomai nereikia.

    `find_spec` NEIMPORTUOJA torch (tai kainuotų sekundes paleidžiant) — tik pasako, kur jis.
    """
    keliai = []
    # `VERTEJAS_BE_TORCH_CUDA=1` — tik patikrai (`56_`): leidžia įsitikinti, kad be šio
    # kelio bibliotekų tikrai nelieka, ir kad „veikia" nereiškia „atsitiktinai guli PATH'e".
    if os.environ.get('VERTEJAS_BE_TORCH_CUDA') != '1':
        try:
            import importlib.util
            spec = importlib.util.find_spec('torch')
            if spec and spec.origin:
                keliai.append(os.path.join(os.path.dirname(spec.origin), 'lib'))
        except Exception:
            pass
    # Atsarginis kelias: jei šalia atsitiktinai yra Diktuoklė, jos rinkinys irgi tinka.
    # Tai ne priklausomybė, o paskutinė galimybė — pirmas visada torch.
    # ⭐ `VERTEJAS_BE_DIKTUOKLES=1` tą atsarginį kelią išjungia. Jungiklis reikalingas
    # PATIKRAI: šiame kompiuteryje Diktuoklė įdiegta, tad be jo neįmanoma įrodyti, kad
    # savarankiškumas tikras, o ne tik atrodo. (Diagnostinių jungiklių taisyklė — antirez.)
    if os.environ.get('VERTEJAS_BE_DIKTUOKLES') != '1':
        keliai.append(os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Diktuokle', 'cuda'))
    return [k for k in keliai if k and os.path.isdir(k)]


for _k in _cuda_katalogai():
    try:
        os.add_dll_directory(_k)
    except Exception:
        pass
    os.environ['PATH'] = _k + os.pathsep + os.environ.get('PATH', '')

from faster_whisper import WhisperModel

PAPRIKA_VIETINIS = r'D:\_Balsas Lietuviksas\_darbal\paprika-ct2-int8'
PAPRIKA_HF = 'RobertasTa/paprika-whisper-lt-v3-ct2-int8'
BENDRAS = 'Systran/faster-whisper-medium'

# Ausys renkamos KIEKVIENAI PUSEI ATSKIRAI (Robertas 09-12 16:50: „ar galima dėt skirtingas
# ausis kiekvienam iš pašnekovų?"). Priežastis gyva: lietuviui tinka mūsų specializuota Paprika,
# o rusui — didelis daugiakalbis modelis, nes per garsiakalbius sugautas garsas sunkus.
# WER pamatuotas 09-12 ant FLEURS (`AUSYS_KALBA.md`); dydžiai — ką reikės parsisiųsti.
AUSYS_SARASAS = [
    ('paprika', 'Paprika — lietuviškos (mūsų)', 'lt', '484 MB'),
    ('small',   'Whisper small — greitos',      None, '484 MB'),
    ('medium',  'Whisper medium — vidutinės',   None, '1,5 GB'),
    ('large-v3', 'Whisper large — tiksliausios', None, '3,1 GB'),
]
AUSU_KELIAI = {'small': 'Systran/faster-whisper-small',
               'medium': 'Systran/faster-whisper-medium',
               'large-v3': 'Systran/faster-whisper-large-v3'}
# Kurios ausys siūlomos kiekvienai kalbai iš karto.
NUMATYTOS = {'lt': 'paprika'}
NUMATYTOS_KITOMS = 'medium'


def ausu_sarasas(kalba: str):
    """[(raktas, rodomas vardas)] — tik tos ausys, kurios tai kalbai turi prasmę."""
    return [(r, '%s · %s' % (K.t(pav), dydis)) for r, pav, tik_kalbai, dydis in AUSYS_SARASAS
            if tik_kalbai is None or tik_kalbai == kalba]


def numatytos(kalba: str):
    return NUMATYTOS.get(kalba, NUMATYTOS_KITOMS)


def lietuviskos_ausys():
    """Kol Paprika nepateko į `wyoming-faster-whisper`, imam ją tiesiai; vėliau — iš katalogo."""
    return PAPRIKA_VIETINIS if os.path.isdir(PAPRIKA_VIETINIS) else PAPRIKA_HF


class Ausys:
    def __init__(self, kalbos=('lt', 'ru'), iranga='cuda', pasirinkimai=None):
        self.iranga = iranga
        self.kalbos = tuple(kalbos)
        # {kalba: ausų raktas}; ko nėra — numatytosios tai kalbai.
        self.pasirinkimai = {k: (pasirinkimai or {}).get(k) or numatytos(k) for k in self.kalbos}
        self._modeliai = {}

    def uzkrauk(self, pranesk=None):
        for k in self.kalbos:
            if pranesk:
                pranesk('Kraunu ausis (%s: %s)…' % (k, self.pasirinkimai.get(k)))
            self._modelis(k)
        # ⛔ Detektorius reikalingas TIK kai kalbos dvi — jis sprendžia, kuri iš jų skamba.
        # Su viena kalba (sekretorės režimas) `kas_ir_kuria_kalba` jį apeina jau pirmose
        # savo eilutėse, tad modelis būdavo užkraunamas ir NIEKADA nepaliečiamas.
        # ⭐ Kaina pamatuota 2026-09-19 (`_matavimas\53_vram.py`): sekretorei reikėjo
        # 3,15 GB vietoj 1,4 GB — 1,8 GB vaizdo atminties už nieką. Rasta ne skaitant kodą,
        # o matuojant: sekretorė be vertėjo ir be antrų ausų negalėjo būti beveik tokia pat
        # sunki kaip vertėjas, ir tas neatitikimas atvedė čia.
        if len(self.kalbos) > 1:
            self._detektorius()
        self._plokste_tikrai_veikia(pranesk)

    def _plokste_tikrai_veikia(self, pranesk=None):
        """Bandomasis atpažinimas; nepavykus — visos ausys perkraunamos į procesorių.

        ⛔ Be šito atsarginio kelio dovana pas žmogų BE NVIDIA lūžtų, ir lūžtų pačiu
        blogiausiu momentu. Priežastis užrašyta mūsų pačių guard'e (Rule 2): `ctranslate2`
        modelį į CUDA **užkrauna ir be cuBLAS** — „užsikrovė per 2,2 s" atrodo kaip sėkmė, o
        `cublas64_12.dll is not found` ateina tik pirmame `transcribe()`. Todėl krovimo
        try/except nesuveiktų NIEKADA; vienintelis būdas sužinoti — pabandyti atpažinti.

        Pusė sekundės tylos — tiek, kiek daro Diktuoklė. Kaina veikiančiai plokštei
        nedidelė, o kaina jos neturinčiam žmogui — ar programa iš viso veiks.
        """
        if self.iranga != 'cuda' or not self._modeliai:
            return
        try:
            tyla = np.zeros(8000, dtype=np.float32)
            modelis = next(iter(self._modeliai.values()))
            segmentai, _ = modelis.transcribe(tyla, language=self.kalbos[0],
                                              beam_size=1, vad_filter=False)
            list(segmentai)          # generatorius — be šito niekas neįvyksta
        except Exception:
            if pranesk:
                pranesk(K.t('Vaizdo plokštė netinka — pereinam į procesorių…'))
            self.iranga = 'cpu'
            self._modeliai.clear()
            for k in self.kalbos:
                self._modelis(k)
            if len(self.kalbos) > 1:
                self._detektorius()

    def _modelis(self, kalba):
        """Modelis pagal TOS PUSĖS pasirinkimą. Tas pats raktas dviem pusėms — vienas modelis."""
        raktas = self.pasirinkimai.get(kalba, NUMATYTOS_KITOMS)
        if raktas not in self._modeliai:
            kelias = lietuviskos_ausys() if raktas == 'paprika' else AUSU_KELIAI[raktas]
            tipas = 'int8' if raktas == 'paprika' else ('float16' if self.iranga == 'cuda' else 'int8')
            self._modeliai[raktas] = WhisperModel(kelias, device=self.iranga, compute_type=tipas)
        return self._modeliai[raktas]

    def _detektorius(self):
        """Kalbą sprendžia NEŠALIŠKAS modelis: Paprika specializuota ir lietuviškai girdi
        net rusišką kalbą, todėl detekcijai ji netinka (09-12 gyvas radinys)."""
        for kalba in self.kalbos:
            if self.pasirinkimai.get(kalba) != 'paprika':
                return self._modelis(kalba)
        # Abi pusės su specializuotomis ausimis — imam bendrąsias vien detekcijai.
        if 'detekcija' not in self._modeliai:
            self._modeliai['detekcija'] = WhisperModel(
                AUSU_KELIAI[NUMATYTOS_KITOMS], device=self.iranga,
                compute_type='float16' if self.iranga == 'cuda' else 'int8')
        return self._modeliai['detekcija']

    def klausyk(self, garsas: np.ndarray, kalba: str):
        seg, _ = self._modelis(kalba).transcribe(
            garsas, language=kalba, beam_size=1, vad_filter=False,
            condition_on_previous_text=False)
        seg = list(seg)
        if not seg:
            return '', -10.0
        return (' '.join(s.text.strip() for s in seg),
                float(np.mean([s.avg_logprob for s in seg])))

    def kuria_kalba(self, garsas: np.ndarray):
        """Kalbos tikimybės iš BENDRO modelio, imant tik mūsų kalbas. → (kalba, skirtumas).

        ⛔ 09-12 gyvai: sprendimas vien iš `avg_logprob` nuvedė klaidingu keliu. Rusišką blogerį
        Paprika „išgirdo" lietuviškai su −0,63, rusiškos ausys teisingai su −0,66, ir laimėjo
        trys šimtosios — programa vertė rusų kalbą į rusų. Priežastis pamatuota anksčiau:
        Paprika specializuota ir vienodai tikra ir teisi, ir klysdama, tad jos balsas ginče
        sveria per daug.

        Sprendimas: kalbą pirmiausia sako NEŠALIŠKAS detektorius (bendras modelis), o ausų
        ginčas lieka tik tada, kai jis dvejoja. Pamatuota ant 240 įrašų su triukšmu:
        vien detektorius 97,9 %, vien ausys 100 %, kartu **100 % ir 10 kartų greičiau**
        (0,09 s prieš 0,96 s), nes dažniausiai užtenka transkribuoti viena kalba.
        """
        _, _, visos = self._detektorius().detect_language(garsas)
        d = dict(visos)
        tikimybes = {k: float(d.get(k, 0.0)) for k in self.kalbos}
        eile = sorted(tikimybes, key=tikimybes.get, reverse=True)
        return eile[0], tikimybes[eile[0]] - (tikimybes[eile[1]] if len(eile) > 1 else 0.0), tikimybes

    def kas_ir_kuria_kalba(self, garsas: np.ndarray, riba: float = 0.5):
        """→ (kalba, tekstas, pasitikejimas, {kalba: (tekstas, pasitikejimas)}).

        Du keliai: kai detektorius tikras — transkribuojam TIK ta kalba; kai dvejoja —
        klausom abiem ausim ir lyginam pasitikėjimus, kaip anksčiau.
        """
        if len(self.kalbos) == 1:
            k = self.kalbos[0]
            tekstas, p = self.klausyk(garsas, k)
            return k, tekstas, p, {k: (tekstas, p)}
        spejimas, skirtumas, tikimybes = self.kuria_kalba(garsas)
        if skirtumas >= riba:
            tekstas, p = self.klausyk(garsas, spejimas)
            rez = {spejimas: (tekstas, p)}
            rez['_detektorius'] = ('%.2f skirtumas' % skirtumas, tikimybes.get(spejimas, 0.0))
            return spejimas, tekstas, p, rez
        rez = {k: self.klausyk(garsas, k) for k in self.kalbos}
        geriausia = max(rez, key=lambda k: rez[k][1])
        tekstas, pasitik = rez[geriausia]
        rez['_gincas'] = ('detektorius dvejojo (%.2f)' % skirtumas, 0.0)
        return geriausia, tekstas, pasitik, rez

    def atlaisvink(self):
        self._modeliai.clear()

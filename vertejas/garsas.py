# -*- coding: utf-8 -*-
"""GARSAS: mikrofonas, tylos daviklis ir grotuvas (09-12).

Čia sprendžiamas vienintelis klausimas, nuo kurio priklauso visa grandinė: KADA žmogus baigė
kalbėti. Pamatuota (`_matavimas\\PAUZES.md`, Roberto laisvos kalbos įrašas):
  * pauzių mediana 0,58 s, devyni iš dešimties trumpesni nei 1 s;
  * ties 1,0 s slenksčiu kalbėtojas nukertamas ~1 kartą per minutę, ties 0,8 s — 3,5 karto.
Todėl numatyta 1,0 s, o slankiklis lange leidžia 0,5–2,5 s ir veikia POKALBIO METU.

Antras sprendimas: KOL KOLONĖLĖ KALBA, AUSYS KURČIOS. Kitaip ji išverstų savo pačios vertimą.
EMEET turi aido slopinimą, bet pasikliauti juo negalima — pusiau dupleksas daromas čia.

Trečias: gabalo galas — DVIGUBA taisyklė (tyla + ar tekstas atrodo baigtas) buvo plane, bet
tekstą matome tik po atpažinimo, todėl čia lieka tik tyla, o „nebaigtą" gabalą prie kito
prijungia `variklis.py`.
"""
import queue
import threading
import time
from collections import deque

import numpy as np
import sounddevice as sd
from faster_whisper.vad import VadOptions, get_speech_timestamps

DAZNIS = 16000
REMAS = 0.032                  # 32 ms — tiek garso imam vienu kartu
# Kietai įrašytas slenkstis netinka: to paties kompiuterio mikrofonai skiriasi šimtus kartų.
# 09-12 Roberto kompe fonas buvo 0,00003, o slenkstis stovėjo 0,006 — kalbos jis nebūtų
# pagavęs NIEKADA. Todėl slenkstis nustatomas pagal TIKRĄ foną pirmąją sekundę.
FONO_LANGAS = 10.0             # s — per tiek atgal žiūrim, kas šiam mikrofonui yra tyla
FONO_DAUGIKLIS = 6.0           # kalba turi būti bent tiek kartų garsesnė už foną
MAZIAUSIAS_SLENKSTIS = 0.0004  # apsauga nuo visiškai mirusio mikrofono
ILGIAUSIAS_GABALAS = 30.0      # s — apsauga nuo žmogaus, kuris nedaro pauzių išvis
TRUMPIAUSIA_KALBA = 0.3        # s GRYNOS kalbos; trumpiau — spragtelėjimas


class Mikrofonas:
    """Klauso nuolat. Kai randa gabalą (kalba → tyla), atiduoda jį per `gabalai` eilę."""

    def __init__(self, irenginys=None, pauze=1.0):
        self.irenginys = irenginys
        self.pauze = pauze
        self.gabalai = queue.Queue()
        self.lygis = 0.0            # bangai lange
        self.tylos_dalis = 0.0      # juostelei lange
        self.kurcias = False        # True, kol kalba kolonėlė
        self.renka = False          # False — tik rodom bangą, gabalų nekaupiam
        self.irasas = None          # `GarsoIrasas`, kai pokalbis įrašinėjamas (09-18)
        self._dirba = False
        self._sriautas = None
        self._buferis = []
        self._tylos_pradzia = None
        self._kalbeta = False
        self._kalbos_remai = 0      # KALBOS rėmai, ne viso buferio: kitaip spragtelėjimas
                                     # su po jo einančia pauze atrodo kaip replika
        self.slenkstis = MAZIAUSIAS_SLENKSTIS
        self.fonas = 0.0
        self._fono_langas = deque(maxlen=int(FONO_LANGAS / REMAS))
        self._nuo_perskaiciavimo = 0

    # ---------- valdymas ----------
    def pradek(self):
        if self._dirba:
            return
        self._dirba = True
        self._buferis, self._tylos_pradzia, self._kalbeta = [], None, False
        self._kalbos_remai = 0
        self._fono_langas.clear()
        self.slenkstis = MAZIAUSIAS_SLENKSTIS
        self._sriautas = sd.InputStream(samplerate=DAZNIS, channels=1, dtype='float32',
                                        blocksize=int(DAZNIS * REMAS), device=self.irenginys,
                                        callback=self._remas)
        self._sriautas.start()

    def stok(self):
        self._dirba = False
        if self._sriautas is not None:
            self._sriautas.stop()
            self._sriautas.close()
            self._sriautas = None
        self.lygis = self.tylos_dalis = 0.0

    def klausyk(self, ar_klausyti: bool):
        """Ausys kurčios, kol kalba kolonėlė. Sugrįžus — buferis švarus."""
        self.kurcias = not ar_klausyti
        if not ar_klausyti:
            self._buferis, self._tylos_pradzia, self._kalbeta = [], None, False
            self._kalbos_remai = 0
            self.lygis = self.tylos_dalis = 0.0

    # ---------- srautas ----------
    def _remas(self, duomenys, kadru, laikas, busena):
        if not self._dirba:
            return
        g = duomenys[:, 0].copy()
        # ⭐ Garso įrašas gauna rėmą PIRMAS ir BE JOKIŲ sąlygų — net kai ausys kurčios
        # (kalba kolonėlė) ir net kai gabalų nerenkam. Kitaip įraše atsirastų spragos, ir
        # stenogramos laiko žymos nebesutaptų su vieta garse. `deda` daro tik `queue.put`.
        if self.irasas is not None:
            self.irasas.deda(g)
        rms = float(np.sqrt(np.mean(g * g) + 1e-12))
        # Banga rodo tiesą net kurčia būsena? Ne: kol kalba kolonėlė, rodome ramybę,
        # kitaip žmogus matytų „girdžiu" tada, kai negirdim.
        # Banga mastelį ima iš to paties slenksčio — kitaip tyliame mikrofone ji visada
        # gulėtų ant nulio, nors kalba girdima.
        self.lygis = 0.0 if self.kurcias else min(1.0, rms / max(1e-6, self.slenkstis * 3.0))
        if self.kurcias:
            return
        # Fonas sekamas NUOLAT, o ne matuojamas kartą pradžioje: imam 20-ą procentilį iš
        # paskutinių 3 s, tad net jei žmogus kalba beveik be perstojo, tyliausi rėmai vis tiek
        # parodo, kas šiam mikrofonui yra tyla. Taip prisitaikom ir prie kambario, kuriame
        # įsijungė ventiliatorius.
        self._fono_langas.append(rms)
        self._nuo_perskaiciavimo += 1
        if len(self._fono_langas) < 16:
            # Pirmas pusmetis sekundės: fono dar nežinom, o atsarginis slenkstis triukšmingame
            # mikrofone laikytų kalba net tylą. Todėl tik klausom. Žmogus tuo metu tikrai
            # nekalba: programa arba ką tik paleista, arba ką tik baigė sakyti vertimą.
            return
        if self._nuo_perskaiciavimo >= 8:
            self._nuo_perskaiciavimo = 0
            # 10-as procentilis per 10 s: net kalbant be perstojo, tarp žodžių lieka
            # mikropauzių, ir būtent jos parodo tikrąjį foną. 20-as procentilis per 3 s
            # ilgesnėje replikoje pakildavo iki paties balso ir nukirsdavo sakinį.
            self.fonas = float(np.percentile(self._fono_langas, 10))
            self.slenkstis = max(self.fonas * FONO_DAUGIKLIS, MAZIAUSIAS_SLENKSTIS)
        yra_kalba = rms > self.slenkstis
        dabar = time.time()
        if yra_kalba:
            self._kalbeta = True
            self._kalbos_remai += 1
            self._tylos_pradzia = None
            self.tylos_dalis = 0.0
            self._buferis.append(g)
        elif self._kalbeta:
            # Tyla PO kalbos — kaupiam ją kartu su garsu: jei žmogus tik stabtelėjo,
            # ta tyla turi likti gabalo viduje, o ne dingti.
            self._buferis.append(g)
            if self._tylos_pradzia is None:
                self._tylos_pradzia = dabar
            praejo = dabar - self._tylos_pradzia
            self.tylos_dalis = min(1.0, praejo / max(0.1, self.pauze))
            if praejo >= self.pauze:
                self._atiduok()
        if self._kalbeta and len(self._buferis) * REMAS >= ILGIAUSIAS_GABALAS:
            self._atiduok()

    def _atiduok(self):
        g = np.concatenate(self._buferis) if self._buferis else np.zeros(0, dtype='float32')
        kalbos_sek = self._kalbos_remai * REMAS
        self._buferis, self._tylos_pradzia, self._kalbeta = [], None, False
        self._kalbos_remai = 0
        self.tylos_dalis = 0.0
        # Sprendžia KALBOS kiekis, ne gabalo ilgis: durų trinktelėjimas (0,15 s) kartu su
        # po jo einančia 1,3 s tyla sudaro 1,45 s gabalą, kuris pagal ilgį atrodytų kaip replika.
        # Kol nepaspausta „Pradėti", mikrofonas jau klauso (kad banga rodytų tiesą ir būtų
        # galima pasitikrinti įrangą), bet gabalai niekur nededami — Roberto pastaba 09-12 16:24:
        # „mikrofono garso kreivę leisti tikrinti dar Play nepaspaudus… jei garso nėra, eini
        # kolonėlės derinti".
        if kalbos_sek >= TRUMPIAUSIA_KALBA and self.renka:
            self.gabalai.put(g)


class Grotuvas:
    """Groja vertimą. Kol groja — mikrofonas kurčias (pusiau dupleksas)."""

    def __init__(self, mikrofonas: Mikrofonas = None, irenginys=None):
        self.mikrofonas = mikrofonas
        self.irenginys = irenginys
        self.groja = False          # ar dabar kalba kolonėlė (09-18)
        self._uzraktas = threading.Lock()

    def nutrauk(self) -> bool:
        """Nutraukia tai, kas skamba, NEDELSIANT. → `True`, jei tikrai kažkas grojo.

        Grąžinama reikšmė svarbi: iš jos variklis sužino, ar „Baigti" buvo paspaustas
        kolonėlei kalbant. Jei taip — pabaigos frazių nebesako, nes Roberto sprendimas
        09-18 yra „stop reiškia stop".

        Roberto atvejis 09-18: *„pradėjom konferenciją, dėl kažkokių priežasčių ją reikia
        sustabdyti… o tie šnekoriai sau varo, kol nebaigs savo pasakojimų."* Be šito
        „Baigti" laukdavo, kol prisistatymas nuskambės iki galo — o jis ilgas.

        `sd.stop()` iš kitos gijos grąžina `sd.wait()` iš karto.
        """
        grojo = self.groja
        try:
            sd.stop()
        except Exception:
            pass
        return grojo

    def grok(self, garsas: np.ndarray, daznis: int):
        if garsas is None or not len(garsas):
            return
        if garsas.dtype == np.int16:
            garsas = garsas.astype('float32') / 32768.0
        with self._uzraktas:
            if self.mikrofonas:
                self.mikrofonas.klausyk(False)
            try:
                self.groja = True
                sd.play(garsas, daznis, device=self.irenginys)
                sd.wait()
            finally:
                self.groja = False
                # Trumpa atvanga: garsiakalbio uodega dar sklinda, o mikrofonas jau įjungtas.
                time.sleep(0.15)
                if self.mikrofonas:
                    self.mikrofonas.klausyk(True)


def ar_tikra_kalba(gabalas: np.ndarray) -> bool:
    """Silero VAD kaip antras sargas: energijos slenkstis praleidžia bildesį (durys, kėdė).

    Pamatuota 09-12: grynas energijos daviklis kapoja kalbą ties skiemenimis ir laiko kalba
    bet kokį trinktelėjimą; Silero atskiria balsą nuo triukšmo.
    """
    try:
        seg = get_speech_timestamps(gabalas, VadOptions(threshold=0.5, min_speech_duration_ms=200,
                                                        min_silence_duration_ms=300, speech_pad_ms=100),
                                    sampling_rate=DAZNIS)
        return bool(seg) and sum(s['end'] - s['start'] for s in seg) >= DAZNIS * 0.3
    except Exception:
        return True


def irenginiu_sarasas():
    """Mikrofonai žmogui: kiekvienas įrenginys VIENĄ kartą, gražiu vardu, veikiančiu keliu.

    ⛔ Iki 09-18 tas pats mikrofonas sąraše kartodavosi. Priežastis: PortAudio tą patį įrenginį
    rodo per kelis kelius (MME, DirectSound, WASAPI, WDM-KS), o **MME vardus kerpa ties 31
    simboliu**. Todėl „Microphone (EMEET OfficeCore Lu" ir „Microphone (EMEET OfficeCore Luna
    Plus)" atrodė kaip du skirtingi įrenginiai, ir žmogus natūraliai rinkdavosi antrąjį —
    gražesnį, pilnu vardu.

    ⛔ O jis **lūžta**: WASAPI keliu 16 kHz atidaryti negalima („Invalid sample rate", pamatuota
    su EMEET Luna Plus 09-18), ir programa nebūtų prasidėjusi iš viso.

    ⇒ Vardus lyginam ne tiksliai, o **pagal prefiksą**: jei vienas yra kito pradžia, tai tas pats
    įrenginys. Rodom ILGESNĮ vardą (jis pilnas), o naudojam PIRMĄ indeksą — `query_devices`
    grąžina MME pirmą, o jis 16 kHz priima.
    """
    matyti, sarasas = {}, []
    for i, d in enumerate(sd.query_devices()):
        if d['max_input_channels'] <= 0:
            continue
        vardas = d['name']
        rastas = None
        for turimas, vieta in matyti.items():
            if vardas.startswith(turimas) or turimas.startswith(vardas):
                rastas = vieta
                break
        if rastas is not None:
            # Tas pats įrenginys kitu keliu: indekso NEKEIČIAM, tik pasiimam pilnesnį vardą.
            if len(vardas) > len(sarasas[rastas][1]):
                sarasas[rastas] = (sarasas[rastas][0], vardas)
            continue
        matyti[vardas] = len(sarasas)
        sarasas.append((i, vardas))
    return sarasas


def irenginio_indeksas(vardas):
    """Įsimintą mikrofono VARDĄ paverčia šios akimirkos PortAudio indeksu.

    ⛔ Iki 2026-09-19 nustatymuose gulėjo pats indeksas. O jis slankioja: pamatuota
    gyvai — kai EMEET kolonėlė persijungė iš laido į dongle, `OfficeCore Luna Plus`
    galai iš sistemos dingo, ir visi už jo buvę įrenginiai pasislinko. Vertėjas tada
    tyliai imtų VISAI KITĄ mikrofoną — be klaidos, be pranešimo.

    ⛔ Vardo NEGALIMA paduoti `sounddevice`'ui tiesiai: jis pats rastų atitikmenį ir
    galėtų pagauti WASAPI kelią, o tas su šia kolonėle ties 16 kHz lūžta („Invalid
    sample rate", pamatuota 09-18). Todėl einam per `irenginiu_sarasas()` — ten jau
    parinktas veikiantis (MME) indeksas.

    Sena reikšmė (skaičius) praleidžiama nepakeista, tad seni nustatymai nelūžta.
    """
    if vardas is None or isinstance(vardas, int):
        return vardas
    sarasas = irenginiu_sarasas()
    for i, v in sarasas:
        if v == vardas:
            return i
    # Vardai kertami skirtinguose keliuose (MME – ties 31 simboliu), tad lyginam ir prefiksą.
    for i, v in sarasas:
        if v.startswith(vardas) or vardas.startswith(v):
            return i
    return None          # dingo (atjungtas) → sistemos numatytasis

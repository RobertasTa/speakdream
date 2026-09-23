# -*- coding: utf-8 -*-
"""GARSO ĮRAŠAS šalia stenogramos (Roberto sprendimas 2026-09-18).

Kam jis: stenogramoje kalbėtojo žodžiai yra **mašinos ausų versija**, ir iki šiol patikrinti
jos nebuvo kaip — ausų klaida atrodo lygiai taip pat, kaip teisingai išgirstas sakinys.
Robertas: *„gal šalia transkribų ir garso įrašą daryti? Tada išvis idealas būtų — net tada,
kai klaidų įsivėlė."* Su garsu kiekvieną eilutę galima pasitikrinti prie šaltinio.

Trys sprendimai, be kurių tai neveiktų:

1. **Rašom IŠTISAI, ne iškirptus kalbos gabalus.** Stenogramos žyma `[00:01:00]` turi rodyti į
   tą pačią vietą garse. Iškirpus tylą laikai išsiderintų ir patikra sugriūtų. FLAC tylą
   suspaudžia beveik iki nieko, tad tai nieko nekainuoja.
2. **Rašom atskira GIJA.** Mikrofono `callback` yra realaus laiko — disko operacija jame
   duotų pertrūkius garse. Callback tik įmeta rėmą į eilę (mikrosekundės).
3. **FLAC, ne OGG.** Patikrai reikia formato **be nuostolių**: suspaustas su nuostoliais garsas
   nebetinka ginčui, kas iš tikro nuskambėjo. Pamatuota tikru Roberto balsu:
   WAV 110 MB/val · **FLAC 23 MB/val** · OGG rašant lūžta (libsndfile).

⚠️ Įraše girdėsis ir pati kolonėlė — ji kalba tame pačiame kambaryje, ir mikrofonas ją gauna
net tada, kai ausys „kurčios". Tai teisinga: faile yra tai, kas kambaryje skambėjo.
"""
import os
import queue
import threading
import time

import numpy as np
import soundfile as sf

VARDAS = 'garsas.flac'
FORMATAS = 'FLAC'
POTIPIS = 'PCM_16'


class GarsoIrasas:
    """Ištisinis pokalbio įrašas. Gyvena tiek, kiek stenograma.

    Naudojimas:
        ir = GarsoIrasas(katalogas, daznis=16000)
        ir.deda(remas)      # iš mikrofono callback — TIK įmeta į eilę
        ir.uzverk()
    """

    def __init__(self, katalogas: str, daznis: int = 16000, pranesk=None):
        self.kelias = os.path.join(katalogas, VARDAS)
        self.daznis = daznis
        # ⭐ Įrašo NULIS. Stenograma ima jį savo atskaitos tašku, kad `[00:01:00]` rodytų į
        # 1:00 garso faile (Roberto reikalavimas: „kad galėtum būtent tą vietą atsisukti").
        # Kitaip stenograma pradėtų skaičiuoti nuo savo sukūrimo, o garsas — nuo savo.
        self.pradzia = time.time()
        self._pranesk = pranesk
        self._eile = queue.Queue()
        self._dirba = True
        self.sugedo = False
        self.sekundes = 0.0
        self._failas = None
        try:
            self._failas = sf.SoundFile(self.kelias, 'w', samplerate=daznis, channels=1,
                                        format=FORMATAS, subtype=POTIPIS)
        except Exception as e:
            self.sugedo = True
            self._dirba = False
            self._sakyk('atidaryti nepavyko (%s)' % e)
            return
        self._gija = threading.Thread(target=self._darbas, daemon=True)
        self._gija.start()

    def _sakyk(self, tekstas):
        if self._pranesk:
            try:
                self._pranesk('garso įrašas: ' + tekstas)
            except Exception:
                pass

    # ---------- iš mikrofono gijos ----------
    def deda(self, remas: np.ndarray):
        """Kviečiama iš realaus laiko callback — todėl daro TIK `put`, nieko daugiau."""
        if self._dirba:
            self._eile.put(remas)

    # ---------- rašymo gija ----------
    def _darbas(self):
        while True:
            try:
                remas = self._eile.get(timeout=0.2)
            except queue.Empty:
                if not self._dirba:
                    break
                continue
            if remas is None:
                break
            try:
                self._failas.write(remas)
                self.sekundes += len(remas) / float(self.daznis)
            except Exception as e:
                if not self.sugedo:
                    self.sugedo = True
                    self._sakyk('rašymas nutrūko (%s)' % e)
                break

    def uzverk(self):
        """Užveria failą, prieš tai išrašęs viską, kas dar eilėje."""
        if not self._dirba and self._failas is None:
            return
        self._dirba = False
        self._eile.put(None)
        try:
            self._gija.join(timeout=5.0)
        except Exception:
            pass
        try:
            if self._failas is not None:
                self._failas.close()
        except Exception:
            pass
        self._failas = None

    @property
    def megabaitai(self) -> float:
        try:
            return os.path.getsize(self.kelias) / 1048576.0
        except Exception:
            return 0.0

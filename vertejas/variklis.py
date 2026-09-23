# -*- coding: utf-8 -*-
"""VARIKLIS: sujungia garsą, ausis, vertėją ir balsą (09-12).

Dirba pagal `ALGORITMAS.md` — jei kas nors čia prasilenkia su tuo failu, klysta KODAS.

Gijos (kaip Diktuoklėje): langas NIEKADA nelaukia. Modelių krovimas ir kiekvieno gabalo
apdorojimas vyksta fone, o į langą eina Qt signalai. Vienintelis dalykas, kurį langas kviečia
tiesiogiai (`garso_lygis`, `tylos_dalis`), yra du skaičiai iš atminties.
"""
import os
import queue
import re
import threading
import time
import traceback
from datetime import datetime

from PyQt6.QtCore import QObject, pyqtSignal

import garsas as G
from ausys import Ausys
from balsas import Balsai
from frazes import (REPETICIJA, atsisveikinimas, lytis_pagal_balsa, pranesimas_apie_irasa,
                    pranesimas_apie_irasa_baigta, sveikinimas, sveikinimas_sekretores,
                    vardas_pagal_balsa)
from garso_irasas import VARDAS as GARSO_VARDAS
from garso_irasas import GarsoIrasas
# ⛔ Sąsajos kalba pasiekiama per `K`, ne per `kalba`: `kalba` šiame faile yra kintamasis
# 36 vietose (`for kalba, …`, parametrai, raktai), ir modulio vardas būtų tyliai užgožtas.
# ⚠️ Verčiam TIK tai, kas keliauja į EKRANĄ (`_pranesk`, `Klaida`). `_zurnalas` lieka
# lietuviškas — jis skirtas derinimui, ne vartotojui.
import kalba as K
from stenograma import Stenograma, naujas_katalogas
from vertimas import Vertejas

ZURNALO_KELIAS = os.path.join(os.environ.get('LOCALAPPDATA', os.path.expanduser('~')),
                              'SpeakDream', 'vertejas.log')


class Klaida(Exception):
    """Klaida, kurią galima pasakyti žmogui vienu sakiniu (skirtingai nuo pėdsako)."""


class Variklis(QObject):
    busena_sig = pyqtSignal(str, str)
    eilute_sig = pyqtSignal(str, str, str)
    baigta_sig = pyqtSignal()          # variklis sustojo pats — langas grąžina mygtukus
    paruosta_sig = pyqtSignal(bool)    # modeliai užkrauti (ar nepavyko) — langas atrakina „Pradėti"

    def __init__(self):
        super().__init__()
        self.langas = None
        self.mik = None
        self.grotuvas = None
        self.ausys = None
        self.vertejas = None
        self.balsai = Balsai()
        self.skyryba = None
        self.stenograma = None
        self.garso_irasas = None
        self.nust = {}
        self._gija = None
        self._dirba = False
        self._pauze = False
        self._nutildyta = False     # ar „Baigti" nutraukė kalbančią kolonėlę (09-18)
        self._paruosta = False      # ar modeliai jau užkrauti („Paruošti darbui", 09-18)
        self._kraunasi = False
        self._zurnalas_ijungtas = True
        # ⛔ Failus gali užverti DVI gijos: pabaigos gija (po atsisveikinimo) ir lango
        # uždarymas kryžiuku, kuris jos nelaukia. Be užrakto jos susidurtų viduryje.
        self._failu_uzraktas = threading.Lock()
        os.makedirs(os.path.dirname(ZURNALO_KELIAS), exist_ok=True)

    # ---------- ką kviečia langas ----------
    def garso_lygis(self):
        return self.mik.lygis if self.mik else 0.0

    def tylos_dalis(self):
        return self.mik.tylos_dalis if self.mik else 0.0

    def zurnalo_kelias(self):
        return ZURNALO_KELIAS

    def kalbos_pakeistos(self, a, b):
        pass          # kalbos paimamos paleidžiant; pokalbio metu jos užrakintos

    def stebek(self, irenginys=None):
        """Mikrofonas atidaromas IŠKART paleidus programą, dar nespaudus „Pradėti".

        Banga tada rodo tiesą ir įrangą galima pasitikrinti prieš pokalbį, o ne jo viduryje.
        Gabalai kol kas niekur nededami (`renka=False`).
        """
        try:
            if self.mik is not None:
                self.mik.stok()
            # Nustatymuose guli mikrofono VARDAS; indeksą randam šią akimirką.
            self.mik = G.Mikrofonas(G.irenginio_indeksas(irenginys), 1.0)
            self.mik.renka = False
            self.mik.pradek()
            self.grotuvas = G.Grotuvas(self.mik)
            return True
        except Exception as e:
            self._pranesk(K.t('Mikrofonas neatsidaro: %s')
                          % str(e).splitlines()[0], '#ff6a6a')
            self.mik = None
            return False

    def mikrofonas_pakeistas(self, irenginys):
        if not self._dirba:
            self.stebek(irenginys)

    def pauze_pakeista(self, sekundes):
        # Slankiklis veikia POKALBIO METU — tai buvo Roberto sąlyga.
        if self.mik:
            self.mik.pauze = sekundes

    def pradek(self):
        if self._dirba:
            return
        self.nust = self.langas.nustatymai() if self.langas else {}
        self._zurnalas_ijungtas = bool(self.nust.get('zurnalas', True))
        self._dirba, self._pauze, self._nutildyta = True, False, False
        self._gija = threading.Thread(target=self._darbas, daemon=True)
        self._gija.start()

    def pauze(self, ar):
        self._pauze = ar
        if self.mik:
            self.mik.klausyk(not ar)
        self.busena_sig.emit(K.t('Pauzė') if ar else K.t('Klausau'),
                             '#E8B84B' if ar else '#4ADE80')

    def baik(self):
        if not self._dirba:
            return
        self._dirba = False
        # ⛔ Pirma NUTILDOM tai, kas skamba, ir tik tada einam į pabaigą. Kitaip pabaigos
        # frazė atsistotų į eilę už dar tebeskambančio prisistatymo, ir „Baigti" atrodytų
        # neveikiantis (Robertas pagavo 09-18).
        # ⛔ Ir jei kolonėlė tuo metu KALBĖJO — pabaigos frazių nebesakom iš viso:
        # *„stop turėtų iškart sustabdyti bet kokią vertėjų kalbą, dabar jie dar tęsia
        # pabaigą"* (Roberto sprendimas 09-18). Ramiai baigiant pokalbį atsisveikinimas lieka.
        self._nutildyta = bool(self.grotuvas and self.grotuvas.nutrauk())
        threading.Thread(target=self._pabaiga, daemon=True).start()

    # ---------- darbas fone ----------
    def _pranesk(self, tekstas, spalva='#ffaa00'):
        self.busena_sig.emit(tekstas, spalva)

    def _ar_sekretore(self):
        return self.nust.get('rezimas') == 'sekretore'

    def pabandyk_balsa(self, kalba, raktas, lytis=None, greitis=1.0, garsas=1.0):
        """Duoda išgirsti pasirinktą balsą (Roberto prašymas 09-18).

        *„Šalia balsų ko gero reiktų mažo mygtuko, kad balsą pabandyti — ar tinkamą pasirinkai,
        ar būtent jį nori naudoti."* Iki tol balsą išgirsti buvo galima tik pradėjus pokalbį.

        Sako prisistatymą tuo pačiu vardu ir lytimi, kaip sakytų gyvai — tada girdi ne šiaip
        balsą, o tiksliai tą sakinį, kurį išgirs kambarys.
        """
        if self._dirba or self._kraunasi or not raktas:
            return
        threading.Thread(target=self._pabandyk_fone,
                         args=(kalba, raktas, lytis, greitis, garsas), daemon=True).start()

    def _pabandyk_fone(self, kalba, raktas, lytis, greitis, garsas=1.0):
        try:
            self._pranesk(K.t('Kraunu balsą…'))
            self.balsai.nustatyk(kalba, raktas, self._pranesk)
            vardas = vardas_pagal_balsa(raktas, kalba)
            tekstas = sveikinimas(kalba, vardas=vardas, lytis=lytis, trumpas=True)
            self._pranesk(K.t('Klausom: %s') % vardas, '#E8B84B')
            g, dz = self.balsai.sakyk(kalba, tekstas, greitis, garsas)
            if self.grotuvas:
                self.grotuvas.grok(g, dz)
            self._pranesk(K.t('Pasiruošęs') if not self._paruosta
                          else K.t('Paruošta — galima pradėti'),
                          '#e6e6e6' if not self._paruosta else '#4ADE80')
        except Exception as e:
            self._zurnalas('balso bandymas nepavyko: %s' % traceback.format_exc())
            self._pranesk(K.t('Balso paleisti nepavyko: %s')
                          % str(e).splitlines()[0][:60], '#ff6a6a')

    def _zurnalas(self, tekstas):
        if not self._zurnalas_ijungtas:
            return
        try:
            with open(ZURNALO_KELIAS, 'a', encoding='utf-8') as f:
                f.write('%s  %s\n' % (datetime.now().strftime('%H:%M:%S'), tekstas))
        except Exception:
            pass

    def _darbas(self):
        try:
            self._paruosk()
            if not self._dirba:
                return
            # `_pasisveikink` nuo 09-18 pats sprendžia kiekvienai pusei atskirai: prisistatymas,
            # vien pranešimas apie įrašymą, ar nieko. Atskiros šakos čia nebereikia.
            self._pasisveikink()
            self._pranesk(K.t('Klausau'), '#4ADE80')
            if self._ar_sekretore():
                self._ciklas_sekretore()
            else:
                self._ciklas()
        except Klaida as e:
            self._zurnalas('SUSTOJO: %s' % e)
            self._pranesk(str(e), '#ff6a6a')
            self._dirba = False
            self.baigta_sig.emit()
        except Exception:
            self._zurnalas('KLAIDA: ' + traceback.format_exc())
            self._pranesk(K.t('Klaida — žr. žurnalą (⚙)'), '#ff6a6a')
            self._dirba = False
            self.baigta_sig.emit()

    def paruosk_darbui(self):
        """„Paruošti darbui" — modeliai kraunami PRIEŠ pokalbį (Roberto sprendimas 09-18).

        *„Kiek keistai atrodo, kai paspaudi pradėti — vyksta žodynų, kalbos modulių užkrovimas.
        Aš manau, Play tai jau dirbam."* Todėl ilgas krovimas atskirtas nuo pokalbio pradžios:
        paruošimas trunka tiek, kiek trunka, o „Pradėti" nuo šiol reiškia „kalbam".
        """
        if self._paruosta or self._kraunasi or self._dirba:
            return
        self._kraunasi = True
        self.nust = self.langas.nustatymai() if self.langas else {}
        self._zurnalas_ijungtas = bool(self.nust.get('zurnalas', True))
        threading.Thread(target=self._kraunam_fone, daemon=True).start()

    def _kraunam_fone(self):
        try:
            self._kraukk_modelius()
            self._paruosta = True
            self._pranesk(K.t('Paruošta — galima pradėti'), '#4ADE80')
        except Klaida as e:
            self._zurnalas('PARUOŠIMAS SUSTOJO: %s' % e)
            self._pranesk(str(e), '#ff6a6a')
        except Exception:
            self._zurnalas('KLAIDA ruošiant: ' + traceback.format_exc())
            self._pranesk(K.t('Klaida — žr. žurnalą (⚙)'), '#ff6a6a')
        finally:
            self._kraunasi = False
            self.paruosta_sig.emit(self._paruosta)

    def atlaisvink(self):
        """Paruošimas atšaukiamas (pakeistos kalbos ar balsai) — modeliai išmetami."""
        self._paruosta = False
        if self.vertejas:
            self.vertejas.atlaisvink()
            self.vertejas = None
        if self.ausys:
            self.ausys.atlaisvink()
            self.ausys = None
        self.skyryba = None

    def _paruosk(self):
        # Jei „Paruošti darbui" nebuvo spausta, kraunam čia pat — senas kelias lieka gyvas.
        if not self._paruosta:
            self._kraukk_modelius()
        self._pradek_pokalbi()

    def _kraukk_modelius(self):
        a, b = self.nust['a_kalba'], self.nust['b_kalba']
        sekretore = self._ar_sekretore()
        # Sekretorės režimu antra pusė nedalyvauja: kalba viena, vertimo nėra, tad ir
        # „abi pusės ta pačia kalba" nėra klaida.
        if not sekretore and a == b:
            raise Klaida(K.t('Abi pusės kalba ta pačia kalba — versti nėra ko.'))
        data = datetime.now().strftime('%Y-%m-%d %H:%M')
        if sekretore:
            self._zurnalas('--- PRADŽIA (sekretorė) %s: %s, pauzė %.1f s'
                           % (data, a, self.nust['pauze']))
        else:
            self._zurnalas('--- PRADŽIA %s: %s <-> %s, pauzė %.1f s'
                           % (data, a, b, self.nust['pauze']))
        self._pranesk(K.t('Kraunu ausis…'))
        kalbos = (a,) if sekretore else tuple(dict.fromkeys([a, b]))
        pasirinkimai = {a: self.nust.get('a_ausys')}
        if not sekretore:
            pasirinkimai[b] = self.nust.get('b_ausys')
        self.ausys = Ausys(kalbos=kalbos, pasirinkimai=pasirinkimai)
        self.ausys.uzkrauk(self._pranesk)
        # Skyryba tarp ausų ir vertėjo: pamatuota 4,12 → 5,00 (žr. `skyryba.py` antraštę).
        self._pranesk(K.t('Kraunu skyrybą…'))
        try:
            from skyryba import Punctuator
            self.skyryba = Punctuator()
        except Exception as e:
            self.skyryba = None
            self._zurnalas('skyryba neužsikrovė (%s) — verčiam be jos' % str(e).splitlines()[0][:80])
        # ⭐ Sekretorei vertėjo NEKRAUNAM iš viso — ji neverčia. Tai ne tik greičiau: abu
        # Marian modeliai nebeužima vaizdo atminties, o jos kiekis mums yra atskiras
        # klausimas (`BUSENA.md` — Roberto užduotis pamatuoti prieš viešinimą).
        if not sekretore:
            self._pranesk(K.t('Kraunu vertėją…'))
            self.vertejas = Vertejas()
            for is_k, i_k in ((a, b), (b, a)):
                if not self.vertejas.ar_moka(is_k, i_k):
                    raise Klaida(K.t('Nemoku versti %s → %s.') % (is_k, i_k))
            self.vertejas.uzkrauk([(a, b), (b, a)], self._pranesk)
        # Balsas sekretorei reikalingas tik vienas — prisistatyti ir pasakyti, kad baigė.
        poros = [(a, self.nust['a_balsas'])]
        if not sekretore:
            poros.append((b, self.nust['b_balsas']))
        for kalba, raktas in poros:
            if not raktas:
                raise Klaida(K.t('Kalbai „%s" nepasirinktas balsas.') % kalba)
            self.balsai.nustatyk(kalba, raktas, self._pranesk)
    def _pradek_pokalbi(self):
        """Tai, kas turi vykti nuo „Pradėti", o ne nuo paruošimo: mikrofonas pradeda rinkti,
        atsidaro stenograma ir garso įrašas. ⛔ Stenograma NEGALI prasidėti su paruošimu —
        jos nulis turi sutapti su pokalbio pradžia."""
        a, b = self.nust['a_kalba'], self.nust['b_kalba']
        # Mikrofonas jau klauso nuo programos paleidimo (`stebek`) — dabar tik pasakom
        # pauzės ilgį ir įjungiam gabalų rinkimą.
        if self.mik is None and not self.stebek(self.nust.get('mikrofonas')):
            raise Klaida(K.t('Nepavyko atidaryti mikrofono.'))
        self.mik.pauze = self.nust['pauze']
        while not self.mik.gabalai.empty():
            self.mik.gabalai.get()          # ką girdėjo iki „Pradėti" — neverčiam
        self.mik.renka = True
        self._pradek_stenograma(a, b)

    def _pradek_garso_irasa(self, katalogas):
        """Garso įrašas guli TAME PAČIAME kataloge kaip stenograma — jie priklauso vienas
        kitam: tekstas sako, kas buvo pasakyta, garsas leidžia tai pasitikrinti.

        Įrašo nebuvimas pokalbio nestabdo (stenograma lieka), bet ir nenutylimas: žmogui buvo
        pasakyta, kad įrašinėsim.
        """
        self.garso_irasas = None
        if not self.nust.get('garso_irasas', True):
            self._zurnalas('garso įrašas išjungtas')
            return
        try:
            self.garso_irasas = GarsoIrasas(katalogas, G.DAZNIS, pranesk=self._zurnalas)
            if self.garso_irasas.sugedo:
                self.garso_irasas = None
                raise Klaida('failo atidaryti nepavyko')
            if self.mik is not None:
                self.mik.irasas = self.garso_irasas
            self._zurnalas('garso įrašas: %s' % self.garso_irasas.kelias)
        except Exception as e:
            self.garso_irasas = None
            self._zurnalas('garso įrašo pradėti nepavyko (%s)' % e)
            self._pranesk(K.t('Garso įrašyti nepavyko — stenograma rašoma'), '#ffaa00')

    def _pradek_stenograma(self, a, b):
        """Stenograma atidaroma PRIEŠ sveikinimą — nuo jo ir prasideda pokalbio laikas."""
        self.stenograma = None
        sekretore = self._ar_sekretore()
        # ⛔ Sekretorės režime stenogramos išjungti negalima — visas režimas yra ji viena
        # (`ALGORITMAS.md` 10.6). Varnelė dantratyje jam įtakos neturi.
        if not sekretore and not self.nust.get('stenograma', True):
            self._zurnalas('stenograma išjungta')
            return
        try:
            kalbos = [a] if sekretore else [a, b]
            balsai = {a: self.nust.get('a_balsas')}
            lytys = {a: self.nust.get('a_lytis')}
            if not sekretore:
                balsai[b] = self.nust.get('b_balsas')
                lytys[b] = self.nust.get('b_lytis')
            # ⛔ Eilė svarbi: katalogas → GARSAS → stenograma. Antraštėje rašom, kad laiko
            # žymos atitinka vietą įraše, tad įrašas turi būti jau tikrai atidarytas —
            # kitaip failas žadėtų tai, ko nėra.
            katalogas = naujas_katalogas()
            self._pradek_garso_irasa(katalogas)
            self.stenograma = Stenograma(
                kalbos, balsai=balsai, lytys=lytys, sekretore=sekretore,
                pranesk=self._zurnalas, katalogas=katalogas,
                garso_vardas=(GARSO_VARDAS if self.garso_irasas is not None else None),
                pradzia=(self.garso_irasas.pradzia if self.garso_irasas is not None else None))
            self._zurnalas('stenograma: %s' % self.stenograma.katalogas)
        except Exception as e:
            self.stenograma = None
            self._zurnalas('stenogramos pradėti nepavyko (%s)' % e)
            # Sekretorei stenograma yra VISAS darbas — be jos tęsti nėra ko, ir tylus
            # „veikiu" būtų melas. Vertėjui tai tik praradimas: pokalbis verčiamas toliau.
            if self._ar_sekretore():
                raise Klaida(K.t('Nepavyko pradėti stenogramos — '
                                 'sekretorė be jos neturi ką veikti.'))
            self._pranesk(K.t('Stenogramos rašyti nepavyko — pokalbis verčiamas be jos'),
                          '#ffaa00')

    def _sakyk(self, kalba, tekstas, butinai=False):
        """Kolonėlės balsas. Kol groja — ausys kurčios (pusiau dupleksas `garsas.py`).

        Greitis imamas iš lango KIEKVIENĄ KARTĄ, ne iš paleidimo nustatymų: slankiklis veikia
        pokalbio metu, kaip ir pauzė.

        → `True`, jei tikrai pasakyta. ⛔ Paspaudus „Baigti" nutylam **nedelsiant** ir net
        nesintezuojam kitos frazės: Roberto atvejis 09-18 — sustabdžius konferenciją
        prisistatymas varydavo iki galo. `butinai=True` — pabaigos pranešimai, kurių
        nutildyti negalima (10.6 sk.: „išjungti galima viską, išskyrus pranešimą apie įrašymą").
        """
        if not butinai and not self._dirba:
            return False
        greitis, garsas = 1.0, 1.0
        if self.langas:
            puse = 'a' if kalba == self.nust.get('a_kalba') else 'b'
            try:
                p = self.langas.a if puse == 'a' else self.langas.b
                greitis = p.dabartinis_greitis()
                garsas = p.dabartinis_garsas()
            except Exception:
                pass
        g, dz = self.balsai.sakyk(kalba, tekstas, greitis, garsas)
        # Sintezė gali trukti — per tą laiką „Baigti" jau galėjo būti paspaustas.
        if not butinai and not self._dirba:
            return False
        self.grotuvas.grok(g, dz)
        return True

    def _pasisveikink(self):
        rasom_garsa = self.garso_irasas is not None
        # Būseną rodom tik tada, kai tikrai kas nors nuskambės: jei abu prisistatymai išjungti
        # ir nieko nerašom, „Prisistatau…" būtų melas ekrane.
        if (self.nust.get('sveikintis_a', True) or self.nust.get('sveikintis_b', True)
                or self.stenograma is not None or rasom_garsa or self._ar_sekretore()):
            self._pranesk(K.t('Prisistatau…'))
        if self._ar_sekretore():
            # Roberto sprendimas 09-18: sekretorė TRUMPAI prisistato ją įjungus, kad visi
            # žinotų, jog bus stenografuojama. Viena kalba — kambaryje ji viena.
            kalba = self.nust['a_kalba']
            t = sveikinimas_sekretores(
                kalba, vardas_pagal_balsa(self.nust.get('a_balsas'), kalba),
                lytis_pagal_balsa(self.nust.get('a_balsas')), garsas=rasom_garsa)
            self._zurnalas('sekretorės prisistatymas [%s]: %s' % (kalba, t))
            self._sakyk(kalba, t)
            return
        trumpai = bool(self.nust.get('trumpai'))
        rasom = self.stenograma is not None
        # ⭐ Prisistatymas KIEKVIENAI PUSEI atskirai (Roberto sumanymas 09-18): šeimininkas
        # programą sustatė pats ir jos pasakojimo nereikia, o svečiui gali būti pirmas kartas.
        # Abu prisistatymai ~17 s, vienas ~9 s.
        sveikinom_a = False
        for puse in ('a', 'b'):
            kalba = self.nust[puse + '_kalba']
            # Vardas — iš PASIRINKTO BALSO: su `vardas=None` Ingutė prisistatydavo Reginute.
            vardas = vardas_pagal_balsa(self.nust.get(puse + '_balsas'), kalba)
            if self.nust.get('sveikintis_' + puse, True):
                t = sveikinimas(kalba, vardas=vardas, lytis=self.nust[puse + '_lytis'],
                                pauze=self.nust['pauze'], trumpas=trumpai, stenograma=rasom,
                                garsas=rasom_garsa)
                self._zurnalas('sveikinimas [%s]: %s' % (kalba, t))
                sveikinom_a = sveikinom_a or puse == 'a'
            elif rasom or rasom_garsa:
                # ⛔ Prisistatymo šiai pusei nesakom, bet apie ĮRAŠYMĄ pasakom (10.6 sk.):
                # nutylėjus ji nežinotų, kad įrašinėjama, ir negalėtų nesutikti.
                t = pranesimas_apie_irasa(kalba, garsas=rasom_garsa)
                self._zurnalas('tik pranešimas apie įrašymą [%s]: %s' % (kalba, t))
            else:
                continue
            self._sakyk(kalba, t)
        # Repeticija yra prisistatymo dalis ir sakoma šeimininko kalba — be jo prisistatymo
        # ji kabėtų ore.
        if not trumpai and sveikinom_a:
            k = self.nust['a_kalba']
            self._sakyk(k, REPETICIJA[k])

    # Kiek žodžių gali tekti vienam skyrybos ženklui, kad tekstą dar laikytume „su skyryba".
    # Paprika ir mūsų lietuviškos ausys skyrybos neduoda VISAI — jų tekste ženklų nė vieno.
    ZODZIU_VIENAM_ZENKLUI = 15

    @staticmethod
    def _jau_su_skyryba(tekstas: str) -> bool:
        """Ar ausys skyrybą jau davė pačios.

        ⛔ Rasta 09-18 gyvo testo stenogramoje: rusiškose eilutėse buvo `,,` `,,,` `..` — nes
        Whisper rusų kalbai skyrybą grąžina PATS, o mes dėjom `punct_restore` ant viršaus.
        Lietuviškose eilutėse to nebuvo: Paprika skyrybos neduoda, ir atstatymas dirba švariai.
        """
        zenklu = sum(tekstas.count(z) for z in '.,!?;:')
        if not zenklu:
            return False
        zodziu = len(tekstas.split())
        return zenklu >= max(1, zodziu / Variklis.ZODZIU_VIENAM_ZENKLUI)

    @staticmethod
    def _be_dubliu(tekstas: str) -> str:
        """Tinklelis: `,,` → `,`, `..` → `.`, `.,` → `.`, tarpas prieš ženklą — šalin.

        Reikalingas ir tada, kai atstatymas praleistas: ausys kartais pačios grąžina `..`.
        Daugtaškio (`…` arba `...`) NELIEČIAM — tai prasminga skyryba.
        """
        t = re.sub(r'\.{4,}', '...', tekstas)
        t = re.sub(r'(?<![.…])([,;:!?])[\s]*(?:[,;:!?]\s*)+', r'\1 ', t)
        t = re.sub(r'(?<!\.)\.\.(?!\.)', '.', t)
        t = re.sub(r'\.\s*,', '.', t)
        t = re.sub(r'\s+([,.;:!?])', r'\1', t)
        return re.sub(r'\s{2,}', ' ', t).strip()

    def _skyryba(self, tekstas):
        """Ausų tekstas be taškų → su taškais. Grąžina (tvarkingas, sekundės)."""
        if self.skyryba is None:
            return self._be_dubliu(tekstas), 0.0
        # ⛔ Jei ausys skyrybą jau davė, atstatymo NEBEKARTOJAM: jis nieko neprideda, kainuoja
        # ~0,25 s ir gamina dvigubus ženklus. Vertimui tekstas ir taip tinkamas.
        if self._jau_su_skyryba(tekstas):
            return self._be_dubliu(tekstas), 0.0
        ts = time.time()
        try:
            r = self.skyryba.restore(tekstas)
            tvarkingas = (r[0] if isinstance(r, tuple) else r) or tekstas
        except Exception:
            tvarkingas = tekstas
        return self._be_dubliu(tvarkingas), time.time() - ts

    def _ciklas_sekretore(self):
        """SEKRETORĖ: tas pats garsas ir ausys, tik be vertimo ir be balso.

        Viskas, kas nuskamba, eina į VIENĄ failą — kalba viena (`ALGORITMAS.md` 10.1).
        Pusiau duplekso čia nereikia, nes kolonėlė pokalbio metu tyli: ji prabilo tik
        prisistatydama ir prabils tik pasakydama, kad baigė.

        ⛔ Santraukos nedarom. Sekretorė užrašo, bet neapibendrina (6 sk.).
        """
        kalba = self.nust['a_kalba']
        while self._dirba:
            try:
                gabalas = self.mik.gabalai.get(timeout=0.2)
            except queue.Empty:
                continue
            if not self._dirba or self._pauze:
                continue
            t0 = time.time()
            if not G.ar_tikra_kalba(gabalas):
                self._zurnalas('praleista: ne kalba (%.1f s garso)' % (len(gabalas) / G.DAZNIS))
                continue
            self._pranesk(K.t('Užrašau…'), '#E8B84B')
            _, tekstas, pasitik, visos = self.ausys.kas_ir_kuria_kalba(gabalas)
            t_ausys = time.time() - t0
            if not tekstas.strip():
                self._pranesk(K.t('Klausau'), '#4ADE80')
                continue
            # Skyryba reikalinga ir be vertimo: failą skaitys žmogus, o ausys taškų neduoda.
            tvarkingas, t_sk = self._skyryba(tekstas)
            self._zurnalas('[%s] %.1f s garso | ausys %.2f s skyryba %.2f s\n    girdėjau: %s'
                           % (kalba, len(gabalas) / G.DAZNIS, t_ausys, t_sk, tvarkingas))
            if self.stenograma is not None:
                kada = self.stenograma.nuo_pradzios(t0 - len(gabalas) / G.DAZNIS)
                self.stenograma.zmogus(kalba, tvarkingas, kada)
            # Antrasis langelis („KAS IŠVERSTA") sekretorės režimu lieka tuščias — versti
            # nėra ko, o tuščia eilutė ten geriau nei sugalvotas turinys.
            self.eilute_sig.emit(tvarkingas, '', kalba)
            self._pranesk(K.t('Klausau'), '#4ADE80')

    def _ciklas(self):
        a, b = self.nust['a_kalba'], self.nust['b_kalba']
        while self._dirba:
            try:
                gabalas = self.mik.gabalai.get(timeout=0.2)
            except queue.Empty:
                continue
            if not self._dirba or self._pauze:
                continue
            t0 = time.time()
            if not G.ar_tikra_kalba(gabalas):
                self._zurnalas('praleista: ne kalba (%.1f s garso)' % (len(gabalas) / G.DAZNIS))
                continue
            self._pranesk(K.t('Verčiu…'), '#E8B84B')
            kalba, tekstas, pasitik, visos = self.ausys.kas_ir_kuria_kalba(gabalas)
            t_ausys = time.time() - t0
            if not tekstas.strip():
                self._pranesk(K.t('Klausau'), '#4ADE80')
                continue
            if kalba not in (a, b):
                self._zurnalas('praleista: nesava kalba %s' % kalba)
                self._pranesk(K.t('Klausau'), '#4ADE80')
                continue
            i_kalba = b if kalba == a else a
            # Ausų tekstas be skyrybos vertėjui yra svetimas — atstatom prieš verčiant.
            # ⛔ Per `_skyryba`, o NE sava kopija. Iki 09-18 vakaro čia stovėjo atskiras,
            # beveik toks pat blokas, o `_skyryba` metodą kvietė tik sekretorė — tad dvigubos
            # skyrybos taisymas į vertėjo kelią nepateko. Robertas tai pamatė iškart:
            # žurnale eilutė buvo švari (ten rašomas AUSŲ tekstas), o stenogramoje ta pati
            # replika turėjo „Привет!," ir „кавычками??" (ten rašomas APDOROTAS).
            tvarkingas, t_sk = self._skyryba(tekstas)
            t1 = time.time()
            vertimas, tikrumas = self.vertejas.versk(tvarkingas, kalba, i_kalba,
                                                     pranesk=self._zurnalas)
            t_vert = time.time() - t1
            self._zurnalas('[%s→%s] %.1f s garso | ausys %.2f s %s | vertimas %.2f s conf %.2f\n'
                           '    girdėjau: %s\n    sakau:    %s'
                           % (kalba, i_kalba, len(gabalas) / G.DAZNIS, t_ausys,
                              ' '.join('%s %.2f' % (k, v[1]) for k, v in visos.items()),
                              t_vert, tikrumas, tekstas, vertimas))
            # Į stenogramą žmogaus žodžiai eina IŠKART, dar prieš įgarsinimą: jei programa
            # nulūš verčiant, pasakyta replika neturi dingti. Žymę duoda REPLIKOS PRADŽIA —
            # gabalo gavimo laikas minus paties gabalo trukmė (10.2 sk.).
            if self.stenograma is not None:
                kada = self.stenograma.nuo_pradzios(t0 - len(gabalas) / G.DAZNIS)
                self.stenograma.zmogus(kalba, tvarkingas, kada)
            if vertimas.strip():
                self.eilute_sig.emit(tvarkingas, vertimas, kalba)
                # Žymė imama PRIEŠ `_sakyk`: jis laukia, kol kolonėlė nutils, ir po jo
                # `time.time()` rodytų kalbėjimo pabaigą, o žymą duoda pradžia (10.2 sk.).
                kada_v = (self.stenograma.nuo_pradzios(time.time())
                          if self.stenograma is not None else None)
                # Rašom TĄ vertimą, kuris skambėjo balsu (Roberto sprendimas 09-18):
                # stenograma yra pokalbio liudytoja, ne pagerinta redakcija. Todėl jei
                # „Baigti" nutildė kolonėlę dar prieš grojimą, į failą nerašom nieko —
                # kambaryje tas sakinys neskambėjo.
                if self._sakyk(i_kalba, vertimas) and self.stenograma is not None:
                    self.stenograma.vertejas(i_kalba, vertimas, kada_v)
            self._pranesk(K.t('Klausau'), '#4ADE80')

    def _pabaiga(self):
        try:
            rasem = self.stenograma is not None
            rasem_garsa = self.garso_irasas is not None
            # ⛔ „Stop reiškia stop" (Roberto sprendimas 09-18): jei „Baigti" paspaustas
            # kolonėlei KALBANT, pabaigos frazių nebesakom iš viso. Ramiai baigiant pokalbį
            # (kolonėlė tyli) atsisveikinimas ir pranešimas apie įrašą lieka.
            # ⚠️ Kaina, kurią Robertas priėmė sąmoningai: nutraukus niekas garsiai nepasako,
            # kad įrašas baigtas. Ekrane būsena vis tiek pasikeičia į „Pasiruošęs".
            if self._nutildyta:
                self._zurnalas('pabaiga tyli: „Baigti" paspaustas kolonėlei kalbant')
            # ⛔ Atsisveikinimą išjungti galima, bet ne tada, kai buvo rašoma: žmonės turi
            # sužinoti, kad įrašas baigtas, kitaip liks manyti, jog tebeveikia (10.6 sk.).
            elif self.balsai:
                # ⛔ Sekretorė nesako „ačiū, kad leidote padėti" — ji nieko neverčia ir
                # pokalbyje nedalyvavo. Bet pasakyti, kad **užrašinėti baigė**, privalo:
                # tai vienintelis dalykas, kurio išjungti negalima (10.6 sk.).
                sekretore = self._ar_sekretore()
                pranesem = False
                for puse in (('a',) if sekretore else ('a', 'b')):
                    k = self.nust.get(puse + '_kalba')
                    if not k:
                        continue
                    lytis = self.nust.get(puse + '_lytis')
                    # Padėka — kiekvienai pusei atskirai (Roberto sumanymas 09-18), o
                    # pranešimas apie baigtą įrašą — visada, kai buvo rašoma.
                    if not sekretore and self.nust.get('atsisveikinti_' + puse, True):
                        t = atsisveikinimas(k, lytis=lytis, stenograma=rasem,
                                            garsas=rasem_garsa)
                    elif rasem or rasem_garsa:
                        t = pranesimas_apie_irasa_baigta(k, lytis, garsas=rasem_garsa)
                    else:
                        continue
                    if not pranesem:
                        self._pranesk(K.t('Atsisveikinu…'))
                        pranesem = True
                    self._zurnalas('atsisveikinimas [%s]: %s' % (k, t))
                    # `butinai` — čia `_dirba` jau `False`, o pasakyti privalom.
                    self._sakyk(k, t, butinai=True)
        except Exception:
            self._zurnalas('KLAIDA atsisveikinant: ' + traceback.format_exc())
        finally:
            if self.mik:
                # Mikrofono NEUŽDAROM: banga turi judėti ir po „Baigti", kad kitą pokalbį
                # vėl būtų galima pasitikrinti įrangą.
                self.mik.renka = False
            # Modeliai atlaisvinami ⇒ paruošimo nebėra, kitam pokalbiui reikės iš naujo.
            self._paruosta = False
            if self.vertejas:
                self.vertejas.atlaisvink()
            if self.ausys:
                self.ausys.atlaisvink()
            self._uzverk_failus()
            self._pranesk(K.t('Pasiruošęs'), '#e6e6e6')

    def _uzverk_failus(self):
        """Užveria garso įrašą ir stenogramą. Saugu kviesti kelis kartus ir iš kelių gijų.

        ⛔ Išskirta iš `_pabaiga` 2026-09-18, kai Robertas uždarė langą kryžiuku nespaudęs
        „Baigti": kolonėlė pasakė „Garso įrašą sustabdžiau", o failai liko neužverti —
        FLAC antraštėje liko „trukmė nežinoma" (2⁶³−1 rėmų), ir dalis grotuvų tokio failo
        nebeatidaro. Duomenys viduje būna sveiki, bet žmogus to nežino.

        Priežastis buvo ne laukimo trūkumas, o tai, kad greitas ir BŪTINAS darbas (užverti
        failus, milisekundės) stovėjo vienoje eilėje už lėto ir nebūtino (atsisveikinti
        balsu, ~8 s). Pabaigos giją nužudo `sys.exit`, ir eilė nutrūksta ties kalbėjimu.
        """
        with self._failu_uzraktas:
            # ⛔ „--- PABAIGA" rašom tik tada, kai tikrai buvo ką užverti. Perkėlus užvėrimą
            # čia iš `_pabaiga`, žurnale atsirasdavo pabaiga be pradžios: šitas metodas
            # kviečiamas ir tiesiog uždarant programą, kurioje pokalbio nebuvo.
            uzverem = self.garso_irasas is not None or self.stenograma is not None
            # Garso įrašą užveriam PIRMA — jis turi pagauti ir atsisveikinimą, kuris ką tik
            # nuskambėjo. Mikrofoną atrišam, kad kitas pokalbis neatsidurtų sename faile.
            if self.garso_irasas is not None:
                if self.mik is not None:
                    self.mik.irasas = None
                irasas, self.garso_irasas = self.garso_irasas, None
                irasas.uzverk()
                self._zurnalas('garso įrašas: %.1f s, %.1f MB'
                               % (irasas.sekundes, irasas.megabaitai))
            if self.stenograma is not None:
                # Užveriam PASKUTINĮ kartą — visa kita jau įrašyta po kiekvienos replikos.
                sten, self.stenograma = self.stenograma, None
                self._zurnalas('stenograma užrašyta: %s' % sten.katalogas)
                sten.uzverk()
            if uzverem:
                self._zurnalas('--- PABAIGA\n')

    def uzverk_skubiai(self):
        """Langas uždaromas kryžiuku — failai užveriami TĄ PAČIĄ akimirką, tyliai.

        Kryžiukas stipresnis už „Baigti": žmogus nori, kad programos nebeliktų, ir laukti
        aštuonių sekundžių atsisveikinimo nesiruošia. Todėl čia nekalbam — tai ta pati
        Roberto taisyklė „stop reiškia stop" (10.6 sk. išimtis), tik dar griežtesnė.

        Dirba lango gijoje ir grįžta per milisekundes: `uzverk()` tik užbaigia failus.
        """
        self._dirba = False
        if self.grotuvas:
            self.grotuvas.nutrauk()
        if self.mik:
            self.mik.renka = False
        self._uzverk_failus()

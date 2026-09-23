# -*- coding: utf-8 -*-
"""VERTĖJO LANGAS — sąsaja (09-12).

Roberto užsakymas: „daryk pačią GUI… paskui skriptais aplipdysi." Todėl čia TIK sąsaja:
kas lange yra, kaip atrodo ir kaip reaguoja. Garso, ausų, vertėjo ir balso čia nėra —
jiems palikti aiškūs kabliukai (`self.variklis`), kuriuos prijungsim kitu žingsniu.

Stilius — iš Diktuoklės (tamsus fonas #1b1b1b, Segoe UI, gintarinė banga), kad dovanos
atrodytų iš tos pačios šeimos. Roberto: „GUI panašus į Diktuoklės."

Kas lange ir KODĖL (viskas iš PLANAS.md „PROGRAMOS PIPELINE IR GUI"):
  * DU LANGELIAI — šeimininkas ir svečias. Šeimininko kalba pirmame: konferencijos savininkas
    visada pradeda pirmas, tad sveikinimas eina jo kalba, paskui svečio.
  * Kiekviename langelyje — kalba IR balsas. Balsas renkamas iš Piper sąrašo; lytis iš balso
    (Piper kataloge jos nėra, todėl žinomų balsų lentelė + vartotojo pasirinkimas).
  * BANGA — mikrofono tiesa. „Pasiruošęs" yra tik pažadas; jei mikrofonas išjungtas, banga
    nemeluoja (ta pati mintis kaip Diktuoklėje).
  * PAUZĖS SLANKIKLIS pagrindiniame lange, ne nustatymuose: vieni kalba trumpom pauzėm, kiti
    ilgom, ir koreguoti reikia pokalbio EIGOJE, nesustabdžius. Šalia — tylos juostelė: matai,
    kada kolonėlė „nusprendė", kad žmogus baigė.
  * TEKSTAS dviem stulpeliais — kas pasakyta ir kas išversta. Antras kanalas šalia balso.
  * Mygtukai: Pradėti ↔ Pauzė ir Baigti. Pauzė — telefonas suskambo; Baigti — atsisveikinimas.
  * Sveikinimo ir atsisveikinimo jungikliai: kolonėlė kalba tik du kartus, o kam ir to per daug —
    išjungia (Robertas: „gali ir nenaudoti, jei juos tai erzina").

⛔ Ko lange NĖRA sąmoningai (v6): abejonės ženklų, griežtumo slankiklio, priminimų. Kolonėlė
į pokalbį nesikiša — perspėja sveikinime ir tyli.
"""
import os
import sys

from PyQt6.QtCore import QProcess, Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QAction, QColor, QFont, QFontMetrics, QPainter, QTextCursor
from PyQt6.QtWidgets import (QApplication, QComboBox, QDialog, QFrame, QGridLayout,
                             QHBoxLayout, QLabel, QMenu, QMessageBox, QPushButton, QSlider,
                             QTextEdit, QVBoxLayout, QWidget)

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import nustatymai as N
from ausys import ausu_sarasas, numatytos
from balsas import MUSU_BALSAI, NUMATYTI
from frazes import lytis_pagal_balsa
# ⛔ Vertimo funkcija pasiekiama per trumpinį `K`, o ne kaip `t()` (PHOTO home) ar `K.t()`.
# Priežastis pamatuota, ne pasirinkta iš skonio: `t` šiame faile jau yra lokalus kintamasis
# (QGridLayout ir QTextEdit), o `kalba` — dažniausias vardas visoje programoje (54 vietos:
# `for kalba, balsai in…`, parametrai, `dabartine_kalba()`). Bet kuris iš tų dviejų vardų būtų
# tyliai užgožtas ir programa kristų su „object is not callable". `K` neužimtas nė karto ir
# dera prie jau esančio `nustatymai as N`.
import kalba as K

INSTRUKCIJA = """SpeakDream — gyvas pokalbio vertėjas be interneto.

KAM JIS SKIRTAS
Dviem žmonėms, kalbantiems skirtingomis kalbomis, susikalbėti be trečio žmogaus.
Kolonėlė stovi tarp jūsų: girdi, verčia ir pasako kita kalba.

KAIP PRADĖTI
1. Kairėje pasirinkite savo kalbą, dešinėje — svečio.
2. Kiekvienam pasirinkite balsą. Lytis atspėjama iš balso; galite nurodyti patys.
3. Pasirinkite mikrofoną. Geltona banga turi judėti, kai kalbate — jei nejuda,
   mikrofonas neveikia arba pasirinktas ne tas.
4. Spauskite „Pradėti".

KAIP KALBĖTI
Kalbėkite po vieną–dvi mintis ir padarykite pauzę. Vertėjas laukia, kol nutilsite,
ir tik tada verčia. Kuo trumpiau kalbate, tuo greičiau išgirsite vertimą.
Pauzės ilgį galite keisti slankikliu net pokalbio metu.

KĄ DARYTI, JEI IŠVERTĖ NETIKSLIAI
Paprašykite pašnekovo tą pačią mintį pasakyti kitais žodžiais. Vertėjas nežino,
kada suklydo, todėl niekada to neslepia — apie tai jis įspėja ir prisistatydamas.

NUSTATYMAI (dantratis)
Prisistatyti pradžioje — vertėjas pasisveikina abiem kalbomis ir paaiškina, kaip kalbėti.
Trumpas prisistatymas — tik pasisveikinimas, be paaiškinimų.
Padėkoti pabaigoje — paspaudus „Baigti" vertėjas padėkoja abiem.
Rodyti tekstą — parodo, ką išgirdo ir ką išvertė. Reikalinga derinant.

PRIVATUMAS
Garsas ir tekstas lieka šiame kompiuteryje. Niekur nesiunčiama.
"""

# ⛔ Kalbų pavadinimai NEVERČIAMI — kiekvienas rašomas savo kalba, kad žmogus savąją
# atpažintų net tada, kai visa kita sąsaja jam nesuprantama.
# „?" → „Neradote atsakymo? Klauskite DI". ⚠️ BRIEF_URL užpildomas PASKELBUS dovaną
# (kaip Diktuoklėje: `raw.githubusercontent.com/RobertasTa/<repo>/main/AI_CONSULTANT_BRIEF.md`).
# Nuoroda įrašyta IŠ ANKSTO (repo vardas nuspręstas 2026-09-21), kad publikavimo dieną nereikėtų
# perstatyti paketo. Kol repo neviešas, nuoroda neatsidaro — todėl promptas pats priduria, kad
# tas pats failas guli šalia programos (meluoti apie neegzistuojančią nuorodą būtų blogiau).
KUREJO_PUSLAPIS = 'https://github.com/RobertasTa'
BRIEF_URL = 'https://raw.githubusercontent.com/RobertasTa/speakdream/master/AI_CONSULTANT_BRIEF.md'

KALBOS = [('lt', 'Lietuvių'), ('ru', 'Русский'), ('en', 'English'), ('de', 'Deutsch')]
LYTYS = [(None, K.t('pagal balsą')), ('m', K.t('moteris')), ('v', K.t('vyras'))]
# ⛔ Numatytųjų balsų sąrašo čia NEBĖRA — jis imamas iš `balsas.py` (`NUMATYTI`, `MUSU_BALSAI`).
# Buvo dvi kopijos: 09-16 Ingutė įtaisyta `balsas.py`, o langas liko su savo sena eilute, todėl
# sąraše Ingutės nebuvo IŠ VISO ir programa tebekalbėjo Reginute. Robertas pastebėjo 09-18.

STULPELIU = 34
STULPELIO_PLOTIS = 4
STULPELIO_TARPAS = 3
BANGOS_AUKSTIS = 34
GINTARAS = QColor(232, 184, 75)
GINTARAS_BLANKUS = QColor(58, 58, 42)
ZALIA = QColor(74, 222, 128)
# Lemputėms — jokių NAUJŲ spalvų: ta pati mėlyna, kaip slankikliuose ir varnelėse, ir ta
# pati pilka, kaip antraštėse (Roberto sąlyga 09-18: „kad į vaivorykštę neįsiveltume").
MELYNA = QColor(22, 104, 193)
PILKA = QColor(154, 154, 154)

STILIUS = """
QWidget#saknis { background: #1b1b1b; }
QLabel { color: #d8d8d8; font-family: 'Segoe UI'; font-size: 13px; }
/* „Neaktyvus" turi ir ATRODYTI neaktyvus. Su savu stiliumi Qt pats to nepadaro: spalva
   nurodyta tiesiogiai, tad išjungtas valdiklis lieka toks pat ryškus. Roberto pastaba
   09-18: sekretorės režimu „svečio" pusė turi visa pilka pataptų. Naujų spalvų nėra —
   #5a5a5a ir #6a6a6a lange jau yra. */
QLabel:disabled { color: #5a5a5a; }
QLabel#antraste { color: #9a9a9a; font-size: 11px; }
QLabel#antraste:disabled { color: #5a5a5a; }
QLabel#busena { color: #e6e6e6; font-size: 13px; }
QLabel#uzuomina { color: #7d7d7d; font-size: 11px; }
QPushButton {
    background: #343434; color: #c8c8c8; border: none; border-radius: 5px;
    padding: 7px 15px; font-family: 'Segoe UI'; font-size: 13px;
}
QPushButton:hover { background: #444444; }
QPushButton:disabled { background: #2a2a2a; color: #6a6a6a; }
QPushButton[aktyvus="taip"] { background: #1668C1; color: #ffffff; }
QPushButton#ikona { padding: 6px 9px; font-size: 14px; }
QPushButton#ikona::menu-indicator { image: none; width: 0px; }
/* Režimo perjungiklis antraščių eilutėje. Ne mygtukas-dėžė, o tekstas: Roberto sąlyga
   09-18 — „kad į vaivorykštę programoje neįsiveltume". Spalvų NAUJŲ nėra nė vienos:
   #1668C1 jau yra slankikliuose, varnelėse ir meniu; #9a9a9a — pačių antraščių spalva. */
QPushButton#rezimas {
    background: transparent; border: none; padding: 0px 2px;
    font-size: 11px; color: #9a9a9a;
}
QPushButton#rezimas:hover { background: transparent; color: #d8d8d8; }
QPushButton#rezimas:checked { color: #1668C1; font-weight: bold; }
QPushButton#rezimas:disabled { background: transparent; color: #5a5a5a; }
QLabel#rezimo_skirtukas { color: #5a5a5a; font-size: 11px; }
QDialog { background: #1b1b1b; }
QMenu { background: #2b2b2b; color: #dddddd; border: 1px solid #3d3d3d; }
QMenu::item { padding: 6px 26px 6px 22px; }
QMenu::item:selected { background: #1668C1; color: #ffffff; }
QMenu::item:disabled { color: #8a8a8a; }
/* Skirtukai su TIRŠTESNIU tarpu (Roberto pastaba 09-18: „gal biskutį didesnius tarpus padaryk,
   kad tos grupės aiškiau matytųsi"). Anksčiau tarpas aplink liniją buvo toks pat kaip tarp
   eilučių, tad grupė nuo grupės nesiskyrė. Linija lieka ta pati — keičiasi tik oras aplink ją. */
QMenu::separator { height: 1px; background: #3d3d3d; margin: 11px 10px; }
QComboBox {
    background: #2b2b2b; color: #d8d8d8; border: 1px solid #3d3d3d;
    border-radius: 5px; padding: 5px 8px; font-size: 13px;
}
QComboBox:hover { border: 1px solid #4f4f4f; }
QComboBox:disabled { background: #242424; color: #5a5a5a; border: 1px solid #2f2f2f; }
QComboBox:disabled:hover { border: 1px solid #2f2f2f; }
QComboBox::drop-down { border: none; width: 18px; }
QComboBox QAbstractItemView {
    background: #2b2b2b; color: #dddddd; border: 1px solid #3d3d3d;
    selection-background-color: #1668C1; selection-color: #ffffff; outline: none;
}
QTextEdit {
    background: #242424; color: #d8d8d8; border: 1px solid #3d3d3d;
    border-radius: 5px; padding: 6px; font-family: 'Segoe UI'; font-size: 13px;
}
QCheckBox { color: #b8b8b8; font-size: 12px; spacing: 6px; }
QCheckBox::indicator { width: 14px; height: 14px; border-radius: 3px;
                       border: 1px solid #4a4a4a; background: #2b2b2b; }
QCheckBox::indicator:checked { background: #1668C1; border: 1px solid #1668C1; }
QSlider::groove:horizontal { height: 4px; background: #3a3a3a; border-radius: 2px; }
QSlider::handle:horizontal { background: #c8c8c8; width: 12px; height: 12px;
                             margin: -5px 0; border-radius: 6px; }
QSlider::handle:horizontal:hover { background: #ffffff; }
QSlider::sub-page:horizontal { background: #1668C1; border-radius: 2px; }
/* Garsumo slankiklis — TOS PAČIOS mėlynos šviesesnis atspalvis (Roberto prašymas 09-18:
   „kad jie skirtųsi ir vizualiai"). Ne nauja spalva: vaivorykštės taisyklė lieka. */
QSlider#garsas::sub-page:horizontal { background: #5FA8EA; }
/* Ir greičio juosta (Roberto patikslinimas 09-18): mėlyna užpildo dalis pilkėja kartu su
   rankenėle, kitaip juosta liktų vienintelis ryškus daiktas pilkoje pusėje. */
QSlider::groove:horizontal:disabled { background: #2a2a2a; }
QSlider::handle:horizontal:disabled { background: #5a5a5a; }
QSlider::sub-page:horizontal:disabled { background: #3a3a3a; }
QFrame#skirtukas { background: #303030; }
"""


class Banga(QWidget):
    """Mikrofono tiesa: užrašas „Pasiruošęs" gali meluoti, banga — ne."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(STULPELIU * (STULPELIO_PLOTIS + STULPELIO_TARPAS), BANGOS_AUKSTIS)
        self.lygiai = [0.0] * STULPELIU

    def stumk(self, lygis: float):
        self.lygiai = self.lygiai[1:] + [max(0.0, min(1.0, lygis))]
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setPen(Qt.PenStyle.NoPen)
        x, vidurys = 0, self.height() / 2
        for lygis in self.lygiai:
            h = max(6.0, min(self.height() - 2.0, lygis * (self.height() - 2)))
            p.setBrush(GINTARAS if lygis > 0.03 else GINTARAS_BLANKUS)
            p.drawRoundedRect(int(x), int(vidurys - h / 2), STULPELIO_PLOTIS, int(h), 2.0, 2.0)
            x += STULPELIO_PLOTIS + STULPELIO_TARPAS
        p.end()


class TylosJuostele(QWidget):
    """Kiek tylos prabėgo nuo kalbos pabaigos — iki slenksčio, už kurio kolonėlė verčia.

    Be jos pauzės slankiklis būtų aklas: nematyti, ar kolonėlė nusprendė per anksti,
    ar žmogus tikrai baigė.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(6)
        self.setMinimumWidth(120)
        self.dalis = 0.0

    def nustatyk(self, dalis: float):
        self.dalis = max(0.0, min(1.0, dalis))
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QColor(48, 48, 48))
        p.drawRoundedRect(0, 1, self.width(), 4, 2.0, 2.0)
        if self.dalis > 0:
            p.setBrush(ZALIA if self.dalis >= 1.0 else GINTARAS)
            p.drawRoundedRect(0, 1, int(self.width() * self.dalis), 4, 2.0, 2.0)
        p.end()


class Lempute(QWidget):
    """Ar įrašymas įjungtas — matoma vienu žvilgsniu, neatveriant dantračio.

    Roberto sumanymas 09-18: *„užsisvajojęs vartotojas gali pamiršti, kokie te nustatymai
    parinkti… užpuls, pvz., mešką alzhaimeris ir pamirš, kad stenogramos neįjungė, o derybos
    bus pasibaigę."* Skirta ne pokalbiui stebėti, o TAM žmogui, kuris prieš derybas viską
    sustato ir spaudžia „Pradėti".

    ⛔ Rodo TIKROVĘ, o ne varnelę. Jei rašyti nepavyktų (nėra vietos diske, teisių), lemputė
    gęsta. Mėlyna lemputė, po kuria nieko nerašoma, būtų blogiau nei jokios — tai ta pati
    bėda, kaip kolonėlė, sakanti „garso įrašą sustabdžiau" jo nesustabdžiusi (09-18).

    Spustelėjus — atveria dantratį. NEperjungia: netyčia užkabinus pokalbio metu įrašymas
    tyliai išsijungtų, o kaip tik to ir vengiam.
    """

    spausta = pyqtSignal()

    def __init__(self, rusis, parent=None):
        super().__init__(parent)
        self.rusis = rusis              # 'garsas' arba 'stenograma'
        self.dega = False
        self.setFixedSize(22, 22)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def uzdek(self, ar: bool, paaiskinimas: str = ''):
        # Kviečiama laikmačio ritmu, tad perpiešiam TIK pasikeitus: kitaip 30 kartų per
        # sekundę piešinys be jokios priežasties.
        ar = bool(ar)
        if paaiskinimas and paaiskinimas != self.toolTip():
            self.setToolTip(paaiskinimas)
        if ar != self.dega:
            self.dega = ar
            self.update()

    def mousePressEvent(self, e):
        self.spausta.emit()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        spalva = MELYNA if self.dega else PILKA
        if self.rusis == 'garsas':
            # Mikrofonas, ne garsiakalbis (Roberto pastaba 09-18, patikslinta): įrašinėjam
            # tai, ką GIRDI kambarys, o garsiakalbis reikštų, kad kažkas grojama.
            pen = p.pen()
            pen.setColor(spalva)
            pen.setWidth(2)
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(spalva)
            p.drawRoundedRect(8, 3, 6, 10, 3.0, 3.0)      # kapsulė
            p.setPen(pen)
            p.setBrush(Qt.BrushStyle.NoBrush)
            p.drawArc(5, 6, 12, 11, 180 * 16, 180 * 16)   # lankas po ja
            p.drawLine(11, 17, 11, 19)                    # kojelė
        else:
            # Lapas su eilutėmis — stenograma.
            pen = p.pen()
            pen.setColor(spalva)
            pen.setWidth(1)
            p.setPen(pen)
            p.setBrush(Qt.BrushStyle.NoBrush)
            p.drawRoundedRect(5, 3, 12, 16, 2.0, 2.0)
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(spalva)
            for y in (7, 10, 13, 16):
                p.drawRect(7, y, 8 if y < 16 else 5, 1)
        p.end()


class Pasnekovas(QWidget):
    """Vienas langelis: kieno tai pusė, kokia kalba ir kokiu balsu jam kalbama."""

    pakeista = pyqtSignal()
    balsas_bandomas = pyqtSignal()      # paspaustas ▸ prie balso (09-18)

    def __init__(self, antraste: str, kalba: str, parent=None, desineje=None):
        super().__init__(parent)
        v = QVBoxLayout(self)
        v.setContentsMargins(0, 0, 0, 0)
        v.setSpacing(5)
        a = QLabel(antraste)
        a.setObjectName('antraste')
        self._desineje = list(desineje or [])
        if desineje is None:
            v.addWidget(a)
        else:
            # `desineje` — valdikliai į TĄ PAČIĄ antraštės eilutę, prie pat dešinio krašto
            # (Roberto sprendimas 09-18 dėl režimo perjungiklio). Kai jo nėra, viskas lieka
            # kaip buvo.
            e = QHBoxLayout()
            e.setContentsMargins(0, 0, 0, 0)
            e.setSpacing(6)
            e.addWidget(a)
            e.addStretch(1)
            for w in desineje:
                e.addWidget(w)
            v.addLayout(e)
        self.kalba = QComboBox()
        for k, pav in KALBOS:
            self.kalba.addItem(pav, k)
        self.kalba.setCurrentIndex([k for k, _ in KALBOS].index(kalba))
        v.addWidget(self.kalba)
        # Ausys kiekvienai pusei ATSKIRAI: lietuviui tinka specializuota Paprika, o svečiui —
        # didelis daugiakalbis modelis (Roberto klausimas 09-12 16:50).
        self.ausys = QComboBox()
        v.addWidget(self.ausys)
        # Balsas ir šalia jo mažas ▸ — duoda išgirsti, ar pasirinkai tą, kurį norėjai
        # (Roberto prašymas 09-18). Iki tol balsą išgirsti buvo galima tik pradėjus pokalbį.
        bl = QHBoxLayout()
        bl.setContentsMargins(0, 0, 0, 0)
        bl.setSpacing(6)
        self.balsas = QComboBox()
        bl.addWidget(self.balsas, 1)
        self.bandyk = QPushButton('▸')
        self.bandyk.setObjectName('ikona')
        self.bandyk.setToolTip(K.t('Pasiklausyti šio balso'))
        self.bandyk.setCursor(Qt.CursorShape.PointingHandCursor)
        self.bandyk.clicked.connect(lambda: self.balsas_bandomas.emit())
        bl.addWidget(self.bandyk)
        v.addLayout(bl)
        e = QHBoxLayout()
        e.setSpacing(6)
        l = QLabel(K.t('Balsas:'))
        l.setObjectName('uzuomina')
        e.addWidget(l)
        self.lytis = QComboBox()
        for k, pav in LYTYS:
            self.lytis.addItem(pav, k)
        e.addWidget(self.lytis, 1)
        v.addLayout(e)
        # Kalbėjimo greitis kiekvienai pusei ATSKIRAI (Robertas 09-12 19:10: „Ruslanas labai
        # greitai kalba… gal kas supranta gerai greitesnę šneką, o kitam gali prireikti
        # sulėtinti"). Vienam svečiui greita rusų kalba įprasta, kitam — nesuprantama.
        gr = QHBoxLayout()
        gr.setSpacing(6)
        gl = QLabel(K.t('Greitis:'))
        gl.setObjectName('uzuomina')
        gr.addWidget(gl)
        self.greitis = QSlider(Qt.Orientation.Horizontal)
        self.greitis.setRange(60, 140)      # 0,6–1,4 karto
        self.greitis.setValue(100)
        self.greitis.valueChanged.connect(self._greitis_pakeistas)
        gr.addWidget(self.greitis, 1)
        self.greicio_reiksme = QLabel('1,00×')
        self.greicio_reiksme.setObjectName('uzuomina')
        self.greicio_reiksme.setFixedWidth(38)
        gr.addWidget(self.greicio_reiksme)
        v.addLayout(gr)
        # Garsumas kiekvienai pusei ATSKIRAI (Roberto prašymas 09-18). ⛔ Tai NE balsų
        # sulyginimas — tas jau padarytas `balsas.py` (visi penki suvesti į vieną LUFS
        # medianą 09-18). Slankiklis skirtas KAMBARIUI: svečias sėdi toliau nuo kolonėlės,
        # vienas žmogus prasčiau girdi. Jei jis dengtų mūsų pačių klaidą, žmogus kiekvieną
        # kartą turėtų pradėti nuo derinimo.
        ga = QHBoxLayout()
        ga.setSpacing(6)
        gal = QLabel(K.t('Garsas:'))
        gal.setObjectName('uzuomina')
        ga.addWidget(gal)
        self.garsas = QSlider(Qt.Orientation.Horizontal)
        self.garsas.setObjectName('garsas')     # šviesesnė mėlyna — skirtųsi nuo greičio
        self.garsas.setRange(-6, 6)        # decibelais: pusiau tyliau … dvigubai garsiau
        self.garsas.setValue(0)
        self.garsas.valueChanged.connect(self._garsas_pakeistas)
        ga.addWidget(self.garsas, 1)
        self.garso_reiksme = QLabel('0 dB')
        self.garso_reiksme.setObjectName('uzuomina')
        self.garso_reiksme.setFixedWidth(38)
        ga.addWidget(self.garso_reiksme)
        v.addLayout(ga)
        self.kalba.currentIndexChanged.connect(self._kalba_pakeista)
        self.balsas.currentIndexChanged.connect(self._balsas_pakeistas)
        self.uzpildyk_ausis()

    def blankink(self, ar: bool):
        """Visa pusė pilka — bet NE tai, kas paduota `desineje`.

        ⛔ Negalima tiesiog `setEnabled(False)` pačiam Pasnekovui: režimo perjungiklis gyvena
        jo antraštės eilutėje, tad kartu su tėvu numirtų ir jis — ir iš sekretorės nebebūtų
        kaip grįžti. Robertas pagavo 09-18; tai TA PATI Qt duobė, kaip 09-12 su greičio
        slankikliu, tik iš kitos pusės.
        """
        tik_savi = Qt.FindChildOption.FindDirectChildrenOnly
        for w in self.findChildren(QWidget, options=tik_savi):
            if w not in self._desineje:
                w.setEnabled(not ar)

    def dabartine_kalba(self) -> str:
        return self.kalba.currentData()

    def dabartinis_balsas(self):
        return self.balsas.currentData()

    def dabartine_lytis(self):
        p = self.lytis.currentData()
        return p if p else lytis_pagal_balsa(self.dabartinis_balsas() or '')

    def uzpildyk_balsus(self, balsai):
        """balsai — [(raktas, rodomas_vardas), …]; tuščias sarasas = balso tai kalbai nėra."""
        self.balsas.blockSignals(True)
        self.balsas.clear()
        if not balsai:
            self.balsas.addItem(K.t('— balso nėra —'), None)
        for raktas, pav in balsai:
            self.balsas.addItem(pav, raktas)
        self.balsas.blockSignals(False)
        self._balsas_pakeistas()

    def dabartines_ausys(self):
        return self.ausys.currentData()

    def uzpildyk_ausis(self, pasirinkta=None):
        kalba = self.dabartine_kalba()
        dabar = pasirinkta or self.ausys.currentData() or numatytos(kalba)
        self.ausys.blockSignals(True)
        self.ausys.clear()
        for raktas, pav in ausu_sarasas(kalba):
            self.ausys.addItem(pav, raktas)
        i = self.ausys.findData(dabar)
        self.ausys.setCurrentIndex(i if i >= 0 else max(0, self.ausys.findData(numatytos(kalba))))
        self.ausys.blockSignals(False)

    def dabartinis_greitis(self) -> float:
        return self.greitis.value() / 100.0

    def _greitis_pakeistas(self, v):
        self.greicio_reiksme.setText(('%.2f×' % (v / 100.0)).replace('.', ','))

    def dabartinis_garsas(self) -> float:
        """Slankiklio decibelai → daugiklis. 0 dB = 1,0 (balsas skamba taip, kaip sulygintas)."""
        return 10.0 ** (self.garsas.value() / 20.0)

    def _garsas_pakeistas(self, v):
        self.garso_reiksme.setText('%+d dB' % v if v else '0 dB')

    def _kalba_pakeista(self):
        self.uzpildyk_ausis()
        self.pakeista.emit()

    def _balsas_pakeistas(self):
        l = lytis_pagal_balsa(self.dabartinis_balsas() or '')
        self.lytis.setItemText(0, K.t('pagal balsą: %s')
                               % {'m': K.t('moteris'), 'v': K.t('vyras')}.get(
                                   l, K.t('nežinoma')))
        self.pakeista.emit()


class Langas(QWidget):
    # ⛔ 2026-09-21 PAMATUOTA: išdėstymui reikia 408 px, o langas buvo laikomas ties 370 —
    # Qt tada spaudė laukelius nuo 32 iki 22 px ir kirpo raidžių uodegas („Lietuvių" → „Lietuviu",
    # „ingutė" → „inqutė"). Konstanta liko nuo laikų be režimo perjungiklio, lempučių ir pauzės
    # eilutės. Abi pakeltos +40; keičiant išdėstymą — permatuoti (`layout().minimumSize()`).
    AUKSTIS = 410              # be teksto: tik tai, ką nustatai prieš pokalbį
    AUKSTIS_SU_TEKSTU = 670    # derinant ir gyvo testo metu

    def __init__(self, variklis=None):
        super().__init__()
        self.issaugota = N.skaityk()
        self.variklis = variklis     # čia prisijungs garsas/ausys/vertėjas/balsas
        self.dirba = False
        self.pauze = False
        # Režimas („vertejas" / „sekretore") — reikalingas jau statant viršutinę eilutę.
        self.rezimas = self.issaugota.get('rezimas', 'vertejas')
        self.setObjectName('saknis')
        # Programos vardas — SpeakDream (Roberto sprendimas 2026-09-21), po jo režimas.
        self.setWindowTitle('SpeakDream — ' + K.t('Vertėjas'))
        self.setStyleSheet(STILIUS)
        # Kolonėlė stovės ant stalo, o ne prie monitoriaus — langas kompaktiškas kaip
        # Diktuoklės; tekstas atsiveria tik derinant.
        self.setMinimumWidth(700)
        self.setMinimumHeight(self.AUKSTIS)
        self.resize(700, self.AUKSTIS)

        v = QVBoxLayout(self)
        v.setContentsMargins(16, 14, 16, 12)
        v.setSpacing(12)

        # --- viršus: du langeliai ---
        g = QGridLayout()
        g.setHorizontalSpacing(14)
        # Režimo perjungiklis (Roberto sprendimas 09-17: „vertėjas gauna dvi funkcijas — ir
        # vertėjas, ir susirinkimo sekretorė"). Vieta ir dydis — jo 09-18: nedideli, antraščių
        # eilutėje prie pat dešinio lango krašto, aktyvus mėlynas, neaktyvus pilkas.
        self.m_vertejas = QPushButton(K.t('Vertėjas'))
        self.m_sekretore = QPushButton(K.t('Sekretorė'))
        for mb in (self.m_vertejas, self.m_sekretore):
            mb.setObjectName('rezimas')
            mb.setCheckable(True)
            mb.setCursor(Qt.CursorShape.PointingHandCursor)
            mb.setFlat(True)
            # ⛔ Plotį rezervuojam pagal PASTORINTĄ tekstą. Aktyvus režimas piešiamas
            # `font-weight: bold`, o Qt mygtuko plotį skaičiuoja pagal esamą, NEpastorintą
            # šriftą — tad aktyviam tekstui pritrūksta vietos ir paskutinė raidė nukerpama.
            # Lietuviškai to nesimatė („Vertėjas" trumpas), o Robertas pagavo 09-19 vos
            # perjungęs į anglų ir vokiečių: „Translatoı", „Übersetzeı".
            # 📌 Dėsnis: vertimai beveik visada ILGESNI už originalą, tad plotis, nustatytas
            # pagal lietuvišką tekstą, kitoms kalboms netinka.
            mb.ensurePolished()          # be šito `font()` dar nežino stiliaus dydžio
            storas = QFont(mb.font())
            storas.setBold(True)
            mb.setMinimumWidth(QFontMetrics(storas).horizontalAdvance(mb.text()) + 10)
        self.m_vertejas.clicked.connect(lambda: self._rezimas_pasirinktas('vertejas'))
        self.m_sekretore.clicked.connect(lambda: self._rezimas_pasirinktas('sekretore'))
        skirtukas = QLabel('·')
        skirtukas.setObjectName('rezimo_skirtukas')
        self.a = Pasnekovas(K.t('ŠEIMININKAS (kalba pirmas)'), self.issaugota['a_kalba'])
        self.b = Pasnekovas(K.t('SVEČIAS'), self.issaugota['b_kalba'],
                            desineje=[self.m_vertejas, skirtukas, self.m_sekretore])
        g.addWidget(self.a, 0, 0)
        rodykle = QLabel('⇄')
        rodykle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        rodykle.setStyleSheet('color: #5a5a5a; font-size: 20px;')
        g.addWidget(rodykle, 0, 1)
        g.addWidget(self.b, 0, 2)
        g.setColumnStretch(0, 1)
        g.setColumnStretch(2, 1)
        v.addLayout(g)

        # --- PARUOŠTI DARBUI ---
        # Roberto sprendimas 09-18: *„keistai atrodo, kai paspaudi pradėti — vyksta žodynų,
        # kalbos modulių užkrovimas. Aš manau, Play tai jau dirbam."* Todėl ilgas krovimas
        # atskirtas: šitas mygtukas aktyvus, kol viršuje renkiesi kalbėtojus, o „Pradėti"
        # atsirakina tik po jo.
        pr = QHBoxLayout()
        pr.setSpacing(10)
        self.paruosti = QPushButton('⚙  ' + K.t('Paruošti darbui'))
        self.paruosti.setCursor(Qt.CursorShape.PointingHandCursor)
        self.paruosti.clicked.connect(self._paruosti_paspaustas)
        pr.addWidget(self.paruosti)
        self.paruosimo_uzuomina = QLabel(K.t('kalbos ir balsai dar keičiami'))
        self.paruosimo_uzuomina.setObjectName('uzuomina')
        pr.addWidget(self.paruosimo_uzuomina)
        pr.addStretch(1)
        v.addLayout(pr)

        sk = QFrame()
        sk.setObjectName('skirtukas')
        sk.setFixedHeight(1)
        v.addWidget(sk)

        # --- mikrofonas ir banga ---
        m = QHBoxLayout()
        m.setSpacing(10)
        self.mikrofonas = QComboBox()
        self.mikrofonas.setMinimumWidth(230)
        m.addWidget(self.mikrofonas, 1)
        self.banga = Banga()
        m.addWidget(self.banga)
        v.addLayout(m)

        # --- mygtukai ---
        mg = QHBoxLayout()
        mg.setSpacing(8)
        # Dvi lemputės PRIEŠ mygtukus (Roberto vieta, 09-18): tas, kuris sustato programą
        # deryboms, mato vienu žvilgsniu, ką pasirinko, ir tada spaudžia „Pradėti".
        self.l_stenograma = Lempute('stenograma')
        self.l_stenograma.spausta.connect(self._rodyk_nustatymus)
        self.l_garsas = Lempute('garsas')
        self.l_garsas.spausta.connect(self._rodyk_nustatymus)
        mg.addWidget(self.l_stenograma)
        mg.addWidget(self.l_garsas)
        mg.addSpacing(6)
        self.pradeti = QPushButton('▶  ' + K.t('Pradėti'))
        self.pradeti.clicked.connect(self.perjunk)
        self.baigti = QPushButton('■  ' + K.t('Baigti'))
        self.baigti.clicked.connect(self.stok)
        self.baigti.setEnabled(False)
        mg.addWidget(self.pradeti)
        mg.addWidget(self.baigti)
        mg.addStretch(1)
        self.busena = QLabel(K.t('Pasiruošęs'))
        self.busena.setObjectName('busena')
        mg.addWidget(self.busena)
        # Dantratis ir klaustukas — šeimos standartas (SDF, TempCleaner, PHOTO home,
        # Diktuoklė). Robertas 09-12 18:00: „nustatymus per dantratį daryk… gal dar kokių
        # atsiras, tai eigoje bus paprasčiau. Taip pat iškart klaustuką įmontuok."
        self.b_nust = QPushButton('⚙')
        self.b_nust.setObjectName('ikona')
        self.b_nust.setToolTip(K.t('Nustatymai'))
        self.b_nust.clicked.connect(self._rodyk_nustatymus)
        self.b_pag = QPushButton('?')
        self.b_pag.setObjectName('ikona')
        self.b_pag.setToolTip(K.t('Pagalba'))
        pagalba = QMenu(self.b_pag)
        pagalba.addAction(K.t('Apie…'), self._rodyk_apie)
        pagalba.addAction(K.t('Instrukcija'), self._rodyk_instrukcija)
        # ⭐ Trečias punktas — šeimos standartas (Diktuoklėje jis vadinasi lygiai taip pat).
        # Roberto sumanymas: žmogus, kuriam instrukcijos neužtenka, nueina pas savo dirbtinį
        # intelektą, o tas gauna PARUOŠTĄ tiesos failą ir nebeprasimano.
        pagalba.addAction(K.t('Neradote atsakymo? Klauskite DI'), self._rodyk_di)
        self.b_pag.setMenu(pagalba)
        mg.addSpacing(8)
        mg.addWidget(self.b_nust)
        mg.addWidget(self.b_pag)
        for b in (self.pradeti, self.baigti, self.b_nust, self.b_pag):
            b.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        v.addLayout(mg)

        # --- pauzės slankiklis + tylos juostelė ---
        p = QHBoxLayout()
        p.setSpacing(10)
        pl = QLabel(K.t('Pauzė:'))
        p.addWidget(pl)
        self.slankiklis = QSlider(Qt.Orientation.Horizontal)
        self.slankiklis.setRange(5, 25)       # 0,5–2,5 s
        self.slankiklis.setValue(int(self.issaugota['pauze']))
        self.slankiklis.setFixedWidth(150)
        self.slankiklis.valueChanged.connect(self._pauze_pakeista)
        p.addWidget(self.slankiklis)
        self.pauzes_reiksme = QLabel('1,0 s')
        self.pauzes_reiksme.setFixedWidth(40)
        p.addWidget(self.pauzes_reiksme)
        self.tyla = TylosJuostele()
        p.addWidget(self.tyla, 1)
        u = QLabel(K.t('kiek tylos — tiek laukia'))
        u.setObjectName('uzuomina')
        p.addWidget(u)
        v.addLayout(p)

        # --- tekstas dviem stulpeliais: PASLĖPTAS ---
        # Robertas 09-12 17:50: „teksto nereikia visai, nebent tik derinimo metu. Juk niekas
        # į monitorių nežiūrės — kolonėlė ant stalo bus, į ją ir kalbės." Todėl langas
        # kompaktiškas kaip Diktuoklės, o tekstas gyvena už jungiklio: mums derinant ir
        # gyvo testo metu jis būtinas (matom, ką ausys išgirdo ir ką vertėjas padarė),
        # pokalbio metu — nereikalingas.
        self.tekstas = QWidget()
        t = QGridLayout(self.tekstas)
        t.setContentsMargins(0, 0, 0, 0)
        t.setHorizontalSpacing(10)
        t.setVerticalSpacing(4)
        ka = QLabel(K.t('KAS PASAKYTA'))
        ka.setObjectName('antraste')
        kb = QLabel(K.t('KAS IŠVERSTA'))
        kb.setObjectName('antraste')
        t.addWidget(ka, 0, 0)
        t.addWidget(kb, 0, 1)
        self.originalas = QTextEdit()
        self.originalas.setReadOnly(True)
        self.vertimas = QTextEdit()
        self.vertimas.setReadOnly(True)
        t.addWidget(self.originalas, 1, 0)
        t.addWidget(self.vertimas, 1, 1)
        t.setColumnStretch(0, 1)
        t.setColumnStretch(1, 1)
        self.tekstas.setVisible(False)
        v.addWidget(self.tekstas, 1)

        # Nustatymai gyvena dantratyje, ne lange: pokalbio metu jų niekas neliečia,
        # o naujų (Robertas: „gal dar kokių atsiras") ten telpa be lango perstatymo.
        self.nust = {k: self.issaugota[k] for k in
                     ('sveikintis_a', 'sveikintis_b', 'trumpai',
                      'atsisveikinti_a', 'atsisveikinti_b', 'tekstas', 'zurnalas', 'virsuje',
                      'stenograma', 'garso_irasas')}

        self.a.pakeista.connect(self._kalbos_pakeistos)
        self.b.pakeista.connect(self._kalbos_pakeistos)
        self.a.balsas_bandomas.connect(lambda: self._balsas_bandomas(self.a))
        self.b.balsas_bandomas.connect(lambda: self._balsas_bandomas(self.b))
        # „Pradėti" atsirakina tik paruošus (Roberto sprendimas 09-18: Play = jau dirbam).
        self.paruosta = False
        self.pradeti.setEnabled(False)
        self._ikelk_irenginius()
        self._ikelk_balsus()
        self._atnaujink_rezima()
        if self.nust.get('virsuje'):
            self._virsuje(True)
        if self.nust.get('tekstas'):
            self._teksto_jungiklis(True)

        # Banga juda nuo pat paleidimo, dar nespaudus „Pradėti" — kad mikrofoną
        # būtų galima patikrinti prieš pokalbį, o ne pokalbio viduryje.
        self.laikmatis = QTimer(self)
        self.laikmatis.timeout.connect(self._tiksi)
        self.laikmatis.start(64)
        self._atnaujink_lemputes()      # teisingos nuo pirmos akimirkos, dar nepratiksėjus
        # Mikrofonas atidaromas iškart: banga turi rodyti tiesą DAR NESPAUDUS „Pradėti",
        # kad įrangą būtų galima pasitikrinti prieš pokalbį.
        if self.variklis and hasattr(self.variklis, 'stebek'):
            QTimer.singleShot(200, lambda: self.variklis.stebek(self.mikrofonas.currentData()))
        self.mikrofonas.currentIndexChanged.connect(self._mikrofonas_pakeistas)

    # ---------- kabliukai varikliui ----------
    def _ikelk_irenginius(self):
        # ⛔ Sąrašą ima `garsas.irenginiu_sarasas()`, o NE savo kopija. Iki 09-18 čia stovėjo
        # atskiras, beveik toks pat ciklas — du tiesos šaltiniai tam pačiam dalykui. Būtent
        # dėl tokio dublikato 09-16 Ingutė nepateko į balsų sąrašą, nors `balsas.py` ją turėjo.
        try:
            from garsas import irenginiu_sarasas
            for i, vardas in irenginiu_sarasas():
                # ⛔ Įsimenam VARDĄ, ne indeksą `i` — indeksai slankioja, kai įrenginiai
                # atsijungia (žr. `garsas.irenginio_indeksas`). 09-19 pamatuota gyvai.
                self.mikrofonas.addItem(vardas, vardas)
        except Exception:
            self.mikrofonas.addItem(K.t('Mikrofonas nerastas'), None)
        pask = self.issaugota.get('mikrofonas')
        if pask is not None:
            i = self.mikrofonas.findData(pask)
            if i >= 0:
                self.mikrofonas.setCurrentIndex(i)

    def _ikelk_balsus(self):
        """Balsų sarasas iš Piper katalogo; jei kalbos ten nėra — mūsų pridėtas balsas."""
        sarasas = {}
        try:
            import json
            from huggingface_hub import hf_hub_download
            d = json.load(open(hf_hub_download('rhasspy/piper-voices', 'voices.json'), encoding='utf-8'))
            for raktas, x in d.items():
                k = x['language']['family']
                sarasas.setdefault(k, []).append((raktas, '%s (%s)' % (x['name'], x['quality'])))
        except Exception:
            pass
        # Lietuvių kalbai imam SAVO balsus ir katalogo įrašus PAKEIČIAM, o ne papildom.
        # Nuo 09-17 Reginutė jau yra oficialiame kataloge (PR #103), tad senas „pridedam savo"
        # davė tą patį balsą DU kartus (Robertas pamatė 09-18: „lietuviškos vertėjos dvi ir abi
        # reginutės"). Paimti katalogo versijos negalim: jos konfige `phoneme_type: lithuanian`,
        # kurio dabartinis piper-tts neužkrauna — fonemas paduodam patys (`balsas.py`).
        # ⏭️ Sulietus PR #296 šitą pakeitimą reikės atšaukti ir grįžti prie katalogo.
        for kalba, balsai in MUSU_BALSAI.items():
            sarasas[kalba] = list(balsai)
        self._balsu_sarasas = sarasas
        self._kalbos_pakeistos()
        # Balsas: pirma tai, ką vartotojas rinkosi praeitą kartą; jei nėra — numatytasis
        # (rusišką Robertas rinkosi ausimis 09-12 — Ruslanas).
        for zyme, puse in (('a', self.a), ('b', self.b)):
            raktas = self.issaugota.get(zyme + '_balsas') or NUMATYTI.get(puse.dabartine_kalba())
            if raktas:
                i = puse.balsas.findData(raktas)
                if i >= 0:
                    puse.balsas.setCurrentIndex(i)
            lytis = self.issaugota.get(zyme + '_lytis')
            if lytis:
                j = puse.lytis.findData(lytis)
                if j >= 0:
                    puse.lytis.setCurrentIndex(j)
            puse.greitis.setValue(int(self.issaugota.get(zyme + '_greitis', 100)))
            puse.garsas.setValue(int(self.issaugota.get(zyme + '_garsas', 0)))
            puse.uzpildyk_ausis(self.issaugota.get(zyme + '_ausys'))

    def _kalbos_pakeistos(self):
        # Apsauga nuo rekursijos: balsų sąrašo perpildymas pats sukelia `pakeista`,
        # o tas grįžta čia. Be vėliavėlės langas kryžmai kviečia save iki kritimo.
        if getattr(self, '_pildo', False):
            return
        self._pildo = True
        try:
            self._perpildyk_balsus()
        finally:
            self._pildo = False
        if self.variklis:
            self.variklis.kalbos_pakeistos(self.a.dabartine_kalba(), self.b.dabartine_kalba())
        self._atsauk_paruosima(K.t('pakeista kalba'))

    def _perpildyk_balsus(self):
        for puse in (self.a, self.b):
            k = puse.dabartine_kalba()
            dabar = puse.dabartinis_balsas()
            nauji = self._balsu_sarasas.get(k, [])
            if [r for r, _ in nauji] != [puse.balsas.itemData(i) for i in range(puse.balsas.count())]:
                puse.uzpildyk_balsus(nauji)
                if dabar:
                    i = puse.balsas.findData(dabar)
                    if i >= 0:
                        puse.balsas.setCurrentIndex(i)

    # ---------- dantratis ir klaustukas ----------
    def _rodyk_nustatymus(self):
        m = QMenu(self)

        def varnele(tekstas, raktas, veiksmas=None, leidziama=True, priverstinai=None):
            v = QAction(tekstas, self, checkable=True)
            # `priverstinai` — kai režimas pats nulemia reikšmę ir nustatymas nieko nekeičia.
            v.setChecked(bool(self.nust[raktas]) if priverstinai is None else priverstinai)
            v.setEnabled(leidziama)
            v.triggered.connect(lambda ar, r=raktas, f=veiksmas: self._perjunk(r, ar, f))
            m.addAction(v)
            return v

        # ⛔ Sekretorės režimu šitie keturi punktai nieko nekeičia, ir varnelė, kurią galima
        # nuimti, MELUOTŲ: nuėmus „Rašyti stenogramą" ji vis tiek būtų rašoma. Tai ta pati
        # „slapta neįrašinėjam" taisyklė iš kitos pusės (Robertas pamatė 09-18). Todėl jie
        # lieka matomi, bet užrakinti — kaip ir svečio pusė.
        sek = self.rezimas == 'sekretore'
        # ⭐ Prisistatymas ir padėka — ATSKIROS EILUTĖS kiekvienai pusei (Roberto sumanymas
        # 09-18): *„savininkas žino, kas ką darys… gali tekti tik svečiui paleisti tą
        # prisistatymą, kad laiko negaišinti."* Abu trunka ~17 s, vienas — ~9 s.
        # ⛔ Nuėmus abi varneles pranešimas apie ĮRAŠYMĄ vis tiek nuskamba abiem kalbomis
        # (10.6 sk.) — jo išjungti negalima.
        varnele(K.t('Prisistatyti šeimininkui'), 'sveikintis_a', leidziama=not sek,
                priverstinai=True if sek else None)
        varnele(K.t('Prisistatyti svečiui'), 'sveikintis_b', leidziama=not sek,
                priverstinai=False if sek else None)
        varnele(K.t('Trumpas prisistatymas'), 'trumpai',
                leidziama=(self.nust['sveikintis_a'] or self.nust['sveikintis_b']) and not sek,
                priverstinai=True if sek else None)
        varnele(K.t('Padėkoti šeimininkui'), 'atsisveikinti_a', leidziama=not sek,
                priverstinai=False if sek else None)
        varnele(K.t('Padėkoti svečiui'), 'atsisveikinti_b', leidziama=not sek,
                priverstinai=False if sek else None)
        m.addSeparator()
        # Stenograma numatytai ĮJUNGTA, todėl katalogą pasiekti turi būti taip pat lengva,
        # kaip ją išjungti — kitaip numatytas įjungimas būtų nesąžiningas (10.7 sk.).
        varnele(K.t('Rašyti susirinkimo stenogramą') if sek else K.t('Rašyti pokalbio stenogramą'),
                'stenograma', leidziama=not sek, priverstinai=True if sek else None)
        # Garso įrašas — ATSKIRA varnelė, nes tai kitos klasės dalykas nei tekstas: faile
        # lieka žmonių balsai. Kolonėlė apie jį praneša atskirais žodžiais.
        # ⛔ Buvo „(galima atsisukti)" — ir VISOS TRYS kalbos nepriklausomai išvertė tai kaip
        # „galima atsisakyti" (можно отказаться / kann abgelehnt werden / you can decline).
        # Trys vienodos klaidos ⇒ kaltas ne vertimas, o dviprasmis lietuviškas sakinys.
        # Roberto sprendimas 2026-09-19: *„su galėsite perklausyti gerokai geriau."*
        varnele(K.t('Įrašinėti garsą (galėsite perklausyti)'), 'garso_irasas')
        v = QAction(K.t('Atverti stenogramų katalogą…'), self)
        v.triggered.connect(self._rodyk_stenogramas)
        m.addAction(v)
        m.addSeparator()
        # ⭐ SĄSAJOS KALBA (Roberto užsakymas 2026-09-19): *„padarai dovaną pasauliui, pasiima
        # vokietis programą su lietuvišku interfeisu — ką jis supranta?"*
        # ⛔ Ne langelis pagrindiniame lange, kaip kitose dovanose: čia jau yra TRYS kalbų
        # langeliai (šeimininko, svečio, ausų), ir ketvirtas šalia jų verstų klausti, kuri iš
        # jų kuri. Roberto forma: *„dantratis, kalba į šoną, langelis prasiplečia."*
        # Kalbų vardai rašomi SAVO kalba — taip savąją atpažįsti ir tada, kai visa kita
        # sąsaja nesuprantama.
        kalbu_meniu = m.addMenu(K.t('Kalba'))
        for kodas in K.KALBOS:
            vk = QAction(K.VARDAI[kodas], self, checkable=True)
            vk.setChecked(kodas == K.LANG)
            vk.triggered.connect(lambda _ar, kod=kodas: self._kalba_pasirinkta(kod))
            kalbu_meniu.addAction(vk)
        varnele(K.t('Visada viršuje'), 'virsuje', self._virsuje)
        varnele(K.t('Rodyti tekstą (derinimui)'), 'tekstas', self._teksto_jungiklis)
        varnele(K.t('Rašyti derinimo žurnalą'), 'zurnalas')
        if self.nust['zurnalas']:
            v = QAction(K.t('Žurnalas: vertejas.log…'), self)
            v.triggered.connect(self._rodyk_zurnala)
            m.addAction(v)
        m.addSeparator()
        # Tas pats sąžiningumas kaip Diktuoklėje: sakom, kas iš tikrųjų vyksta.
        for tekstas in (K.t('Garsas ir tekstas lieka šiame kompiuteryje'),
                        K.t('Ausys: Paprika — Kristijonas Jakubsonas'),
                        K.t('Vertimas: OPUS-MT, Helsinkio universitetas')):
            v = QAction(tekstas, self)
            v.setEnabled(False)
            m.addAction(v)
        m.exec(self.b_nust.mapToGlobal(self.b_nust.rect().bottomLeft()))

    def _paruosti_paspaustas(self):
        if self.variklis and hasattr(self.variklis, 'paruosk_darbui'):
            self.paruosti.setEnabled(False)
            self.paruosimo_uzuomina.setText(K.t('kraunu…'))
            self.variklis.paruosk_darbui()

    def paruosimas_baigtas(self, pavyko: bool):
        """Variklis pranešė, kad modeliai užkrauti (arba nepavyko)."""
        self.paruosta = bool(pavyko)
        self.paruosti.setEnabled(not pavyko)
        self.pradeti.setEnabled(pavyko)
        self.paruosimo_uzuomina.setText(
            K.t('viskas užkrauta — galima pradėti') if pavyko else K.t('paruošti nepavyko'))
        # Užkrovus modelius kalbos ir balsai jau nebekeičiami: jie įkrauti tokie, kokie buvo.
        self._uzrakink(pavyko)

    def _balsas_bandomas(self, puse):
        if not (self.variklis and hasattr(self.variklis, 'pabandyk_balsa')):
            return
        # Su garsumu — kitaip ▸ meluotų: girdėtum ne tą garsą, kurį išgirs kambarys.
        self.variklis.pabandyk_balsa(puse.dabartine_kalba(), puse.dabartinis_balsas(),
                                     puse.dabartine_lytis(), puse.dabartinis_greitis(),
                                     puse.dabartinis_garsas())

    def _rezimas_pasirinktas(self, kuris):
        """Režimas keičiamas TIK tarp pokalbių: vidury pokalbio tai reikštų kitą programą."""
        if self.dirba:
            self._atnaujink_rezima()      # grąžinam varneles į tikrą padėtį
            self.rodyk_busena(K.t('Režimą galima keisti tik sustabdžius'), '#E8B84B')
            return
        self.rezimas = kuris
        self._atnaujink_rezima()
        self._atsauk_paruosima(K.t('režimas pakeistas'))

    def _atsauk_paruosima(self, kodel=''):
        """Pakeitus kalbą, balsą ar režimą, užkrauti modeliai nebetinka — ruošiamės iš naujo."""
        if not getattr(self, 'paruosta', False):
            return
        if self.variklis and hasattr(self.variklis, 'atlaisvink'):
            self.variklis.atlaisvink()
        self._atstatyk_paruosima()
        if kodel:
            self.rodyk_busena(K.t('Paruošimas atšauktas (%s) — paruoškite iš naujo') % kodel,
                              '#E8B84B')

    def _atnaujink_rezima(self):
        sekretore = self.rezimas == 'sekretore'
        self.m_vertejas.setChecked(not sekretore)
        self.m_sekretore.setChecked(sekretore)
        # Roberto sprendimas 09-18: antra pusė sekretorės režimu lieka MATOMA, bet užrakinta —
        # matosi, kad ji yra ir kad čia nenaudojama.
        # Pilkėja viskas — antraštė, laukeliai, užrašai ir greičio juosta (Roberto
        # patikslinimas: „tame tarpe ir greičio juosta") — IŠSKYRUS patį perjungiklį,
        # kitaip iš sekretorės nebebūtų kaip grįžti.
        self.b.blankink(sekretore)
        self._uzrakink(self.dirba)
        self.setWindowTitle('SpeakDream — ' + (K.t('Sekretorė') if sekretore else K.t('Vertėjas')))

    def _perjunk(self, raktas, ar, veiksmas=None):
        self.nust[raktas] = ar
        if veiksmas:
            veiksmas(ar)

    def _virsuje(self, ar):
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, ar)
        self.show()

    def _kalba_pasirinkta(self, kodas):
        """Sąsajos kalba pakeista dantratyje — programa persileidžia.

        Roberto sprendimas 09-19: *„interfeiso kalba be programos perkrovimo nesigaus, bet tai
        viskas gražu, veiks taip pat — pasispaudė varnelę, programa persikrovė."* Gyvas
        perpiešimas būtų kainavęs daugiau nei visi vertimai kartu sudėjus, o kalbą žmogus
        renkasi kartą.

        ⛔ EILĖ SVARBI, ir ji ne akivaizdi:
          1. `close()` — jis išsaugo VISUS nustatymus (su dar SENA kalba) ir tvarkingai užveria
             stenogramą bei garso įrašą (tas pats kelias, kaip kryžiukui, patikrintas `46_`);
          2. tik PO to įrašom naują kalbą — kitaip pirmas žingsnis ją tyliai perrašytų atgal;
          3. ir tik po to keliam naują procesą — kitaip jis spėtų perskaityti failą per anksti.
        """
        if kodas == K.LANG:
            return
        # Vidury derybų persileisti negalima: dingtų ir pokalbis, ir įrašas. Ta pati taisyklė,
        # kaip režimui (09-18) — keičiama tik tarp pokalbių.
        if self.dirba:
            self.rodyk_busena(K.t('Kalbą galima keisti tik sustabdžius'), '#E8B84B')
            return
        self.close()
        try:
            K.issaugoti_kalba(kodas)
        except Exception as e:
            self.rodyk_busena(K.t('Kalbos išsaugoti nepavyko: %s')
                              % str(e).splitlines()[0], '#ff6a6a')
            self.show()
            return
        # Supakuotoje dovanoje `sys.executable` yra pati programa, o paleidus iš šaltinių —
        # Python, kuriam dar reikia paduoti skriptą. Kelias imamas absoliutus: darbinis
        # katalogas naujam procesui gali būti kitas.
        if getattr(sys, 'frozen', False):
            pavyko = QProcess.startDetached(sys.executable, sys.argv[1:])
        else:
            pavyko = QProcess.startDetached(sys.executable,
                                            [os.path.abspath(sys.argv[0])] + sys.argv[1:])
        # ⛔ `startDetached` grąžina, ar pavyko. Netikrinant jo programa užsidarytų NET tada,
        # kai naujas langas neatsidaro — žmogus liktų be nieko ir nesuprastų, kas nutiko
        # (nustatymuose kalba jau pakeista, tad paleidęs ranka jis pamatytų naują kalbą, o
        # dingimo priežasties nesužinotų niekada).
        if not pavyko:
            self.show()
            self.rodyk_busena(K.t('Nepavyko persileisti — paleiskite programą patys'), '#ff6a6a')
            return
        QApplication.quit()

    def _rodyk_zurnala(self):
        if self.variklis and hasattr(self.variklis, 'zurnalo_kelias'):
            os.startfile(self.variklis.zurnalo_kelias())

    def _rodyk_stenogramas(self):
        """Atveria stenogramų katalogą — ir tuščią, jei dar nieko neužrašyta."""
        import stenograma as S
        try:
            os.startfile(S.paruosk_kataloga())
        except Exception as e:
            self.rodyk_busena(K.t('Nepavyko atverti katalogo: %s')
                              % str(e).splitlines()[0], '#ff6a6a')

    def _rodyk_apie(self):
        d = QDialog(self)
        d.setWindowTitle(K.t('Apie programą'))
        lay = QVBoxLayout(d)
        lay.setContentsMargins(18, 16, 18, 14)
        lay.setSpacing(8)
        p = QLabel('SpeakDream')
        p.setStyleSheet('font-size: 18px; font-weight: bold; color: #ffffff;')
        lay.addWidget(p)
        lay.addWidget(QLabel(K.t('Gyvas pokalbio vertėjas be interneto —\n'
                                 'garsas niekur nesiunčiamas, viskas lieka kompiuteryje.')))
        a = QLabel('Robertas & Claude')
        a.setStyleSheet('color: #8f8f8f;')
        lay.addWidget(a)
        # Šeimos taisyklė (Robertas 09-08, ES DI aktas 50 str.): kas daryta su DI, pasakoma
        # viršuje. Nuo 09-21 ir ikona — GPT piešinys, tad žyma apima ir ją.
        di = QLabel(K.t('Sukurta naudojant DI: kodą rašė Claude, ikoną nupiešė DI.\n'
                        'Jūsų pokalbis yra jūsų — programa jį tik išverčia.'))
        di.setStyleSheet('color: #E8B84B; font-size: 12px;')
        lay.addWidget(di)
        s = QLabel(K.t('Ausys — Paprika, Kristijonas Jakubsonas (CC BY 4.0)\n'
                       'Vertimas — OPUS-MT, Helsinkio universitetas (CC BY 4.0)\n'
                       'Balsas — Piper (MIT); lietuviškas balsas Reginutė\n'
                       'Variklis — faster-whisper (MIT)'))
        s.setStyleSheet('color: #9a9a9a; font-size: 12px;')
        lay.addWidget(s)
        n = QLabel(K.t('Kūrėjo puslapis: <a href="https://github.com/RobertasTa" '
                       'style="color:#4f9cf7; font-weight:bold;">GitHub</a>'))
        n.setOpenExternalLinks(True)
        lay.addWidget(n)
        b = QPushButton(K.t('Gerai'))
        b.clicked.connect(d.accept)
        e = QHBoxLayout()
        e.addStretch(1)
        e.addWidget(b)
        lay.addLayout(e)
        d.exec()

    def _rodyk_instrukcija(self):
        d = QDialog(self)
        d.setWindowTitle(K.t('Instrukcija'))
        d.setMinimumSize(560, 420)
        lay = QVBoxLayout(d)
        t = QTextEdit()
        t.setReadOnly(True)
        # ⚠️ Raktas čia — VISAS instrukcijos tekstas (1 321 simbolis). Patikra, tikrinanti
        # `K.t("…")` su konstanta, jo nemato, tad `_matavimas\51_vertimu_patikra.py` turi
        # atskirą ilgųjų tekstų sąrašą (`PER_KINTAMAJI`).
        t.setPlainText(K.t(INSTRUKCIJA))
        lay.addWidget(t)
        b = QPushButton(K.t('Gerai'))
        b.clicked.connect(d.accept)
        e = QHBoxLayout()
        e.addStretch(1)
        e.addWidget(b)
        lay.addLayout(e)
        d.exec()

    def _rodyk_di(self):
        """„Neradote atsakymo? Klauskite DI" — atveria claude.ai su PARUOŠTU klausimu.

        ⛔ Taip daro visos šeimos dovanos (`diktuokle.py` `_klausk_di`), ir taip turi būti:
        žmogui neduodam namų darbo „susirask failą ir nusiųsk" — paspaudė ir jau kalbasi.
        `claude.ai/new?q=` tik UŽPILDO laukelį; išsiunčia pats žmogus. Tinklas liečiamas
        TIK čia ir tik jo ranka.

        Promptas pirma nurodo patarėjui tiesos failą ir tik tada palieka vietą klausimui.
        Priežastis pamatuota 2026-09-19: dirbtinis intelektas, atsakinėdamas iš atminties,
        prasimano — `opus-mt-ja-en` egzistuoja, o `opus-mt-en-ja` NE. Be brief'o patarėjas
        liepia žmogui daryti tai, kas neįmanoma.
        """
        import urllib.parse
        import webbrowser

        d = QMessageBox(self)
        d.setWindowTitle(K.t('Neradote atsakymo? Klauskite DI'))
        ikona = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'SpeakDream.ico')
        if os.path.exists(ikona):
            from PyQt6.QtGui import QIcon
            d.setIconPixmap(QIcon(ikona).pixmap(64, 64))
        d.setText(K.t(
            'Kas įvyks paspaudus „Gerai":\n\n'
            '1. Atsidarys naršyklė su DI padėjėjo claude.ai puslapiu. Žinutės\n'
            '   laukelyje jau bus įrašyta angliška pradžia — prisistatymas,\n'
            '   kas per programa ir ko apie ją klausiama.\n'
            '2. NEIŠSIGĄSKITE raudono pranešimo virš žinutės — claude.ai jį\n'
            '   rodo visada, kai tekstas ateina per nuorodą.\n'
            '3. Žinutės gale, po žodžių „My question:", įrašykite SAVO\n'
            '   klausimą — galima lietuviškai — ir spauskite siuntimą.\n'
            '4. Jei DI atsakys angliškai — paprašykite atsakyti jūsų kalba.\n\n'
            'Pastaba: claude.ai gali paprašyti prisijungti (nemokama paskyra).\n'
            'Niekas neišsiunčiama be jūsų rankos.'))
        d.setStandardButtons(QMessageBox.StandardButton.Ok
                             | QMessageBox.StandardButton.Cancel)
        d.button(QMessageBox.StandardButton.Ok).setText(K.t('Gerai'))
        d.button(QMessageBox.StandardButton.Cancel).setText(K.t('Atšaukti'))
        if d.exec() != QMessageBox.StandardButton.Ok:
            return

        # ⚠️ Kol dovana nepaskelbta, viešos brief'o nuorodos dar nėra — tada patarėjui
        # sakom, kad failas guli ŠALIA programos, ir žmogus gali jį įkelti pats.
        # Paskelbus užpildyti BRIEF_URL, ir šis sakinys pasikeis savaime.
        if BRIEF_URL:
            saltinis = ('Please read %s first — it is the author\'s briefing about this app.'
                        ' If that link does not open yet, the same file, AI_CONSULTANT_BRIEF.md,'
                        ' sits next to the program on my computer; ask me to paste it.'
                        % BRIEF_URL)
        else:
            saltinis = ('The author\'s briefing file AI_CONSULTANT_BRIEF.md sits next to the'
                        ' program on my computer; ask me to paste it if you need the details.')
        # ⛔ Paskutinis sakinys prieš klausimą yra svarbiausias, ir jis atsirado iš gyvo
        # bandymo 2026-09-19: Robertas paklausė būtent apie japonų kalbą, o tai atvejis, kur
        # `opus-mt-en-ja` NEEGZISTUOJA. Patarėjas, atsakinėdamas iš atminties, tokį modelį
        # drąsiai pasiūlytų. Todėl jam čia pat liepiama paleisti patikros įrankį — jis
        # paklausia HuggingFace ir grąžina tiesą, o ne prisiminimą.
        promptas = (
            '%s This is an offline two-person conversation interpreter for Windows: it'
            ' listens through a conference speakerphone, translates, speaks the translation'
            ' aloud, and writes a transcript plus an audio recording. Nothing leaves the PC.'
            ' IMPORTANT: if my question is about adding or installing another language, do'
            ' NOT name translation models from memory — model names that sound right often'
            ' do not exist (for example opus-mt-ja-en exists but opus-mt-en-ja does not).'
            ' Instead tell me to run, in the program folder,'
            ' "prideti_kalba.py <two-letter language code>": it checks the real catalogues'
            ' and prints exactly what is possible and what to change. Ask me for its output'
            ' and answer from that. Then answer my question in plain, human language, in the'
            ' language I write in, no programmer jargon. My question: ' % saltinis)
        webbrowser.open('https://claude.ai/new?q=' + urllib.parse.quote(promptas))

    def _teksto_jungiklis(self, ar):
        """Tekstas atsiveria ir užsiveria kartu su lango aukščiu — kad neliktų tuščio ploto."""
        self.tekstas.setVisible(ar)
        self.setMinimumHeight(self.AUKSTIS_SU_TEKSTU if ar else self.AUKSTIS)
        self.resize(self.width(), self.AUKSTIS_SU_TEKSTU if ar else self.AUKSTIS)

    def _mikrofonas_pakeistas(self, _):
        if self.variklis and hasattr(self.variklis, 'mikrofonas_pakeistas'):
            self.variklis.mikrofonas_pakeistas(self.mikrofonas.currentData())

    def _pauze_pakeista(self, v):
        self.pauzes_reiksme.setText(('%.1f s' % (v / 10)).replace('.', ','))
        if self.variklis:
            self.variklis.pauze_pakeista(v / 10)

    def _tiksi(self):
        if self.variklis:
            self.banga.stumk(self.variklis.garso_lygis())
            self.tyla.nustatyk(self.variklis.tylos_dalis())
        self._atnaujink_lemputes()

    def _atnaujink_lemputes(self):
        """Lemputės rodo TIKROVĘ, ne varnelę (žr. `Lempute`).

        Prieš pokalbį tikrovė yra nustatymas — kas bus rašoma paspaudus „Pradėti".
        Pokalbio metu tikrovė yra failas: klausiam variklio, ar jis TIKRAI atviras. Jei
        rašyti nepavyko, lemputė gęsta, nors varnelė dantratyje liktų įjungta.

        Atnaujinama laikmačio ritmu, o ne tik keičiant nustatymą: taip lemputė pagauna ir
        tai, ko langas nedaro pats (variklio sprendimus, gedimą pusiaukelėje).
        """
        sek = self.rezimas == 'sekretore'
        # ⛔ Sekretorės režimu stenograma rašoma VISADA — varnelė ten nieko nereiškia
        # (ji ir dantratyje užrakinta).
        stenograma = True if sek else bool(self.nust.get('stenograma', True))
        garsas = bool(self.nust.get('garso_irasas', True))
        if self.dirba and self.variklis:
            stenograma = getattr(self.variklis, 'stenograma', None) is not None
            garsas = getattr(self.variklis, 'garso_irasas', None) is not None
        self.l_stenograma.uzdek(
            stenograma,
            (K.t('Pokalbis užrašinėjamas') if self.dirba
             else K.t('Pokalbis bus užrašytas į stenogramą'))
            if stenograma else K.t('Stenograma išjungta'))
        self.l_garsas.uzdek(
            garsas,
            (K.t('Garsas įrašinėjamas — balsai lieka faile') if self.dirba
             else K.t('Garsas bus įrašinėjamas — balsai liks faile'))
            if garsas else K.t('Garso įrašas išjungtas'))

    # ---------- valdymas ----------
    def perjunk(self):
        if not self.dirba:
            self.dirba, self.pauze = True, False
            self.pradeti.setText('❚❚  ' + K.t('Pauzė'))
            self.baigti.setEnabled(True)
            self.rodyk_busena(K.t('Klausau'), '#4ADE80')
            self._uzrakink(True)
            if self.variklis:
                self.variklis.pradek()
        else:
            self.pauze = not self.pauze
            self.pradeti.setText(('▶  ' + K.t('Tęsti')) if self.pauze
                                 else ('❚❚  ' + K.t('Pauzė')))
            self.rodyk_busena(K.t('Pauzė') if self.pauze else K.t('Klausau'),
                              '#E8B84B' if self.pauze else '#4ADE80')
            if self.variklis:
                self.variklis.pauze(self.pauze)

    def stok(self):
        self.dirba, self.pauze = False, False
        self.pradeti.setText('▶  ' + K.t('Pradėti'))
        self.baigti.setEnabled(False)
        self.rodyk_busena(K.t('Pasiruošęs'), '#e6e6e6')
        self._uzrakink(False)
        # Pokalbiui pasibaigus modeliai atlaisvinami, tad „Pradėti" vėl laukia paruošimo.
        self._atstatyk_paruosima()
        if self.variklis:
            self.variklis.baik()

    def _uzrakink(self, ar):
        # ⛔ Qt: išjungus TĖVĄ, visi vaikai miršta kartu — `greitis.setEnabled(True)` po
        # `self.a.setEnabled(False)" nieko nereiškia. Robertas tai pagavo gyvai 09-12 17:30:
        # „pauzės laiko tarpą galima koreguoti, bet kalbėtojų greičio ne".
        # Todėl rakinam TIK tai, ko keisti negalima vidury pokalbio (kalba, ausys, balsas,
        # lytis, mikrofonas), o greičio slankiklis lieka gyvas.
        self.mikrofonas.setEnabled(not ar)
        for puse in (self.a, self.b):
            for w in (puse.kalba, puse.ausys, puse.balsas, puse.lytis):
                w.setEnabled(not ar)
        # Sekretorės režimu antra pusė pilka visada, ne tik pokalbio metu.
        if self.rezimas == 'sekretore':
            self.b.blankink(True)

    def issaugok(self):
        d = {'a_kalba': self.a.dabartine_kalba(), 'b_kalba': self.b.dabartine_kalba(),
             'a_balsas': self.a.dabartinis_balsas(), 'b_balsas': self.b.dabartinis_balsas(),
             'a_lytis': self.a.lytis.currentData(), 'b_lytis': self.b.lytis.currentData(),
             'a_greitis': self.a.greitis.value(), 'b_greitis': self.b.greitis.value(),
             'a_garsas': self.a.garsas.value(), 'b_garsas': self.b.garsas.value(),
             'a_ausys': self.a.dabartines_ausys(), 'b_ausys': self.b.dabartines_ausys(),
             'mikrofonas': self.mikrofonas.currentData(),
             'pauze': self.slankiklis.value(),
             'rezimas': self.rezimas,
             # ⛔ Sąsajos kalba čia būtina, nors langas jos nekeičia: `N.rasyk` perrašo failą
             # TUO, kas paduota, tad be šios eilutės pasirinkta kalba dingtų tyliai —
             # pirmą kartą uždarius programą. Pats kalbos pasirinkimas vyksta dantratyje.
             'sasajos_kalba': K.LANG}
        d.update(self.nust)
        N.rasyk(d)

    def closeEvent(self, e):
        # Kalbos, balsai ir greičiai tie patys kiekvieną kartą — kad kitąkart užtektų
        # paspausti „Pradėti".
        try:
            self.issaugok()
        finally:
            # ⛔ Ne `baik()`: tas paleidžia pabaigą ATSKIRA gija ir iškart grįžta, o
            # `sys.exit` ją nužudo ties atsisveikinimu — garso įrašas lieka neužvertas
            # (Robertas pagavo 09-18 uždaręs langą kryžiuku). `uzverk_skubiai` užveria
            # failus čia pat ir tyliai.
            # ⛔ Ir NE tik kai `self.dirba`: jei „Baigti" jau paspaustas, o atsisveikinimas
            # dar skamba, `dirba` jau False, bet failai dar atviri. Užvėrimas kartojamas
            # be žalos, tad kviečiam visada.
            if self.variklis:
                self.variklis.uzverk_skubiai()
        e.accept()

    def nustatymai(self) -> dict:
        """Viskas, ko varikliui reikia, vienoje vietoje: langas atsako už sąsają, ne už logiką."""
        return {
            'a_kalba': self.a.dabartine_kalba(), 'a_balsas': self.a.dabartinis_balsas(),
            'a_lytis': self.a.dabartine_lytis(), 'a_greitis': self.a.dabartinis_greitis(),
            'a_ausys': self.a.dabartines_ausys(),
            'b_kalba': self.b.dabartine_kalba(), 'b_balsas': self.b.dabartinis_balsas(),
            'b_lytis': self.b.dabartine_lytis(), 'b_greitis': self.b.dabartinis_greitis(),
            'b_ausys': self.b.dabartines_ausys(),
            'mikrofonas': self.mikrofonas.currentData(),
            'pauze': self.slankiklis.value() / 10.0,
            'rezimas': self.rezimas,
            **self.nust,
        }

    # ---------- ką kviečia variklis ----------
    def variklis_sustojo(self):
        """Variklis sustojo pats (klaida) — mygtukai turi grįžti į pradinę padėtį,
        kitaip žmogus spaudytų „Pauzė" ant nieko."""
        self.dirba, self.pauze = False, False
        self.pradeti.setText('▶  ' + K.t('Pradėti'))
        self.baigti.setEnabled(False)
        self._uzrakink(False)
        self._atstatyk_paruosima()

    def _atstatyk_paruosima(self):
        """Po pokalbio modeliai atlaisvinami, tad ruoštis reikia iš naujo."""
        self.paruosta = False
        self.paruosti.setEnabled(True)
        self.pradeti.setEnabled(False)
        self.paruosimo_uzuomina.setText(K.t('kalbos ir balsai dar keičiami'))

    def rodyk_busena(self, tekstas, spalva='#e6e6e6'):
        self.busena.setText(tekstas)
        self.busena.setStyleSheet('color: %s;' % spalva)

    def pridek(self, originalas: str, vertimas: str, kalba: str = ''):
        zyme = '[%s] ' % kalba if kalba else ''
        for laukas, tekstas in ((self.originalas, zyme + originalas), (self.vertimas, vertimas)):
            laukas.moveCursor(QTextCursor.MoveOperation.End)
            laukas.insertPlainText(tekstas + '\n\n')
            laukas.moveCursor(QTextCursor.MoveOperation.End)


def paleisk(variklis=None):
    app = QApplication(sys.argv)
    l = Langas(variklis)
    l.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    paleisk()

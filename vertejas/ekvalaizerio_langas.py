# -*- coding: utf-8 -*-
"""EKVALAIZERIO LANGAS (2026-10-29) — atsidaro dantračiu prie „Greitis".

Roberto pasiūlymas: kiekvieną balsą derinti pagal savo norus. Langas paimtas iš Skaityklės
(`skaitykle\\dantratis.py`) ir apkarpytas iki ekvalaizerio: garsumas ir greitis SpeakDream'e
jau stovi pagrindiniame lange, tad antros jų kopijos čia nereikia.

Langas pats garso negroja ir nieko nesaugo: jis tik praneša apie pokyčius (`pakeista`) ir
paprašo perklausos (`klausyti`) — groja ir saugo pagrindinis langas, kad kelias būtų vienas
(09-18 pamoka: du tiesos šaltiniai tam pačiam = defektas).

⭐ „Suki ir girdi" (Skaityklės principas): paleidus slankiklį pavyzdys pasigirsta iš karto.
Skaityklėje garsas keičiasi grojant; čia frazė trumpa ir sintezuojama iš naujo, tad
perklausa paleidžiama atleidus slankiklį.

Greitis čia — ANTRAS tos pusės „Greitis" slankiklio vaizdas (Roberto prašymas 10-29: „kaip
Skaityklėje"). Tiesa viena — pagrindinio lango slankiklis: šis tik praneša
`greitis_pakeistas`, o langas nustato savąjį. Langas modalus, tad atgal sinchronizuoti nėra ko.
Greitis — tos PUSĖS, ne balso (taip jis veikė ir iki šiol); ekvalaizeris — BALSO.
"""
from functools import partial

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QDialog, QGridLayout, QHBoxLayout, QLabel, QPushButton, QSlider, \
    QVBoxLayout

import ekvalaizeris
import kalba as K


class EkvalaizerioLangas(QDialog):
    pakeista = pyqtSignal()
    klausyti = pyqtSignal()
    greitis_pakeistas = pyqtSignal(int)

    def __init__(self, tevas, balso_vardas, eq, greitis=100):
        super().__init__(tevas)
        self.setWindowTitle(K.t('Ekvalaizeris') + ' — ' + balso_vardas)
        self.setStyleSheet(tevas.styleSheet())

        antraste = QLabel(K.t('Ekvalaizeris') + ' — ' + balso_vardas)
        uzuomina = QLabel(K.t('Nustatymai galioja tik šiam balsui. Paleidus slankiklį pavyzdys '
                              'pasigirsta iš karto. Užveskite pelę ant juostos vardo — '
                              'pamatysite, už ką ji atsakinga.'))
        uzuomina.setObjectName('uzuomina')
        uzuomina.setWordWrap(True)

        tinklas = QGridLayout()
        tinklas.setHorizontalSpacing(14)
        tinklas.setVerticalSpacing(4)
        self.juostos = []
        self._reiksmes = []
        for i, (daznis, vardas, aprasas) in enumerate(ekvalaizeris.JUOSTOS):
            reiksme = QLabel()
            reiksme.setAlignment(Qt.AlignmentFlag.AlignHCenter)
            s = QSlider(Qt.Orientation.Vertical)
            s.setRange(-ekvalaizeris.EQ_RIBA, ekvalaizeris.EQ_RIBA)
            s.setPageStep(3)
            s.setMinimumHeight(150)
            s.setValue(int(eq[i]) if eq and i < len(eq) else 0)
            s.setToolTip(K.t(aprasas))
            s.valueChanged.connect(partial(self._juosta_pakeista, i))
            s.sliderReleased.connect(self.klausyti.emit)
            hz = QLabel(('%d Hz' % daznis) if daznis < 1000 else ('%d kHz' % (daznis // 1000)))
            hz.setObjectName('uzuomina')
            hz.setAlignment(Qt.AlignmentFlag.AlignHCenter)
            pav = QLabel(K.t(vardas))
            pav.setAlignment(Qt.AlignmentFlag.AlignHCenter)
            pav.setToolTip(K.t(aprasas))
            tinklas.addWidget(reiksme, 0, i)
            tinklas.addWidget(s, 1, i, Qt.AlignmentFlag.AlignHCenter)
            tinklas.addWidget(hz, 2, i)
            tinklas.addWidget(pav, 3, i)
            self.juostos.append(s)
            self._reiksmes.append(reiksme)
            self._rodyk_db(reiksme, s.value())

        # Tas pats diapazonas kaip pagrindiniame lange (60–140 = 0,60–1,40×).
        self.greitis = QSlider(Qt.Orientation.Horizontal)
        self.greitis.setRange(60, 140)
        self.greitis.setSingleStep(5)
        self.greitis.setPageStep(10)
        self.greitis.setValue(int(greitis))
        self.greitis.setToolTip(K.t('Kalbėjimo greitis — tas pats, kas pagrindiniame lange.'))
        self.greicio_zyme = QLabel()
        self.greicio_zyme.setMinimumWidth(42)
        self.greitis.valueChanged.connect(self._greitis_judintas)
        self.greitis.sliderReleased.connect(self.klausyti.emit)
        self._rodyk_greiti()
        b_numatytas = QPushButton('↺')
        b_numatytas.setObjectName('ikona')
        b_numatytas.setToolTip(K.t('Balso numatytasis greitis (1,00×)'))
        b_numatytas.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        b_numatytas.clicked.connect(lambda: self.greitis.setValue(100))
        gr = QHBoxLayout()
        gr.setSpacing(10)
        gr.addWidget(QLabel(K.t('Greitis:')))
        gr.addWidget(self.greitis, 1)
        gr.addWidget(self.greicio_zyme)
        gr.addWidget(b_numatytas)

        b_klausyti = QPushButton('▸  ' + K.t('Pasiklausyti'))
        b_klausyti.setProperty('aktyvus', 'taip')
        b_klausyti.clicked.connect(self.klausyti.emit)
        b_atstatyti = QPushButton(K.t('Atstatyti'))
        b_atstatyti.setToolTip(K.t('Visos juostos 0 dB — balsas skamba taip, kaip sukurtas'))
        b_atstatyti.clicked.connect(self._atstatyk)
        b_uzdaryti = QPushButton(K.t('Uždaryti'))
        b_uzdaryti.clicked.connect(self.accept)
        for b in (b_klausyti, b_atstatyti, b_uzdaryti):
            b.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        mygtukai = QHBoxLayout()
        mygtukai.addWidget(b_klausyti)
        mygtukai.addWidget(b_atstatyti)
        mygtukai.addStretch(1)
        mygtukai.addWidget(b_uzdaryti)

        visas = QVBoxLayout(self)
        visas.setContentsMargins(14, 12, 14, 12)
        visas.setSpacing(10)
        visas.addWidget(antraste)
        visas.addWidget(uzuomina)
        visas.addLayout(tinklas)
        visas.addSpacing(4)
        visas.addLayout(gr)
        visas.addLayout(mygtukai)

    def eq(self):
        return [s.value() for s in self.juostos]

    def _rodyk_greiti(self):
        self.greicio_zyme.setText(('%.2f×' % (self.greitis.value() / 100.0)).replace('.', ','))

    def _greitis_judintas(self, v):
        self._rodyk_greiti()
        self.greitis_pakeistas.emit(v)

    @staticmethod
    def _rodyk_db(zyme, v):
        zyme.setText(('%+d dB' % v) if v else '0 dB')

    def _juosta_pakeista(self, i, v):
        self._rodyk_db(self._reiksmes[i], v)
        self.pakeista.emit()

    def _atstatyk(self):
        for s in self.juostos:
            s.setValue(0)
        self.klausyti.emit()

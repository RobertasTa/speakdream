# -*- coding: utf-8 -*-
"""VERTĖJAS — paleidimas.

Du žmonės, dvi kalbos, viena kolonėlė tarp jų. Viskas šiame kompiuteryje, be interneto.
Kas ir kodėl vyksta viduje — `ALGORITMAS.md` (jis pirmesnis už kodą).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def _uzkaisk_isvesti():
    """Be konsolės `sys.stdout` ir `sys.stderr` yra `None` — ir tai NUVERČIA programą.

    ⛔ Rasta 2026-09-18 gyvai: paleidus per `pythonw` (be juodo lango) pirmas bibliotekos
    `logging` bandymas kažką parašyti krito su `AttributeError: 'NoneType' object has no
    attribute 'write'`, ir kartu su juo nulūžo visas vertimo ciklas. Robertas pamatė raudoną
    „Klaida — žr. žurnalą" viduryje pokalbio.

    ⚠️ Tai NE paleidimo keistenybė: **įdiegta programa veiks lygiai taip pat**, be konsolės
    (`console=False`). Tas pats spąstas jau užrašytas `OKF_PyInstaller` guard'e po Diktuoklės
    pakavimo — tik ten jį pagavom pakete, o čia jis pasiekė gyvą pokalbį.

    Antra to paties pobūdžio bėda — `UnicodeEncodeError` ties „→": Windows konsolė dirba ne
    UTF-8, o mūsų žurnalo eilutėse yra rodyklių ir lietuviškų raidžių.
    """
    for vardas in ('stdout', 'stderr'):
        srautas = getattr(sys, vardas, None)
        if srautas is None:
            # Niekur nerašom, bet `write` egzistuoja — bibliotekoms to užtenka.
            setattr(sys, vardas, open(os.devnull, 'w', encoding='utf-8'))
        else:
            try:
                srautas.reconfigure(encoding='utf-8', errors='replace')
            except Exception:
                pass


_uzkaisk_isvesti()

from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication

from langas import Langas
from variklis import Variklis


def main():
    app = QApplication(sys.argv)
    # Lango ikona nustatoma PAČIAI programai (Roberto radinys 2026-09-21: užduočių juostoje
    # ikona buvo, o lango antraštėje — bendra Windows). Užduočių juosta ją ima iš exe, o Qt
    # antraštei ieško resurso vardu „IDI_ICON1", kurio PyInstaller neįrašo. Failas ir iš
    # šaltinių, ir pakete guli šalia `main.py` (`.spec` `datas` deda jį į `_internal\`).
    ikona = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'SpeakDream.ico')
    if os.path.exists(ikona):
        app.setWindowIcon(QIcon(ikona))
    # Stenogramų katalogas paruošiamas IŠ KARTO (Roberto sprendimas 09-18), kad „Atverti
    # stenogramų katalogą" veiktų nuo pirmos sekundės — dar nieko neužrašius. Įdiegus
    # programą tą patį turės padaryti instaliatorius.
    from stenograma import paruosk_kataloga
    paruosk_kataloga()
    variklis = Variklis()
    langas = Langas(variklis)
    variklis.langas = langas
    # Fono gijos lango NELIEČIA — jos siunčia signalus, o Qt juos pristato GUI gijoje.
    variklis.busena_sig.connect(langas.rodyk_busena)
    variklis.eilute_sig.connect(langas.pridek)
    variklis.baigta_sig.connect(langas.variklis_sustojo)
    variklis.paruosta_sig.connect(langas.paruosimas_baigtas)
    langas.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()

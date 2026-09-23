# -*- coding: utf-8 -*-
"""SĄSAJOS KALBA — LT / EN / RU / DE (2026-09-19).

Roberto užsakymas: *„padarai dovaną pasauliui, pasiima vokietis programą su lietuvišku
interfeisu — ką jis supranta?"*

Šablonas paimtas iš PHOTO home `foto_namai\\kalba.py` (dviračio neišradinėjam —
`DOVANU_ZEMELAPIS.md` rodo būtent ten): **lietuviškas sakinys yra pats raktas**, `t()` grąžina
vertimą arba, jei jo nėra, patį raktą. Nulis Qt priklausomybių, tad `kalba.py` importuojamas
anksčiau už bet kokį langą.

⛔ **KAS NEVERČIAMA IR KODĖL** (sprendimai 2026-09-19):

* **Kolonėlės frazės** (`frazes.py`) ir **stenogramos failai** (`stenograma.py`) — jų kalba yra
  POKALBIO kalba, ne sąsajos. Stenogramą parsineša pokalbio dalyvis, o ne programos savininkas:
  vokietis, užrašęs lietuvio ir ruso derybas, negali įduoti rusui failo su vokiškomis
  antraštėmis. Riba: **ekranas — sąsajos kalba, kambarys ir failai — pokalbio kalba.**
* **Derinimo žurnalas** (`variklis._zurnalas`) — jis skirtas mums, ne vartotojui; dantratyje taip
  ir parašyta („Rašyti derinimo žurnalą").
* **Balsų vardai** iš Piper katalogo ir **kalbų pavadinimai** — jie visada rašomi savo kalba
  (Deutsch, Русский), o ne verčiami.
* **Santrumpos** `mėn`, `žr`, `tūkst` (`vertimas.py`) — jos skirtos LIETUVIŠKAM tekstui skaidyti
  sakiniais, o ne rodomos ekrane.

Kalbos pasirinkimo eilė:
  1. `VERTEJAS_LANG` aplinkos kintamasis (patikroms — kad testas nepriklausytų nuo nustatymų);
  2. `nustatymai.json` raktas `sasajos_kalba` (žmogaus pasirinkimas dantratyje);
  3. Windows sąsajos kalba: lietuviška sistema → LT, rusiška → RU, vokiška → DE, visos kitos → EN.

⭐ Trečias punktas yra svarbiausias: vokietis, pirmą kartą paleidęs dovaną, **nieko nesirenka** —
programa atsidaro jo kalba pati. Meniu „Kalba" lieka tam, kad būtų galima pasitaisyti (vokietis
Lietuvoje, lietuvis su angliška Windows).
"""
import os

KALBOS = ('lt', 'en', 'ru', 'de')

# Meniu punktai rašomi SAVO kalba — taip daro visi, ir taip žmogus savo kalbą atpažįsta,
# net kai sąsaja jam nesuprantama.
VARDAI = {'lt': 'Lietuvių', 'en': 'English', 'ru': 'Русский', 'de': 'Deutsch'}

# Windows pirminiai kalbų ID (LANGID & 0x3FF) — tas pats žemėlapis, kaip PHOTO home.
_OS_LANGID = {0x27: 'lt', 0x19: 'ru', 0x07: 'de'}


def _os_kalba():
    """Pirmam paleidimui: kokia kalba kalba pati Windows."""
    try:
        import ctypes
        langid = ctypes.windll.kernel32.GetUserDefaultUILanguage()
        return _OS_LANGID.get(langid & 0x3FF, 'en')
    except Exception:
        pass
    try:
        import locale
        loc = (locale.getlocale()[0] or '').lower()
        for pre, k in (('lt', 'lt'), ('ru', 'ru'), ('de', 'de')):
            if loc.startswith(pre):
                return k
    except Exception:
        pass
    return 'en'


def _issaugota_kalba():
    """Žmogaus pasirinkimas iš `nustatymai.json`. ⛔ Atskiro failo NEDAROM: Vertėjas jau turi
    vieną vietą nustatymams, ir antra vieta būtų tas pats „du tiesos šaltiniai", dėl kurio
    09-16 Ingutė nepateko į balsų sąrašą."""
    try:
        import nustatymai
        v = nustatymai.skaityk().get('sasajos_kalba')
        return v if v in KALBOS else None
    except Exception:
        return None


def issaugoti_kalba(kodas):
    """Įrašo pasirinkimą. Įsigalioja perleidus programą (Roberto sprendimas 09-19:
    *„pasispaudė varnelę, programa persikrovė"*) — gyvas perpiešimas kainuotų daugiau nei
    visi vertimai kartu sudėjus, o kalbą žmogus renkasi kartą."""
    if kodas not in KALBOS:
        raise ValueError('nezinoma kalba: %r' % (kodas,))
    import nustatymai
    d = nustatymai.skaityk()
    d['sasajos_kalba'] = kodas
    nustatymai.rasyk(d)


_env = os.environ.get('VERTEJAS_LANG')
LANG = _env if _env in KALBOS else (_issaugota_kalba() or _os_kalba())

_ZODYNAI = {}
for _k in ('en', 'ru', 'de'):
    try:
        _ZODYNAI[_k] = __import__('kalba_' + _k).ZODYNAS
    except Exception:
        # Trūkstamas žodynas neturi nuversti programos: be jo matysis lietuviški raktai,
        # ir tai blogiau nei vertimas, bet daug geriau nei nepasileidžianti dovana.
        _ZODYNAI[_k] = {}


def t(tekstas):
    """Lietuviškas sakinys → tos pačios prasmės sakinys pasirinkta kalba.

    Nerastas raktas grąžinamas toks, koks yra: programa dirba toliau, o trūkumą pagauna
    `_matavimas\\51_vertimu_patikra.py` (paimta iš Diktuoklės) — akimis tokio gedimo nemato
    niekas, išskyrus tą, kuris ta kalba skaito."""
    if LANG == 'lt':
        return tekstas
    return _ZODYNAI.get(LANG, {}).get(tekstas, tekstas)

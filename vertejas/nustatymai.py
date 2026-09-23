# -*- coding: utf-8 -*-
"""NUSTATYMŲ ĮSIMINIMAS (09-12).

Vertėjas nėra programa, kurią atsidarai kartą: kalbos, balsai, greičiai ir mikrofonas tie patys
kiekvieną kartą. Jei jų nereikės rinkti iš naujo, žmogus paleis ir iškart spaus „Pradėti".

Rašom į `%LOCALAPPDATA%\\SpeakDream\\nustatymai.json`. Sakom tiesą (kaip Diktuoklėje): nustatymai
į diską RAŠOMI — bet garsas ir tekstas iš kompiuterio neišeina niekada.
"""
import json
import os

KATALOGAS = os.path.join(os.environ.get('LOCALAPPDATA', os.path.expanduser('~')), 'SpeakDream')
FAILAS = os.path.join(KATALOGAS, 'nustatymai.json')

NUMATYTA = {
    'a_kalba': 'lt', 'b_kalba': 'ru',
    'a_balsas': None, 'b_balsas': None,        # None → iš NUMATYTI sąrašo
    'a_lytis': None, 'b_lytis': None,
    'a_greitis': 100, 'b_greitis': 100,
    'a_ausys': None, 'b_ausys': None,          # None → numatytos tai kalbai
    'mikrofonas': None,                         # None → sistemos numatytasis
    'pauze': 10,                                # dešimtosios sekundės
    # ⭐ Prisistatymas ir padėka — KIEKVIENAI PUSEI ATSKIRAI (Roberto sumanymas 09-18):
    # *„jei savininkas leidžia programą, tai jis žino, kas ką darys ir kaip kalbėti — gali tekti
    # tik svečiui paleisti tą prisistatymą… na pagal poreikį, kad laiko negaišinti."*
    # Abu prisistatymai trunka ~17 s; vienas — ~9 s.
    # ⛔ Bet pranešimas apie ĮRAŠYMĄ sakomas VISADA ir ABIEM (10.6 sk.): nutylėjus jį vienai
    # pusei ta pusė nežinotų, kad įrašinėjama, ir negalėtų nesutikti.
    'sveikintis_a': True, 'sveikintis_b': True,
    'trumpai': False,
    'atsisveikinti_a': True, 'atsisveikinti_b': True,
    'tekstas': False, 'zurnalas': True, 'virsuje': False,
    # ⛔ Stenograma numatytai ĮJUNGTA (Roberto sprendimas 09-17): pamiršus įjungti prarandi
    # pokalbį negrįžtamai, pamiršus išjungti — tik nereikalingą failą, kurį ištrinti užtrunka
    # sekundę. Todėl ir pranešimas apie įrašymą išjungiamas būti negali.
    'stenograma': True,
    # ⛔ Garso įrašas irgi numatytai ĮJUNGTAS (Roberto sprendimas 09-18). Jis uždaro paskutinę
    # skylę: stenogramos eilutės yra mašinos ausų versija, o su garsu jas galima pasitikrinti
    # prie šaltinio. Kaina pamatuota — FLAC ~23 MB valandai.
    # ⚠️ Balsas yra jautresnis dalykas nei tekstas, todėl kolonėlė apie įrašymą praneša
    # ATSKIRAI ir kitais žodžiais nei apie stenogramą.
    'garso_irasas': True,
    'rezimas': 'vertejas',      # 'vertejas' arba 'sekretore'
    # ⭐ SĄSAJOS kalba (2026-09-19) — NE pokalbio kalba. None reiškia „dar nesirinkta",
    # ir tada `kalba.py` ima ją iš Windows: vokietis, pirmą kartą paleidęs dovaną, nieko
    # nesirenka. Keičiama dantratyje („Kalba"), įsigalioja perleidus programą.
    'sasajos_kalba': None,
}


def skaityk() -> dict:
    d = dict(NUMATYTA)
    try:
        with open(FAILAS, encoding='utf-8') as f:
            issaugota = json.load(f)
        if isinstance(issaugota, dict):
            # Seni failai (iki 09-18) turėjo po vieną bendrą raktą abiem pusėms. Perkeliam jį
            # į abi, kad žmogaus pasirinkimas nedingtų tyliai.
            for senas, nauji in (('sveikintis', ('sveikintis_a', 'sveikintis_b')),
                                 ('atsisveikinti', ('atsisveikinti_a', 'atsisveikinti_b'))):
                if senas in issaugota and not any(n in issaugota for n in nauji):
                    for n in nauji:
                        d[n] = bool(issaugota[senas])
            d.update({k: v for k, v in issaugota.items() if k in NUMATYTA})
    except Exception:
        pass          # sugadintas ar nesantis failas — dirbam su numatytaisiais, be triukšmo
    return d


def rasyk(d: dict):
    try:
        os.makedirs(KATALOGAS, exist_ok=True)
        with open(FAILAS, 'w', encoding='utf-8') as f:
            json.dump({k: v for k, v in d.items() if k in NUMATYTA}, f,
                      ensure_ascii=False, indent=1)
    except Exception:
        pass          # negalim išsaugoti — tai ne priežastis trukdyti pokalbiui

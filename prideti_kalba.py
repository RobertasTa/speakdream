# -*- coding: utf-8 -*-
"""AR GALIMA ĮDĖTI ŠIĄ KALBĄ? — patikra prieš darant (2026-09-19).

Šis įrankis skirtas žmogui, kuris nori, kad programa mokėtų dar vieną kalbą, ir jo
konsultantui (dažniausiai — dirbtiniam intelektui).

⛔ **KODĖL JIS EGZISTUOJA.** Dirbtinis intelektas, atsakinėdamas iš atminties, modelių vardus
prasimano. Pamatuota 2026-09-19: `Helsinki-NLP/opus-mt-ja-en` egzistuoja, o
`Helsinki-NLP/opus-mt-en-ja` — **ne**; `opus-mt-ko-en` yra, `opus-mt-en-ko` **nėra**.
Patarėjas, pasitikėjęs atmintimi, liepia pridėti neegzistuojantį modelį, žmogus bando ir
nesupranta, kodėl nepavyksta.

⇒ Šis skriptas nieko nespėja: jis **paklausia HuggingFace** ir Piper katalogo, ir pasako,
kas yra iš tikrųjų. Konsultantui: **paleisk jį ir remkis jo išvestimi, ne savo atmintimi.**

PALEIDIMAS (iš programos katalogo):

    .venv\\Scripts\\python.exe prideti_kalba.py it
    .venv\\Scripts\\python.exe prideti_kalba.py ja ko zh nl

Kalbos kodas — dviraidis ISO 639-1 (`it` italų, `ja` japonų, `ko` korėjiečių, `zh` kinų,
`nl` olandų, `fr` prancūzų, `es` ispanų, `pl` lenkų, `uk` ukrainiečių…).
"""
import os
import sys

CIA = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(CIA, 'vertejas'))

try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

TILTAS = 'en'


def piper_balsai(kalba):
    """Kokie Piper balsai yra tai kalbai. Grąžina [(raktas, vardas, kokybė)]."""
    import json
    from huggingface_hub import hf_hub_download
    d = json.load(open(hf_hub_download('rhasspy/piper-voices', 'voices.json'),
                       encoding='utf-8'))
    rasti = []
    for raktas, x in d.items():
        if x['language']['family'] == kalba:
            rasti.append((raktas, x['name'], x['quality']))
    return sorted(rasti)


def ar_yra_modelis(vardas):
    from huggingface_hub import HfApi
    try:
        HfApi().model_info(vardas)
        return True
    except Exception:
        return False


def vertimo_kelias(kalba):
    """Ar yra pora su tiltu (anglų) abiem kryptimis. Grąžina {kryptis: vardas arba None}."""
    rez = {}
    for is_k, i_k in ((kalba, TILTAS), (TILTAS, kalba)):
        vardas = 'Helsinki-NLP/opus-mt-%s-%s' % (is_k, i_k)
        rez[(is_k, i_k)] = vardas if ar_yra_modelis(vardas) else None
    return rez


def tikrink(kalba):
    print('=' * 74)
    print('KALBA: %s' % kalba)
    print('=' * 74)

    # 1. Ausys
    try:
        from faster_whisper.tokenizer import _LANGUAGE_CODES
        moka = kalba in _LANGUAGE_CODES
    except Exception:
        moka = None
    if moka is True:
        print('1. AUSYS       ✅ Whisper šią kalbą supranta — nieko daryti nereikia.')
    elif moka is False:
        print('1. AUSYS       ⛔ Whisper šios kalbos NEPALAIKO. Toliau eiti nėra prasmės.')
        return
    else:
        print('1. AUSYS       ⚠️ nepavyko patikrinti (sena faster-whisper versija).')

    # 2. Balsas
    balsai = piper_balsai(kalba)
    if balsai:
        print('2. BALSAS      ✅ Piper turi %d balsą (-ų):' % len(balsai))
        for raktas, vardas, kok in balsai[:6]:
            print('                  %-34s %s (%s)' % (raktas, vardas, kok))
        if len(balsai) > 6:
            print('                  … ir dar %d' % (len(balsai) - 6))
    else:
        print('2. BALSAS      ⛔ Piper šiai kalbai balso NETURI.')
        print('               ⇒ Ją bus galima SUPRASTI ir įrašyti į stenogramą, bet')
        print('                 kolonėlė ja NEKALBĖS. Tai riba, kurios apeiti negalim.')

    # 3. Vertimas
    kelias = vertimo_kelias(kalba)
    is_kalbos = kelias[(kalba, TILTAS)]
    i_kalba = kelias[(TILTAS, kalba)]
    print('3. VERTIMAS    per anglų kalbą (tiltas):')
    print('               %s → en : %s' % (kalba, is_kalbos or '⛔ MODELIO NĖRA'))
    print('               en → %s : %s' % (kalba, i_kalba or '⛔ MODELIO NĖRA'))

    print()
    if balsai and is_kalbos and i_kalba:
        verdiktas = '✅ GALIMA ĮDĖTI — veiks abiem kryptimis.'
    elif is_kalbos and not i_kalba:
        verdiktas = ('⚠️ TIK VIENA KRYPTIMI: iš šios kalbos išversti galima, Į JĄ — ne.\n'
                     '   Praktiškai tai reiškia, kad ja kalbantį suprasim ir užrašysim,\n'
                     '   bet atsakyti jam ta kalba negalėsim.')
    elif i_kalba and not is_kalbos:
        verdiktas = '⚠️ TIK VIENA KRYPTIMI: į šią kalbą versti galima, IŠ jos — ne.'
    else:
        verdiktas = '⛔ NEGALIMA: vertimo modelių nėra nė viena kryptimi.'
    print(verdiktas)

    if is_kalbos or i_kalba:
        print()
        print('KĄ TIKSLIAI PRIDĖTI (tik tai, kas pažymėta ✅ aukščiau):')
        print()
        print('  1) Faile  vertejas\\vertimas.py,  žodyne POROS:')
        if is_kalbos:
            print("         ('%s', 'en'): ('%s', None)," % (kalba, is_kalbos))
        if i_kalba:
            print("         ('en', '%s'): ('%s', None)," % (kalba, i_kalba))
        print()
        print('     ⚠️ Trečiasis narys yra taikinio žymė. Jis reikalingas TIK grupiniams')
        print('        modeliams (vardai su keliomis kalbomis, pvz. `…-zle-bat`), ir tada')
        print('        būna toks: \'>>lit<<\'. Šitiems modeliams jis privalo būti None.')
        print()
        print('  2) Faile  vertejas\\langas.py,  sąraše KALBOS — pridėti eilutę:')
        if balsai:
            print("         ('%s', '<kalbos pavadinimas TA PAČIA kalba>')," % kalba)
            print('     ⛔ Pavadinimą rašyti tos kalbos rašmenimis (Italiano, 日本語, Nederlands) —')
            print('        žmogus savo kalbą sąraše atpažįsta tik taip.')
        else:
            print('         (praleisti — be balso kalbos į sąrašą dėti neverta)')
        print()
        print('  3) Paleisti programą, pasirinkti tą kalbą ir spausti „Paruošti darbui".')
        print('     Pirmą kartą modeliai PARSISIŲS (balsas ~60 MB, vertėjas ~300 MB),')
        print('     tad paruošimas truks ilgiau nei įprastai. Tai normalu.')
        print()
        print('  4) ⚠️ PATIKRINTI SKAIČIUS prieš tikras derybas: pasakyti kainą su')
        print('     kableliu ir laiką. Daugiakalbės ausys skaičius rašo skaitmenimis,')
        print('     ir ne kiekvienas balsas juos perskaito teisingai.')
    print()


def main():
    kalbos = [a.lower() for a in sys.argv[1:] if not a.startswith('-')]
    if not kalbos:
        print(__doc__)
        return 2
    for k in kalbos:
        tikrink(k)
    return 0


if __name__ == '__main__':
    sys.exit(main())

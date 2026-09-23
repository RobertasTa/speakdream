# -*- coding: utf-8 -*-
"""VERTĖJAS: OPUS-MT grupiniai modeliai (09-12).

Variklis rinktas matavimais (`VARIKLIO_PASIRINKIMAS.md`): `opus-mt-tc-base-zle-bat` (152 MB)
ru→lt duoda 51,07 chrF++ ir lenkia net Gemma 31B (19 GB). Auklėti nereikia — pamatuota, kad
nei LoRA, nei distiliacija kokybės neprideda: modelis mokytas ant OPUS, o mūsų duomenys iš ten pat.

Modulinė sandara („du langeliai"): kiekvienai kalbų porai — savas modelis, parsiunčiamas tik
tada, kai jo prireikia. Pamatuota (`PLANAS.md` „KITOS KALBOS"):
  lt↔ru tiesiogiai (grupinis, 152 MB) · lt↔en 57,8/58,8 · lt↔de 51,7 (grupinis, 949 MB)
  **zh tiesioginio su lt ar ru NĖRA** — tik per anglų, ir tai kainuoja ~12 chrF++.
Todėl kinų kalbai grandinė sudedama iš dviejų žingsnių automatiškai.
"""
import os
import re

import torch
from transformers import MarianMTModel, MarianTokenizer

# Tiesioginės poros: (modelis, taikinio žymė). Žymė reikalinga grupiniams modeliams.
POROS = {
    ('ru', 'lt'): ('Helsinki-NLP/opus-mt-tc-base-zle-bat', '>>lit<<'),
    ('lt', 'ru'): ('Helsinki-NLP/opus-mt-tc-base-bat-zle', '>>rus<<'),
    ('en', 'lt'): ('Helsinki-NLP/opus-mt-tc-big-en-lt', None),
    ('lt', 'en'): ('Helsinki-NLP/opus-mt-tc-big-lt-en', None),
    ('de', 'lt'): ('Helsinki-NLP/opus-mt-tc-bible-big-deu_eng_fra_por_spa-bat', '>>lit<<'),
    ('lt', 'de'): ('Helsinki-NLP/opus-mt-tc-bible-big-bat-deu_eng_nld', '>>deu<<'),
    ('en', 'ru'): ('Helsinki-NLP/opus-mt-en-ru', None),
    ('ru', 'en'): ('Helsinki-NLP/opus-mt-ru-en', None),
    ('de', 'ru'): ('Helsinki-NLP/opus-mt-de-ru', None),
    ('ru', 'de'): ('Helsinki-NLP/opus-mt-ru-de', None),
    ('en', 'de'): ('Helsinki-NLP/opus-mt-en-de', None),
    ('de', 'en'): ('Helsinki-NLP/opus-mt-de-en', None),
    ('zh', 'en'): ('Helsinki-NLP/opus-mt-zh-en', None),
    ('en', 'zh'): ('Helsinki-NLP/opus-mt-en-zh', None),
}
TILTAS = 'en'      # kalba, per kurią einam, kai tiesioginės poros nėra

MAX_ILGIS = 384        # tokenų riba įvesčiai (tas pats skaičius, kaip matavime 39)
MODELIO_RIBA = 512     # Marian pozicijų riba — daugiau nei tiek negrąžins iš principo
# Išvesties riba nebėra kieta: buvęs `max_new_tokens=256` ilgesnį vertimą nukirpdavo taip pat
# TYLIAI, kaip įvestį kirpo `truncation`. Dabar ji skaičiuojama iš įvesties ilgio, o jei vis
# dėlto atsimuštų — tai pasakoma žurnalui (09-18).
NAUJU_SANTYKIS = 1.7   # kiek tokenų išvesčiai vienam įvesties tokenui
NAUJU_ATSARGA = 16

# ---------------------------------------------------------------------------
# SKAIDYMAS SAKINIAIS (09-17, ALGORITMAS.md 4 sk. 6 p.)
#
# Dvi priežastys, abi užrašytos matavimuose:
#   kokybė   — `_matavimas\39_sakiniu_grupes.py`: keturi sakiniai vienu gabalu 52,25 chrF++,
#              po vieną 53,12 (A geresnis 33 grupėse iš 50). Marian mokytas ant SAKINIŲ porų.
#   būtinybė — `truncation=True, max_length=384` nukerpa įvestį TYLIAI. Gabalui iš 30 s garso
#              tai netelpa, bet verčiant iš sukaupto transkripto galas dingtų be pranešimo.
#
# Sakinių ribas ką tik atstatė `skyryba.py`, todėl čia jų neatradinėjam — tik pjaustom.
# ⛔ Kai abejojam, NESKAIDOM: praleistas pjūvis kainuoja truputį kokybės, pjūvis vidury
# sakinio sugadina abi puses.
# ---------------------------------------------------------------------------

# Santrumpos, po kurių taškas nėra sakinio galas. Vieno rašmens santrumpos („t.", „г.", „z.")
# atmetamos atskira taisykle, todėl čia jų nerašom.
SANTRUMPOS = {
    # lietuvių
    'val', 'min', 'sek', 'mėn', 'pvz', 'psl', 'str', 'gyv', 'proc', 'kt', 'pan', 'žr',
    'dr', 'doc', 'prof', 'mob', 'tel', 'sav', 'vnt', 'egz', 'past', 'red', 'plg',
    'mln', 'mlrd', 'tūkst',
    # rusų
    'гг', 'ул', 'кв', 'руб', 'коп', 'тыс', 'млн', 'млрд', 'им', 'др', 'проф', 'доц', 'стр',
    # anglų / vokiečių
    'mr', 'mrs', 'ms', 'st', 'vs', 'etc', 'fig', 'no', 'inc', 'ltd', 'bzw', 'usw', 'ca', 'nr',
}

# Kandidatas į pjūvį: sakinio pabaigos ženklas (su galimomis uždarančiomis kabutėmis) + tarpas.
_GALAS = re.compile(r'[.!?…]+[»”"\'’)\]]*\s+')
# Žodis prieš tašką — reikia jam patikrinti, ar tai ne santrumpa.
_ZODIS_PRIES = re.compile(r'([^\s.!?…]*)[.!?…]+[»”"\'’)\]]*\s*$')


def _ar_tikras_galas(kaire: str, desine: str) -> bool:
    """Ar šioje vietoje sakinys tikrai baigiasi. Klystam TIK neskaidydami."""
    if not desine:
        return False
    # Po pjūvio turi prasidėti nauja mintis: didžioji raidė, skaitmuo arba atidaranti kabutė.
    pirmas = desine[0]
    if not (pirmas.isupper() or pirmas.isdigit() or pirmas in '«„"\'‘(—-'):
        return False
    m = _ZODIS_PRIES.search(kaire)
    if m:
        zodis = m.group(1)
        # „2026 m.", „т.е.", „A." — inicialas ar vieno rašmens santrumpa sakinio nebaigia.
        if len(zodis) <= 1:
            return False
        if zodis.lower() in SANTRUMPOS:
            return False
    return True


def i_sakinius(tekstas: str) -> list:
    """Tekstą — į sakinius. Grąžina bent vieną elementą (patį tekstą), jei ribų nerasta."""
    tekstas = (tekstas or '').strip()
    if not tekstas:
        return []
    sakiniai, pradzia = [], 0
    for m in _GALAS.finditer(tekstas):
        pjuvis = m.end()
        if _ar_tikras_galas(tekstas[pradzia:pjuvis], tekstas[pjuvis:]):
            sakiniai.append(tekstas[pradzia:pjuvis].strip())
            pradzia = pjuvis
    likutis = tekstas[pradzia:].strip()
    if likutis:
        sakiniai.append(likutis)
    return sakiniai or [tekstas]


class Vertejas:
    def __init__(self, iranga='cuda'):
        self.iranga = iranga if torch.cuda.is_available() else 'cpu'
        self._modeliai = {}

    # ---------- kelias ----------
    def kelias(self, is_kalbos, i_kalba):
        """Grąžina žingsnių sąrašą: [(iš, į)]. Per tiltą — du žingsniai."""
        if is_kalbos == i_kalba:
            return []
        if (is_kalbos, i_kalba) in POROS:
            return [(is_kalbos, i_kalba)]
        if (is_kalbos, TILTAS) in POROS and (TILTAS, i_kalba) in POROS:
            return [(is_kalbos, TILTAS), (TILTAS, i_kalba)]
        return None

    def ar_moka(self, is_kalbos, i_kalba):
        return self.kelias(is_kalbos, i_kalba) is not None

    def uzkrauk(self, poros, pranesk=None):
        for a, b in poros:
            k = self.kelias(a, b) or []
            for zingsnis in k:
                if pranesk:
                    pranesk('Kraunu vertėją (%s→%s)…' % zingsnis)
                self._modelis(zingsnis)

    def _modelis(self, zingsnis):
        if zingsnis not in self._modeliai:
            vardas, zyme = POROS[zingsnis]
            tok = MarianTokenizer.from_pretrained(vardas)
            mod = MarianMTModel.from_pretrained(vardas).to(self.iranga).eval()
            self._modeliai[zingsnis] = (tok, mod, zyme)
        return self._modeliai[zingsnis]

    # ---------- vertimas ----------
    def _telpa(self, tok, zyme, dalis):
        """Ar dalis telpa į modelio įvestį. Netelpanti būtų nukirpta TYLIAI — to ir vengiam."""
        ivestis = (zyme + ' ' + dalis) if zyme else dalis
        return len(tok(ivestis)['input_ids']) <= MAX_ILGIS

    def _sutalpink(self, tok, zyme, dalis, pranesk=None):
        """Netelpantį sakinį perlaužia per pusę ties žodžiu ir bando dar kartą.

        Iš 30 s garso toks sakinys neateina (ilgiausia pamatuota įvestis — 221 tokenas),
        bet iš sukaupto transkripto gali. Geriau perlaužta vieta, kurią matom žurnale,
        negu tyliai dingęs galas.
        """
        if self._telpa(tok, zyme, dalis):
            return [dalis]
        zodziai = dalis.split()
        if len(zodziai) < 2:
            return [dalis]       # vienas milžiniškas žodis — nėra kur laužti
        if pranesk:
            pranesk('per ilgas sakinys (%d žodžių) — laužiam per pusę' % len(zodziai))
        vidurys = len(zodziai) // 2
        return (self._sutalpink(tok, zyme, ' '.join(zodziai[:vidurys])) +
                self._sutalpink(tok, zyme, ' '.join(zodziai[vidurys:])))

    def _vienas(self, zingsnis, dalis, pranesk=None):
        """Vienas žingsnis, viena dalis → (vertimas, pasitikėjimas)."""
        tok, mod, zyme = self._modelis(zingsnis)
        isvestys, blogiausias = [], None
        for gabalas in self._sutalpink(tok, zyme, dalis, pranesk):
            ivestis = (zyme + ' ' + gabalas) if zyme else gabalas
            ids = tok([ivestis], return_tensors='pt', truncation=True,
                      max_length=MAX_ILGIS).to(self.iranga)
            nauju = min(MODELIO_RIBA,
                        int(ids['input_ids'].shape[1] * NAUJU_SANTYKIS) + NAUJU_ATSARGA)
            with torch.no_grad():
                isvestis = mod.generate(**ids, max_new_tokens=nauju, num_beams=4,
                                        return_dict_in_generate=True, output_scores=True)
            # Atsimušus į ribą vertimo galo nebūtų, ir seniau to niekas nesužinotų.
            if pranesk and isvestis.sequences.shape[1] >= nauju:
                pranesk('vertimas atsimušė į išvesties ribą (%d tokenų) — galas gali būti nukirptas'
                        % nauju)
            isvestys.append(tok.decode(isvestis.sequences[0], skip_special_tokens=True))
            p = float(isvestis.sequences_scores[0])
            blogiausias = p if blogiausias is None else min(blogiausias, p)
        return ' '.join(t for t in isvestys if t), (blogiausias or 0.0)

    def versk(self, tekstas: str, is_kalbos: str, i_kalba: str, pranesk=None):
        """→ (vertimas, pasitikejimas). Pasitikėjimas eina TIK į žurnalą (v6: vartotojui nerodom).

        Tekstas SKAIDOMAS SAKINIAIS ir kiekvienas verčiamas atskirai — žr. `i_sakinius`.
        Pasitikėjimas grąžinamas blogiausias iš visų sakinių ir visų žingsnių: vienas
        suverstas sakinys neturi pasislėpti už gerų kaimynų vidurkio.
        """
        tekstas = (tekstas or '').strip()
        if not tekstas:
            return '', 0.0
        zingsniai = self.kelias(is_kalbos, i_kalba)
        if zingsniai is None:
            return '', -99.0
        if not zingsniai:
            return tekstas, 0.0
        vertimai, blogiausias = [], None
        for sakinys in i_sakinius(tekstas):
            for zingsnis in zingsniai:     # per tiltą (kinų) — du žingsniai tam pačiam sakiniui
                sakinys, p = self._vienas(zingsnis, sakinys, pranesk)
                blogiausias = p if blogiausias is None else min(blogiausias, p)
            if sakinys.strip():
                vertimai.append(sakinys.strip())
        return ' '.join(vertimai), (blogiausias or 0.0)

    def atlaisvink(self):
        self._modeliai.clear()
        if self.iranga == 'cuda':
            torch.cuda.empty_cache()

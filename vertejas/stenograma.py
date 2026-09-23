# -*- coding: utf-8 -*-
"""STENOGRAMA — pokalbio užrašas į txt failus (Roberto sumanymas 09-17, kodas 09-18).

Kam ji: iki šiol dovana buvo **nepatikrinama** — žmogus girdi vertimą ir neturi jokio būdo
sužinoti, ar jam nemeluojama. Stenograma tą uždaro ne mūsų pažadu, o tuo, kad išeina iš mūsų
rankų: parėjęs namo bet kuris dalyvis gali ją nunešti profesionaliam vertėjui ir pasitikrinti.

Visi sprendimai — `ALGORITMAS.md` 10 skyriuje. Trys, kuriuos verta matyti čia pat:

  1. **Faile yra viskas, kas TA KALBA nuskambėjo kambaryje — ir nieko daugiau.** Todėl lietuvio
     žodžių, išverstų atgal į lietuvių, LT faile nebūna: kambaryje jie taip neskambėjo.
  2. **Viena laiko žyma vienam kalbėjimo įvykiui, ta pati visuose failuose** — vienkalbiuose
     failuose porą atkuria tik ji. Be poros profesionalas vertimo įvertinti negali.
  3. **Rašom po kiekvienos replikos**, ne pabaigoje: derybos vyksta vieną kartą, ir jei programa
     nulūš, pokalbis neturi dingti kartu su ja.

Formatas — pirmiausia duomenys, tik paskui skaitinys (Roberto reikalavimas: *„jei nori tekstą su
skriptu koreguot, kad būtų paprasta, lengva ir be klaidų"*). Vardų mes nežinom, bet kas norės —
vienu `replace` pavers „LT žmogus" Petru:

    [00:01:00] LT žmogus: Mes siūlome 50 000 Eur kainą.
    [00:01:15] LT vertėja: Mes manome, kad tai per daug, siūlome 40 000 Eur.

⛔ Ko čia NĖRA sąmoningai: santraukos ir išvadų. Tam reikėtų LLM, o LLM derybų stenogramoje
prigalvotų to, ko niekas nesakė. **Sekretorė užrašo, bet neapibendrina.**
"""
import os
import time

CIA = os.path.dirname(os.path.abspath(__file__))
# ⭐ Roberto sprendimas 09-18: stenogramos gula **šalia programos**, o ne paslėptos AppData
# gilumoje — *„kad net tuščią galima būtų atidaryti"*. Katalogas sukuriamas paleidžiant
# programą (`paruosk_kataloga`), ne tada, kai jo pirmą kartą prireikia.
SALIA = os.path.join(os.path.dirname(CIA), 'Stenogramos')
# Atsarginis kelias: įdiegus į `Program Files` rašyti šalia programos neleis teisės. Tada
# grįžtam ten, kur guli žurnalas ir nustatymai.
APPDATA = os.path.join(os.environ.get('LOCALAPPDATA', os.path.expanduser('~')),
                       'SpeakDream', 'stenogramos')


def kur_rasom() -> str:
    """Kur dėti stenogramas: šalia programos, o jei ten rašyti negalima — AppData.

    ⛔ Neužtenka patikrinti, ar katalogas yra: `Program Files` katalogą sukurti gali pavykti,
    o įrašyti į jį — ne. Todėl tikrinam tikru bandymu įrašyti.
    """
    try:
        os.makedirs(SALIA, exist_ok=True)
        bandymas = os.path.join(SALIA, '.rasymo_bandymas')
        with open(bandymas, 'w', encoding='utf-8') as f:
            f.write('')
        os.remove(bandymas)
        return SALIA
    except Exception:
        return APPDATA


def paruosk_kataloga() -> str:
    """Sukuria katalogą programos paleidimo metu ir grąžina jo kelią.

    Kad „Atverti stenogramų katalogą" veiktų nuo pirmos sekundės — dar nieko neužrašius.
    Po įdiegimo tą patį turės padaryti instaliatorius.
    """
    kelias = kur_rasom()
    try:
        os.makedirs(kelias, exist_ok=True)
    except Exception:
        pass
    return kelias

# Failo vardo dalis pagal kalbą. ASCII sąmoningai: failų vardus dar teks rašyti ranka,
# siųsti paštu ir minėti skriptuose.
FAILO_VARDAS = {'lt': 'lietuviskai', 'ru': 'rusiskai', 'en': 'angliskai', 'de': 'vokiskai'}

# Žymės — TO FAILO kalba, nes failą skaitys tos kalbos žmogus.
ZMOGUS = {'lt': 'žmogus', 'ru': 'человек', 'en': 'person', 'de': 'Person'}
VERTEJAS = {
    'lt': {'m': 'vertėja', 'v': 'vertėjas', None: 'vertėjas'},
    'ru': {'m': 'переводчица', 'v': 'переводчик', None: 'переводчик'},
    'en': {'m': 'interpreter', 'v': 'interpreter', None: 'interpreter'},
    'de': {'m': 'Dolmetscherin', 'v': 'Dolmetscher', None: 'Dolmetscher'},
}

# Antraštė — tos pačios kalbos, kaip ir failas. Kiekviena eilutė prasideda „# ", kad skriptas,
# kuris keis vardus, ją praleistų viena sąlyga.
ANTRASTE = {
    'lt': ['Automatinė pokalbio stenograma. Programa: {programa}.',
           'Pradėta {data}. Kalbos: {kalbos}. Balsai: {balsai}.',
           'Kalbėtojų žodžiai užrašyti mašinos ausimis ir gali skirtis nuo to, kas nuskambėjo.',
           'Kas kalba, programa nežino — žino tik kalbą.',
           '{garsas}'],
    'ru': ['Автоматическая стенограмма разговора. Программа: {programa}.',
           'Начато {data}. Языки: {kalbos}. Голоса: {balsai}.',
           'Слова говорящих записаны машинным слухом и могут отличаться от сказанного.',
           'Кто говорит, программа не знает — знает только язык.',
           '{garsas}'],
    'en': ['Automatic conversation transcript. Program: {programa}.',
           'Started {data}. Languages: {kalbos}. Voices: {balsai}.',
           'Speakers’ words were written down by machine hearing and may differ from what was said.',
           'The program does not know who is speaking — only the language.',
           '{garsas}'],
    'de': ['Automatisches Gesprächsprotokoll. Programm: {programa}.',
           'Begonnen {data}. Sprachen: {kalbos}. Stimmen: {balsai}.',
           'Die Worte der Sprecher wurden maschinell gehört und können vom Gesagten abweichen.',
           'Wer spricht, weiß das Programm nicht — nur die Sprache.',
           '{garsas}'],
}

# Originalų failas mišrus, todėl jo antraštė — lietuviškai (programos kalba), o eilutėse
# vien kalbos kodai: bet kuri kita kalba nuskriaustų vieną pusę.
ANTRASTE_ORIGINALAI = [
    'Automatinė pokalbio stenograma — TIK ORIGINALAI. Programa: {programa}.',
    'Pradėta {data}. Kalbos: {kalbos}.',
    'Čia užrašyta tik tai, ką sakė ŽMONĖS, kiekvienas savo kalba. Vertėjo žodžių čia nėra.',
    'Kalbėtojų žodžiai užrašyti mašinos ausimis ir gali skirtis nuo to, kas nuskambėjo.',
    '{garsas}',
]

PROGRAMA = 'SpeakDream'

# ⭐ Svarbiausia eilutė tam, kas failą gaus į rankas: **laiko žymos sutampa su garso įrašu**
# (Roberto reikalavimas 09-18: *„kad jei pagavai kažkokį įtarimą stenogramoje, galėtum būtent
# tą vietą atsisukti"*). Todėl garsas rašomas IŠTISAI, o ne iškirptais gabalais.
GARSO_EILUTE = {
    'lt': {True: 'Garso įrašas: {vardas} — laiko žymos šiame faile atitinka vietą įraše.',
           False: 'Garso įrašo nėra.'},
    'ru': {True: 'Аудиозапись: {vardas} — отметки времени в этом файле соответствуют месту в записи.',
           False: 'Аудиозаписи нет.'},
    'en': {True: 'Audio recording: {vardas} — timestamps in this file match positions in the recording.',
           False: 'There is no audio recording.'},
    'de': {True: 'Tonaufnahme: {vardas} — die Zeitmarken entsprechen den Stellen in der Aufnahme.',
           False: 'Eine Tonaufnahme gibt es nicht.'},
}


def naujas_katalogas(saknis=None, pradzia=None) -> str:
    """Sukuria NAUJĄ katalogą šiam pokalbiui ir grąžina kelią.

    Atskirta nuo `Stenograma`, kad variklis galėtų katalogą gauti PIRMAS, jame atidaryti garso
    įrašą ir tik tada rašyti stenogramos antraštę — kitaip antraštė turėtų žadėti garso failą,
    kurio atsiradimo dar niekas nepatikrino.
    """
    saknis = saknis or kur_rasom()
    vardas = time.strftime('%Y-%m-%d_%H-%M-%S', time.localtime(pradzia or time.time()))
    # ⛔ Katalogas TURI būti naujas. Paspaudus „Baigti" ir tuoj pat „Pradėti", vardas sutaptų
    # iki sekundės, ir antras pokalbis perrašytų pirmą — o stenograma tam ir daroma, kad
    # pokalbis nedingtų. Rasta patikra 09-18.
    kelias = os.path.join(saknis, vardas)
    n = 2
    while os.path.exists(kelias):
        kelias = os.path.join(saknis, '%s_%d' % (vardas, n))
        n += 1
    os.makedirs(kelias, exist_ok=True)
    return kelias


def _laikas(sekundes: float) -> str:
    """Sekundės nuo pokalbio pradžios → [HH:MM:SS]."""
    s = max(0, int(sekundes))
    return '%02d:%02d:%02d' % (s // 3600, (s // 60) % 60, s % 60)


class Stenograma:
    """Vieno pokalbio užrašas. Vertėjo režimu — trys failai, sekretorės — vienas.

    Naudojimas:
        st = Stenograma(['lt', 'ru'], balsai={'lt': 'Ingutė', 'ru': 'Руслан'},
                        lytys={'lt': 'm', 'ru': 'v'})
        st.zmogus('lt', 'Mes siūlome 50 000 Eur kainą.', kada)
        st.vertejas('ru', 'Мы предлагаем цену 50 000 евро.', kada)
        st.uzverk()

    `kada` — sekundės nuo pokalbio pradžios, REPLIKOS PRADŽIA (ne rašymo momentas).
    Nieko nepadavus imamas dabartinis laikas — tai atsarginis kelias, ne numatytas.
    """

    def __init__(self, kalbos, balsai=None, lytys=None, sekretore=False,
                 saknis=None, pranesk=None, garso_vardas=None, katalogas=None,
                 pradzia=None):
        self.kalbos = [k for k in kalbos if k]
        self.sekretore = bool(sekretore)
        self.balsai = balsai or {}
        self.lytys = lytys or {}
        # Garso failo vardas, jei pokalbis įrašinėjamas — eina į antraštę.
        self.garso_vardas = garso_vardas
        self._pranesk = pranesk
        # `pradzia` paduodama, kai pokalbis įrašinėjamas: imam GARSO ĮRAŠO nulį, kad stenogramos
        # žyma rodytų tą pačią vietą garse. Be to kiekvienas skaičiuotų nuo savo pradžios.
        self._pradzia = pradzia or time.time()
        self._failai = {}          # kalba → failas; 'originalai' → mišrus failas
        self.katalogas = katalogas
        self.sugedo = False
        self._atidaryk(saknis)

    # ---------- atidarymas ----------
    def _atidaryk(self, saknis):
        try:
            if self.katalogas is None:
                self.katalogas = naujas_katalogas(saknis, self._pradzia)
            priesdelis = 'susirinkimas' if self.sekretore else 'pokalbis'
            for k in self.kalbos:
                kelias = os.path.join(self.katalogas,
                                      '%s_%s.txt' % (priesdelis, FAILO_VARDAS.get(k, k)))
                self._failai[k] = open(kelias, 'w', encoding='utf-8')
                self._antraste(self._failai[k], ANTRASTE.get(k, ANTRASTE['en']), k)
            # Originalų failas prasmingas tik tada, kai yra ką atskirti nuo vertimų.
            if not self.sekretore:
                kelias = os.path.join(self.katalogas, 'pokalbis_originalai.txt')
                self._failai['originalai'] = open(kelias, 'w', encoding='utf-8')
                self._antraste(self._failai['originalai'], ANTRASTE_ORIGINALAI)
        except Exception as e:
            self.sugedo = True
            self._sakyk('stenogramos rašyti nepavyko (%s)' % e)

    def _antraste(self, f, eilutes, kalba=None):
        data = time.strftime('%Y-%m-%d %H:%M', time.localtime(self._pradzia))
        kalbos = ', '.join(k.upper() for k in self.kalbos)
        balsai = ', '.join('%s: %s' % (k.upper(), self.balsai.get(k) or '—')
                           for k in self.kalbos) or '—'
        g = GARSO_EILUTE.get(kalba or 'lt', GARSO_EILUTE['lt'])
        garsas = g[bool(self.garso_vardas)].format(vardas=self.garso_vardas or '')
        for e in eilutes:
            f.write('# ' + e.format(programa=PROGRAMA, data=data, kalbos=kalbos,
                                    balsai=balsai, garsas=garsas) + '\n')
        f.write('#\n')
        f.flush()

    def _sakyk(self, tekstas):
        if self._pranesk:
            try:
                self._pranesk('stenograma: ' + tekstas)
            except Exception:
                pass

    # ---------- rašymas ----------
    def _eilute(self, f, kada, zyme, tekstas):
        if f is None or not tekstas:
            return
        # Viena replika — viena eilutė, niekada nelaužoma. Ausys naujų eilučių neduoda,
        # bet paranoja pigi: skriptas, kuris tikisi vienos eilutės, jų neturi rasti dviejų.
        tekstas = ' '.join(str(tekstas).split())
        try:
            f.write('[%s] %s: %s\n' % (_laikas(kada), zyme, tekstas))
            f.flush()          # po KIEKVIENOS replikos: nulūžus programai užrašas lieka
        except Exception as e:
            if not self.sugedo:
                self.sugedo = True
                self._sakyk('rašymas nutrūko (%s)' % e)

    def _kada(self, kada):
        return time.time() - self._pradzia if kada is None else kada

    def nuo_pradzios(self, laikas: float) -> float:
        """`time.time()` momentą paverčia sekundėmis nuo pokalbio pradžios.

        Variklis juo paverčia REPLIKOS PRADŽIĄ (gabalo gavimo laikas minus gabalo trukmė),
        o ne rašymo momentą — tai ir yra 10.2 punktas.
        """
        return laikas - self._pradzia

    def zmogus(self, kalba: str, tekstas: str, kada: float = None):
        """Žmogaus replika: į savo kalbos failą IR į originalų failą, ta pačia žyma."""
        kada = self._kada(kada)
        zyme = '%s %s' % (kalba.upper(), ZMOGUS.get(kalba, ZMOGUS['en']))
        self._eilute(self._failai.get(kalba), kada, zyme, tekstas)
        # Originalų faile — vien kalbos kodas: failas mišrus, ir bet kuri kalba žymėse
        # nuskriaustų vieną pusę.
        self._eilute(self._failai.get('originalai'), kada, kalba.upper(), tekstas)

    def vertejas(self, kalba: str, tekstas: str, kada: float = None):
        """Vertėjos replika: TIK į tos kalbos failą.

        Rašom tą vertimą, kuris SKAMBĖJO balsu (Roberto sprendimas 09-18): stenograma yra
        pokalbio liudytoja, ne pagerinta redakcija. Į originalų failą ji neina niekada —
        tas failas tam ir yra, kad jame nebūtų nė vieno mūsų mašinos sakinio.
        """
        kada = self._kada(kada)
        lytis = self.lytys.get(kalba)
        vardas = VERTEJAS.get(kalba, VERTEJAS['en'])
        zyme = '%s %s' % (kalba.upper(), vardas.get(lytis, vardas[None]))
        self._eilute(self._failai.get(kalba), kada, zyme, tekstas)

    # ---------- pabaiga ----------
    def uzverk(self):
        for f in self._failai.values():
            try:
                f.close()
            except Exception:
                pass
        self._failai.clear()

    @property
    def ar_veikia(self):
        return bool(self._failai) and not self.sugedo

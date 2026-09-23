# -*- coding: utf-8 -*-
"""NUMATYTOSIOS FRAZĖS — ką kolonėlė sako pati, ne versdama (09-12).

Roberto tekstas (16:55) ir patikslinimai (17:10):
  * balsą vartotojas renkasi pats iš Piper sąrašo → vardas ir LYTIS ateina iš balso:
    moteriškas balsas sako „aš vertėja", vyriškas — „aš vertėjas" (rusiškai keičiasi ir
    veiksmažodis: „успела/успел"); jei lytis nežinoma — beginė formuluotė, be „vertėja(s)";
  * pauzės ilgis ateina iš PROGRAMOS nustatymo → frazėje sakomas tas pats skaičius,
    kuris tuo metu nustatytas slankikliu;
  * sakinių skaičius kol kas 4, bet tai ne galutinis sprendimas (Robertas: „pagalvosim, kai
    vertimą tikrinsim… gal ne konkrečiai 4 sakiniai, o kaip ten pas diplomatus būna").
    Todėl jis irgi parametras, o `kiekis=None` duoda formuluotę be skaičiaus.

⛔ Piper kataloge (`voices.json`, 176 balsai) LYTIES LAUKO NĖRA — tik vardas, kalba, kokybė.
Todėl žinomų balsų lytis laikoma čia, o nežinomo balso lytį pasirenka vartotojas sąsajoje
(numatyta — beginė formuluotė, kuri tinka bet kuriam balsui).

Pagal v6 kolonėlė kalba TIK du kartus: sveikindamasi ir atsisveikindama. Eigoje tyli.
"""

# Žinomų balsų lytis: 'm' — moteris, 'v' — vyras. Nežinomas balsas → None → beginė formuluotė.
BALSU_LYTIS = {
    'ingute': 'm', 'reginute1': 'm', 'reginute': 'm',
    'irina': 'm', 'ruslan': 'v', 'denis': 'v', 'dmitri': 'v',
    'thorsten': 'v', 'eva_k': 'm', 'kerstin': 'm', 'karlsson': 'v',
    'amy': 'm', 'lessac': 'm', 'ryan': 'v', 'joe': 'v', 'kusal': 'v', 'kathleen': 'm',
}

VARDAI = {'lt': 'Reginutė', 'ru': 'Руслан', 'en': 'Reginute', 'de': 'Reginute'}

# ⛔ Vardas turi ateiti iš PASIRINKTO BALSO, o ne iš kalbos. Kitaip Ingutė prisistatydavo
# „aš esu Reginutė" — ta pati 09-16 nesuderinamumo pusė, kurią Robertas pagavo balsų sąraše
# 09-18. Nežinomam balsui grįžtam prie `VARDAI[kalba]`, kaip buvo.
VARDAI_PAGAL_BALSA = {
    'ingute': 'Ingutė', 'reginute1': 'Reginutė', 'reginute': 'Reginutė',
    'ruslan': 'Руслан', 'irina': 'Ирина', 'denis': 'Денис', 'dmitri': 'Дмитрий',
    'thorsten': 'Thorsten', 'eva_k': 'Eva', 'kerstin': 'Kerstin', 'karlsson': 'Karlsson',
    'amy': 'Amy', 'lessac': 'Lessac', 'ryan': 'Ryan', 'joe': 'Joe', 'kathleen': 'Kathleen',
}

# „aš esu X, jūsų vertėja / vertėjas" — arba, jei lytis nežinoma, beginė forma.
PRISISTATYMAS = {
    'lt': {'m': 'Labas, aš esu {vardas}, jūsų vertėja.',
           'v': 'Labas, aš esu {vardas}, jūsų vertėjas.',
           None: 'Labas, aš esu {vardas}. Versiu jūsų pokalbį.'},
    'ru': {'m': 'Здравствуйте, я {vardas}, ваша переводчица.',
           'v': 'Здравствуйте, я {vardas}, ваш переводчик.',
           None: 'Здравствуйте, я {vardas}. Буду переводить ваш разговор.'},
    'en': {'m': 'Hello, I am {vardas}, your interpreter.',
           'v': 'Hello, I am {vardas}, your interpreter.',
           None: 'Hello, I am {vardas}. I will interpret your conversation.'},
    'de': {'m': 'Hallo, ich bin {vardas}, Ihre Dolmetscherin.',
           'v': 'Hallo, ich bin {vardas}, Ihr Dolmetscher.',
           None: 'Hallo, ich bin {vardas}. Ich übersetze Ihr Gespräch.'},
}

# „…kad spėčiau išversti" — rusiškai ir vokiškai veiksmažodis turi giminę.
# ⛔ NEBENAUDOJAMA nuo 2026-09-18: pauzė reikalinga NE tam, kad spėtume (spėjam — 1,7 s), o tam,
# kad turėtume kada kalbėti; kitaip kolonėlė kalbėtų žmogui per burną. Naujoji formuluotė tą ir
# sako: „padarykite pauzę — tada išversiu" (`ALGORITMAS.md` 10.8).
SPECIAU = {
    'lt': {'m': 'kad spėčiau išversti', 'v': 'kad spėčiau išversti', None: 'kad spėčiau išversti'},
    'ru': {'m': 'чтобы я успела перевести', 'v': 'чтобы я успел перевести', None: 'чтобы я успевала переводить'},
    'en': {'m': 'so that I can translate', 'v': 'so that I can translate', None: 'so that I can translate'},
    'de': {'m': 'damit ich übersetzen kann', 'v': 'damit ich übersetzen kann', None: 'damit ich übersetzen kann'},
}

# ⛔ NEBENAUDOJAMA nuo 2026-09-18 (`ALGORITMAS.md` 6 ir 10.8 sk.): sveikinime nebesakom, kiek
# sakinių kalbėti. Skaičiaus pagrįsti nėra kuo — AIIC apie atkarpos ilgį nesako nieko, o
# profesinėse gairėse riba visur yra „baigta mintis". Žodynas paliktas, kad vertimai nedingtų.
KIEK_SAKINIU = {
    'lt': {4: 'ne daugiau kaip keturis sakinius iš karto', 3: 'ne daugiau kaip tris sakinius iš karto',
           2: 'ne daugiau kaip du sakinius iš karto', None: 'trumpai, po vieną mintį'},
    'ru': {4: 'не больше четырёх предложений подряд', 3: 'не больше трёх предложений подряд',
           2: 'не больше двух предложений подряд', None: 'коротко, по одной мысли'},
    'en': {4: 'no more than four sentences at a time', 3: 'no more than three sentences at a time',
           2: 'no more than two sentences at a time', None: 'briefly, one thought at a time'},
    'de': {4: 'höchstens vier Sätze am Stück', 3: 'höchstens drei Sätze am Stück',
           2: 'höchstens zwei Sätze am Stück', None: 'kurz, einen Gedanken auf einmal'},
}

# Pauzė sakoma taip, kaip ji nustatyta slankikliu. Netipinei reikšmei — „trumpą pauzę".
PAUZE = {
    'lt': {0.5: 'pusės sekundės pauzę', 0.8: 'trumpą pauzę', 1.0: 'vienos sekundės pauzę',
           1.2: 'trumpą pauzę', 1.5: 'pusantros sekundės pauzę', 2.0: 'dviejų sekundžių pauzę',
           2.5: 'dviejų su puse sekundės pauzę', None: 'trumpą pauzę'},
    'ru': {0.5: 'паузу в полсекунды', 0.8: 'короткую паузу', 1.0: 'паузу в одну секунду',
           1.2: 'короткую паузу', 1.5: 'паузу в полторы секунды', 2.0: 'паузу в две секунды',
           2.5: 'паузу в две с половиной секунды', None: 'короткую паузу'},
    'en': {0.5: 'a half-second pause', 0.8: 'a short pause', 1.0: 'a one-second pause',
           1.2: 'a short pause', 1.5: 'a pause of a second and a half', 2.0: 'a two-second pause',
           2.5: 'a pause of two and a half seconds', None: 'a short pause'},
    'de': {0.5: 'eine halbe Sekunde Pause', 0.8: 'eine kurze Pause', 1.0: 'eine Sekunde Pause',
           1.2: 'eine kurze Pause', 1.5: 'anderthalb Sekunden Pause', 2.0: 'zwei Sekunden Pause',
           2.5: 'zweieinhalb Sekunden Pause', None: 'eine kurze Pause'},
}

# Naujasis nurodymas (09-18). Riba — BAIGTA MINTIS, ne sakinių skaičius.
NURODYMAS = {
    'lt': 'Pasakykite mintį iki galo ir padarykite {pauze} — tada išversiu.',
    'ru': 'Договорите мысль до конца и сделайте {pauze} — тогда я переведу.',
    'en': 'Finish your thought and then make {pauze} — I will translate it then.',
    'de': 'Sprechen Sie Ihren Gedanken zu Ende und machen Sie dann {pauze} — dann übersetze ich.',
}

# Roberto pastebėjimas: žmogus, pirmą kartą dirbantis su vertėju, nežino, kad po vertimo žodis
# pašnekovui NEPERDUODAMAS.
TOLIAU = {
    'lt': 'Kai baigsiu, galite kalbėti toliau; perleisti žodį pašnekovui nebūtina.',
    'ru': 'Когда я закончу, можете говорить дальше; передавать слово собеседнику не обязательно.',
    'en': 'When I have finished, you may keep speaking; you do not have to hand over to the other person.',
    'de': 'Wenn ich fertig bin, können Sie weitersprechen; Sie müssen das Wort nicht abgeben.',
}

# Prie kolonėlės žmogus instinktyviai kreipiasi į kolonėlę.
VIENAS_SU_KITU = {
    'lt': 'Kalbėkite vienas su kitu, ne su manimi — aš tik verčiu.',
    'ru': 'Говорите друг с другом, а не со мной — я только перевожу.',
    'en': 'Please speak to each other, not to me — I only translate.',
    'de': 'Sprechen Sie miteinander, nicht mit mir — ich übersetze nur.',
}

# ⛔ ĮRAŠYMAS. Šitos frazės išjungti negalima (`ALGORITMAS.md` 10.6): gyvą sekretorę žmonės mato,
# skaitmeninės — ne, o nežinodamas svečias negali ir nesutikti. Sakoma ir pradžioje, ir pabaigoje.
UZRASYSIU = {
    'lt': 'Pokalbį užrašysiu.', 'ru': 'Разговор я запишу.',
    'en': 'I will write the conversation down.', 'de': 'Ich schreibe das Gespräch mit.',
}
UZRASYSIU_SEKRETORE = {
    'lt': 'Susirinkimą užrašysiu.', 'ru': 'Собрание я запишу.',
    'en': 'I will write the meeting down.', 'de': 'Ich schreibe die Sitzung mit.',
}

# ⛔ GARSO ĮRAŠAS — atskiras pranešimas, ne to paties sakinio dalis (09-18). „Užrašysiu" ir
# „įrašinėsiu balsus" žmogui reiškia skirtingus dalykus: tekstą jis įsivaizduoja, o balso
# įrašo — ne. Todėl sakom abu, o ne vieną vietoj kito.
GARSAS_IRASOMAS = {
    'lt': 'Taip pat įrašinėsiu garsą — jūsų balsai liks įraše.',
    'ru': 'Я также буду записывать звук — ваши голоса останутся в записи.',
    'en': 'I will also record the audio — your voices will be in the recording.',
    'de': 'Ich nehme außerdem den Ton auf — Ihre Stimmen bleiben in der Aufnahme.',
}
GARSAS_BAIGTAS = {
    'lt': {'m': 'Garso įrašą sustabdžiau.', 'v': 'Garso įrašą sustabdžiau.',
           None: 'Garso įrašas sustabdytas.'},
    'ru': {'m': 'Запись звука я остановила.', 'v': 'Запись звука я остановил.',
           None: 'Запись звука остановлена.'},
    'en': {'m': 'I have stopped the audio recording.', 'v': 'I have stopped the audio recording.',
           None: 'The audio recording has stopped.'},
    'de': {'m': 'Ich habe die Tonaufnahme beendet.', 'v': 'Ich habe die Tonaufnahme beendet.',
           None: 'Die Tonaufnahme ist beendet.'},
}
IRASAS_BAIGTAS = {
    'lt': {'m': 'Užrašinėti baigiau.', 'v': 'Užrašinėti baigiau.',
           None: 'Užrašinėti baigiau.'},
    'ru': {'m': 'Запись я закончила.', 'v': 'Запись я закончил.',
           None: 'Запись окончена.'},
    'en': {'m': 'I have finished writing.', 'v': 'I have finished writing.',
           None: 'I have finished writing.'},
    'de': {'m': 'Ich habe die Mitschrift beendet.', 'v': 'Ich habe die Mitschrift beendet.',
           None: 'Die Mitschrift ist beendet.'},
}

# Sekretorės režimu ji ne verčia, o užrašo — todėl ir prisistato kitaip.
# ⛔ Roberto patikslinimas 09-18: sekretorė **turi trumpai prisistatyti ją įjungus, kad visi
# žinotų, jog bus stenografuojama**. Vien „Susirinkimą užrašysiu" (mano pirmas siūlymas) per
# maža: iš kur tas balsas ir kas kalba, žmonės nesupranta.
PRISISTATYMAS_SEKRETORE = {
    'lt': {'m': 'Labas, aš esu {vardas}, jūsų sekretorė.',
           'v': 'Labas, aš esu {vardas}, jūsų sekretorius.',
           None: 'Labas, aš esu {vardas}.'},
    'ru': {'m': 'Здравствуйте, я {vardas}, ваш секретарь.',
           'v': 'Здравствуйте, я {vardas}, ваш секретарь.',
           None: 'Здравствуйте, я {vardas}.'},
    'en': {'m': 'Hello, I am {vardas}, your secretary.',
           'v': 'Hello, I am {vardas}, your secretary.',
           None: 'Hello, I am {vardas}.'},
    'de': {'m': 'Hallo, ich bin {vardas}, Ihre Protokollantin.',
           'v': 'Hallo, ich bin {vardas}, Ihr Protokollant.',
           None: 'Hallo, ich bin {vardas}.'},
}

# Trumpajam prisistatymui — „esu pasiruošusi / pasiruošęs".
PASIRUOSE = {
    'lt': {'m': 'Esu pasiruošusi.', 'v': 'Esu pasiruošęs.', None: 'Galime pradėti.'},
    'ru': {'m': 'Я готова.', 'v': 'Я готов.', None: 'Можно начинать.'},
    'en': {'m': 'I am ready.', 'v': 'I am ready.', None: 'I am ready.'},
    'de': {'m': 'Ich bin bereit.', 'v': 'Ich bin bereit.', None: 'Wir können beginnen.'},
}

ISPEJIMAS = {
    'lt': ('Kai kuriuos žodžius galiu išversti netiksliai. '
           'Tada paprašykite pašnekovo tą pačią mintį pasakyti kitais žodžiais, '
           'ir vertimas turėtų pasitaisyti.'),
    'ru': ('Некоторые слова я могу перевести неточно. '
           'Тогда попросите собеседника сказать ту же мысль другими словами, '
           'и перевод должен стать лучше.'),
    'en': ('Some words I may translate inaccurately. '
           'If that happens, ask the other person to say the same thing in different words, '
           'and the translation should improve.'),
    'de': ('Manche Wörter übersetze ich möglicherweise ungenau. '
           'Bitten Sie dann Ihren Gesprächspartner, denselben Gedanken mit anderen Worten zu sagen, '
           'dann wird die Übersetzung besser.'),
}

REPETICIJA = {
    'lt': 'Pabandykime. Pasakykite vieną sakinį ir nutilkite.',
    'ru': 'Давайте попробуем. Скажите одно предложение и сделайте паузу.',
    'en': 'Let us try. Say one sentence and then pause.',
    'de': 'Versuchen wir es. Sagen Sie einen Satz und machen Sie dann eine Pause.',
}

ATSISVEIKINIMAS = {
    'lt': 'Ačiū, kad leidote padėti. Tikiuosi, susikalbėjote.',
    'ru': 'Спасибо, что позволили помочь. Надеюсь, вы поняли друг друга.',
    'en': 'Thank you for letting me help. I hope you understood each other.',
    'de': 'Danke, dass ich helfen durfte. Ich hoffe, Sie haben sich verstanden.',
}


def _balso_saknis(balso_vardas: str):
    """`ru_RU-ruslan-medium` → `ruslan`."""
    if not balso_vardas:
        return None
    v = balso_vardas.lower()
    if '-' in v:
        dalys = v.split('-')
        v = dalys[1] if len(dalys) > 1 else dalys[0]
    return v


def lytis_pagal_balsa(balso_vardas: str):
    """'m' / 'v' / None. Vardas — kaip Piper kataloge (`ru_RU-ruslan-medium` → `ruslan`)."""
    return BALSU_LYTIS.get(_balso_saknis(balso_vardas))


def vardas_pagal_balsa(balso_vardas: str, kalba: str = None):
    """Kaip kolonėlė pati save vadina. Nežinomam balsui — senasis vardas pagal kalbą."""
    v = VARDAI_PAGAL_BALSA.get(_balso_saknis(balso_vardas))
    return v or VARDAI.get(kalba, 'Reginutė')


def sveikinimas(kalba: str, vardas: str = None, lytis=None, pauze: float = 1.0,
                su_ispejimu: bool = True, trumpas: bool = False,
                stenograma: bool = False, sekretore: bool = False,
                garsas: bool = False) -> str:
    """Sveikinimas viena kalba.

    Trys lygiai (`ALGORITMAS.md` 10.6). **Išjungti galima viską, išskyrus pranešimą apie
    įrašymą** — todėl `stenograma=True` prideda jį prie abiejų kalbamų lygių, o „tylų" lygį
    (nieko nesakom) leidžia tik pats variklis ir tik tada, kai stenograma išjungta.

      pilnas  — prisistatymas · kaip kalbėti · kreipkitės vienas į kitą · įspėjimas · užrašysiu
      trumpas — prisistatymas · „esu pasiruošusi" · užrašysiu
    """
    vardas = vardas or VARDAI.get(kalba, 'Reginutė')
    d = [PRISISTATYMAS[kalba].get(lytis, PRISISTATYMAS[kalba][None]).format(vardas=vardas)]
    if trumpas:
        d.append(PASIRUOSE[kalba].get(lytis, PASIRUOSE[kalba][None]))
    else:
        d.append(NURODYMAS[kalba].format(
            pauze=PAUZE[kalba].get(round(pauze, 1), PAUZE[kalba][None])))
        d.append(TOLIAU[kalba])
        d.append(VIENAS_SU_KITU[kalba])
        if su_ispejimu:
            d.append(ISPEJIMAS[kalba])
    if stenograma:
        d.append((UZRASYSIU_SEKRETORE if sekretore else UZRASYSIU)[kalba])
    if garsas:
        d.append(GARSAS_IRASOMAS[kalba])
    return ' '.join(d)


def sveikinimas_sekretores(kalba: str, vardas: str = None, lytis=None,
                           garsas: bool = False) -> str:
    """Sekretorės prisistatymas — trumpas visada.

    Roberto sprendimas 09-18: ją įjungus ji **trumpai prisistato, kad visi žinotų, jog bus
    stenografuojama**. Ilgo nurodymo čia nėra sąmoningai: sekretorė neverčia, tad nei pauzių,
    nei „kalbėkite vienas su kitu" jai nereikia — susirinkimo pradžioje tai būtų trukdymas.
    """
    vardas = vardas or VARDAI.get(kalba, 'Reginutė')
    d = PRISISTATYMAS_SEKRETORE.get(kalba, PRISISTATYMAS_SEKRETORE['en'])
    dalys = [d.get(lytis, d[None]).format(vardas=vardas), UZRASYSIU_SEKRETORE[kalba]]
    if garsas:
        dalys.append(GARSAS_IRASOMAS[kalba])
    return ' '.join(dalys)


def pranesimas_apie_irasa(kalba: str, sekretore: bool = False, garsas: bool = False) -> str:
    """Vien pranešimas apie įrašymą, be jokio prisistatymo.

    Sakomas tada, kai žmogus prisistatymą išjungė, bet stenograma liko: **išjungti galima
    viską, išskyrus pranešimą apie įrašymą** (`ALGORITMAS.md` 10.6). Svečias apie įrašinėjimą
    gali nežinoti, o nežinodamas negali ir nesutikti.
    """
    d = [(UZRASYSIU_SEKRETORE if sekretore else UZRASYSIU)[kalba]]
    if garsas:
        d.append(GARSAS_IRASOMAS[kalba])
    return ' '.join(d)


def pranesimas_apie_irasa_baigta(kalba: str, lytis=None, garsas: bool = False) -> str:
    """Vien pranešimas, kad įrašas baigtas — be atsisveikinimo.

    Sakomas, kai atsisveikinimas išjungtas, o stenograma buvo rašoma: tas pats 10.6 principas
    iš kitos pusės. Žmogus turi sužinoti ir kada įrašymas prasidėjo, ir kada baigėsi.
    """
    d = [IRASAS_BAIGTAS[kalba].get(lytis, IRASAS_BAIGTAS[kalba][None])]
    if garsas:
        d.append(GARSAS_BAIGTAS[kalba].get(lytis, GARSAS_BAIGTAS[kalba][None]))
    return ' '.join(d)


def atsisveikinimas(kalba: str, lytis=None, stenograma: bool = False,
                    garsas: bool = False) -> str:
    """Atsisveikinimas viena kalba.

    ⛔ Jei buvo rašoma stenograma, BŪTINAI pasakom, kad įrašas baigtas (Roberto sprendimas
    09-17): kitaip žmonės liks manyti, kad tebeveikia. Nutylėti galima tik tada, kai
    stenogramos nebuvo.
    """
    d = [ATSISVEIKINIMAS[kalba]]
    if stenograma:
        d.append(IRASAS_BAIGTAS[kalba].get(lytis, IRASAS_BAIGTAS[kalba][None]))
    if garsas:
        d.append(GARSAS_BAIGTAS[kalba].get(lytis, GARSAS_BAIGTAS[kalba][None]))
    return ' '.join(d)

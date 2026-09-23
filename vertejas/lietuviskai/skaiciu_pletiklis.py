# Lithuanian number and abbreviation expansion, run before phonemization.
#
# Lithuanian numerals inflect for case and gender, so "5000 eurų" is not one
# string but several depending on the sentence around it. Left to espeak-ng,
# digits come out with the wrong endings ("penki tūkstantčei"), and clock
# times are read as plain numbers. None of this is the model's problem: the
# text simply has to reach it already written out the way a person would say
# it.
#
# Case codes used throughout: V nominative, G accusative, K genitive,
# I instrumental; the _f suffix marks feminine forms. In compound ordinals
# only the LAST part takes the ordinal ending ("du tūkstančiai penktais").
#
# Deliberately not covered (these fall back to the nominative): the locative,
# rare pronominal forms, and collective numerals ("dveji metai"). They are
# added when a real sentence needs them, not in advance.
import re

# --- cardinal units -------------------------------------------------------
VNT = {
    1: {"V": "vienas", "G": "vieną", "K": "vieno", "I": "vienu",
        "V_f": "viena", "G_f": "vieną", "K_f": "vienos", "I_f": "viena"},
    2: {"V": "du", "G": "du", "K": "dviejų", "I": "dviem",
        "V_f": "dvi", "G_f": "dvi", "K_f": "dviejų", "I_f": "dviem"},
    3: {"V": "trys", "G": "tris", "K": "trijų", "I": "trimis",
        "V_f": "trys", "G_f": "tris", "K_f": "trijų", "I_f": "trimis"},
    4: {"V": "keturi", "G": "keturis", "K": "keturių", "I": "keturiais",
        "V_f": "keturios", "G_f": "keturias", "K_f": "keturių", "I_f": "keturiomis"},
    5: {"V": "penki", "G": "penkis", "K": "penkių", "I": "penkiais",
        "V_f": "penkios", "G_f": "penkias", "K_f": "penkių", "I_f": "penkiomis"},
    6: {"V": "šeši", "G": "šešis", "K": "šešių", "I": "šešiais",
        "V_f": "šešios", "G_f": "šešias", "K_f": "šešių", "I_f": "šešiomis"},
    7: {"V": "septyni", "G": "septynis", "K": "septynių", "I": "septyniais",
        "V_f": "septynios", "G_f": "septynias", "K_f": "septynių", "I_f": "septyniomis"},
    8: {"V": "aštuoni", "G": "aštuonis", "K": "aštuonių", "I": "aštuoniais",
        "V_f": "aštuonios", "G_f": "aštuonias", "K_f": "aštuonių", "I_f": "aštuoniomis"},
    9: {"V": "devyni", "G": "devynis", "K": "devynių", "I": "devyniais",
        "V_f": "devynios", "G_f": "devynias", "K_f": "devynių", "I_f": "devyniomis"},
}
# 11-19 inflect like feminine -a nouns (vienuolika / vienuolikos / ...).
# The first stem used to be "vien" instead of "vienuo", so 11 came out as a
# non-word everywhere - inside 111 and in the ordinal too. It was found by
# accident while checking a price, and would otherwise have shipped.
PALIKT = {n: "vienuo dvy try keturio penkio šešio septynio aštuonio devynio".split()[n - 11] + "lika"
          for n in range(11, 20)}


def _palikt(n, forma):
    z = PALIKT[n]
    if forma == "K":
        return z[:-1] + "os"
    return z  # V/G/I coincide in practice


DESIMT = {10: "dešimt", 20: "dvidešimt", 30: "trisdešimt",
          40: "keturiasdešimt", 50: "penkiasdešimt", 60: "šešiasdešimt",
          70: "septyniasdešimt", 80: "aštuoniasdešimt", 90: "devyniasdešimt"}
DESIMT_K = {10: "dešimties", 20: "dvidešimties", 30: "trisdešimties",
            40: "keturiasdešimties", 50: "penkiasdešimties",
            60: "šešiasdešimties", 70: "septyniasdešimties",
            80: "aštuoniasdešimties", 90: "devyniasdešimties"}


# "tūkstantis" is an i-stem with a t/č alternation, so the general ending
# rules below produce non-words for it ("tūkstantiį", "tūkstantio"). Its
# singular forms are therefore spelled out:
TUKSTANTIS_VNS = {"V": "tūkstantis", "G": "tūkstantį",
                  "K": "tūkstančio", "I": "tūkstančiu"}


def _grupe(zodis_vns, zodis_dgs, zodis_kilm, n, forma):
    """The group word (hundred/thousand/million) for a count and a case."""
    # The singular is required not only by 1 but by 21, 31 ... 91 as well
    # ("dvidešimt vienas tūkstantis", not the plural). 11 is the exception.
    vienas = (n % 10 == 1 and n % 100 != 11)
    if vienas and zodis_vns == "tūkstantis":
        return TUKSTANTIS_VNS.get(forma, zodis_vns)
    if forma == "K":
        return zodis_kilm if not vienas else zodis_vns[:-2] + ("o" if zodis_vns.endswith("as") else "io")
    if vienas:
        return {"V": zodis_vns, "G": zodis_vns[:-1] + "į" if zodis_vns.endswith("is")
                else zodis_vns[:-2] + "ą", "I": zodis_vns[:-2] + "u"}.get(forma, zodis_vns)
    # 2-9 take the plural; 10-19 and the tens take the genitive
    if n % 10 == 0 or 11 <= n % 100 <= 19:
        return zodis_kilm
    return {"V": zodis_dgs, "G": zodis_dgs[:-2] + "us",
            "I": zodis_dgs[:-2] + "ais"}.get(forma, zodis_dgs)


def kiekinis(n, forma="V", gimine=""):
    """0-999 999 999 as a cardinal in the given case (V/G/K/I) and gender."""
    if n == 0:
        return {"V": "nulis", "G": "nulį", "K": "nulio", "I": "nuliu"}[forma]
    if n < 0:
        return "minus " + kiekinis(-n, forma, gimine)
    dalys = []

    def trejetas(m, f):
        z = []
        if m >= 100:
            s = m // 100
            if s > 1:
                # The multiplier in front of "hundred" agrees with the case
                # too ("devynIŲ šimtų", not "devynI šimtų").
                z.append(VNT[s].get(f, VNT[s]["V"]))
            z.append(_grupe("šimtas", "šimtai", "šimtų", s, f))
            m %= 100
        if 11 <= m <= 19:
            z.append(_palikt(m, f))
            m = 0
        elif m >= 10:
            d = m - m % 10
            # Inside a compound numeral the tens do NOT inflect - only the
            # last part does. "devynių eurų devyniasdešimtIES devynių centų"
            # was wrong; "devyniasdešimt devynių" is right. The genitive form
            # of the tens is used only when the tens are themselves last,
            # i.e. when there are no units after them.
            paskutine = (m % 10 == 0)
            z.append(DESIMT_K[d] if (f == "K" and paskutine) else DESIMT[d])
            m %= 10
        if m:
            z.append(VNT[m][f + gimine] if (f + gimine) in VNT[m] else VNT[m][f])
        return z

    if n >= 1_000_000:
        mln = n // 1_000_000
        # The multiplier in front of "million" used to be locked to the
        # nominative, so "skirs 5 mln." came out with a mismatched case. It
        # has to agree, exactly like the one in front of "hundred".
        mln_f = forma if forma in ("G", "I", "K") else "V"
        if mln > 1:
            dalys += trejetas(mln, mln_f)
        dalys.append(_grupe("milijonas", "milijonai", "milijonų", mln, forma))
        n %= 1_000_000
    if n >= 1000:
        t = n // 1000
        # Same rule for the thousands multiplier, and it took three passes to
        # get right. First it was locked to the nominative ("penkI
        # tūkstančius"). Then the genitive was left out, which showed up as
        # "nuo du tūkstančių eurų" as soon as genitive prepositions were
        # handled. Finally the agreement was conditioned on the thousands
        # being the LAST group, so "nuo 3500 eurų" gave "nuo trys tūkstančiai
        # penkių šimtų" - in Lithuanian separate groups (thousands + hundreds)
        # are BOTH inflected. That is not the same rule as the tens above:
        # there the tens and units sit inside one group.
        tukst_f = forma if forma in ("G", "I", "K") else "V"
        if t > 1:
            dalys += trejetas(t, tukst_f)
        dalys.append(_grupe("tūkstantis", "tūkstančiai", "tūkstančių", t, forma))
        n %= 1000
    if n:
        dalys += trejetas(n, forma)
    return " ".join(dalys)


# --- ordinals -------------------------------------------------------------
KELINT_KAM = {1: "pirm", 2: "antr", 3: "treči", 4: "ketvirt", 5: "penkt",
              6: "šešt", 7: "septint", 8: "aštunt", 9: "devint", 10: "dešimt",
              20: "dvidešimt", 30: "trisdešimt", 40: "keturiasdešimt",
              50: "penkiasdešimt", 60: "šešiasdešimt", 70: "septyniasdešimt",
              80: "aštuoniasdešimt", 90: "devyniasdešimt"}
for _n in range(11, 20):
    KELINT_KAM[_n] = PALIKT[_n][:-1] + "t"
# endings: (gender, case) -> ending; the pronominal forms are separate
KELINT_GAL = {("m", "V"): "as", ("m", "G"): "ą", ("m", "K"): "o",
              ("m", "Idgs"): "ais", ("m", "Vdgs"): "i",
              ("f", "V"): "a", ("f", "G"): "ą", ("f", "K"): "os", ("m", "Kdgs"): "ų"}
IVARDZ = {("m", "V"): "asis", ("m", "G"): "ąjį", ("f", "V"): "oji",
          ("f", "G"): "ąją", ("m", "Idgs"): "aisiais"}


def kelintinis(n, gimine="m", forma="V", ivardz=False):
    """Compound ordinal: only the LAST part takes the ordinal ending."""
    if n <= 0:
        return kiekinis(n)
    lik = n % 100
    if lik == 0:
        lik = n % 1000 if n % 1000 else n  # 1900 -> "šimtųjų"? fallback žemiau
    baze = n - (n % 100)
    pask = n % 100
    priek = ""
    if pask == 0:                     # apvalūs: 2000-aisiais (fallback kiekinis+gal)
        kam = KELINT_KAM.get(n // (10 ** (len(str(n)) - 1)))
        return kiekinis(n) + ("-aisiais" if forma == "Idgs" else "")
    if pask > 20 and pask % 10:
        priek = DESIMT[pask - pask % 10] + " "
        pask = pask % 10
    kam = KELINT_KAM[pask]
    gal = (IVARDZ if ivardz else KELINT_GAL).get((gimine, forma))
    if gal is None:
        gal = KELINT_GAL[("m", "V")]
    zodis = priek + kam + gal
    return (kiekinis(baze) + " " if baze else "") + zodis


# --- abbreviations --------------------------------------------------------
SANTRUMPOS = [(r"\bproc\.", " procentai"), (r"\bval\.(?=\s|$)", " valandos"),
              (r"\bEur\b", " eurų"), (r"\bmln\.", " milijonai"),
              (r"\bkm\b", " kilometrų"), (r"\bkg\b", " kilogramų"),
              (r"\bLR\b", "Lietuvos Respublikos")]

# --- SPELLED-OUT ABBREVIATIONS --------------------------------------------
# „MTL" Reginute isbardavo kaip vientisa zodi, o Ona kiekviena raide taria
# atskirai su mazute pauze — todel ju girdisi. Perrasom raidziu vardais.
RAIDZIU_VARDAI = {
    "A": "a", "Ą": "a nosinė", "B": "bė", "C": "cė", "Č": "čė", "D": "dė",
    "E": "e", "Ę": "e nosinė", "Ė": "ė", "F": "ef", "G": "gė", "H": "ha",
    "I": "i", "Į": "i nosinė", "Y": "ilgoji i", "J": "jot", "K": "ka",
    "L": "el", "M": "em", "N": "en", "O": "o", "P": "pė", "Q": "kū",
    "R": "er", "S": "es", "Š": "eš", "T": "tė", "U": "u", "Ų": "u nosinė",
    "Ū": "ilgoji u", "V": "vė", "W": "dviguba vė", "X": "iks", "Z": "zė",
    "Ž": "žė",
}
# Skaitomos kaip ZODIS, ne raidemis — neliesti.
# ⭐ JAV ir FIBA irodyti duomenimis (09-03, Roberto pastaba): LIEPA garsyno
# tekstuose „ES" israsyta kaip „E ES", „NMA" kaip „EN EM A", bet „JAV"
# paliktas NEISSKAIDYTAS, o g2p zodynas ji raso j' e v' = „jav" sulietai.
# ⇒ pilni raidziu vardai (em, es, el, te, ve) — norma (patvirtina ir LIEPA,
# ir zodynas: TV -> „te ve", KGB -> „ka ge be", LRT -> „el er te"),
# BET JAV yra tikra isimtis.
SANTRUMPOS_ZODZIU = {
    "NATO", "UNESCO", "UNICEF", "SODRA", "LIEPA", "COVID", "AIDS", "LED",
    "PIN", "WIFI", "USB", "PDF", "GPS", "JAV", "FIBA", "NASA", "DELFI",
    # The second exception after JAV, and both were found the same way - by
    # listening, not by rule. Spelling out the letters stays the default for
    # everything else (the corpus writes "E ES", "EN EM A"); these two have
    # grown into single words in everyday speech.
    "VMI",
}


_ZODZIU_SARASAS = None


def _yra_tikras_zodis(s):
    """Is this an ordinary Lithuanian word that merely happens to be written
    in capitals? Checked against the pronunciation lexicon, so that words like
    "ORAI" or "KARAS" written for emphasis are not spelled out letter by
    letter. News text contains both abbreviations and shouted words."""
    global _ZODZIU_SARASAS
    if _ZODZIU_SARASAS is None:
        import io
        import os
        _ZODZIU_SARASAS = set()
        # The path is searched rather than hard-coded: on a small server the
        # full lexicon is not there, and without a fallback this protection
        # would fail SILENTLY - "ORAI" would start being read as four letters.
        # A short word list (33 895 words of 4-6 letters) ships beside the
        # module, and that is all this check needs.
        cia = os.path.dirname(os.path.abspath(__file__))
        for kelias in (os.path.join(r"D:\_Balsas Lietuviksas", "_modeliai",
                                    "g2p-lt", "lexicon.tsv"),
                       os.path.join(cia, "piper_lt", "zodziai_trumpi.txt"),
                       os.path.join(cia, "zodziai_trumpi.txt")):
            if os.path.exists(kelias):
                for eil in io.open(kelias, encoding="utf-8"):
                    _ZODZIU_SARASAS.add(eil.split("\t", 1)[0].strip())
                break
    return s.lower() in _ZODZIU_SARASAS


def raidem(m):
    """AAA -> the letter names, as one fragment ("vė em i")."""
    s = m.group(0)
    if s in SANTRUMPOS_ZODZIU:
        return s
    # The lexicon check applies only from 4 letters up. Shorter capitalised
    # strings (ES, JAV, VU) collide with real words too often, and in capitals
    # they are almost always abbreviations anyway. From 4 letters, genuine
    # words become plausible, and those are protected.
    if len(s) >= 4 and _yra_tikras_zodis(s):
        return s
    # How an abbreviation should sound took five rounds of listening, and the
    # shape below is the result rather than a first guess.
    #
    # The corpus writes spelled-out letters as ordinary words mid-sentence,
    # with no separators at all ("Rusijos ir Europos Sąjungos E ES"), and the
    # model learned them that way. Putting a separator between every letter
    # therefore isolates the abbreviation into a kind of fragment the model
    # never saw in training - and it was audibly worse, letters rattling out
    # one at a time.
    #
    # Removing the separators entirely was worse in a different way: the
    # sentence then became ONE fragment, and the rate levelling in
    # synth_reginute works per fragment, so the whole text sped up. What
    # sounded rushed was the speech around the abbreviation, not the
    # abbreviation itself.
    #
    # So: the letters are joined by SPACES (they run together, as in the
    # corpus), and the hyphens stay only on the OUTSIDE. That still makes the
    # abbreviation its own fragment, which synth_reginute recognizes by the
    # surrounding hyphens and speaks slower (SANTRUMPOS_LETUMAS). Redundant
    # hyphens before punctuation are cleaned up in isplesk().
    return " - " + " ".join(RAIDZIU_VARDAI.get(c, c) for c in s) + " - "


# A Lithuanian noun agrees with the number in front of it, in three forms:
# 21 euRAS (singular) · 2-9, 22-29 euRAI (plural) · 10, 11-19, 20, 30 euRŲ
# (genitive plural).
EURAI = ("euras", "eurai", "eurų")
CENTAI = ("centas", "centai", "centų")
# Units of measurement need the same agreement. The fourth field is gender:
# "" masculine, "_f" feminine ("dvi tonos", not "du tonos").
# The table used to hold only km/kg/proc, so every other unit was read out as
# a letter ("du gė" for "2 g") - which is exactly as odd as it looks.
VIENETAI = {
    "km":  ("kilometras", "kilometrai", "kilometrų", ""),
    "cm":  ("centimetras", "centimetrai", "centimetrų", ""),
    "mm":  ("milimetras", "milimetrai", "milimetrų", ""),
    "kg":  ("kilogramas", "kilogramai", "kilogramų", ""),
    "ml":  ("mililitras", "mililitrai", "mililitrų", ""),
    "ha":  ("hektaras", "hektarai", "hektarų", ""),
    # electricity units, common in household text:
    "kW":  ("kilovatas", "kilovatai", "kilovatų", ""),
    "Wh":  ("vatvalandė", "vatvalandės", "vatvalandžių", "_f"),
    "kWh": ("kilovatvalandė", "kilovatvalandės", "kilovatvalandžių", "_f"),
    "proc": ("procentas", "procentai", "procentų", ""),
}
# Single-letter units (W, A, V, m, g, t, l) are deliberately NOT included.
# Every one of them has a second meaning in Lithuanian text: V is also the
# Roman numeral five, A. V. W. are initials in names, g. is "street", t. is
# part of common abbreviations. Requiring a number in front rejects most of
# those cases but not all: "5 A klasė" (class 5A) would become "five amperes
# class". The cost is that "2 m" and "500 g" stay as letters - better an odd
# reading in a rare place than a confident lie in a common one. Adding them
# back is one line in the table and one in the pattern.
VIENETU_SABLONAS = "kWh|kW|Wh|km|kg|cm|mm|ml|ha|proc\\."


def _skaic_forma(n, formos):
    d10, d100 = n % 10, n % 100
    if d10 == 1 and d100 != 11:
        return formos[0]
    if d10 == 0 or 11 <= d100 <= 19:
        return formos[2]
    return formos[1]


# Case forms of "el. paštas" (e-mail). All of them except the rare dative
# plural are in the stress dictionary, so the accent comes from there rather
# than from espeak.
EL_PASTAS = {"paštas": "elektroninis", "paštu": "elektroniniu",
             "pašto": "elektroninio", "paštą": "elektroninį",
             "pašte": "elektroniniame", "paštai": "elektroniniai",
             "paštus": "elektroninius", "paštų": "elektroninių",
             "paštais": "elektroniniais", "paštams": "elektroniniams"}

MOT_ZODZIAI = r"(valand|dien|minut|savait|sekund|viet|klas|kart(?!ą))"
GAL_VEIKSMAZODZIAI = r"(kainuoja|kainavo|moka|mokėjo|sumokėjo|gavo|gaus|" \
                     r"turi|turėjo|siekia|siekė|sudaro|sudarė|uždirba|uždirbo|" \
                     r"skyrė|skirs|prarado|laimėjo|surinko)"


def isplesk(t):
    # "el. paštu" -> "elektroniniu paštu". espeak expands "el." into the
    # NOMINATIVE and keeps the full stop, so any other case came out
    # ungrammatical and with a pause in the middle of the phrase
    # (`ˋeɭektronʲinʲis. paʃˋtu`). The adjective now agrees with the noun.
    # The wording is not invented: the speaker says "faksu ar elektroniniu
    # paštu" in the training data, so the model has heard this exact phrase.
    def _el_pastas(m):
        vnt = m.group(2)
        zodis = EL_PASTAS.get(vnt.lower(), "elektroninis")
        return (zodis.capitalize() if m.group(1)[0].isupper() else zodis) + " " + vnt
    t = re.sub(r"\b([Ee]l)\.\s*(pašt[a-ząčęėįšųūž]*)", _el_pastas, t)
    # Units of measurement, made to agree with the number in front of them.
    # `km` used to expand to a fixed genitive plural, so "12 km" happened to
    # be right while "5 km" and "100,5 km" were not. The unit has to agree
    # with the LAST number actually spoken - for a decimal, that is the
    # fractional part, exactly as people say it. This must run BEFORE the
    # general abbreviation table.
    def _vienetas(m):
        sk, tr, vnt = m.group(1), m.group(2), m.group(3)
        n = int(tr) if tr else int(sk)
        *formos, gim = VIENETAI[vnt.rstrip(".")]
        skaic = (f"{kiekinis(int(sk), 'V', gim)} kablelis "
                 f"{kiekinis(int(tr), 'V', gim)}" if tr
                 else kiekinis(int(sk), "V", gim))
        # The full stop in "proc." belongs to the abbreviation, but at the end
        # of a sentence it also ends the sentence - and the synthesis splits
        # phrases on it. So it is put back.
        liko = m.string[m.end():]
        galas = "." if (vnt.endswith(".") and
                        (not liko.strip() or re.match(r"\s+[A-ZĄČĘĖĮŠŲŪŽ]", liko))) else ""
        return f"{skaic} {_skaic_forma(n, formos)}{galas}"
    t = re.sub(r"\b(\d{1,9})(?:,(\d{1,2}))?\s*(" + VIENETU_SABLONAS +
               r")(?=\s|$|[.,;:!?])", _vienetas, t)
    # "5 mln." is a MULTIPLIER, not a unit. In the abbreviation table it was
    # locked to the nominative, so a sentence like "skirs 5 mln. eurų" put the
    # number in the accusative and the millions in the nominative. Turning it
    # into a real number lets `kiekinis` choose the case, which it already
    # knows how to do.
    t = re.sub(r"\b(\d{1,3})\s*mln\.", lambda m: str(int(m.group(1)) * 1_000_000), t)
    # "tūkst." the same way. It was not in the table at all, so it reached the
    # phonemizer unexpanded, in the middle of a phrase. It is common in news.
    t = re.sub(r"\b(\d{1,3})\s*tūkst\.", lambda m: str(int(m.group(1)) * 1000), t)
    # `mlrd.` is deliberately left alone: 4 mlrd. = 4 000 000 000 exceeds what
    # `kiekinis` covers (999 999 999) and would come out as bare digits, which
    # is worse than the abbreviation. It stays with the old table.
    # Plain abbreviations
    for r, z in SANTRUMPOS:
        t = re.sub(r, z, t)
    # Letter-by-letter abbreviations: 2-5 capitals in a row -> letter names.
    # Only if the whole run is capitals (so "Vilnius" is untouched) and not
    # followed by lowercase (so a capitalised ordinary word at the start of a
    # sentence is not split apart).
    t = re.sub(r"\b[A-ZĄČĘĖĮŠŲŪŽ]{2,5}\b", raidem, t)
    # Clean up the hyphens: collapse doubles, and drop them before punctuation
    # and at line edges, so nothing is left dangling.
    t = re.sub(r"(?:\s*-\s*){2,}", " - ", t)
    t = re.sub(r"\s*-\s*(?=[.,:;!?])", "", t)
    t = re.sub(r"\s*-\s*$", "", t, flags=re.MULTILINE)
    t = re.sub(r"^\s*-\s*", "", t, flags=re.MULTILINE)
    # Prices: "9,99 Eur" -> "nine euros ninety nine cents", not "nine comma
    # ninety nine". Must run BEFORE the general decimal rule below, and it
    # also matches the already-expanded "eurų" form from the table above.
    def _kaina(m):
        e, c = int(m.group(1)), int(m.group(2))
        pries = (m.string[:m.start()].rstrip().split() or [""])[-1].lower()
        kilm = pries in ("nuo", "iki", "ligi")
        f = "K" if kilm else "V"
        dalys = [kiekinis(e, f), EURAI[2] if kilm else _skaic_forma(e, EURAI)]
        if c:
            dalys += [kiekinis(c, f), CENTAI[2] if kilm else _skaic_forma(c, CENTAI)]
        return " ".join(dalys)
    t = re.sub(r"\b(\d+),(\d{1,2})\s*(?:Eur\b|eurų|eurai|euro|euru|€)", _kaina, t)
    # Decimal comma: "9,99" -> "nine comma ninety nine". Without this the
    # comma stayed between the two words and the whole thing was spoken as one
    # glued-together word. Must run BEFORE the remaining number rules, which
    # would otherwise process the two halves separately.
    t = re.sub(r"\b(\d+),(\d{1,2})\b",
               lambda m: f"{kiekinis(int(m.group(1)))} kablelis "
                         f"{kiekinis(int(m.group(2)))}", t)
    # Clock times. A whole hour is read as an ordinal ("the fifteenth hour"),
    # otherwise as hour + minutes. After "nuo"/"iki"/"ligi" Lithuanian needs
    # the GENITIVE - "nuo aštuntos valandos", not "nuo aštuntą valandą" -
    # which is what made opening hours sound ungrammatical.
    NUO_IKI = ("nuo", "iki", "ligi")

    def _laikas(m):
        h, mi = int(m.group(1)), int(m.group(2))
        pries = (m.string[:m.start()].rstrip().split() or [""])[-1].lower()
        kilm = pries in NUO_IKI
        if mi == 0:
            return (kelintinis(h, "f", "K") + " valandos" if kilm
                    else kelintinis(h, "f", "G") + " valandą")
        val = kiekinis(h, "K") if kilm else kiekinis(h)
        return val + " " + (kiekinis(mi) if mi > 9 else "nulis " + kiekinis(mi))
    t = re.sub(r"\b(\d{1,2}):(\d{2})\b", _laikas, t)
    # Years take an ordinal in the instrumental: "2015 metais" / "2015 m."
    t = re.sub(r"\b(1\d{3}|2\d{3})\s*(m\.|metais)\b",
               lambda m: kelintinis(int(m.group(1)), "m", "Idgs") + " metais", t)
    t = re.sub(r"\b(1\d{3}|2\d{3})\s*metų\b",
               lambda m: kelintinis(int(m.group(1)), "m", "Kdgs") + " metų", t)
    t = re.sub(r"\b(1\d{3}|2\d{3})-(ai|ų|į)?[a-zų]*\b",
               lambda m: kelintinis(int(m.group(1)), "m", "Idgs", ivardz=True), t)
    # Feminine accusative: "15 valandą/vietą/klasę" takes an ordinal
    t = re.sub(r"\b(\d{1,3})\s+(" + MOT_ZODZIAI + r"[ąę])",
               lambda m: kelintinis(int(m.group(1)), "f", "G") + " " + m.group(2), t)
    # Masculine ordinal, accusative: "23 kartą" -> "the twenty-third time"
    t = re.sub(r"\b(\d{1,3})\s+(kartą|numerį|aukštą|etapą|turą|sezoną|puslapį)\b",
               lambda m: kelintinis(int(m.group(1)), "m", "G") + " " + m.group(2), t)
    # Feminine cardinals: "2 valandas/dienas" -> "dvi valandas", not "du"
    t = re.sub(r"\b(\d{1,4})\s+(" + MOT_ZODZIAI + r"(as|os|es|ių|ę))",
               lambda m: kiekinis(int(m.group(1)),
                                  "G" if m.group(2).endswith(("as", "es", "ę")) else "V",
                                  "_f") + " " + m.group(2), t)
    # Accusative after a verb that governs it: "kainuoja 25 eurus"
    t = re.sub(GAL_VEIKSMAZODZIAI + r"\s+(\d{1,9})\b",
               lambda m: m.group(1) + " " + kiekinis(int(m.group(2)), "G"), t)
    # Masculine accusative before a noun: "3 mėnesius/eurus/kartus"
    t = re.sub(r"\b(\d{1,9})\s+([a-ząčęėįšųūž]+(?:us|į|ą))\b",
               lambda m: kiekinis(int(m.group(1)), "G") + " " + m.group(2), t)
    # Prepositions that govern the genitive: "nuo 2000 eurų" used to leave the
    # number in the nominative. Clock times after "nuo/iki" were already
    # handled; ordinary numbers were not.
    # The list is deliberately short - only prepositions that ALWAYS take the
    # genitive. "po" is ambiguous ("po du" vs "po dviejų valandų"), and "už,
    # per, prieš, apie" take the accusative. Same principle as with the units
    # above: skip the risky ones rather than be confidently wrong.
    t = re.sub(r"\b(nuo|iki|ligi|be|dėl|iš|tarp|virš|šalia|arti)\s+(\d{1,9})\b",
               lambda m: m.group(1) + " " + kiekinis(int(m.group(2)), "K"), t)
    # "minus N" already reads naturally for temperatures; anything left over
    # becomes a plain nominative cardinal.
    t = re.sub(r"\b\d{1,9}\b", lambda m: kiekinis(int(m.group(0))), t)
    return re.sub(r"\s{2,}", " ", t)


if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding="utf-8")
    testai = [
        "dar 2015 metais priimto sprendimo",
        "1998 metų sausį", "2026-aisiais",
        "ilgiau kaip 3 mėnesius iš eilės",
        "susitiksim 15:00, o vakarienė 19:30",
        "užėmė 3 vietą, o 2 valandas laukė",
        "kainuoja 25 eurus, o bauda siekia 150 Eur",
        "mieste gyvena 2 mln. žmonių, tai 45 proc.",
        "nuvažiavo 12 km ir nešė 80 kg",
        "temperatūra minus 5 laipsniai",
        "gavo 1234567 eurų palikimą",
        "jau 23 kartą laimėjo 7 vietą",
    ]
    for x in testai:
        print(f"{x:44s} -> {isplesk(x)}")

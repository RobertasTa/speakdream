# -*- coding: utf-8 -*-
"""EKVALAIZERIS kiekvienam balsui (2026-10-29).

Roberto pasiūlymas: prie „Greitis" slankiklio — dantratis, kuris atveria ekvalaizerį, kad
kiekvieną balsą būtų galima derinti pagal savo ausį. Mechanizmas paimtas iš Skaityklės
(`SKAITYKLE programa\\skaitykle\\garsas.py`, 2026-10-28) — ten jis pamatuotas ir veikia.

Skirtumai nuo Skaityklės:
  * BE garsumo slankiklio — SpeakDream garsumą jau turi pagrindiniame lange („Garsas").
  * Visa frazė apdorojama VIENU kartu (`reset=True`): sintezė grąžina visą frazę, gabalais
    negrojam, tad Skaityklės `reset=False` spąstas čia nekyla.
  * Lygus ekvalaizeris (visi 0) garso NELIEČIA visai — senas kelias lieka bitas į bitą.

Juostos — oktavos 125 Hz … 8 kHz (ISO 266), tos pačios, kuriomis skaičiuojamas kalbos
suprantamumas. Virš ~11 kHz mūsų garso nėra: Piper balsai 22 050 Hz.
Biblioteka `pedalboard` (Spotify, GPL-3.0 — tinka mūsų GPL v3).

⛔ Skaityklės pamatuotas spąstas: `pedalboard.Limiter` NĖRA apsauga nuo kirpimo — jis pakelia
garsą net tada, kai niekas slenksčio neperžengia. Todėl `Compressor` + minkštas kirpimas.
"""
import numpy as np

# (dažnis Hz, pavadinimas, ką daro) — aprašai iš garso inžinierių vadovų balsui.
JUOSTOS = (
    (125, 'Gylis', 'Balso kūnas ir sodrumas. Per daug — balsas dunda.'),
    (250, 'Šiluma', 'Šiltumas. Per daug — balsas tampa neaiškus, „purvinas".'),
    (500, 'Pilnumas', 'Balso pilnumas. Per daug — skamba kaip iš kartoninės dėžės.'),
    (1000, 'Vidurys', 'Balso branduolys. Per daug — nosinis, „telefoninis" skambesys.'),
    (2000, 'Aiškumas', 'Žodžių suprantamumas — čia gyvena priebalsiai.'),
    (4000, 'Ryškumas', 'Artumas, balsas „prie ausies". Per daug — rėžia ausį.'),
    (8000, 'S garsai', 'Gaivumas, s, š, z, ž. Per daug — švilpia; per mažai — duslu.'),
)
Q_OKTAVA = 1.41         # vienos oktavos pločio juosta
EQ_RIBA = 12            # ± dB kiekvienai juostai (įprasta grafiniams ekvalaizeriams)
SLENKSTIS = 0.89        # −1 dBFS: virš jo minkštas kirpimas


def lygus(eq) -> bool:
    return not eq or not any(int(v) for v in eq)


def minkstas_kirpimas(a):
    """Žemiau SLENKSČIO — nepaliesta; virš — tanh kreive švelniai iki 1,0 (ne kampu)."""
    virs = np.abs(a) > SLENKSTIS
    if not virs.any():
        return a
    a = a.copy()
    v = np.abs(a[virs]) - SLENKSTIS
    a[virs] = np.sign(a[virs]) * (SLENKSTIS + (1 - SLENKSTIS) * np.tanh(v / (1 - SLENKSTIS)))
    return a


def apdorok(bangos, daznis, eq):
    """Visa frazė per 7 juostas. Lygus `eq` — grąžinama ta pati banga, nepaliesta."""
    if lygus(eq) or not len(bangos):
        return bangos
    import pedalboard as pb
    filtrai = [pb.PeakFilter(cutoff_frequency_hz=float(f), gain_db=float(g), q=Q_OKTAVA)
               for (f, _, _), g in zip(JUOSTOS, eq)]
    lenta = pb.Pedalboard(filtrai + [
        pb.Compressor(threshold_db=-2.0, ratio=20.0, attack_ms=1.0, release_ms=80.0)])
    y = lenta.process(np.asarray(bangos, dtype='float32'), float(daznis), reset=True)
    return minkstas_kirpimas(y)

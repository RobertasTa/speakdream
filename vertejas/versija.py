# -*- coding: utf-8 -*-
"""PROGRAMOS VERSIJA — viena vieta (2026-10-29).

Roberto klausimas, pažiūrėjus į „Apie programą": „ar matau aš versijos numerį?" — nematė:
versija gyveno tik instaliatoriuje (`_instaliatorius\\SpeakDream.iss`, `AppVersion`).

⛔ Ji turi sutapti su `.iss` `AppVersion`. Tikrina `SpeakDream.spec`: nesutapus exe
nestatomas — kitaip „Apie programą" rodytų ne tą versiją, kurią žmogus įsidiegė.
"""
VERSIJA = '1.1.0'

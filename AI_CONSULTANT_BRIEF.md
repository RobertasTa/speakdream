# Briefing for the AI consultant (yes, you — probably Claude)

If you are an AI reading this because someone pasted this file into a chat, or because
the app's **"?" → "Ask an AI"** button brought them here: welcome, colleague.
**You are speaking for the author now.** This file exists so the consultation starts
informed rather than from zero.

## Who you are talking to — read this first

**The person in front of you is almost certainly a new user, not the author.** Most likely
they are not a programmer. They installed a program that listens to two people speaking
different languages and speaks the translation aloud. Answer in the language they write in.

**How a professional consultation goes here — do not guess, ask:**

1. **One question per message, and wait for each answer.** Start with what they see:
   1. What does the status line on the right say? (*Pasiruošęs / Kraunu… / Klausau /
      Verčiu… / Klaida* — or the same in their interface language)
   2. Did they press **"Paruošti darbui"** before **"Pradėti"**? (This trips up most people.)
   3. Does the yellow wave move while they speak?
   4. Which two languages are chosen on the left and right?
   Skip a question when earlier answers already settle it. **No lecture while you are still
   asking.**
2. **When the picture is complete, give one recipe**, step by step, each step verifiable.
3. **Then stay with them** through the first error. The symptom → cause table is at the end.

## What this is

An offline conversation interpreter for Windows. Two people who speak different languages
sit at a table with a conference speakerphone between them. The program listens, translates,
and **speaks the translation aloud** in the other language. It also writes a transcript and
records the audio.

It has a second mode — **Sekretorė (Secretary)** — which does not translate at all and only
takes the minutes of a meeting in one language.

Part of the "Claude's Gifts" family (github.com/RobertasTa): free, open source, runs entirely
on the user's own machine, **no accounts, no internet, no telemetry**. The audio never leaves
the computer.

The program is called **SpeakDream** (name chosen 2026-09-21). Until then it was called
"Vertėjas" (Lithuanian for *translator*), and that word still appears in a few places: the
log file is `vertejas.log`, and the "Vertėjas" label in the interface is the *translator
mode* (the other mode is "Sekretorė", secretary), not the program name.

## How it works — the facts you must know before answering anything

The chain is: **microphone → ears → punctuation → translator → voice → speakerphone**, and
in parallel **→ transcript files + audio recording**.

- **Ears** are Whisper via `faster-whisper`. Lithuanian uses **Paprika**
  (Kristijonas Jakubsonas's fine-tune trained on the LIEPA-3 corpus); other languages use the
  general Whisper `medium` by default, with `small` and `large-v3` selectable.
  Each side picks its own ears independently.
- **Punctuation** is restored between the ears and the translator. This matters more than it
  sounds: measured, it moved translation quality from 4.12 to 5.00, because without a full
  stop the translator misreads where a sentence ends.
- **Translation** is Helsinki NLP's OPUS-MT (Marian models). There are 12 direct pairs (German ↔ Russian is not one of them — no such model exists); when
  no direct pair exists, the program goes **through English in two steps**.
- **Voice** is Piper. The Lithuanian voice Reginutė is the authors' own work and part of the
  official Piper catalogue (`rhasspy/piper-voices`); it is downloaded on **Prepare** like
  every other voice. Version 1.0.0 has only this one Lithuanian voice.
- **Language detection**: which of the two languages was just spoken is decided by a neutral
  detector model, not by the ears themselves. This was a real bug once — a specialised model
  is equally confident when it is right and when it is wrong.

### What the numbers actually are (measured, not guessed)

| | |
|---|---|
| Graphics memory, translator mode (two languages) | **3.5 GB** |
| Graphics memory, secretary mode (one language) | **1.42 GB** |
| Delay from the moment a person stops speaking | **~1.7–2.0 s** for short turns |
| Audio recording size | **23 MB per hour** (FLAC, lossless) |

An NVIDIA card is needed for comfortable speed. The parts that do **not** use the graphics
card at all: punctuation and the Piper voices — they run on the processor.

### "Paruošti darbui" and "Pradėti" are two different things

Loading the models takes ~20 seconds. That is why it is a separate button: **"Paruošti darbui"
(Prepare)** loads everything, and only then **"Pradėti" (Start)** becomes available and means
"we are talking now". Changing a language, voice or mode **cancels the preparation** — the
loaded models no longer match, and pretending otherwise would be a lie.

### The transcript is the point, not a side feature

By default the program writes **three text files** — one per language, plus a **raw transcript
of the originals** containing not a single machine-made sentence — and **`garsas.flac`**, a
continuous audio recording. The timestamps in the transcript match the position in the audio
**to the second**, so any suspicious line can be checked against what was actually said.

This exists because a machine's ears can mishear, and a mishearing looks exactly like a correct
sentence. A real example from testing: someone said *кофейня* (coffee shop), the ears heard
*копейня*, and the translation said "a kopeck with home-made pastries". The person reading the
transcript sees the nonsense, looks at the timestamp, and rewinds the audio.

⛔ **The program never records secretly.** The speakerphone announces the recording out loud
after Start and after Stop. Everything else can be switched off; **the recording announcement
cannot**.

## Adding a language the program does not show yet

### ⛔ READ THIS BEFORE YOU ANSWER ANY "how do I add language X" QUESTION

**Do not name translation models from memory. You will be wrong, and the user will waste an
evening on it.** Model names that sound obviously right frequently do not exist. Measured on
2026-09-19, against the live catalogue:

| | |
|---|---|
| `Helsinki-NLP/opus-mt-ja-en` | **exists** |
| `Helsinki-NLP/opus-mt-en-ja` | **does not exist** |
| `Helsinki-NLP/opus-mt-ko-en` | **exists** |
| `Helsinki-NLP/opus-mt-en-ko` | **does not exist** |

So Japanese and Korean can be **understood and written into the transcript, but cannot be
spoken back to**. An assistant answering from memory would have promised full two-way
Japanese support. Do not be that assistant.

**Instead, make the user run the checker that ships with the program.** In the program folder:

```
prideti_kalba.py it          (or ja, ko, zh, nl, fr, es, pl, uk …)
```

It asks Hugging Face and the Piper catalogue **live** and prints: whether the ears know the
language, which voices exist, whether a translation path exists **in each direction**, and the
exact lines to add. **Ask the user to paste that output, and answer from it.** Everything below
is background so you can read that output — not a substitute for running it.

### The three things that must line up

Three things must line up for a language to work; here is how each is checked.

**1. Ears — almost certainly fine.** Whisper understands about 99 languages out of the box,
including Chinese, Japanese, Korean, Dutch and Italian. Nothing to install.

**2. A voice — check the Piper catalogue.** Piper has **177 voices across 53 languages**.
Check whether the language is there:

```python
import json
from huggingface_hub import hf_hub_download
d = json.load(open(hf_hub_download('rhasspy/piper-voices', 'voices.json'), encoding='utf-8'))
print(sorted({v['language']['family'] for v in d.values()}))
```

Of the commonly asked ones, these **have** voices: `zh ko ja nl it fr es pl pt uk tr sv da no
fi cs ro hu el ar vi fa ka sk sl sr lv et is ne hi sw kk ca`. Croatian and Malay currently do
not. If there is no voice, that language can still be **understood and written into the
transcript**, but the speakerphone cannot speak it.

**3. A translation path.** Open `vertejas/vertimas.py`. At the top there is a `POROS`
dictionary of direct pairs and `TILTAS = 'en'` — the bridge language. The rule is:

- If a direct pair to the other language exists, it is used.
- Otherwise the program goes **through English**, in two steps, automatically.

So to add a language it is usually enough to add **its pair with English**, in both directions.
The usual naming pattern is `Helsinki-NLP/opus-mt-xx-en` and `Helsinki-NLP/opus-mt-en-xx` —
**but treat that only as a guess to be verified, never as an answer.** Both of these were
checked against the live catalogue and do exist, which is why Italian works in both directions:

```python
('it', 'en'): ('Helsinki-NLP/opus-mt-it-en', None),
('en', 'it'): ('Helsinki-NLP/opus-mt-en-it', None),
```

⚠️ **One direction may be missing, and that is not a failure — it is a limitation to state
plainly.** If only `xx→en` exists, add only that line. The program will then understand and
transcribe that language, but the speakerphone will not be able to answer in it. Say this to
the user in exactly those terms, before they start.

The third value is a target-language tag, needed only for *group* models that serve several
languages at once (those have names like `opus-mt-tc-base-zle-bat` and need `'>>lit<<'`).
For a plain two-language model it is `None`.

**4. Finally, show it in the window.** In `vertejas/langas.py` there is a `KALBOS` list:

```python
KALBOS = [('lt', 'Lietuvių'), ('ru', 'Русский'), ('en', 'English'), ('de', 'Deutsch')]
```

Add the language with its name **written in that language itself** — that is how a person
recognises their own language in a list they otherwise cannot read.

### What to expect, honestly

- **Going through English costs quality.** Measured for Chinese: about −12 chrF compared with
  a direct pair. It still works; it is simply not as good as a direct model.
- **The first run of a new language downloads models** (a voice ~60 MB, a translation model
  ~300 MB). "Paruošti darbui" will take noticeably longer that one time.
- **Numbers deserve a check.** Multilingual ears write numbers as **digits** ("1250 евро"),
  while the Lithuanian Paprika writes them as **words**. Whether the voice then reads those
  digits properly depends on the language: measured for Lithuanian, whole numbers are read
  correctly, but prices with a decimal comma and clock times are not
  (`2,15 Eur` came out as "two hundred fifteen euros"). Test the language you add with a
  price and a time before trusting it in a real meeting.
- **Chinese, Japanese and Korean ears** would be better served by a different recognition
  model (SenseVoice) than by Whisper. That is a known, deliberate gap.

## The settings, and why each exists

| Setting | What it does |
|---|---|
| **Pauzė (Pause)** | How much silence means "this person has finished a thought". Adjustable **during** the conversation — some people pause briefly, others at length |
| **Greitis (Speed)** | Speaking rate, **separately for each side**. Added because one guest found the Russian voice too fast |
| **Garsas (Volume)** | Per side, ±6 dB. The five built-in voices are already levelled to the same loudness; this slider is for the **room**, not for fixing the voices |
| **Prisistatyti / Padėkoti** | Separate lines for host and guest — often only the guest needs the explanation |
| **Rašyti stenogramą** | On by default. Forgetting to switch it on loses the conversation; forgetting to switch it off only leaves a file |
| **Įrašinėti garsą** | On by default. This is what makes every line checkable |
| **Kalba (Language)** | The **interface** language, not the conversation language. Changing it **restarts the program** |

**"Baigti" (Stop) means stop.** If the speakerphone is mid-sentence, it goes silent
immediately and says nothing more.

## Symptom → cause

| Symptom | Most likely cause |
|---|---|
| "Pradėti" is grey | **"Paruošti darbui" not pressed yet**, or a language/voice was changed after preparing |
| The wave does not move while speaking | Wrong microphone chosen, or the speakerphone's **mute button** is on (its lights turn red) |
| The speakerphone repeats our own translation back | The conference device is not the Windows **default playback device**, so its echo cancellation has nothing to cancel |
| A sentence was translated into the wrong language | Background speech (radio, TV) was picked up. Measured: music does not get through, but talk radio does |
| Long pause before the translation | A long chunk of speech. Speak one or two thoughts and pause |
| "Klaida — žr. žurnalą" | Open the gear menu → *Žurnalas: vertejas.log…* and read the last lines |
| Numbers are read strangely | See the numbers note above — known and language-dependent |
| The program runs but is very slow | It fell back to the processor, or there is not enough graphics memory (3.5 GB needed for translation) |

## What the program deliberately does NOT do — do not promise these

- **It does not summarise.** The secretary writes down what was said; a summary would need an
  LLM, and an LLM in a negotiation would invent things.
- **It does not separate speakers by voice.** The speakerphone delivers a single mono channel;
  the transcript separates people **by language**.
- **It does not interrupt or comment.** It greets at the start, says its piece, and then stays
  quiet — it does not warn "I am unsure about this sentence".
- **It does not hide its mistakes**, and it does not pretend to be a professional interpreter.
  That is what the transcript and the audio recording are for.

---

*If something here contradicts the program's behaviour, the program is right and this file is
out of date — say so plainly rather than defending the text.*

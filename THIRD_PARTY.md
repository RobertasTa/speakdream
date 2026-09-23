# Third-party components and why this program is GPL v3

SpeakDream
Copyright (C) 2026 Robertas & Claude (Anthropic AI)

This program is free software: you can redistribute it and/or modify it under
the terms of the **GNU General Public License, version 3**, as published by the
Free Software Foundation. See [LICENSE](LICENSE) for the full text.

This program is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE. See the GNU General Public License for more details.

**Complete source code** for this program is available at
<https://github.com/RobertasTa/speakdream>.

## What this means for you

- **Using the program: no obligations at all.** Download it, run it, use it at
  home or at work. GPL restricts distribution, never use.
- **Changing it for yourself: no obligations either.** Build your own version,
  add what you need, keep it on your own machine. The author actively helps
  with this — see [AI_CONSULTANT_BRIEF.md](AI_CONSULTANT_BRIEF.md).
- **Sharing your changed version: pass the freedom on.** If you distribute a
  modified copy, it must also be GPL v3 and its source must be available.

## Why GPL v3 and not something more permissive

Not a philosophical choice — an honest one. Two components we ship are
copyleft: **PyQt6** (`GPL-3.0-only`) and **Piper** (`GPL-3.0-or-later`). A
program that bundles them can only be distributed under GPL v3. Everything else
below is permissive and would have allowed MIT; these two decide.

## Software components (versions as shipped in 1.0.0)

Licenses taken from each package's own metadata or project page.

| Component | Version | License | Role |
|---|---|---|---|
| PyQt6 | 6.11 | GPL-3.0-only | user interface |
| Piper (piper-tts) | 1.8 | GPL-3.0-or-later | text-to-speech engine |
| faster-whisper | 1.2 | MIT | speech recognition (Whisper) |
| CTranslate2 | 4.8 | MIT | Whisper inference engine |
| PyTorch | 2.11 (CUDA 12.8) | BSD-3-Clause | runs the translation models; ships the CUDA libraries |
| Transformers | 5.17 | Apache-2.0 | loads the OPUS-MT models |
| Tokenizers | 0.23 | Apache-2.0 | tokenization for the translation models |
| SentencePiece | 0.2 | Apache-2.0 | tokenization for the translation models |
| ONNX Runtime | 1.30 | MIT | runs the voices and the punctuation model |
| huggingface_hub | 1.31 | Apache-2.0 | downloads models on first use |
| sounddevice | 0.5 | MIT | microphone and speaker access |
| soundfile (libsndfile) | 0.14 | BSD-3-Clause / LGPL-2.1 (libsndfile) | writes the FLAC recording |
| NumPy | 2.5 | BSD-3-Clause | audio arrays |
| punctuators | 0.0.7 | see project page | punctuation model runtime |
| PyInstaller | 6.22 | GPL-2.0-or-later with bootloader exception | packaging only, not part of the shipped program's license terms |

## Models (downloaded on first use, or bundled)

| Model | Author | License | Used for |
|---|---|---|---|
| `RobertasTa/paprika-whisper-lt-v3-ct2-int8` (Paprika) | Kristijonas Jakubsonas; CTranslate2 conversion by the authors | CC BY 4.0 | Lithuanian ears |
| Whisper `medium` (via faster-whisper) | OpenAI | MIT | ears for other languages, language detection |
| `Helsinki-NLP/opus-mt-tc-base-zle-bat`, `…-bat-zle`, `…-tc-big-en-lt`, `…-tc-big-lt-en`, `…-tc-bible-big-deu_eng_fra_por_spa-bat`, `…-bat-deu_eng_nld`, `opus-mt-en-ru`, `ru-en`, `en-de`, `de-en`, `zh-en`, `en-zh` | University of Helsinki (OPUS-MT) | CC BY 4.0 | translation |
| `1-800-BAD-CODE/xlm-roberta_punctuation_fullstop_truecase` | 1-800-BAD-CODE | Apache-2.0 | punctuation and casing before translation |
| `punct_restore` (word-preserving wrapper) | Kristijonas Jakubsonas | Apache-2.0 | same |
| Piper voices from `rhasspy/piper-voices` (e.g. `ru_RU-ruslan-medium`) | Rhasspy / voice authors | per voice — see each voice's MODEL_CARD | Russian, English, German voices |
| `lt_LT-reginute1-medium` (Reginutė) from `rhasspy/piper-voices`, downloaded on first use | Robertas & Claude (trained on the LIEPA corpus) | CC BY 4.0 | Lithuanian voice |

Silero VAD (MIT) is used through faster-whisper for voice activity detection.

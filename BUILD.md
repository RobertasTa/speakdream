# SpeakDream — build recipe

## Environment

- Python 3.12 venv `.venv` with `pip install -r requirements.txt`.
  `torch` must be the CUDA build (the one on PyPI with `+cu128` in its version,
  or from the PyTorch index): the packaged program takes its CUDA libraries
  from `torch\lib` — that is what makes it self-contained.
- Build ALWAYS through `python -m PyInstaller` (venv shims break — family
  lesson), from the repo root:

```
.venv\Scripts\python.exe -m PyInstaller SpeakDream.spec --noconfirm
```

Takes about 6 minutes. Read `build\SpeakDream\warn-SpeakDream.txt` afterwards
and grep for the program's own module names — there must be none missing
(`skaiciu_pletiklis` is a known, harmless entry).

## What you get

`dist\SpeakDream\` — an onedir package (NOT onefile: onefile would unpack
several GB into temp on every start):

- `SpeakDream.exe` + `_internal\` (Qt, torch with CUDA DLLs, the icon,
  `AI_CONSULTANT_BRIEF.md`, `prideti_kalba.py`, the Lithuanian phonemizer with
  its dictionaries, the bundled voice files).
- about 4.9 GB, ~18 000 files. The speech models are NOT inside — the program
  downloads them into the Hugging Face cache on the first "Prepare".

## Smoke test after every build (mandatory)

1. Start `dist\SpeakDream\SpeakDream.exe` — the window title must read
   `SpeakDream — …` within a few seconds (check the title, not "process alive").
2. "?" → About, Instructions; switch the interface language in the gear menu.
3. Prepare → Start with a real microphone: one sentence each way.

## Installer

Inno Setup 6, script `_instaliatorius\SpeakDream.iss` (+ our own
`Lithuanian.isl`). Compile from PowerShell into `%TEMP%` and move the result —
Inno Setup cannot write the output onto some drives directly:

```
& "$env:LOCALAPPDATA\Programs\Inno Setup 6\ISCC.exe" "/O$env:TEMP\speakdream_setup" _instaliatorius\SpeakDream.iss
Move-Item "$env:TEMP\speakdream_setup\SpeakDream-1.0.0-setup.exe" dist\
```

About 6 minutes with `lzma2/ultra64`; result about 1.9 GiB. It must stay under
2 GiB — GitHub Releases reject larger files (with `lzma2/normal` it was 2.12 GiB).
Record its SHA-256 before publishing (`Get-FileHash`).

## Voice files

No voice models are committed or bundled. The Lithuanian voice Reginutė is
downloaded from the official Piper catalogue (`rhasspy/piper-voices`,
`lt/lt_LT/reginute1/medium/`) on **Prepare**, like every other voice. Only its
config `vertejas\balsai\lt_LT-reginute1-medium.onnx.json` is ours and ships with
the program: it uses `espeak` phonemes because the program phonemizes Lithuanian
itself (`vertejas\lietuviskai\`) — current piper-tts cannot load the catalogue
config's `phoneme_type: lithuanian`.

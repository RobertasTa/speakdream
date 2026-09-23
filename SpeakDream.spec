# -*- mode: python ; coding: utf-8 -*-
"""SpeakDream (buves VERTEJAS) — PyInstaller receptas (2026-09-19; vardas 2026-09-21).

Statyti IS SIO katalogo ir VISADA per `python -m PyInstaller` (seimos pamoka: venv shim'ai luzta):

    .venv\\Scripts\\python.exe -m PyInstaller SpeakDream.spec --noconfirm

⛔ PRIES LIECIANT — `\\\\NAS-Rtrob\\OKF_Zinios\\OKF_PyInstaller\\paketo_patikros_guard.md`.
Ten astuonios taisykles, ir kiekviena is tikros klaidos, pagautos TIK pakete.

SPRENDIMAI (dalis paveldeta is Diktuokles `Diktuokle.spec`, dviracio neieskom):

  * ONEDIR, ne onefile. onefile kaskart isspakuotu kelis GB i temp — langas atsidarytu
    ne per sekunde, o per minute.
  * UPX isjungtas: UPX + antivirusai = false positive (seimos taisykle).
  * `console=False`. ⛔ Tai reiskia `sys.stdout is None` — spastas, kuris 09-18 gyvai
    nuverte vertimo cikla. Apsauga jau yra `main.py` `_uzkaisk_isvesti()`, ir ji cia
    BUTINA (guard Rule 8).
  * MODELIU PAKETE NERA. Paprika, Whisper medium, du Marian ir Piper balsai sveria kelis
    GB ir gyvena HuggingFace kese; programa juos randa pati.
  * CUDA BIBLIOTEKOS PAKETE YRA (patikslinta 2026-09-19 vakare, PAMATUOTA).
    Senas irasas sake, kad ju nera ir kad `ausys.py` skolinasi is
    `%LOCALAPPDATA%\\Diktuokle\\cuda` — tai pasene: ryta `ausys.py` perejo prie torch,
    o `collect_all("torch")` visas reikiamas DLL atsineca. Suskaiciuota
    `dist\\Vertejas\\_internal\\torch\\lib` (senasis paketo vardas): 37 DLL, tarp ju
    `cublas64_12`, `cublasLt64_12` ir visas `cudnn*_9` rinkinys — tiek pat, kiek venv'e.
    ⚠️ NEPATIKRINTA PAKETE: ar `_cuda_katalogai()` tuos DLL RANDA, kai `find_spec('torch')`
    sukasi PyInstaller viduje. Diske jie guli; ar kelias nurodo teisingai — atsakys tik
    gyvas testas. Iki tol „savarankiska" nesakom (guard: nesakyk „veikia", kol nepamatei
    pakete). Krentant lieka `ausys.py` bandomasis inference — kritimas i CPU.
  * ⚠️ `ausys.PAPRIKA_VIETINIS` yra kietas kelias `D:\\_Balsas Lietuviksas\\...`. Roberto
    kompiuteryje jis yra; svetimame krenta i HuggingFace kopija. Viesinant perziureti.
  * Ikona — `vertejas/SpeakDream.ico`, is Roberto GPT paveikslo, kirpta pagal geometrija
    (`_ikona\\kirpk_kvadrata.py`, 2026-09-21). Paketo katalogas ir exe — `SpeakDream`.
"""
from PyInstaller.utils.hooks import collect_all, collect_submodules

KATALOGAS = "vertejas"

# torch itraukiamas VISAS: ji tempia `transformers` Marian modeliai (vertimas.py).
# ⚠️ Cia jis GEROKAI storesnis nei Diktuokleje (ten 0,53 GB): sioje aplinkoje tai CUDA
# versija, diske ~4,2 GB. Paketas bus atitinkamai didelis — pamatuota, ne speta.
torch_d, torch_b, torch_h = collect_all("torch")
tr_d, tr_b, tr_h = collect_all("transformers")
ct2_d, ct2_b, ct2_h = collect_all("ctranslate2")
ort_d, ort_b, ort_h = collect_all("onnxruntime")
fw_d, fw_b, fw_h = collect_all("faster_whisper")
hf_d, hf_b, hf_h = collect_all("huggingface_hub")
sp_d, sp_b, sp_h = collect_all("sentencepiece")
piper_d, piper_b, piper_h = collect_all("piper")
sd_d, sd_b, sd_h = collect_all("sounddevice")
sf_d, sf_b, sf_h = collect_all("soundfile")

a = Analysis(
    [f"{KATALOGAS}/main.py"],
    pathex=[KATALOGAS],
    binaries=(torch_b + tr_b + ct2_b + ort_b + fw_b + hf_b + sp_b + piper_b
              + sd_b + sf_b),
    datas=[
        (f"{KATALOGAS}/SpeakDream.ico", "."),
        # ⭐ Konsultanto tiesos failas ir kalbų patikros įrankis. Jie reikalingi ne programai,
        # o ŽMOGUI: „?" → „Neradote atsakymo? Klauskite DI" atveria pirmąjį, o antrasis
        # neleidžia dirbtiniam intelektui prasimanyti modelių vardų.
        ("AI_CONSULTANT_BRIEF.md", "."),
        ("prideti_kalba.py", "."),
        # Lietuviskas fonemizatorius su zodynais — BE ju Ingute kalbetu ne taip, kaip
        # ismatuota (09-16 pamoka: truko `lt_raides.tsv` ir `lt_kreipiniai.tsv`).
        (f"{KATALOGAS}/lietuviskai", "lietuviskai"),
        # ⛔ 2026-09-19: SITOS EILUTES TRUKO, ir 13:41 surinkimas isejo BE Ingutes
        # balso (`lt_LT-ingute-medium.onnx`, 63,5 MB). Simptomas: „Paruosti darbui"
        # krinta ties ketvirtu zingsniu (balsai), o IS SALTINIU viskas praeina —
        # nes ten failas vietoje. Tiksliai guard'o Rule esme: testuok PAKETA.
        # 2026-09-23 v1.0.0: tik Reginutes konfigas (modelis — is Piper katalogo). Ingutes
        # .onnx NEDEDAM, kol ji nepublikuota; grazinant — vel visas `balsai` katalogas.
        (f"{KATALOGAS}/balsai/lt_LT-reginute1-medium.onnx.json", "balsai"),
    ] + torch_d + tr_d + ct2_d + ort_d + fw_d + hf_d + sp_d + piper_d + sd_d + sf_d,
    hiddenimports=(
        # Musu paciu moduliai. Kalbu zodynai kraunami per `__import__` (kalba.py),
        # tad PyInstaller ju NERANDA — juos butina isvardyti, kitaip pakete sasaja
        # butu tik lietuviska, ir tai nesimatytu iki pirmo paleidimo svetima kalba.
        ["kalba", "kalba_en", "kalba_ru", "kalba_de",
         "ausys", "balsas", "frazes", "garsas", "garso_irasas",
         "langas", "nustatymai", "skyryba", "stenograma", "variklis", "vertimas"]
        + torch_h + tr_h + ct2_h + ort_h + fw_h + hf_h + sp_h + piper_h + sd_h + sf_h
        + collect_submodules("PyQt6")
    ),
    hookspath=[],
    runtime_hooks=[],
    # ⛔ `excludes` ismeta ir tai, ka importuoji virsuje (guard Rule 1): pries kiekviena
    # nauja varda cia — patikrink, ar jo nera musu importuose.
    excludes=["tkinter", "matplotlib", "pandas", "PIL", "IPython", "notebook", "pytest"],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="SpeakDream",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=f"{KATALOGAS}/SpeakDream.ico",
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name="SpeakDream",
)

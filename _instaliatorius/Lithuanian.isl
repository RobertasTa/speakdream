; *** Inno Setup 6 lietuviski pranesimai ***
;
; Kodel sis failas apskritai egzistuoja: Inno Setup pagrindiniame rinkinyje
; lietuviu kalbos NERA, ir neoficialiame (38 kalbos) taip pat - patikrinta
; 2026-09-11 per jrsoftware/issrc repo API. Lietuviska dovana, kurios diegimas
; nemoka lietuviskai, yra puse dovanos, todel isverteme patys.
;
; Terminai suderinti su Windows lietuviska sasaja: Setup -> "Diegimas",
; Wizard -> "vediklis", Folder -> "aplankas", Shortcut -> "nuoroda",
; Browse -> "Narsyti", Uninstall -> "Salinimas".
;
; & zymi spartuji klavisa - VISADA islaikomas.
; %n = nauja eilute, %1 %2 %3 = Inno Setup istatomos reiksmes - NEVERSTI.
;
; Vertimas: Robertas Tarasevicius ir Claude (Anthropic AI), 2026.
; Laisvai naudojamas ir platinamas.

[LangOptions]
LanguageName=Lietuvi<0173>
LanguageID=$0427
LanguageCodePage=1257

[Messages]

; *** Programos antrastes
SetupAppTitle=Diegimas
SetupWindowTitle=Diegimas – %1
UninstallAppTitle=Šalinimas
UninstallAppFullTitle=%1 šalinimas

; *** Bendri
InformationTitle=Informacija
ConfirmTitle=Patvirtinimas
ErrorTitle=Klaida

; *** SetupLdr pranesimai
SetupLdrStartupMessage=Bus įdiegta %1. Ar norite tęsti?
LdrCannotCreateTemp=Nepavyko sukurti laikinojo failo. Diegimas nutrauktas
LdrCannotExecTemp=Nepavyko paleisti failo laikinajame aplanke. Diegimas nutrauktas
HelpTextNote=

; *** Paleidimo klaidos
LastErrorMessage=%1.%n%nKlaida %2: %3
SetupFileMissing=Diegimo aplanke trūksta failo %1. Ištaisykite problemą arba parsisiųskite programą iš naujo.
SetupFileCorrupt=Diegimo failai sugadinti. Parsisiųskite programą iš naujo.
SetupFileCorruptOrWrongVer=Diegimo failai sugadinti arba netinka šiai diegimo programos versijai. Ištaisykite problemą arba parsisiųskite programą iš naujo.
InvalidParameter=Komandinėje eilutėje perduotas netinkamas parametras:%n%n%1
SetupAlreadyRunning=Diegimas jau vykdomas.
WindowsVersionNotSupported=Ši programa nepalaiko jūsų kompiuteryje veikiančios Windows versijos.
WindowsServicePackRequired=Šiai programai reikia %1 Service Pack %2 arba naujesnio.
NotOnThisPlatform=Ši programa neveiks %1 sistemoje.
OnlyOnThisPlatform=Šią programą galima paleisti tik %1 sistemoje.
OnlyOnTheseArchitectures=Šią programą galima įdiegti tik tose Windows versijose, kurios skirtos šioms procesorių architektūroms:%n%n%1
WinVersionTooLowError=Šiai programai reikia %1 %2 arba naujesnės versijos.
WinVersionTooHighError=Šios programos negalima įdiegti %1 %2 ar naujesnėje versijoje.
AdminPrivilegesRequired=Norint įdiegti šią programą, reikia prisijungti administratoriaus teisėmis.
PowerUserPrivilegesRequired=Norint įdiegti šią programą, reikia prisijungti administratoriaus teisėmis arba būti Power Users grupės nariu.
SetupAppRunningError=Diegimo programa aptiko, kad %1 šiuo metu veikia.%n%nUždarykite visus jos langus ir spustelėkite „Gerai“, arba „Atšaukti“, kad išeitumėte.
UninstallAppRunningError=Šalinimo programa aptiko, kad %1 šiuo metu veikia.%n%nUždarykite visus jos langus ir spustelėkite „Gerai“, arba „Atšaukti“, kad išeitumėte.

; *** Klausimai pradzioje
PrivilegesRequiredOverrideTitle=Diegimo būdo pasirinkimas
PrivilegesRequiredOverrideInstruction=Pasirinkite diegimo būdą
PrivilegesRequiredOverrideText1=%1 galima įdiegti visiems naudotojams (reikia administratoriaus teisių) arba tik jums.
PrivilegesRequiredOverrideText2=%1 galima įdiegti tik jums arba visiems naudotojams (reikia administratoriaus teisių).
PrivilegesRequiredOverrideAllUsers=Diegti &visiems naudotojams
PrivilegesRequiredOverrideAllUsersRecommended=Diegti &visiems naudotojams (rekomenduojama)
PrivilegesRequiredOverrideCurrentUser=Diegti tik &man
PrivilegesRequiredOverrideCurrentUserRecommended=Diegti tik &man (rekomenduojama)

; *** Ivairios klaidos
ErrorCreatingDir=Nepavyko sukurti aplanko „%1“
ErrorTooManyFilesInDir=Nepavyko sukurti failo aplanke „%1“, nes jame per daug failų

; *** Bendri diegimo pranesimai
ExitSetupTitle=Išeiti iš diegimo
ExitSetupMessage=Diegimas nebaigtas. Jei dabar išeisite, programa nebus įdiegta.%n%nDiegimą galėsite paleisti kitą kartą.%n%nIšeiti iš diegimo?
AboutSetupMenuItem=&Apie diegimo programą...
AboutSetupTitle=Apie diegimo programą
AboutSetupMessage=%1 %2 versija%n%3%n%n%1 svetainė:%n%4
AboutSetupNote=
TranslatorNote=Vertimas: Robertas Tarasevičius ir Claude (Anthropic AI)

; *** Mygtukai
ButtonBack=< At&gal
ButtonNext=&Toliau >
ButtonInstall=Į&diegti
ButtonOK=Gerai
ButtonCancel=Atšaukti
ButtonYes=&Taip
ButtonYesToAll=Taip &visiems
ButtonNo=&Ne
ButtonNoToAll=N&e visiems
ButtonFinish=&Baigti
ButtonBrowse=&Naršyti...
ButtonWizardBrowse=Na&ršyti...
ButtonNewFolder=&Naujas aplankas

; *** Kalbos pasirinkimo langas
SelectLanguageTitle=Diegimo kalbos pasirinkimas
SelectLanguageLabel=Pasirinkite kalbą, kuria vyks diegimas.

; *** Bendras vediklio tekstas
ClickNext=Spustelėkite „Toliau“, jei norite tęsti, arba „Atšaukti“, jei norite išeiti.
BeveledLabel=
BrowseDialogTitle=Aplanko pasirinkimas
BrowseDialogLabel=Pasirinkite aplanką iš sąrašo ir spustelėkite „Gerai“.
NewFolderName=Naujas aplankas

; *** „Sveiki“ puslapis
WelcomeLabel1=Sveiki! Tai [name] diegimo vediklis
WelcomeLabel2=Į jūsų kompiuterį bus įdiegta [name/ver].%n%nPrieš tęsiant patariama uždaryti kitas programas.

; *** Slaptazodzio puslapis
WizardPassword=Slaptažodis
PasswordLabel1=Šis diegimas apsaugotas slaptažodžiu.
PasswordLabel3=Įveskite slaptažodį ir spustelėkite „Toliau“. Slaptažodyje skiriamos didžiosios ir mažosios raidės.
PasswordEditLabel=&Slaptažodis:
IncorrectPassword=Įvestas slaptažodis neteisingas. Bandykite dar kartą.

; *** Licencijos puslapis
WizardLicense=Licencinė sutartis
LicenseLabel=Prieš tęsdami perskaitykite šią svarbią informaciją.
LicenseLabel3=Perskaitykite licencinę sutartį. Norėdami tęsti diegimą, turite sutikti su jos sąlygomis.
LicenseAccepted=&Sutinku su sutarties sąlygomis
LicenseNotAccepted=&Nesutinku su sutarties sąlygomis

; *** Informaciniai puslapiai
WizardInfoBefore=Informacija
InfoBeforeLabel=Prieš tęsdami perskaitykite šią svarbią informaciją.
InfoBeforeClickLabel=Kai būsite pasiruošę tęsti diegimą, spustelėkite „Toliau“.
WizardInfoAfter=Informacija
InfoAfterLabel=Prieš tęsdami perskaitykite šią svarbią informaciją.
InfoAfterClickLabel=Kai būsite pasiruošę tęsti diegimą, spustelėkite „Toliau“.

; *** Naudotojo informacija
WizardUserInfo=Naudotojo informacija
UserInfoDesc=Įveskite savo duomenis.
UserInfoName=&Naudotojo vardas:
UserInfoOrg=&Organizacija:
UserInfoSerial=&Serijos numeris:
UserInfoNameRequired=Turite įvesti vardą.

; *** Diegimo vietos pasirinkimas
WizardSelectDir=Diegimo vietos pasirinkimas
SelectDirDesc=Kur įdiegti [name]?
SelectDirLabel3=[name] bus įdiegta į šį aplanką.
SelectDirBrowseLabel=Jei norite tęsti, spustelėkite „Toliau“. Jei norite pasirinkti kitą aplanką, spustelėkite „Naršyti“.
DiskSpaceGBLabel=Reikia bent [gb] GB laisvos vietos diske.
DiskSpaceMBLabel=Reikia bent [mb] MB laisvos vietos diske.
CannotInstallToNetworkDrive=Į tinklo diską įdiegti negalima.
CannotInstallToUNCPath=Į UNC kelią įdiegti negalima.
InvalidPath=Turite įvesti pilną kelią su disko raide, pavyzdžiui:%n%nC:\APP%n%narba UNC kelią:%n%n\\serveris\bendrinys
InvalidDrive=Pasirinkto disko ar bendrinio aplanko nėra arba jis nepasiekiamas. Pasirinkite kitą.
DiskSpaceWarningTitle=Per mažai vietos diske
DiskSpaceWarning=Diegimui reikia bent %1 KB laisvos vietos, o pasirinktame diske yra tik %2 KB.%n%nAr vis tiek tęsti?
DirNameTooLong=Aplanko vardas arba kelias per ilgas.
InvalidDirName=Netinkamas aplanko vardas.
BadDirName32=Aplankų varduose negali būti šių ženklų:%n%n%1
DirExistsTitle=Aplankas jau yra
DirExists=Aplankas%n%n%1%n%njau yra. Ar vis tiek diegti į jį?
DirDoesntExistTitle=Aplanko nėra
DirDoesntExist=Aplanko%n%n%1%n%nnėra. Ar sukurti jį?

; *** Komponentu pasirinkimas
WizardSelectComponents=Komponentų pasirinkimas
SelectComponentsDesc=Kuriuos komponentus įdiegti?
SelectComponentsLabel2=Pažymėkite komponentus, kuriuos norite įdiegti, ir nuimkite varneles nuo tų, kurių nenorite. Kai būsite pasiruošę, spustelėkite „Toliau“.
FullInstallation=Pilnas diegimas
CompactInstallation=Kompaktiškas diegimas
CustomInstallation=Pasirinktinis diegimas
NoUninstallWarningTitle=Komponentai jau yra
NoUninstallWarning=Aptikta, kad šie komponentai jūsų kompiuteryje jau įdiegti:%n%n%1%n%nNuėmus nuo jų varneles, jie nebus pašalinti.%n%nAr vis tiek tęsti?
ComponentSize1=%1 KB
ComponentSize2=%1 MB
ComponentsDiskSpaceGBLabel=Dabartiniam pasirinkimui reikia bent [gb] GB vietos diske.
ComponentsDiskSpaceMBLabel=Dabartiniam pasirinkimui reikia bent [mb] MB vietos diske.

; *** Papildomos uzduotys
WizardSelectTasks=Papildomos užduotys
SelectTasksDesc=Kokias papildomas užduotis atlikti?
SelectTasksLabel2=Pažymėkite papildomas užduotis, kurias reikia atlikti diegiant [name], ir spustelėkite „Toliau“.

; *** Pradzios meniu aplankas
WizardSelectProgramGroup=Pradžios meniu aplankas
SelectStartMenuFolderDesc=Kur sukurti programos nuorodas?
SelectStartMenuFolderLabel3=Programos nuorodos bus sukurtos šiame Pradžios meniu aplanke.
SelectStartMenuFolderBrowseLabel=Jei norite tęsti, spustelėkite „Toliau“. Jei norite pasirinkti kitą aplanką, spustelėkite „Naršyti“.
MustEnterGroupName=Turite įvesti aplanko vardą.
GroupNameTooLong=Aplanko vardas arba kelias per ilgas.
InvalidGroupName=Netinkamas aplanko vardas.
BadGroupName=Aplanko varde negali būti šių ženklų:%n%n%1
NoProgramGroupCheck2=&Nekurti Pradžios meniu aplanko

; *** Pasiruose diegti
WizardReady=Pasiruošta diegti
ReadyLabel1=[name] pasiruošta diegti į jūsų kompiuterį.
ReadyLabel2a=Spustelėkite „Įdiegti“, jei norite tęsti, arba „Atgal“, jei norite peržiūrėti ar pakeisti nustatymus.
ReadyLabel2b=Spustelėkite „Įdiegti“, jei norite tęsti.
ReadyMemoUserInfo=Naudotojo duomenys:
ReadyMemoDir=Diegimo vieta:
ReadyMemoType=Diegimo tipas:
ReadyMemoComponents=Pasirinkti komponentai:
ReadyMemoGroup=Pradžios meniu aplankas:
ReadyMemoTasks=Papildomos užduotys:

; *** Parsisiuntimas
DownloadingLabel2=Siunčiami failai...
ButtonStopDownload=&Stabdyti siuntimą
StopDownload=Ar tikrai norite sustabdyti siuntimą?
ErrorDownloadAborted=Siuntimas nutrauktas
ErrorDownloadFailed=Siuntimas nepavyko: %1 %2
ErrorDownloadSizeFailed=Nepavyko sužinoti dydžio: %1 %2
ErrorProgress=Netinkama eiga: %1 iš %2
ErrorFileSize=Netinkamas failo dydis: tikėtasi %1, rasta %2

; *** Isskleidimas
ExtractingLabel=Išskleidžiami failai...
ButtonStopExtraction=&Stabdyti išskleidimą
StopExtraction=Ar tikrai norite sustabdyti išskleidimą?
ErrorExtractionAborted=Išskleidimas nutrauktas
ErrorExtractionFailed=Išskleidimas nepavyko: %1

; *** Archyvo klaidos
ArchiveIncorrectPassword=Neteisingas slaptažodis
ArchiveIsCorrupted=Archyvas sugadintas
ArchiveUnsupportedFormat=Nepalaikomas archyvo formatas

; *** Ruosiamasi diegti
WizardPreparing=Ruošiamasi diegti
PreparingDesc=Ruošiamasi įdiegti [name] į jūsų kompiuterį.
PreviousInstallNotCompleted=Ankstesnės programos diegimas arba šalinimas nebuvo baigtas. Kad jis būtų užbaigtas, kompiuterį reikia paleisti iš naujo.%n%nPaleidę kompiuterį iš naujo, paleiskite šį diegimą dar kartą, kad užbaigtumėte [name] diegimą.
CannotContinue=Diegti toliau negalima. Spustelėkite „Atšaukti“, kad išeitumėte.
ApplicationsFound=Šios programos naudoja failus, kuriuos reikia atnaujinti. Patariama leisti diegimo programai jas automatiškai uždaryti.
ApplicationsFound2=Šios programos naudoja failus, kuriuos reikia atnaujinti. Patariama leisti diegimo programai jas automatiškai uždaryti. Baigus diegimą jos bus paleistos iš naujo.
CloseApplications=&Automatiškai uždaryti programas
DontCloseApplications=&Neuždaryti programų
ErrorCloseApplications=Nepavyko automatiškai uždaryti visų programų. Prieš tęsiant patariama pačiam uždaryti visas programas, naudojančias atnaujinamus failus.
PrepareToInstallNeedsRestart=Kompiuterį reikia paleisti iš naujo. Tai padarę, paleiskite diegimą dar kartą, kad užbaigtumėte [name] diegimą.%n%nAr paleisti iš naujo dabar?

; *** Diegiama
WizardInstalling=Diegiama
InstallingLabel=Palaukite, kol [name] bus įdiegta į jūsų kompiuterį.

; *** Diegimas baigtas
FinishedHeadingLabel=[name] diegimas baigtas
FinishedLabelNoIcons=[name] įdiegta į jūsų kompiuterį.
FinishedLabel=[name] įdiegta į jūsų kompiuterį. Programą galite paleisti per sukurtas nuorodas.
ClickFinish=Spustelėkite „Baigti“, kad išeitumėte.
FinishedRestartLabel=Kad [name] diegimas būtų užbaigtas, kompiuterį reikia paleisti iš naujo. Ar paleisti dabar?
FinishedRestartMessage=Kad [name] diegimas būtų užbaigtas, kompiuterį reikia paleisti iš naujo.%n%nAr paleisti dabar?
ShowReadmeCheck=Taip, noriu perskaityti README failą
YesRadio=&Taip, paleisti kompiuterį iš naujo dabar
NoRadio=&Ne, paleisiu iš naujo vėliau
RunEntryExec=Paleisti %1
RunEntryShellExec=Peržiūrėti %1

; *** Kito disko prasymas
ChangeDiskTitle=Reikia kito disko
SelectDiskLabel2=Įdėkite diską %1 ir spustelėkite „Gerai“.%n%nJei šio disko failai yra kitame aplanke, nei rodoma žemiau, įveskite teisingą kelią arba spustelėkite „Naršyti“.
PathLabel=&Kelias:
FileNotInDir2=Failo „%1“ nepavyko rasti aplanke „%2“. Įdėkite teisingą diską arba pasirinkite kitą aplanką.
SelectDirectoryLabel=Nurodykite, kur yra kitas diskas.

; *** Diegimo eigos pranesimai
SetupAborted=Diegimas nebaigtas.%n%nIštaisykite problemą ir paleiskite diegimą iš naujo.
AbortRetryIgnoreSelectAction=Pasirinkite veiksmą
AbortRetryIgnoreRetry=&Bandyti dar kartą
AbortRetryIgnoreIgnore=&Nepaisyti klaidos ir tęsti
AbortRetryIgnoreCancel=Atšaukti diegimą
RetryCancelSelectAction=Pasirinkite veiksmą
RetryCancelRetry=&Bandyti dar kartą
RetryCancelCancel=Atšaukti

; *** Busenos pranesimai
StatusClosingApplications=Uždaromos programos...
StatusCreateDirs=Kuriami aplankai...
StatusExtractFiles=Išskleidžiami failai...
StatusDownloadFiles=Siunčiami failai...
StatusCreateIcons=Kuriamos nuorodos...
StatusCreateIniEntries=Kuriami INI įrašai...
StatusCreateRegistryEntries=Kuriami registro įrašai...
StatusRegisterFiles=Registruojami failai...
StatusSavingUninstall=Įrašoma šalinimo informacija...
StatusRunProgram=Baigiamas diegimas...
StatusRestartingApplications=Programos paleidžiamos iš naujo...
StatusRollback=Pakeitimai atšaukiami...

; *** Ivairios klaidos
ErrorInternal2=Vidinė klaida: %1
ErrorFunctionFailedNoCode=%1 nepavyko
ErrorFunctionFailed=%1 nepavyko; kodas %2
ErrorFunctionFailedWithMessage=%1 nepavyko; kodas %2.%n%3
ErrorExecutingProgram=Nepavyko paleisti failo:%n%1

; *** Registro klaidos
ErrorRegOpenKey=Klaida atveriant registro raktą:%n%1\%2
ErrorRegCreateKey=Klaida kuriant registro raktą:%n%1\%2
ErrorRegWriteKey=Klaida rašant į registro raktą:%n%1\%2

; *** INI klaidos
ErrorIniEntry=Klaida kuriant INI įrašą faile „%1“.

; *** Failu kopijavimo klaidos
FileAbortRetryIgnoreSkipNotRecommended=&Praleisti šį failą (nerekomenduojama)
FileAbortRetryIgnoreIgnoreNotRecommended=&Nepaisyti klaidos ir tęsti (nerekomenduojama)
SourceIsCorrupted=Šaltinio failas sugadintas
SourceDoesntExist=Šaltinio failo „%1“ nėra
SourceVerificationFailed=Nepavyko patikrinti šaltinio failo: %1
VerificationSignatureDoesntExist=Parašo failo „%1“ nėra
VerificationSignatureInvalid=Parašo failas „%1“ netinkamas
VerificationKeyNotFound=Parašo faile „%1“ naudojamas nežinomas raktas
VerificationFileNameIncorrect=Neteisingas failo vardas
VerificationFileTagIncorrect=Neteisinga failo žymė
VerificationFileSizeIncorrect=Neteisingas failo dydis
VerificationFileHashIncorrect=Neteisinga failo maiša
ExistingFileReadOnly2=Esamo failo nepavyko pakeisti, nes jis pažymėtas kaip tik skaitomas.
ExistingFileReadOnlyRetry=&Nuimti „tik skaityti“ požymį ir bandyti dar kartą
ExistingFileReadOnlyKeepExisting=&Palikti esamą failą
ErrorReadingExistingDest=Bandant skaityti esamą failą įvyko klaida:
FileExistsSelectAction=Pasirinkite veiksmą
FileExists2=Failas jau yra.
FileExistsOverwriteExisting=&Perrašyti esamą failą
FileExistsKeepExisting=&Palikti esamą failą
FileExistsOverwriteOrKeepAll=&Taip elgtis ir su kitais tokiais atvejais
ExistingFileNewerSelectAction=Pasirinkite veiksmą
ExistingFileNewer2=Esamas failas naujesnis už tą, kurį bandoma įdiegti.
ExistingFileNewerOverwriteExisting=&Perrašyti esamą failą
ExistingFileNewerKeepExisting=&Palikti esamą failą (rekomenduojama)
ExistingFileNewerOverwriteOrKeepAll=&Taip elgtis ir su kitais tokiais atvejais
ErrorChangingAttr=Bandant pakeisti esamo failo požymius įvyko klaida:
ErrorCreatingTemp=Bandant sukurti failą paskirties aplanke įvyko klaida:
ErrorReadingSource=Bandant skaityti šaltinio failą įvyko klaida:
ErrorCopying=Bandant kopijuoti failą įvyko klaida:
ErrorDownloading=Bandant parsisiųsti failą įvyko klaida:
ErrorExtracting=Bandant išskleisti archyvą įvyko klaida:
ErrorReplacingExistingFile=Bandant pakeisti esamą failą įvyko klaida:
ErrorRestartReplace=RestartReplace nepavyko:
ErrorRenamingTemp=Bandant pervadinti failą paskirties aplanke įvyko klaida:
ErrorRegisterServer=Nepavyko užregistruoti DLL/OCX: %1
ErrorRegSvr32Failed=RegSvr32 nepavyko; išėjimo kodas %1
ErrorRegisterTypeLib=Nepavyko užregistruoti tipų bibliotekos: %1

; *** Salinimo vardo zymos
UninstallDisplayNameMark=%1 (%2)
UninstallDisplayNameMarks=%1 (%2, %3)
UninstallDisplayNameMark32Bit=32 bitų
UninstallDisplayNameMark64Bit=64 bitų
UninstallDisplayNameMarkAllUsers=Visi naudotojai
UninstallDisplayNameMarkCurrentUser=Dabartinis naudotojas

; *** Klaidos po diegimo
ErrorOpeningReadme=Bandant atverti README failą įvyko klaida.
ErrorRestartingComputer=Nepavyko paleisti kompiuterio iš naujo. Padarykite tai patys.

; *** Salinimo pranesimai
UninstallNotFound=Failo „%1“ nėra. Pašalinti negalima.
UninstallOpenError=Failo „%1“ nepavyko atverti. Pašalinti negalima
UninstallUnsupportedVer=Šalinimo žurnalo failas „%1“ yra tokio formato, kurio ši šalinimo programos versija neatpažįsta. Pašalinti negalima
UninstallUnknownEntry=Šalinimo žurnale rastas nežinomas įrašas (%1)
ConfirmUninstall=Ar tikrai norite visiškai pašalinti %1 ir visus jos komponentus?
UninstallOnlyOnWin64=Šį diegimą galima pašalinti tik 64 bitų Windows sistemoje.
OnlyAdminCanUninstall=Šį diegimą gali pašalinti tik administratoriaus teises turintis naudotojas.
UninstallStatusLabel=Palaukite, kol %1 bus pašalinta iš jūsų kompiuterio.
UninstalledAll=%1 sėkmingai pašalinta iš jūsų kompiuterio.
UninstalledMost=%1 pašalinta.%n%nKai kurių elementų pašalinti nepavyko. Juos galite pašalinti patys.
UninstalledAndNeedsRestart=Kad %1 šalinimas būtų užbaigtas, kompiuterį reikia paleisti iš naujo.%n%nAr paleisti dabar?
UninstallDataCorrupted=Failas „%1“ sugadintas. Pašalinti negalima

; *** Salinimo eiga
ConfirmDeleteSharedFileTitle=Šalinti bendrai naudojamą failą?
ConfirmDeleteSharedFile2=Sistema nurodo, kad šio bendrai naudojamo failo nebenaudoja nė viena programa. Ar pašalinti šį failą?%n%nJei kuri nors programa jį vis dėlto naudoja, pašalinus ji gali veikti netinkamai. Jei abejojate, pasirinkite „Ne“. Paliktas failas jokios žalos nepadarys.
SharedFileNameLabel=Failo vardas:
SharedFileLocationLabel=Vieta:
WizardUninstalling=Šalinimo eiga
StatusUninstalling=Šalinama %1...

; *** Isjungimo blokavimo priezastys
ShutdownBlockReasonInstallingApp=Diegiama %1.
ShutdownBlockReasonUninstallingApp=Šalinama %1.

[CustomMessages]

NameAndVersion=%1 %2 versija
AdditionalIcons=Papildomos nuorodos:
CreateDesktopIcon=Sukurti nuorodą &darbalaukyje
CreateQuickLaunchIcon=Sukurti nuorodą &sparčiosios paleisties juostoje
ProgramOnTheWeb=%1 internete
UninstallProgram=Pašalinti %1
LaunchProgram=Paleisti %1
AssocFileExtension=&Susieti %1 su %2 failų tipu
AssocingFileExtension=%1 siejama su %2 failų tipu...
AutoStartProgramGroupDescription=Paleidimas:
AutoStartProgram=Automatiškai paleisti %1
AddonHostProgramNotFound=%1 nerasta jūsų pasirinktame aplanke.%n%nAr vis tiek tęsti?

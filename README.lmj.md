**[漢字版說明書](README.md)**

# Sìn Bōng Ài + Tâioânjī

Che sī chi̍t ê khah sin ê [FHL Taigi-Hakka IME 信望愛台語客語輸入法](https://taigi.fhl.net/TaigiIME/) chuliāukhò͘. Chuliāukhò͘ ū hoattō͘ ti̍tchiap phah Tâioânjī, koh ū siukái kài chē Hànjī ê chhògō͘.

**Chòe sin pánpún (2023-01-08): [FHL_Taioanji-v0.0.1.zip](https://github.com/aiongg/fhl-toj/releases/download/v0.0.1/FHL_Taioanji-v0.0.1.zip)**

Kòekhì ê pánpún:

- Chòe sin pánpún: [FHL_Taioanji-v0.0.0-alpha1.zip](https://github.com/aiongg/fhl-toj/releases/download/v0.0.0-alpha1/FHL_Taioanji-v0.0.0-alpha1.zip)

---

## Tâioânjī

Tâioânjī (TOJ) sī bô liânjīhû ê Pe̍hōejī.

## Windows

### Anchng (Install)

Chù:

- Lí ê tiānnáu suiàu anchng [Sìnbōngài Tâigí Khehgí Suji̍phoat](https://taigi.fhl.net/TaigiIME/).
- Nā thâu chi̍t kái beh anchng Tâioànjī chuliāukhò͘, bián têngkhui tiānnáu.
- Nā beh anchng sin pán, chhiáⁿ seng têngsin khui ki.

**1** Tángló͘ siōng sin ê `FHL_Taioanji-vX.Y.Z.zip`.

**2.** Chhi̍h `解壓縮 (Extract)`:

<img src="soatbeng/01-download.png" width="50%" height="50%">

**3.** Chhi̍h `全部解壓縮 (Extract all)`:

<img src="soatbeng/02-extract.png" width="50%" height="50%">

**4.** Chhi̍h `解壓縮 (Extract)` kàu chi̍t ê Folder:

<img src="soatbeng/03-extract.png" width="50%" height="50%">

**5.** Chhi̍h Folder phah khui:

<img src="soatbeng/04-open.png" width="50%" height="50%">

**6.** Chhi̍h `windows_install.bat` (chhi̍h lo̍h khì bô hoánèng sī chèngsiông)

<img src="soatbeng/05-install.png" width="50%" height="50%">

Ánne to̍h ē sái khai-sí sú-iōng. Nā iáu bô Tâioânjī, chhiáⁿ têng khui tiānnáu koh chhì chi̍t pái.

Ūi tio̍h phah Tâioânjī khah līpiān, suji̍phoat ê siattēng chò 1-9 soán Hànjī:

<img src="soatbeng/06-settings.png" width="50%" height="50%">

---

### Santû (Uninstall)

**1.** Têngsin khui ki. (Oânsêng santû chìnchêng, m̄ thang chhiat ōaⁿ FHL suji̍phoat.)
   
**2.** Chhi̍h `windows_uninstall.bat`

---

### Nā ū tú tio̍h būntê

Nā bô hoattō͘ chng á sī san, chhiáⁿ chhiútōng kā `TalmageOverride.db` chng/san. Ē kì tit ta̍k pái **chng/san chìnchêng ài têngsin khui ki**.

Chhiáⁿ chhiútōng phah khui suji̍phoat ê Folder, kā chuliāu khò͘ santiāu, koh têngkhui tiānnáu to̍h ē sái tit.

#### 1. Phah khui suji̍phoat ê Folder

Phah khui suji̍phoat ê Folder ū 2 ê hoattō͘:

1 (A). Tī `檔案總管 (explorer)` ê Folder Path téngbīn phah:

```
%APPDATA%\FHL TaigiIME\IMTalmage
```

<img src="soatbeng/alt01-manual.png" width="50%" height="50%">

**á sī**

1 (B). Chhōe `cmd` ka phah khui:

<img src="soatbeng/alt02-cmd.png" width="50%" height="50%">

Kā `explorer.exe` phah khui, tio̍h chhiú phah: `explorer.exe "%APPDATA%\FHL TaigiIME\IMTalmage"`

<img src="soatbeng/alt03-open.png" width="50%" height="50%">

#### 2. Kā chuliāu khò͘ santiāu

San `TalmageOverride.db`:

<img src="soatbeng/alt04-override.png" width="50%" height="50%">

---

## Phōngkó (Mac)

Chhiáⁿ tángló͘ kah Windows kāngkhoán ê `FHL_Taioanji.zip`, koh unzip kàu chi̍t ê Folder.

Iōng Finder chhōe `~/Library/Application Support/FHL TaigiIME/IMTalmage`. Kā `TalmageOverride.db` hē tī `IMTalmage`, to̍h ē sái tit súiōng.

Nā beh san tiāu, kā `TalmageOverride.db` san tiāu to̍h ē sái tit.

## Developers

There's just a simple build script in `src/build.py`. You will need a CSV file with 4 columns:

```
1. id - a number
2. original lomaji - fully hyphenated as in the original FHL database
3. taioanji - with hyphens removed (either joined or spaced) as required
4. hanji - desired hanji output

Run the script and copy the output SQLite database `TalmageOverride.db` to the appropriate folder for your platform. To uninstall or modify, you must log out and log back in (or reboot) first.
# Sìn Bōng Ài + Tâioânjī

**Iáu bô hoattō͘ tángló͘, bo̍kchiân teh siá soatbêngsu niâ!!!!!**

v0.0.0-alpha1

Che sī chi̍t ê khah sin ê [FHL Taigi-Hakka IME 信望愛台語客語輸入法](https://taigi.fhl.net/TaigiIME/) chuliāukhò͘. Chuliāukhò͘ ū hoattō͘ ti̍tchiap phah Tâioânjī, koh ū siukái kài chē Hànjī ê chhògō͘.

## Tâioânjī

(Tâioânjī ê kuitēng / soatbêng)

## Windows

### Chng (Install)

**1** Tángló͘ siōng sin ê `FHL_Taioanji.zip` (*iáu bô bāngliān*).

**2.** Chhi̍h `Extract`:

<img src="soatbeng/01-download.png" width="50%" height="50%">

**3.** Chhi̍h `Extract all`:

<img src="soatbeng/02-extract.png" width="50%" height="50%">

**4.** Chhi̍h `Extract` kàu chi̍t ê Folder:

<img src="soatbeng/03-extract.png" width="50%" height="50%">

**5.** Chhi̍h Folder phah khui:

<img src="soatbeng/04-open.png" width="50%" height="50%">

**6.** Chhi̍h `windows_install.bat` (chhi̍h lo̍h khì bô hoánèng sī chèngsiông)

<img src="soatbeng/05-install.png" width="50%" height="50%">

Án-ne tō ē sái khai-sí sú-iōng. Nā iáu bô Tâioânjī, chhiáⁿ têng khui tiānnáu koh chhì chi̍t pái.

---

### Santû (Uninstall)

**1.** Têngkhui tiānnáu. (Oânsêng santû chìnchêng, bô ài chhiat ōaⁿ FHL suji̍phoat.)
   
**2.** Chhi̍h `windows_uninstall.bat`

---

### Nā tú tio̍h būn-tê

Nā bô hoattō͘ chng ā san, chhiáⁿ chhiútōng kā `TalmageOverride.db` chng/san. Ē kì tit ta̍k pái **piànkeng chìnchêng ài têngkhui tiānnáu**.

Chhiáⁿ chhiútōng phah khui suji̍phoat ê Folder, kā chuliāu khò͘ santiāu, koh têngkhui tiānnáu tō ē sái tit.

#### 1. Phah khui suji̍phoat ê Folder

Phah khui suji̍phoat ê Folder ū 2 ê hoattō͘:

A. Tī `explorer` téngbīn phah Folder Path:

```
%APPDATA%\FHL TaigiIME\IMTalmage
```

<img src="soatbeng/alt01-manual.png" width="50%" height="50%">

**iā sī**

B1. Chhōe `cmd` kā phah khui:

<img src="soatbeng/alt02-cmd.png" width="50%" height="50%">

B2. Kā `explorer.exe` phah khui, tio̍h chhiú phah: `explorer.exe "%APPDATA%\FHL TaigiIME\IMTalmage"`

<img src="soatbeng/alt03-open.png" width="50%" height="50%">

#### 2. Kā chuliāu khò͘ santiāu

San `TalmageOverride.db`:

<img src="soatbeng/alt04-override.png" width="50%" height="50%">

---

## Mac

Chhiáⁿ tángló͘ chham Windows kāngkhoán ê `FHL_Taioanji.zip`, koh unzip kàu chi̍t ê Folder.

Iōng Finder chhōe `~/Library/Application Support/FHL TaigiIME/IMTalmage`. Kā `TalmageOverride.db` hē tī `IMTalmage`, tō ē sái tit súiōng.

Nā beh san tiāu, kā `TalmageOverride.db` san tiāu tō ē sái tit.

## Developers

There's just a simple build script in `src/build.py`. You will need a CSV file with 4 columns:

```
1. id - a number
2. original lomaji - fully hyphenated as in the original FHL database
3. taioanji - with hyphens removed (either joined or spaced) as required
4. hanji - desired hanji output

Run the script and copy the output SQLite database `TalmageOverride.db` to the appropriate folder for your platform. To uninstall or modify, you must log out and log back in (or reboot) first.
# Extracted UEFI IFR Dumps (BIOS 1.33.1)

Extracted from `Inspiron_Vostro_5402_5409_5502_5509_1.33.1_64.exe` (`System BIOS with BiosGuard v1.33.1.bin`) using `UEFITool` NE and `ifrextract` (`uifr`):

- `Setup.ifr.txt` — Extracted from `Setup` DXE (`E6A7A1CE-5881-4B49-80BE-69C91811685C`). Contains the main Intel/AMI VarStores (`Setup`, `SaSetup`, `CpuSetup`, `PchSetup`, `MeSetup`, `SiSetup`).
- `DellSetupFormSets.ifr.txt` — Extracted from `DellSetupFormSets` DXE (`05B17EF3-26CB-444A-82F7-92705CFB6B1E`). Contains Dell's F2 Setup UI form definitions (`PowerManData`, `SysConfigData`, `SupportAssistData`, `CommonSetupData`).

Both files are normalized to UTF-8 (escaping non-printable control characters) for clean searching on GitHub or via `scripts/parse_ifr.py`:

```bash
python3 scripts/parse_ifr.py ifr/Setup.ifr.txt --varstores
python3 scripts/parse_ifr.py ifr/Setup.ifr.txt --search "DVMT"
```

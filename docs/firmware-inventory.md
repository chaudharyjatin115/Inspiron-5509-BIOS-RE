# BIOS 1.33.1 Firmware Inventory & Module Map

Extracted from `Inspiron_Vostro_5402_5409_5502_5509_1.33.1_64.exe` using `BIOSUtilities` (`Dell PFS Extract`) and `UEFITool` NE.

## 1. Supported Models (`Model Information v1.0.0.0.txt`)

- **Vendor:** Dell Inc.
- **BIOS Version:** `1.33.1` (Release date: `11/15/2024`)
- **System SKUs:** `0A01`, `0A02` (Inspiron 5509), `0A03`, `0A04` (Inspiron/Vostro 5402 / 5409 / 5502 / 5509)
- **Board Map:** `MockingbirdTgl Board Map v1.0.1.bin`

## 2. PFS Firmware Payload Components

| Component | Version |
| :--- | :--- |
| System BIOS with BiosGuard | `1.33.1` (`16 MB` SPI image) |
| Embedded Controller (EC) | `1.11.0` |
| Backup Embedded Controller | `1.0.0` |
| Intel Management Engine (Consumer) | `15.0.50.2633` |
| Integrated Sensor Hub (ISH + PDT) | `5.4.1.4479` |
| Cypress USB-C PD Controller 0 | `1.25.64.31` |
| Intel Thunderbolt Retimer | `2.1.5` |
| BiosConnect Core / Wireless FV | `1.25.0` |

## 3. Key UEFI Modules (`System BIOS with BiosGuard v1.33.1.bin`)

| Module Name | Phase | GUID | Role / RE Findings |
| :--- | :--- | :--- | :--- |
| `Setup` | DXE | `E6A7A1CE-5881-4B49-80BE-69C91811685C` | Main HII IFR database (`Setup`, `SaSetup`, `CpuSetup`, `PchSetup`, `MeSetup`, `SiSetup`) |
| `DellSetupFormSets` | DXE | `05B17EF3-26CB-444A-82F7-92705CFB6B1E` | Dell F2 BIOS UI (`SysConfigData`, `PowerManData`, `SupportAssistData`) |
| `PlatformSetup` | DXE | `A4F2909C-5E2A-438A-91BA-272B0923049A` | Platform setup setup/init hooks |
| `SetupVariablePei` | PEI | `3E7DD42F-A67E-4D4F-BC02-2B5A6EC8DAE9` | Only updates byte `0x00` (`Revision`) of the 6 setup variables; preserves `0x0E`/`0x1C`/`0x84`/`0x43` |
| `AdvancedAcpiDxe` | DXE | `C3E69EB2-0429-4BD6-AE4A-8CA02FBACC2E` | Reads `Setup` (`0xAEC` bytes), patches DSDT `SS3` from `Setup[0x0E]`, toggles FADT bit 21 & `GNVS.S0ID` from `Setup[0x1C]` |
| `AcpiPlatformFeatures` | DXE | `07709C98-414A-4039-B7D0-29C21F105E92` | Additional ACPI table patching (`LPIT`, `WSMT`, `WDAT`, `SSDT`) |
| `S3Resume2Pei` | PEI | `89E549B0-7CFE-449D-9BA3-10D8B2312D71` | PEI S3 resume vector |
| `FspS3Notify` | PEI | `EA7F0916-B5C8-493F-A006-565CC2041044` | Intel FSP S3 resume notification |
| `S3SaveStateDxe` | DXE | `BDCE85BB-FBAA-4F4E-9264-501A2C249581` | Saves boot script state for S3 |
| `SmmS3SaveState` | SMM | `2D59F041-53A4-40D0-A6CD-844DC0DFEF17` | SMM S3 boot script save |
| `BootScriptExecutorDxe` | DXE | `FA20568B-548B-4B2B-81EF-1BA08D4A3CEC` | Boot script replay on S3 resume |
| `CpuS3DataDxe` | DXE | `4D2E57EE-0E3F-44DD-93C4-D3B57E96945D` | Saves CPU state for S3 resume |
| `AcpiTables` | Freeform | `7E374E25-8E01-4FEE-87F2-390C23C606CD` | Base ROM ACPI tables |
| `CpuAcpiTables` | Freeform | `C38FB0E2-0C43-49C9-B544-9B17AA4DCBA3` | CPU SSDTs (`CpuSsdt`, `Cpu0Ist`, etc.) |
| `DptfAcpiTables` | Freeform | `EA139578-FEA0-4DD2-91B5-6953819EF1E4` | Intel DPTF tables (`DptfTabl`) |
| `DellFlashUpdate2Dxe` | DXE | `F895B482-1970-49A7-84F5-723978086642` | Dell BIOS capsule/flash updater |

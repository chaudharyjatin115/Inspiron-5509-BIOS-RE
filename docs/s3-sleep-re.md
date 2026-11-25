# S3 Sleep vs Modern Standby (S0ix) Reverse Engineering (BIOS 1.33.1)

By default on BIOS 1.33.1, the Inspiron 5509 boots with S3 disabled (`ACPI: PM: (supports S0 S4 S5)` and `[s2idle]` in Linux) because Dell ships Modern Standby (`Low Power S0 Idle`) enabled in NVRAM.

Checking the extracted firmware modules and live `acpidump` shows how S3 vs S0ix is wired up in this BIOS.

## 1. S3 Resume Stack Presence

The BIOS 1.33.1 image (`Inspiron_Vostro_5402_5409_5502_5509_1.33.1_64.exe`) includes the full PEI/DXE/SMM S3 resume modules:

- `S3Resume2Pei` (`89E549B0-7CFE-449D-9BA3-10D8B2312D71`)
- `FspS3Notify` (`EA7F0916-B5C8-493F-A006-565CC2041044`)
- `S3SaveStateDxe` (`BDCE85BB-FBAA-4F4E-9264-501A2C249581`) & `SmmS3SaveState` (`2D59F041-53A4-40D0-A6CD-844DC0DFEF17`)
- `BootScriptExecutorDxe` (`FA20568B-548B-4B2B-81EF-1BA08D4A3CEC`)
- `CpuS3DataDxe` (`4D2E57EE-0E3F-44DD-93C4-D3B57E96945D`)

## 2. DSDT Handlers

In the live `DSDT` dump:

- `Name (SS3, Zero)` controls both `If (SS3) { Name (_S3, Package (0x04) { 0x05, Zero, Zero, Zero }) }` and the wake capability mask inside `GPRW` (`Local0 |= (SS3 << 0x03)`).
- `_PTS` handles `Arg0 == 0x03` (`CWEF = CPWE`, `EV1`, Thunderbolt/TCSS prep, `TPM.PTS`).
- `_WAK` handles `Arg0 == 0x03` (`NHPG`, `NPME`, `EV1`, lid/GFX0 `CLID` restore, PCIe root port `Notify` checks).

## 3. `AdvancedAcpiDxe` Disassembly (`C3E69EB2-0429-4BD6-AE4A-8CA02FBACC2E`)

Disassembling `AdvancedAcpiDxe` with `objdump -d -M intel` confirms that `SS3` and the FADT `LOW_POWER_S0_IDLE_CAPABLE` flag are not hardcoded—they are read directly from the `Setup` NVRAM variable (`EC87D643-EBA4-4BB5-A1E5-3F3E36B20DA9`, `0xAEC` bytes):

1. **Loading `Setup` (`0x202e` - `0x2060`):**
   `AdvancedAcpiDxe` calls `gRT->GetVariable("Setup", ..., &Size, 0xfde0)` with `Size = 0xaec`.
2. **Patching `SS3` in DSDT (`0x13b9` - `0x13f2`):**
   When scanning AML for `SS3_` (`0x5f335353`), it reads `BYTE PTR [0xfdee]` (`0xfde0 + 0x0E`, i.e., `Setup[0x0E]`) and writes it into the DSDT `SS3` object.
3. **Patching `FACP` / `FADT.Flags` (`0x1548` - `0x1562`) and `GNVS.S0ID` (`0x3ce7`):**
   It reads `BYTE PTR [0xfdfc]` (`0xfde0 + 0x1C`, i.e., `Setup[0x1C]`).
   - If `0xfdfc != 0`: sets `FADT.Flags` bit 21 (`0x200000`, `LOW_POWER_S0_IDLE_CAPABLE`) and bit 4 (`0x10`), clears bit 9 (`RTC_S4`), and sets `GNVS.S0ID = 1`.
   - If `0xfdfc == 0`: leaves bit 21 cleared (`and eax, 0xffffffef`) and sets `GNVS.S0ID = 0`.

## 4. `SetupVariablePei` Check (`3E7DD42F-A67E-4D4F-BC02-2B5A6EC8DAE9`)

Disassembling `SetupVariablePei` (`0xfffb7f41` - `0xfffb7fbd`) shows it only writes byte `0x00` (struct `Revision`) across `Setup` (`0x15`), `MeSetup` (`0x04`), `CpuSetup` (`0x19`), `SaSetup` (`0x0E`), `PchSetup` (`0x09`), and `SiSetup` (`0x01`). It does **not** overwrite `Setup[0x0E]` or `Setup[0x1C]` on boot.

## 5. IFR Offsets & Live State

| Setting | VarStore | Offset | Live Factory Value | S3 Value |
| :--- | :--- | :--- | :--- | :--- |
| `Enable ACPI Auto Configuration` | `Setup` | `0x0D` | `0x00` | `0x00` (must be 0 so `0x0E` isn't suppressed) |
| `ACPI S3 Support` | `Setup` | `0x0E` | `0x00` (Disabled) | `0x01` (Enabled) |
| `Low Power S0 Idle Capability` | `Setup` | `0x1C` | `0x01` (Enabled) | `0x00` (Disabled) |
| `Enable 8254 Clock Gate` | `PchSetup` | `0x600` | `0x02` (Runtime + S3 Resume) | `0x02` |
| `Wake From Thunderbolt(TM) Devices` | `Setup` | `0x6C2` | `0x01` (Enabled) | `0x00` (optional, if TBT wakes sleep) |

Commands in `modGRUBShell`:

```text
setup_var_cv Setup 0x0E 0x1 0x01
setup_var_cv Setup 0x1C 0x1 0x00
```

> **Note:** While the firmware modules and ACPI tables implement S3, actual S3 suspend/resume stability (EC, KIOXIA NVMe, eDP panel wake) has to be verified on real hardware via `cat /sys/power/mem_sleep` (`deep`) and `systemctl suspend`. Keep a recovery USB handy in case a board revision hangs on S3 resume and needs `0x0E`/`0x1C` reverted.

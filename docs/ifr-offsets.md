# UEFI IFR Offset Reference (BIOS 1.33.1)

All offsets below come directly from [ifr/Setup.ifr.txt](../ifr/Setup.ifr.txt). Use `setup_var_cv <VarStore> <Offset> <Size> [Value]` in `modGRUBShell.efi`, or inspect live values in Linux with `python3 scripts/check_efivars.py`.

## Graphics & Memory (`SaSetup` — `72C5E28C-7783-43A1-8767-FAD73FCCAFA4`)

| Setting | Offset | Size | IFR Default | Options |
| :--- | :--- | :--- | :--- | :--- |
| `DVMT Pre-Allocated` | `0x84` | `1` | `0xFE` (60M) | `0x00`=0M, `0x01`=32M, `0x02`=64M, `0x03`=96M, `0x04`=128M, `0x05`=160M, `0xFE`=60M |
| `DVMT Total Gfx Mem` | `0x85` | `1` | `0x02` (256M) | `0x01`=128M, `0x02`=256M, `0x03`=MAX |
| `VT-d` | `0x87` | `1` | `0x01` (Enabled) | `0x00`=Disabled, `0x01`=Enabled |
| `Above 4GB MMIO BIOS assignment` | `0x88` | `1` | `0x01` (Enabled) | `0x00`=Disabled, `0x01`=Enabled |

## CPU & Power Limits (`CpuSetup` — `B08F97FF-E6E8-4193-A997-5E9E9B0ADB32`)

| Setting | Offset | Size | IFR Default | Options |
| :--- | :--- | :--- | :--- | :--- |
| `Intel(R) SpeedStep(tm)` | `0x09` | `1` | `0x01` (Enabled) | `0x00`=Disabled, `0x01`=Enabled |
| `Turbo Mode` | `0x16` | `1` | `0x01` (Enabled) | `0x00`=Disabled, `0x01`=Enabled |
| `Power Limit 1 Override` | `0x1B` | `1` | `0x00` (Disabled) | `0x00`=Disabled, `0x01`=Enabled |
| `Power Limit 2 Override` | `0x1D` | `1` | `0x01` (Enabled) | `0x00`=Disabled, `0x01`=Enabled |
| `CFG Lock` (MSR `0xE2` bit 15) | `0x43` | `1` | `0x01` (Enabled) | `0x00`=Disabled, `0x01`=Enabled |
| `Overclocking Lock` | `0xDF` | `1` | `0x01` (Enabled) | `0x00`=Disabled, `0x01`=Enabled |

## ACPI, Sleep & Thunderbolt (`Setup` — `EC87D643-EBA4-4BB5-A1E5-3F3E36B20DA9`)

| Setting | Offset | Size | IFR Default | Options |
| :--- | :--- | :--- | :--- | :--- |
| `Enable ACPI Auto Configuration` | `0x0D` | `1` | `0x00` (Disabled) | `0x00`=Disabled, `0x01`=Enabled |
| `ACPI S3 Support` | `0x0E` | `1` | `0x01` (live: `0x00`) | `0x00`=Disabled, `0x01`=Enabled |
| `Native PCIE Enable` | `0x11` | `1` | `0x01` (Enabled) | `0x00`=Disabled, `0x01`=Enabled |
| `Native ASPM` | `0x12` | `1` | `0x02` (Auto) | `0x00`=Disabled, `0x01`=Enabled, `0x02`=Auto |
| `Low Power S0 Idle Capability` | `0x1C` | `1` | `0x01` (Enabled) | `0x00`=Disabled, `0x01`=Enabled |
| `PEP I2C0` | `0x21` | `1` | `0x01` (Enabled) | `0x00`=Disabled, `0x01`=Enabled |
| `PEP I2C1` | `0x22` | `1` | `0x01` (Enabled) | `0x00`=Disabled, `0x01`=Enabled |
| `LPIT Residency Counter` | `0x3E` | `1` | `0x03` (SLP S0) | `0x01`=C10, `0x03`=SLP S0, `0x07`=PS_ON |
| `Integrated Thunderbolt(TM) Support` | `0x6BE` | `1` | `0x01` (Enabled) | `0x00`=Disabled, `0x01`=Enabled |
| `Wake From Thunderbolt(TM) Devices` | `0x6C2` | `1` | `0x01` (Enabled) | `0x00`=Disabled, `0x01`=Enabled |
| `Thunderbolt Security Level` | `0x6C6` | `1` | `0x00` (No Security) | `0x00`=None, `0x01`=User Auth, `0x02`=Secure Connect, `0x03`=DP Only, `0x04`=USB Dock Only |
| `ITBT Root Port 0` | `0x6F2` | `1` | `0x01` (Enabled) | `0x00`=Disabled, `0x01`=Enabled |
| `PCIE Tunneling for USB4` | `0x8E4` | `1` | `0x01` (Enabled) | `0x00`=Disabled, `0x01`=Enabled |

## PCH & Security Locks (`PchSetup` — `4570B7F1-ADE8-4943-8DC3-406472842384`)

| Setting | Offset | Size | IFR Default | Options |
| :--- | :--- | :--- | :--- | :--- |
| `DeepSx Power Policies` | `0x04` | `1` | `0x00` (Disabled) | `0x00`=Disabled, `0x01`=S5-Batt, `0x02`=S5, `0x03`=S4-Batt, `0x04`=S4 |
| `RTC Memory Lock` | `0x1B` | `1` | `0x01` (Enabled) | `0x00`=Disabled, `0x01`=Enabled |
| `BIOS Lock` | `0x1C` | `1` | `0x01` (Enabled) | `0x00`=Disabled, `0x01`=Enabled |
| `Force unlock on all GPIO pads` | `0x1D` | `1` | `0x00` (Disabled) | `0x00`=Disabled, `0x01`=Enabled |
| `SATA Mode Selection` | `0x49` | `1` | `0x00` (AHCI) | `0x00`=AHCI, `0x01`=RAID/RST |
| `Enable 8254 Clock Gate` | `0x600` | `1` | `0x01` (live: `0x02`) | `0x00`=Disabled, `0x01`=Enabled, `0x02`=Runtime + S3 Resume |
| `SPD Write Disable` | `0x681` | `1` | `0x01` (TRUE) | `0x00`=FALSE, `0x01`=TRUE |

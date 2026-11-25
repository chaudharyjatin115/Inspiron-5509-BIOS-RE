# OEM ACPI Tables (Dell Inspiron 5509, BIOS 1.33.1)

Decompiled ASL (`iasl -d`) from a live `acpidump` on Arch Linux running on SKU `0A02` (`i5-1135G7` Tiger Lake-LP).

Notes:
- `MSDM` and `SLIC` (OEM Windows licensing tables) are omitted.
- OpenCore-injected SSDTs (`SSDT-ALS0`, `SSDT-AWAC`, `SSDT-EC-USBX`, `SSDT-GPI0`, `SSDT-OSYS`, `SSDT-PLUG`, `SSDT-PNLF`, `SSDT-SBUS-MCHC`, `SSDT-GPRW`) are omitted so this directory reflects only Dell's OEM tables.
- Because the dump was taken while booted via OpenCore, `DSDT.dsl` contains the single OpenCore ACPI rename `Method(GPRW,2,N) -> XPRW` (`XPRW` at line 21731).
- The dump reflects factory sleep NVRAM state (`Setup[0x0E] = 0x00`, `Setup[0x1C] = 0x01`), so `DSDT.dsl` has `Name (SS3, Zero)` and `FACP.dsl` has `Low Power S0 Idle (V5) : 1`.

# Dell Inspiron 5509 (BIOS 1.33.1) - BIOS Reverse Engineering & NVRAM Unlock Guide

Firmware reverse-engineering notes, extracted UEFI IFR variable offsets, and live ACPI dump findings for the **Dell Inspiron 5509 / Vostro 5402 / 5502** (`SKU 0A02`, 11th Gen Intel Tiger Lake-LP `i5-1135G7`), extracted directly from official BIOS version **1.33.1** (`Inspiron_Vostro_5402_5409_5502_5509_1.33.1_64.exe`).

---

## 1. BIOS Write Protection & Safety Facts

* **Is the BIOS write-protected?**
  * **SPI Flash (Code ROM):** Yes, Dell enables Intel Boot Guard and BIOS Guard (PFAT) to prevent unauthorized flashing of the core BIOS code.
  * **NVRAM Variable Store (`Setup` / `SaSetup` / `CpuSetup` / `PchSetup`):** **No**, NVRAM variables have runtime attributes `0x07` (`NV + BS + RT` = Non-Volatile, Boot Service, Runtime Access). This means you **can** modify these settings using a modified UEFI shell.
* **Prerequisites for Writing:**
  1. **Disable Secure Boot:** Enter BIOS (`F2` at startup) -> `Security` / `Boot` -> Set **Secure Boot** to **Disabled**. (If Secure Boot is enabled, Dell blocks unsigned EFI utilities like `modGRUBShell` and rejects variable modification calls).
  2. **Clear BIOS Admin Password:** If you set a supervisor/admin password in the Dell BIOS, remove it temporarily so NVRAM variable writes are not rejected.
  3. **`modGRUBShell.efi`** (or `setup_var.efi`).

---

## 2. Reverse Engineering Pipeline (How These Offsets Were Found)

1. **Firmware Extraction:** Unpacked `Inspiron_Vostro_5402_5409_5502_5509_1.33.1_64.exe` with `BIOSUtilities` (`Dell PFS Extract`) to obtain `System BIOS with BiosGuard v1.33.1.bin`, then extracted DXE/PEI sections with `UEFITool` NE.
2. **IFR Extraction:** Ran `ifrextract` (`uifr`) against `Setup` (`E6A7A1CE-5881-4B49-80BE-69C91811685C`) to recover all VarStores, GUIDs, sizes, and hidden option offsets.
3. **PEI/DXE Binary Analysis:** Disassembled `AdvancedAcpiDxe` (`C3E69EB2-0429-4BD6-AE4A-8CA02FBACC2E`) and `SetupVariablePei` (`3E7DD42F-A67E-4D4F-BC02-2B5A6EC8DAE9`) with `objdump -d -M intel` to verify how `Setup` offsets map to `DSDT`/`FACP` patching and confirm PEI doesn't reset them at boot.
4. **Live Hardware Verification:** Cross-checked against Linux `/sys/firmware/efi/efivars/*`, `acpidump` + `iasl -d`, `lspci -nn`, `lsusb -t`, and `/proc/interrupts`.

---

## 3. Extracted Hardware & Variable Mapping

* **System SKU:** `0A02` (Dell Inspiron 5509 / 5402 / 5502)
* **Processor:** 11th Gen Intel Core i5-1135G7 (Iris Xe Graphics 80EU, `8086:9a49`)
* **BIOS Version:** `1.33.1`

### NVRAM VarStores (`Setup` DXE IFR)

| VarStore Name | GUID | Size | Notes |
| :--- | :--- | :--- | :--- |
| `Setup` | `EC87D643-EBA4-4BB5-A1E5-3F3E36B20DA9` | `0xAEC` (2796 B) | Main ACPI, Thunderbolt, general platform settings |
| `SaSetup` | `72C5E28C-7783-43A1-8767-FAD73FCCAFA4` | `0x44C` (1100 B) | System Agent: DVMT, VT-d, Above 4G MMIO |
| `CpuSetup` | `B08F97FF-E6E8-4193-A997-5E9E9B0ADB32` | `0x28E` (654 B) | CPU: CFG Lock, Overclocking Lock |
| `PchSetup` | `4570B7F1-ADE8-4943-8DC3-406472842384` | `0x7EC` (2028 B) | PCH: SATA mode, 8254 clock gate, DeepSx |
| `MeSetup` | `5432122D-D034-49D2-A6DE-65A829EB4C74` | `0x8F` (143 B) | Intel ME settings |
| `SiSetup` | `AAF8E719-48F8-4099-A6F7-645FBD694C3D` | `0x07` (7 B) | Silicon setup |

### Verified Target Variables

| Setting | Variable Store | Offset | Size | BIOS Default | Recommended / Notes |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **DVMT Pre-Allocated** | `SaSetup` | **`0x84`** | `1` B | `0xFE` (60MB) | **`0x03` (96MB)** *(or `0x02` for 64MB)* |
| **DVMT Total Gfx Mem** | `SaSetup` | **`0x85`** | `1` B | `0x02` (256MB) | **`0x03` (MAX)** |
| **CFG Lock (MSR 0xE2)** | `CpuSetup` | **`0x43`** | `1` B | `0x01` (Enabled) | **`0x00` (Disabled)** |
| **Overclocking Lock** | `CpuSetup` | `0xDF` | `1` B | `0x01` (Enabled) | `0x00` (Disabled, if undervolting) |
| **VT-d** | `SaSetup` | `0x87` | `1` B | `0x01` (Enabled) | Keep `0x01` (use `DisableIoMapper` if needed) |
| **Above 4GB MMIO** | `SaSetup` | `0x88` | `1` B | `0x01` (Enabled) | Keep `0x01` |
| **ACPI S3 Support** | `Setup` | `0x0E` | `1` B | `0x00` (Disabled) | `0x01` (Enabled; see [S3 Sleep RE](docs/s3-sleep-re.md)) |
| **Low Power S0 Idle (S0ix)** | `Setup` | `0x1C` | `1` B | `0x01` (Enabled) | `0x00` (Disabled; pairs with `0x0E = 0x01`) |
| **Enable 8254 Clock Gate** | `PchSetup` | `0x600` | `1` B | `0x02` (Runtime + S3) | Keep `0x02` |
| **Integrated Thunderbolt** | `Setup` | `0x6BE` | `1` B | `0x01` (Enabled) | `0x01` (Enabled) |
| **Wake From Thunderbolt** | `Setup` | `0x6C2` | `1` B | `0x01` (Enabled) | `0x00` if TBT causes sleep wake |
| **SATA Mode Selection** | `PchSetup` | `0x49` | `1` B | `0x00` (AHCI) | `0x00` (AHCI) |

> [!NOTE]
> On Intel 11th Gen Tiger Lake Dell laptops, DVMT is located inside **`SaSetup`** (System Agent Setup), **not** `Setup`. You **must** use `setup_var_cv SaSetup ...` (or `setup_var_cv CpuSetup ...` / `setup_var_cv Setup ...`). Standard `setup_var` only accesses `Setup`.

You can check all of the above live on Linux (read-only) with:
```bash
python3 scripts/check_efivars.py
```

---

## 4. Repository Layout & Reverse Engineering Docs

* **[docs/firmware-inventory.md](docs/firmware-inventory.md)** — BIOS `1.33.1` PFS payload versions (`EC 1.11.0`, `ME 15.0.50.2633`, `ISH 5.4.1.4479`, `Cypress PD`, `TBT Retimer`) and key PEI/DXE/SMM module GUIDs.
* **[docs/ifr-offsets.md](docs/ifr-offsets.md)** — Full categorized table of hidden UEFI IFR offsets (`SaSetup`, `CpuSetup`, `Setup`, `PchSetup`) including BIOS/RTC/GPIO locks, power limits, Thunderbolt 4 / USB4 tunneling, and sleep states.
* **[docs/s3-sleep-re.md](docs/s3-sleep-re.md)** — Disassembly of `AdvancedAcpiDxe` and `SetupVariablePei` proving how `Setup[0x0E]` patches `DSDT` `SS3` and `Setup[0x1C]` toggles `FACP.Flags` bit 21 (`LOW_POWER_S0_IDLE_CAPABLE`) and `GNVS.S0ID`, plus the PEI/DXE/SMM S3 module inventory.
* **[docs/acpi-and-hardware-map.md](docs/acpi-and-hardware-map.md)** — Full `DSDT`/`SSDT` findings: PCIe paths (`PEG0.PEGP` NVMe vs empty `RP09`), `GPI0` (`INT34C5`) vs `VoodooGPIO` binary mismatch, `TPD0` `OSYS` initialization order, `OSID()` gating `BRT6` brightness keys, and `xh_Dell_` USB port map vs `lsusb -t`.
* **[ifr/](ifr/)** — Full UTF-8 sanitized `ifrextract` dumps of `Setup` and `DellSetupFormSets` from BIOS `1.33.1`.
* **[acpi/](acpi/)** — Clean decompiled OEM `DSDT` and `SSDT` tables (`.dsl`) from live `acpidump` (`MSDM`/`SLIC` omitted).
* **[scripts/](scripts/)** — `check_efivars.py` (inspect live Linux `efivarfs` offsets) and `parse_ifr.py` (search/list VarStores & options in `ifr/Setup.ifr.txt`).

---

## 5. Preparation: Create the Bootable USB Drive

1. Take any standard USB flash drive (1GB or larger).
2. Format the USB drive as **FAT32** (Master Boot Record / MBR).
3. Open the USB drive and create the following directory path:
   ```text
   EFI
    └── BOOT
   ```
4. Copy `modGRUBShell.efi` into the `EFI/BOOT` folder.
5. Rename `modGRUBShell.efi` inside `EFI/BOOT` to:
   ```text
   BOOTX64.EFI
   ```

*(Final path on USB: `/EFI/BOOT/BOOTX64.EFI`)*

---

## 6. Execution: Changing the Variables

1. Plug the USB flash drive into your Dell Inspiron 5509.
2. Turn on the laptop and immediately tap **`F12`** repeatedly until the One-Time Boot Menu appears.
3. Under **UEFI Boot Devices**, select your USB drive.
4. The modified GRUB shell will load to a command prompt:
   ```text
   grub>
   ```

### Step 1: Read and change DVMT Pre-Allocated
Check your current value (should print `0xfe`):
```text
setup_var_cv SaSetup 0x84 0x1
```
Set DVMT Pre-Allocated to **96MB**:
```text
setup_var_cv SaSetup 0x84 0x1 0x03
```
Verify the change (must now report `0x03`):
```text
setup_var_cv SaSetup 0x84 0x1
```

### Step 2: (Recommended) Set Total Graphics Memory to MAX
```text
setup_var_cv SaSetup 0x85 0x1 0x03
```

### Step 3: (Optional) Disable CFG Lock for Native CPU Power Management
Check current value (should print `0x01`):
```text
setup_var_cv CpuSetup 0x43 0x1
```
Disable CFG Lock:
```text
setup_var_cv CpuSetup 0x43 0x1 0x00
```
Verify the change (must now report `0x00`):
```text
setup_var_cv CpuSetup 0x43 0x1
```

### Step 4: (Experimental) Enable ACPI S3 / Disable S0ix
See [docs/s3-sleep-re.md](docs/s3-sleep-re.md) for firmware disassembly and recovery notes before changing these:
```text
setup_var_cv Setup 0x0E 0x1 0x01
setup_var_cv Setup 0x1C 0x1 0x00
```

### Step 5: Reboot
```text
reboot
```

---

## 7. Post-Reboot OpenCore `config.plist` Cleanup

Once DVMT is set to 96MB in hardware, you can remove the fallback software patches:

1. Mount your EFI partition:
   ```bash
   sudo diskutil mount disk0s1
   ```
2. Open `EFI/OC/config.plist`:
   * **`NVRAM -> Add -> 7C436110-AB2A-4BBB-A880-FE41995C9F82 -> boot-args`**:
     * Remove: `-igfxdvmt`
     * Keep: `-allow3d -disablegfxfirmware`
   * **`DeviceProperties -> Add -> PciRoot(0x0)/Pci(0x2,0x0)`**:
     * You can safely remove: `framebuffer-stolenmem` and `framebuffer-fbmem`.
     * Keep: `framebuffer-patch-enable = 01000000` and `framebuffer-unifiedmem = 00000080`.
   * **`Kernel -> Quirks`** (if you disabled CFG Lock):
     * Set `AppleCpuPmCfgLock` = `false`
     * Set `AppleXcpmCfgLock` = `false`
3. Save `config.plist` and restart.

---

## 8. Troubleshooting

* **Error: `can't set variable using efi` or `write protected`:**
  * Ensure **Secure Boot** is disabled in the `F2` Dell BIOS setup.
  * Ensure no BIOS Admin Password is set.
* **If a future Dell BIOS update resets settings:**
  * Updating your BIOS resets NVRAM variables to factory defaults (`0xFE` / 60MB). Keep this USB drive handy to re-run the `setup_var_cv` commands after any future BIOS update.

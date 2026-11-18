# Dell Inspiron 5509 (BIOS 1.33.1) - DVMT & CFG Lock Modification Guide

This guide contains the verified hardware and firmware offsets extracted directly from the official **Dell Inspiron 5509 / Vostro 5402/5502 BIOS version 1.33.1** (`Inspiron_Vostro_5402_5409_5502_5509_1.33.1_64.exe`).

---

## 1. BIOS Write Protection & Safety Facts

* **Is the BIOS write-protected?**
  * **SPI Flash (Code ROM):** Yes, Dell enables Intel Boot Guard and BIOS Guard (PFAT) to prevent unauthorized flashing of the core BIOS code.
  * **NVRAM Variable Store (`SaSetup` / `CpuSetup`):** **No**, NVRAM variables have runtime attributes `0x07` (`NV + BS + RT` = Non-Volatile, Boot Service, Runtime Access). This means you **can** modify these settings using a modified UEFI shell.
* **Prerequisites for Writing:**
  1. **Disable Secure Boot:** Enter BIOS (`F2` at startup) -> `Security` / `Boot` -> Set **Secure Boot** to **Disabled**. (If Secure Boot is enabled, Dell blocks unsigned EFI utilities like `modGRUBShell` and rejects variable modification calls).
  2. **Clear BIOS Admin Password:** If you set a supervisor/admin password in the Dell BIOS, remove it temporarily so NVRAM variable writes are not rejected.

---

## 2. Extracted Hardware & Variable Mapping

* **System SKU:** `0A02` (Dell Inspiron 5509 / 5402 / 5502)
* **Processor:** 11th Gen Intel Core i5-1135G7 (Iris Xe Graphics 80EU)
* **BIOS Version:** 1.33.1

### Target Variables

| Setting | Variable Store | GUID | Offset | Default | Recommended Value |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **DVMT Pre-Allocated** | `SaSetup` | `72C5E28C-7783-43A1-8767-FAD73FCCAFA4` | **`0x84`** | `0xFE` (60MB) | **`0x03` (96MB)** *(or `0x02` for 64MB)* |
| **DVMT Total Gfx Mem** | `SaSetup` | `72C5E28C-7783-43A1-8767-FAD73FCCAFA4` | **`0x85`** | `0x02` (256MB) | **`0x03` (MAX)** |
| **CFG Lock (MSR 0xE2)** | `CpuSetup` | `B08F97FF-E6E8-4193-A997-5E9E9B0ADB32` | **`0x43`** | `0x01` (Enabled) | **`0x00` (Disabled)** |

> [!NOTE]
> On Intel 11th Gen Tiger Lake Dell laptops, DVMT is located inside **`SaSetup`** (System Agent Setup), **not** `Setup`. You **must** use `setup_var_cv SaSetup ...`. Standard `setup_var` will not work.

---

## 3. Preparation: Create the Bootable USB Drive

1. Take any standard USB flash drive (1GB or larger).
2. Format the USB drive as **FAT32** (Master Boot Record / MBR).
3. Open the USB drive and create the following directory path:
   ```text
   EFI
    └── BOOT
   ```
4. Copy `modGRUBShell.efi` (already downloaded in your `~/Downloads` folder) into the `EFI/BOOT` folder.
5. Rename `modGRUBShell.efi` inside `EFI/BOOT` to:
   ```text
   BOOTX64.EFI
   ```

*(Final path on USB: `/EFI/BOOT/BOOTX64.EFI`)*

---

## 4. Execution: Changing the Variables

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

### Step 4: Reboot
```text
reboot
```

---

## 5. Post-Reboot OpenCore `config.plist` Cleanup

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

## 6. Troubleshooting

* **Error: `can't set variable using efi` or `write protected`:**
  * Ensure **Secure Boot** is disabled in the `F2` Dell BIOS setup.
  * Ensure no BIOS Admin Password is set.
* **If a future Dell BIOS update resets settings:**
  * Updating your BIOS resets NVRAM variables to factory defaults (`0xFE` / 60MB). Keep this USB drive handy to re-run the `setup_var_cv` commands after any future BIOS update.

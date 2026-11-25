# ACPI & Hardware Map (Dell Inspiron 5509, BIOS 1.33.1)

Notes taken from live Linux `acpidump` (`iasl -d`), `lspci -nn`, `lsusb -t`, and `/proc/interrupts` on the i5-1135G7 (Tiger Lake-LP) SKU `0A02`.

## 1. PCIe & Device Paths (`DSDT` vs `lspci`)

| PCI BDF | Device | ACPI Path | Notes |
| :--- | :--- | :--- | :--- |
| `00:02.0` | Intel Iris Xe Graphics (`8086:9a49`) | `\_SB.PC00.GFX0` | Tiger Lake-LP GT2 (80EU) |
| `00:06.0` -> `01:00.0` | KIOXIA BG4 NVMe (`1e0f:0001`) | `\_SB.PC00.PEG0.PEGP` | Primary M.2 NVMe is on `PEG0`, **not** `RP09` |
| `00:07.0` / `00:0d.0` / `00:0d.2` | Thunderbolt 4 RP / USB / NHI | `\_SB.PC00.TRP0` / `TXHC` / `TDM0` | Defined in `TcssSsdt` |
| `00:14.0` | PCH xHCI (`8086:a0ed`) | `\_SB.PC00.XHCI` | 12 HS ports + 4 SS ports (`SSPA() = 0x0D`) |
| `00:15.0` | Serial IO I2C #0 (`8086:a0e8`) | `\_SB.PC00.I2C0` | `TPL1` (disabled when no touchscreen) |
| `00:15.1` | Serial IO I2C #1 (`8086:a0e9`) | `\_SB.PC00.I2C1` | Touchpad `TPD0` (`DLL09D9:00`) |
| `00:1c.0` -> `2c:00.0` | QCA6174 Wi-Fi (`168c:003e`) | `\_SB.PC00.RP07.PXSX` | PCIe Root Port #7 |
| `00:1f.0` | eSPI / LPC (`8086:a082`) | `\_SB.PC00.LPCB` | Contains `ECDV` (`PNP0C09`), `HPET`, `RTC`, `TIMR`, `IPIC` |
| `00:1f.3` | Intel Smart Sound Audio (`8086:a0c8`) | `\_SB.PC00.HDAS` | Uses `NHLT` DMIC table |

Because the primary NVMe sits under `\_SB.PC00.PEG0.PEGP` (and `RP09` is empty), any `SSDT-NVME_OFF` template targeting `RP09.PXSX` does nothing on this laptop.

## 2. I2C Touchpad (`DLL09D9:00`) & GPIO (`INT34C5`)

In Linux `/proc/interrupts`, the touchpad runs in GPIO interrupt mode:
```text
 14: ... IO-APIC 14-fasteoi INT34C5:00
142: ... intel-gpio 3       DLL09D9:00
```

Looking at `DSDT`:
- `\_SB.GPI0._HID` returns `"INT34C5"` when `GPHD == 0` and `PCHS == PCHL` (`0x02`, Tiger Lake-LP).
- `\_SB.PC00.I2C1.TPD0._INI` checks `OSYS < 0x07DC`; if `OSYS` isn't >= `0x07DC` *before* `PC00` children initialize, `TPD0._INI` calls `SRXO (GPDI, One)` and `TPD0._CRS` returns `SBFI` instead of `I2CM(...) + SBFG` (`GpioInt` on `\_SB.GPI0`).
- **Gotcha with `SSDT-OSYS`:** Setting `OSYS = 0x07DF` inside a separate `\_SB.PC09._INI` SSDT runs *after* `\_SB.PC00` and `TPD0._INI`. Using an `_OSI` -> `XOSI` rename with `SSDT-XOSI` fixes `OSYS` during `\_SB.PC00._INI` natively.
- **Gotcha with `VoodooGPIO` (in VoodooI2C 2.9.1):** Even though `VoodooGPIO.kext/Contents/Info.plist` lists `VoodooGPIOTigerLakeLP` -> `INTC1055`, the compiled `VoodooGPIO` Mach-O binary (`v1.1`) only contains `VoodooGPIOIceLakeLP`, `VoodooGPIOCannonLakeLP/H`, `VoodooGPIOSunrisePointLP/H`, and `VoodooGPIOAMD`—no `VoodooGPIOTigerLakeLP` class, and no `INT34C5` match. Dropping `-vi2c-force-polling` without a `VoodooGPIO` build that supports `INT34C5` / Tiger Lake-LP will break trackpad input.

## 3. Brightness Hotkeys (`OSID()` vs `OSYS`)

EC brightness hotkey events in `DSDT` call `EV6` -> `\_SB.PC00.GFX0.BRT6` (`Notify (LCD, 0x86/0x87)`), which is what `BrightnessKeys.kext` listens to. However, `EV6` is gated by:
```asl
If ((\_SB.OSID () >= 0x20))
```
`Method (OSID)` reads `_OSI` directly (`WXP`, `WLG`, `WIN7`, `WIN8`, `WN81`) and does **not** check `OSYS`. Without `_OSI` -> `XOSI` + `SSDT-XOSI`, `OSID()` returns `1` under Darwin and suppresses `BRT6` notifications.

## 4. Clocks, EC, & HPET (`DSDT`)

- **EC:** Named `ECDV` (`PNP0C09`) under `\_SB.PC00.LPCB`.
- **RTC / AWAC:** `AWAC` (`ACPI000E`) is disabled when `STAS != 0` (`SSDT-AWAC`), leaving `RTC` (`PNP0B00`, IRQ 8).
- **HPET / TIMR:** `HPET` (`PNP0103`) only declares `Memory32Fixed` (no IRQ 0/8 overlap with `TIMR` or `RTC`), so no HPET IRQ patch is needed.

## 5. USB Port Map (`xh_Dell_` SSDT vs `lsusb -t`)

`DSDT` `SSPA()` returns `0x0D` (`13`) for `PCHS == PCHL`:
- `HS01`..`HS12` = ports `0x01`..`0x0C` (`1`..`12`)
- `SS01`..`SS04` = ports `0x0D`..`0x10` (`13`..`16`)

Cross-referencing OEM `xh_Dell_` (`SSDT11`) with `lsusb -t`:

| Port | Addr | `xh_Dell_` Status | Hardware |
| :--- | :--- | :--- | :--- |
| `HS01` | `0x01` | `RUPC(1, 3)` | USB 3.2 Type-A Left (USB 2.0) |
| `HS02` | `0x02` | `RUPC(1, 3)` | USB 3.2 Type-A Right (USB 2.0) |
| `HS03` | `0x03` | `TUPC(9)` | USB-C Left (USB 2.0) |
| `HS04` | `0x04` | `GUPC(0)` | Unused |
| `HS05` | `0x05` | `GUPC(0)` (live: `27c6:538d`) | Goodix Fingerprint Reader (no macOS driver) |
| `HS06` | `0x06` | Internal | Integrated Webcam HD (`0bda:565a`) |
| `HS07` | `0x07` | `GUPC(1)` | Realtek USB 2.0 Card Reader (`0bda:0177`) |
| `HS08` | `0x08` | `GUPC(0)` | Unused |
| `HS09` | `0x09` | `GUPC(0)` | Unused |
| `HS10` | `0x0A` | Internal | Qualcomm Atheros Bluetooth (`0cf3:e007`) |
| `SS01` | `0x0D` | `RUPC(1, 3)` | USB 3.2 Type-A Left (SuperSpeed) |
| `SS02` | `0x0E` | `RUPC(1, 3)` | USB 3.2 Type-A Right (SuperSpeed) |
| `SS03` | `0x0F` | `GUPC(0)` | Unused in `xh_Dell_` |
| `TXHC.SS01` | `00:0d.0` | `TUPC(1, 9)` | USB-C Left (Thunderbolt 4 / TCSS USB3) |

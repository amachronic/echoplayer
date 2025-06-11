# Hardware notes

Usage notes for the hardware -- for further information consult the
KiCAD schematic and `pin_assign.ods` file.

## Fast/slow charging mode

To enable 450 mA charging, `~charging_enable` must be pulled to ground,
otherwise the charge is limited to 100 mA. This isn't strictly USB 2.0
compliant but provides an option to draw less current when plugging into
weak USB hosts (eg. a phone).

## Power-on circuit management

The power-on circuit controls the main 3.3V regulator enable pin and
thus is used to power on the STM32 MCU. There are 4 power-on signals
which are active high and OR'd through diodes:

* CPU power (`cpu_power_on` pin)
* RTC wakeup (`rtc_wakeup` pin)
* Power button
* VBUS input

In the normal case, the user will press and hold the power button to
power on the machine. Once the STM32 boots, the bootloader continues
to monitor the button, and if it stays pressed for a certain duration
it will assert the `cpu_power_on` request to keep the CPU powered on
once the power button is released.

The RTC wakeup case is much like the power button case, except that
the bootloader detects the RTC wakeup and boots the firmware with
no user input.

Providing USB power ensures the STM32 is powered even if there is no
software on it. This allows it to be flashed over SWD or USB-DFU.

To shut off the CPU, the firmware should drive `cpu_power_on` low and
wait for some time. It should then trigger a software reset in order
to re-enter the bootloader. If the bootloader is re-entered in this way
it should go into an idle mode to manage battery charging, etc, which
should appear as if the device is 'off' from the user perspective and
respond as expected to the power button / RTC alarm. If USB power is
lost, the bootloader should attempt to shut off the system again.

## Audio codec and jacks

There are two 3.5mm audio jacks driven by the TLV320AIC3104 codec:

- Headphone jack -- direct-coupled (capless) headphone amp output
- Line-out jack -- AC-coupled line output

Both jacks have insert detection and can be driven simultaneously.
The headphone jack supports recording from an inline microphone and
headset button detection following the Android 3.5mm accessory spec.
Both jacks are designed for the CTIA pinout and support 4-pin CTIA
and 3-pin plugs; 4-pin OMTP plugs may not work correctly.

## USB-DFU mode and SWD

The STM32 can be programmed using USB DFU mode by holding SELECT
while inserting a USB cable. This will enter the ST bootloader and
it should appear as a USB-DFU device.

The 6-pin SWD connector can be used to debug and program the STM32
using OpenOCD. This requires an SWD adapter such as the STLINK-V3SET.
The default configuration files for the STM32H743 and your adapter
should be sufficient, no special configuration is required.

Note that software breakpoints in GDB will not work correctly on
Cortex-M7 when the I-cache is enabled, due a bug in OpenOCD. To
work around this, you can use GDB's `hbreak` command to force the
use of hardware breakpoints or you can disable the I-cache.

## Board stackup and ordering information

The board is designed for JLCPCB's 6-layer JLC06101H-3313 stackup.
Trace widths have been selected to get 50-ohm impedance on single
ended signal traces and 90-ohm differential impedance on USB. Via
impedance wasn't taken into account as it shouldn't matter except
at much higher speeds.

For QFN exposed pads the grounding vias in the KiCAD footprint are
smaller than the min. size used on the rest of the board. It should
be fine to enlarge them to the standard via size if required but
JLCPCB seemed to accept them as-is.

| Parameter            | Value                 |
| -------------------- | --------------------- |
| Layers               | 6                     |
| Thickness            | 1.6mm                 |
| Material             | FR-4 TG155            |
| Outer copper weight  | 1 oz                  |
| Inner copper weight  | 0.5 oz                |
| Impedance controlled | Yes                   |
| Stackup              | JLC06101H-3313        |
| Via covering         | Epoxy filled & capped |
| Via pad/hole size    | 0.45mm/0.3mm          |

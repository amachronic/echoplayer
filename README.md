# Echo: Open Hardware Music Player

Echo is an open hardware platform for music players. The goal of
the project is to produce a high quality music player, based on
and designed with free software. It's primarily designed to run
[Rockbox](https://www.rockbox.org), a free music player firmware
with support for many codecs, and a wide array of features.

KiCAD 9.0 was used for the electrical design and PCB layout.
The (unfinished) 3D-printable case is designed using FreeCAD 1.0.
All designs are available under the CERN-OHL-S v2 license.

The current version of the Echo player is called the Echo R1.
In the future, there could be new player models if there are
significant changes to the features or form factor, but old
models will always be supported.

## Echo R1

![3D render of Echo R1 case](/images/echo-r1.png)

- Size: 60x100x15mm (approx)
- Weight: TBD

The R1 has a 4-way D-pad and 6 multi-function buttons on the
faceplate, which can be used to quickly navigate your music
library and control playback. There are dedicated volume and
power buttons (not pictured), and a sliding hold switch near
the power button, which locks the buttons against accidental
presses when the player is in your pocket or bag.

There are two 3.5mm jacks, one for headphones, and one true
line-out port. The headphone jack supports recording from an
in-line microphone and playback control by an in-line remote.
Both jacks can be used simultaneously.

The removable memory card slot allows up to 2 TiB of storage
for your music and files. The USB-C port is used for charging
and file transfer, and supports high-speed USB 2.0.

The battery socket accepts the widely available BL-5C battery,
and the battery can easily be replaced without special tools
when it starts to wear out.

### Hardware specifications

| Component     | Description                               |
| ------------- | ----------------------------------------- |
| CPU           | STM32H743 @ 480 MHz                       |
| Memory        | 32 MiB SDRAM @ 120 MHz                    |
| Audio         | TLV320AIC3104, up to 96 KHz, 0.707 V RMS  |
| Display       | 18-bit, 320x240, 2.3 inch LCD             |
| Storage       | Expandable external memory card slot      |
| USB           | USB 2.0 @ 480 Mbps (High-speed)           |
| Headphone out | Yes (3.5mm jack)                          |
| Line out      | Yes (3.5mm jack)                          |
| Microphone    | Can use wired headphone mic               |
| RTC           | Yes, with wake-up alarm function          |
| Battery       | Replaceable BL-5C battery (~1000 mAH)     |

### Status

The Rev1 prototype PCB is complete but has some problems (see the
list of known issues below). The 3D-printed case for the Rev1 is
unfinished.

Development is currently focused on development of the Rev2 PCB
and fixing mechanical design issues.

### Known issues

- ~~The backlight cannot be disabled, power is supplied to the LEDs
  even when the boost converter is disabled.~~
- ~~The current limit on the backlight LED driver is set too low
  (20 mA paralleled to 4 LEDs, should be 20 mA per LED).~~
- Reference designators in the schematics don't make much sense,
  there are gaps in the numbering and samed-valued components are
  not in contiguous ranges.
- Mounting screws are placed haphazardly and only two of them
  proved to be usable.
- The placement of the LCD and LCD connector is very awkward and
  makes it hard to diassemble the machine non-destructively.
- The lack of mounting holes also makes it difficult to connect
  front and back halves of the case securely.

## License

Unless otherwise noted, all files in this repository, including
this README, are available under the terms of the CERN-OHL-S
version 2 license, which should be found in the file `COPYING.txt`
alongside this README; or at <https://ohwr.org/cern_ohl_s_v2.txt>.

## Credits

Copyright (C) 2024-2025 Aidan MacDonald

# Errata list for Echo-R1-Rev1 PCB

## 1. USB3320C ID pin incorrectly connected

As per the USB3320C datasheet's description of the ID pin:

> For applications not using ID this pin can be connected
> to VDD33. For an A-Device ID is grounded. For a B-Device
> ID is floated.

However, the ID pin is connected to ground, which causes
the DWC2 USB core to go into host mode unless the FDMOD
bit is set by software to force the core to device mode.

Github issue: #9

## 2. HP/LO jacks have incorrect pinout

Due to a mistake in the pin assignment for the 3.5mm jack
footprint, both jacks are incorrectly wired and will not
work with standard headphones. To get normal audio output
a custom 4-pin TRRS male-to-female adapter is needed.

The schematic shows the actual connectivity with notes on
how to construct a custom adapter.

Github issue: #12

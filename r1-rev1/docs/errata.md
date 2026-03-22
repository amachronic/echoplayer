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

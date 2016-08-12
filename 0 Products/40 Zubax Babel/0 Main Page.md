# Zubax Babel

<img src="image.jpg" class="thumbnail" title="Zubax Babel, top view">
<img src="bottom.jpg" class="thumbnail" title="Zubax Babel, bottom view">

Zubax Babel is an advanced USB-CAN and UART-CAN adapter that can be used as a standalone device
or as an embeddable module for <abbr title="Original Equipment Manufacturers">OEM</abbr>.
It features a software-controlled termination resistor, embedded bus power supply
and bus voltage monitoring.
Zubax Babel uses the quasi-standard SLCAN (aka LAWICEL) protocol (with Zubax extensions)
for transferring CAN data over serial port.

It is primarily intended for UAVCAN applications, although other CAN bus protocols are supported equally well.
We recommend the [UAVCAN GUI Tool](http://uavcan.org/GUI_Tool) for use with Zubax Babel; however,
there is a wide selection of software products that can talk with SLCAN adapters
and therefore are compatible with Zubax Babel too.

## Characteristics

### Mechanical

The drawing below documents the basic mechanical characteristics of Zubax Babel,
such as the placement of connectors and mounting holes (click to enlarge):

<img src="drawing.png" height=500 title="Drawing, top view">

Pinout is shown on the diagram:

<img src="pinout.png" height=500 title="Zubax Babel pinout">

### General

#### Environment

Parameter               | Minimum       | Maximum       | Units         | Note
------------------------|---------------|---------------|---------------|-----------------------
Board temperature       | -40           | 85            | &deg;C        |
Relative humidity       | 0             | 100           | %RH           | Non-condensing

#### Power

Parameter       | Minimum       | Typical       | Maximum       | Units |
----------------|---------------|---------------|---------------|-------|
Supply voltage  | 4.1           | 5.0           | 5.5           | V     |
Supply current  | 30            | 50            | 80            | mA    |

#### CAN bus

Parameter                               | Minimum       | Typical       | Maximum       | Units
----------------------------------------|---------------|---------------|---------------|-------
Bit rate (manually configurable)        | 20            | 1000          | 1000          | Kbps
Bit rate (autodetect)                   |        | 1000<br/>500<br/>250<br/>125 |       | Kbps
Positive-going input threshold voltage  |               | 750           | 900           | mV
Negative-going input threshold voltage  | 500           | 650           |               | mV
Differential output voltage, dominant   | 1.5           | 2.0           | 3.0           | V
Differential output voltage, recessive  | -120          | 0             | 12            | mV

#### UART

Parameter                               | Minimum       | Typical       | Maximum       | Units
----------------------------------------|---------------|---------------|---------------|-------
Supported baud rates                    | 2400          | 115200        | 3000000       | baud/s
Low-level input voltage                 | -0.3          | 0             | 1.6           | V
High-level input voltage                | 2.1           | 3.3           | 5.5           | V
Low-level output voltage                | 0             | 0             | 0.5           | V
High-level output voltage               | 2.8           | 3.3           | 3.4           | V
Source/sink current (magnitude)         |               |               | 10            | mA

#### SMD signal pads

Parameter                               | Minimum       | Typical       | Maximum       | Units
----------------------------------------|---------------|---------------|---------------|-------
Low-level input voltage                 | -0.3          | 0             | 1.6           | V
High-level input voltage                | 2.1           | 3.3           | 5.5           | V
Low-level output voltage                | 0             | 0             | 0.5           | V
High-level output voltage               | 2.8           | 3.3           | 3.4           | V
Source/sink current (magnitude)         |               |               | 10            | mA

## Interfaces

### USB

### UAVCAN

### DroneCode Debug Port

### SMD pads

## Accessories

<img src="UAVCAN_Micro_to_DF13_adapter_cable.jpg" height=200 title="UAVCAN Micro to DF13 adapter cable (non-twisted)"
     class="thumbnail">

Zubax Orel 20 can be used with the following accesories:

* [UAVCAN Micro Patch Cable](/uavcan#UAVCAN_Micro_Patch_Cable)
* [UAVCAN Micro to DF13 Adapter Cable](/uavcan#UAVCAN_Micro_to_DF13_Adapter_Cable)

**The acessories can be purchased from [our distributors](https://zubax.com/sales-network).**

## Links

* [Purchase](https://zubax.com/sales-network)
* [Product description](http://zubax.com/product/zubax-babel)

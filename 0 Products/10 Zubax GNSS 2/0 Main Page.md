# Zubax GNSS 2

<img src="image.jpg" class="thumbnail" title="Top view">
<img src="bottom.jpg" class="thumbnail" title="Bottom view">

Zubax GNSS 2 is a high-performance positioning module for outdoor environments with doubly redundant [UAVCAN](/uavcan)
bus interface and USB.
It includes a state-of-the-art GPS/GLONASS receiver, a high-precision barometer,
and a 3-axis compass with thermal compensation.

If you're just looking for a quick-start guide, check out the [tutorials](tutorials),
but please return to this page afterwards.

Links to the firmware sources and 3D printable models are available at the bottom of this page.

## Characteristics

### Mechanical

The drawing below documents the basic mechanical characteristics of Zubax GNSS 2,
such as the placement of connectors, LED indicators and mounting holes (click to enlarge):

<img src="drawing.png" width=500 title="Drawing, bottom view">

<info>
If your Zubax GNSS 2 was supplied with a protective tape on the barometer, make sure to remove it before first use.
</info>

### General

#### Environment

Parameter               | Minimum       | Maximum       | Units | Note
------------------------|---------------|---------------|-------|------------------------------------------------------
Temperature             | -30           | 60            | &deg;C|GNSS hot start is not expected to work reliably below -20&deg;C
Magnetic field strength |               | 1.3           | Gauss |

#### Power supply

Parameter       | Minimum       | Typical       | Maximum       | Units | Note
----------------|---------------|---------------|---------------|-------|----------------------------------------------
Supply voltage  | 4.5           | 5.0           | 5.5           | V     | Any power input
Supply current  | 70            | 95            | 180           | mA    | Any power input

#### CAN bus

Parameter                               | Minimum       | Typical       | Maximum       | Units
----------------------------------------|---------------|---------------|---------------|-------
Bit rate (manually configurable)        | 20            | 1000          | 1000          | Kbps
Bit rate (autodetect)                   |        | 1000<br/>500<br/>250<br/>125 |       | Kbps
Positive-going input threshold voltage  |               | 750           | 900           | mV
Negative-going input threshold voltage  | 500           | 650           |               | mV
Differential output voltage, dominant   | 1.5           | 2.0           | 3.0           | V
Differential output voltage, recessive  | -120          | 0             | 12            | mV

#### DroneCode debug port UART

Parameter                               | Minimum       | Typical       | Maximum       | Units
----------------------------------------|---------------|---------------|---------------|-------
Low-level input voltage                 | -0.3          | 0             | 1.6           | V
High-level input voltage                | 2.1           | 3.3           | 5.5           | V
Low-level output voltage                | 0             | 0             | 0.5           | V
High-level output voltage               | 2.8           | 3.3           | 3.4           | V
Source/sink current                     |               |               | 10            | mA

### Sensor suite

#### GNSS receiver

Please refer to the specifications provided by the sensor manufacturer.

Sensor model:
[u-blox MAX-M8Q](http://www.u-blox.com/en/gps-modules/pvt-modules/max-m8-series-concurrent-gnss-modules.html)

#### Digital barometer

Please refer to the specifications provided by the sensor manufacturer.

Sensor model:
[Measurement Specialties MS5611](http://www.meas-spec.com/product/pressure/MS5611-01BA03.aspx)

#### Three-axis digital compass with thermocompensation

Please refer to the specifications provided by the sensor manufacturer.

Sensor model:
[Honeywell HMC5983](https://aerospace.honeywell.com/~/media/Images/Plymouth%20Website%20PDFs/Magnetic%20Sensors/Data%20Sheets/HMC5983_3_Axis_Compass_IC.ashx)

## Interfaces

Zubax GNSS 2 features three communication interfaces, each of which is described in detail in the subsequent parts
of this document. The interfaces are as follows:

* Doubly redundant [UAVCAN interface](#UAVCAN_interface) with two connectors for each interface.
Connector type is UAVCAN Micro connector (Molex CLIK-Mate).
* USB (CDC ACM profile, also known as virtual serial port).
Connector type is USB micro B (which is the most common USB connector).
* [DroneCode debug and diagnostics port. Connector type is DCD-M (JST SH)](/dronecode_probe).

The device can be powered via the following:

* Any single UAVCAN port
* Both UAVCAN ports simultaneously (the power supply circuit prevents direct current flow between these power inputs)
* USB

It is allowed to power the device simultaneously via USB and UAVCAN, since the power supply circuit prevents
back-powering via these interfaces.

Power supply characteristics are identical regardless of the power input used - refer to the tables below for details.

## Continuous self-diagnostics

Zubax GNSS 2 continuously monitors its own status and sensor outputs for anomalies and malfunctions.
Results of the continuous self-testing are mapped to three health codes: OK, WARNING, and ERROR.
The table below documents how the device uses health codes to report its status.

Health  | Conditions
--------|----------------------------------------------------------------------------------------------
OK      | Everything is OK; all enabled sensors are functioning properly.
WARNING | See below.
ERROR   | Sensor malfunction. The device may stop sending corresponding sensor measurements.

Possible reasons for the health being `WARNING`:

* GNSS fix quality is below the configured threshold (see [configuration parameters](#Configuration_parameters))
(disabled by default).
* Operating temperature range violation (see [characteristics](#Characteristics)).
* Magnetic field strength is too high (see [characteristics](#Characteristics)) (likely a sensor malfunction).
* Magnetic field strength vector remained zero for several seconds (likely a sensor malfunction).

## LED indication

### PPS LED

This LED indicator blinks with the rate of 1 Hz if the GNSS receiver has a navigation fix.

### Status LED

<style>
div.led {
    padding: 0 2px;
    animation-iteration-count: 1;
}
div.led:hover {
    animation-iteration-count: infinite;
}
div.led-ok {
    animation-name: led-ok;
    animation-duration: 1s;
}
div.led-warning {
    animation-name: led-warning;
    animation-duration: 0.3s;
}
div.led-error {
    animation-name: led-error;
    animation-duration: 0.1s;
}
@keyframes led-ok {
    0%   {background-color:red;}
    5%   {background-color:white;}
    100% {background-color:white;}
}
@keyframes led-warning {
    0%   {background-color:red;}
    16%  {background-color:white;}
    100% {background-color:white;}
}
@keyframes led-error {
    0%   {background-color:red;}
    50%  {background-color:white;}
    100% {background-color:white;}
}
</style>

This LED indicator shows the health of the device derived from the continuous self-diagnostics as described above:

Health  | Blinking ON/OFF duration
--------|------------------------------------------------
OK      | <div class="led led-ok">0.05/0.95 seconds</div>
WARNING | <div class="led led-warning">0.05/0.25 seconds</div>
ERROR   | <div class="led led-error">0.05/0.05 seconds</div>

### CAN1 and CAN2 LEDs

These LED indicators show the CAN bus traffic.

Each blink indicates that there was a CAN frame that was *successfully* transmitted or *successfully*
received during the last few milliseconds.
Under high bus load, these LED indicators are expected to glow steadily.
If the interface is not connected to the bus, its LED indicator will be inactive,
even if the device is actually attempting to transmit.

Note that CAN frames filtered out by the hardware acceptance filters will not cause the LED indicators to blink.

### LED indication during firmware update and bootup

During first few seconds after power-on or after restart, and also in the process of firmware update,
Zubax GNSS 2 uses its LED indicators in a different way, as described in the table below.

Status                          | INFO  | CAN1  | CAN2
--------------------------------|-------|-------|-------
CAN bit rate detection          |       | Solid |
Dynamic node ID allocation      | Solid |       |
Update in progress              | Solid | Solid |

States that are not listed in the table indicate errors.

## UAVCAN interface

This section describes the properties specific for this product only.
For general info about the UAVCAN interface, please refer to the [UAVCAN interface documentation page](/uavcan).

<info>If Zubax GNSS 2 is used in a setup with non-redundant CAN bus, only CAN1 must be used.</info>

### Mode and status codes

Zubax GNSS 2 employs the following UAVCAN-defined operating modes:

UAVCAN operating mode   | Conditions
------------------------|----------------------------------------------------------------------------------------------
INITIALIZING            | The device has just started and is not ready to begin normal operation yet.
OPERATIONAL             | This is the main operating mode.
SOFTWARE_UPDATE         | The device is undergoing firmware update via UAVCAN. It will automatically transition to OPERATIONAL mode upon completion.

While the device resides in OPERATIONAL mode, its internal health codes are mapped directly to UAVCAN health codes.
The description of internal health codes is provided above.

The following table describes the meanings of the standard UAVCAN health codes in the mode `SOFTWARE_UPDATE`.

UAVCAN health code      | Possible reasons
------------------------|----------------------------------------------------------------------------------------------
OK                      | Everything is OK.
WARNING                 | Not used.
ERROR                   | Not used.
CRITICAL                | Firmware update has failed; another attempt will be made soon.

<info>
Linux users: You can use [`uavcan_status_monitor`](http://uavcan.org/Implementations/Libuavcan/Platforms/Linux#uavcan_monitor)
to see the status code of each node on the bus.
</info>

### Time synchronization

This device can act as a
[UAVCAN-compliant time synchronization master](http://uavcan.org/Specification/6._Application_level_functions/#time-synchronization),
but this feature is disabled by default.
If time synchronization is enabled, the GNSS UTC time will be used as the time source,
which implies that the time synchronization master will be functional only if the device has had at least one
successful GNSS time fix since power on.

### Services

This device does not call any services.

The following service servers are implemented:

Data type                                       | Note
------------------------------------------------|----------------------------------------------------------------------
`uavcan.protocol.GetNodeInfo`                   | Please refer to the [identification information section](#Identification_information).
`uavcan.protocol.GetDataTypeInfo`               |
`uavcan.protocol.GetTransportStats`             |
`uavcan.protocol.RestartNode`                   |
`uavcan.protocol.file.BeginFirmwareUpdate`      | Request arguments will be ignored; the device will reboot into the bootloader shortly after receiving request.
`uavcan.protocol.param.GetSet`                  | Configuration parameters are described later in this document.
`uavcan.protocol.param.ExecuteOpcode`           | Note that this request may cause transient disruptions to output sensor feeds.

### Messages

Input:

Data type                                       | Note
------------------------------------------------|----------------------------------------------------------------------
`uavcan.protocol.GlobalTimeSync`                | Always synchronizes with network time, if present.
`uavcan.protocol.dynamic_node_id.Allocation`    | Used to allocate node ID if dynamic node ID allocation is enabled (it is enabled by defualt).

Output (publishing frequency is configurable per message type):

Data type                                       | Note
------------------------------------------------|----------------------------------------------------------------------
`uavcan.protocol.GlobalTimeSync`                | Disabled by default
`uavcan.protocol.NodeStatus`                    |
`uavcan.equipment.gnss.Fix`                     |
`uavcan.equipment.gnss.Auxiliary`               |
`uavcan.equipment.ahrs.Magnetometer`            |
`uavcan.equipment.air_data.StaticPressure`      | Disabled by default
`uavcan.equipment.air_data.StaticTemperature`   | Publication rate and priority are the same as for `uavcan.equipment.air_data.StaticPressure`. Disabled by default.
`uavcan.protocol.dynamic_node_id.Allocation`    | Used to allocate node ID if dynamic node ID allocation is enabled (it is enabled by defualt).

## USB interface

USB interface allows to use Zubax GNSS 2 as a standalone USB GNSS receiver,
and also provides access to configuration parameters.

Please refer to the [USB command line interface documentation page](/usb_command_line_interface)
for more information specific to this interface.

### Command-line interface

This section documents supported CLI commands.

#### `zubax_id`

This is the standard Zubax identification command.
It is supported by all devices that implement a command line interface.
Please refer to the [USB command line interface documentation page](/usb_command_line_interface) for more info.

#### `cfg`

Allows to view or modify configuration parameters.

Execute without arguments to get usage info. Supported arguments:

* `list` - list all parameters, their values and ranges
* `set <name> <value>` - change parameter value
* `save` - save all parameters to the non-volatile memory
* `erase` - reset all parameters to defaults

#### `reset`

Restarts the device. Note that sensors will not be restarted.

#### `gnssbridge`

Activates the direct bridge connection between USB CLI and the GNSS receiver.

Once the bridge is activated, the state of the device changes as follows until reboot:

* CLI becomes unavailable because it is being used to communicate with the GNSS receiver.
* The device stops publishing GNSS messages via UAVCAN.
* Status code changes to CRITICAL because GNSS sensor data are not available anymore.

Aside from the above, the device continues to work virtually as usual, e.g., its UAVCAN stack operates normally,
other sensors are working (if enabled), etc.

#### `help`

Print the list of available commands

## Debug port

DroneCode debug port provides access to debug interfaces: SWD and UART.
It allows to update firmware and provides access to the debug UART that is used to log events and report problems.
Debug port can be accessed using [Zubax DroneCode Probe](/dronecode_probe).

This port is not needed for normal usage of the device.

## Configuration parameters

This section documents available configuration parameters.
Read the documentation on the interfaces to learn how to access the configuration parameters.

<info>Reboot is required in order for all configuration changes to take effect.</info>

### `uavcan.bit_rate`

CAN bus bit rate, all interfaces.
Value 0 (which is default) causes the device to detect bit rate automatically at every boot up.

Default value: 0

Units: Bits/sec

### `uavcan.node_id`

UAVCAN Node ID
Value 0 (which is default) causes the device to request a dynamically allocated node ID at every boot up.

Default value: 0

### `uavcan.pubp-time`

Publication interval of `uavcan.protocol.GlobalTimeSync`. Zero means disabled.

Default value: 0

Units: Microsecond

### `uavcan.prio-time`

Priority of `uavcan.protocol.GlobalTimeSync`.

Default value: 1

### `uavcan.pubp-stat`

Publication interval of `uavcan.protocol.NodeStatus`.

Default value: 200000

Units: Microsecond

### `uavcan.prio-stat`

Priority of `uavcan.protocol.NodeStatus`.

Default value: 20

### `uavcan.pubp-pres`

Publication interval of `uavcan.equipment.air_data.StaticPressure`. Zero means disabled.
When disabled:

* The driver of the appropriate sensor will not be initialized.
* The sensor will not be monitored - implying that, if it fails, it will not be detected and reported.

This setting also affects `uavcan.equipment.air_data.StaticTemperature`.

Default value: 0

Units: Microsecond

### `uavcan.prio-pres`

Priority of `uavcan.equipment.air_data.StaticPressure`.
This setting also affects `uavcan.equipment.air_data.StaticTemperature`.

Default value: 16

### `uavcan.pubp-mag`

Publication interval of `uavcan.equipment.ahrs.MagneticFieldStrength`.

Default value: 20000

Units: Microsecond

### `uavcan.prio-mag`

Priority of `uavcan.equipment.ahrs.MagneticFieldStrength`.

Default value: 16

### `uavcan.pubp-fix`

Publication interval of `uavcan.equipment.gnss.Fix`.

Default value: 100000

Units: Microsecond

### `uavcan.pubp-aux`

Publication interval of `uavcan.equipment.gnss.Auxiliary`.

Default value: 1000000

Units: Microsecond

### `uavcan.prio-fix`

Priority of `uavcan.equipment.gnss.Fix`.

Default value: 16

### `uavcan.prio-aux`

Priority of `uavcan.equipment.gnss.Auxiliary`.

Default value: 20

### `pres.variance`

Pressure variance reported via `uavcan.equipment.air_data.StaticAirData`.

Default value: 100

Units: Pascal<sup>2</sup>

### `temp.variance`

Temperature variance reported via `uavcan.equipment.air_data.StaticAirData`.

Default value: 4

Units: Kelvin<sup>2</sup>

### `mag.variance`

Magnetic field variance reported via `uavcan.equipment.ahrs.Magnetometer`.

Default value: 0.005

Units: Gauss<sup>2</sup>

### `gnss.warn_dimens`

Set the node status to WARNING if the number of dimensions in the GNSS solution is below this threshold.
Values: 1 - time-only fix, 2 - 2D fix, 3 - 3D fix.

Default value: 0

### `gnss.warn_sats`

Set the node status to WARNING if the number of satellites used in the GNSS solution is below this threshold.

Default value: 0

## Identification information

This section documents device properties that are reported in response to identification requests:
CLI command `zubax_id` and UAVCAN service `uavcan.protocol.GetNodeInfo`.

* Product ID and UAVCAN node name: `com.zubax.gnss`.
* Hardware version: 2.x.

## Accessories

Zubax GNSS 2 can be used with the following accesories:

* [UAVCAN Micro Patch Cable](/uavcan#UAVCAN_Micro_Patch_Cable)
* [UAVCAN Micro to DF13 Adapter Cable](/uavcan#UAVCAN_Micro_to_DF13_Adapter_Cable)
* [UAVCAN Micro Termination Plug](/uavcan#UAVCAN_Micro_Termination_Plug)
* USB micro B cable (the most common type of USB cable)

<img src="UAVCAN_Micro_to_DF13_adapter_cable.jpg" height=200 title="UAVCAN Micro to DF13 adapter cable (non-twisted)">
<img src="CAN_termination_plug.jpg" height=200 title="UAVCAN Micro Termination Plug">
<img src="MicroB_USB_Plug.jpg" height=200
     title="USB micro B cable (source: wikipedia.org; owner: https://commons.wikimedia.org/wiki/User:Masamic; license: CC SA-3.0)">

**The acessories can be purchased from [our distributors](https://zubax.com/sales-network).**

## Firmware update

Note that firmware update may cause the configuration stored in the non-volatile memory to reset to defaults.

### Via UAVCAN

Zubax GNSS 2 uses PX4 UAVCAN bootloader that implements UAVCAN-compliant firmware update protocol.

Update procedure works as follows:

1. The service `uavcan.protocol.file.BeginFirmwareUpdate` (with any arguments) must be called on the device.
The device will boot into bootloader.
2. When the device is in the bootloader, the service `uavcan.protocol.file.BeginFirmwareUpdate` must be called again,
this time with properly configured fields.
3. After that, the bootloader will erase the firmware and download the new image using the service
`uavcan.protocol.file.Read`.
4. When the new firmware is downloaded and verified, the bootloader will start it.

It is safe to abort the process at any point - in this case the bootloader
will try again until a correct image is loaded.

If you're using PX4 flight stack, please
[follow these instructions](http://dev.px4.io/uavcan-node-firmware.html#placing-the-binaries-in-the-px4-romfs).

### Via DroneCode debug port

Please refer to the [DroneCode probe documentation page](/dronecode_probe) for instructions.

## Links

* [Purchase](https://zubax.com/sales-network)
* [Product description](http://zubax.com/product/zubax-gnss-2)
* [Source repository (firmware sources, 3D printable models, etc)](https://github.com/Zubax/zubax_gnss)
* [Tutorials](tutorials)
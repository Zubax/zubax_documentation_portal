# Using with Pixhawk

<img src="UAVCAN_Micro_to_DF13_adapter_cable.jpg" class="thumbnail"
     title="UAVCAN Micro to DF13 adapter cable (non-twisted)">
<img src="CAN_termination_plug.jpg" class="thumbnail" title="UAVCAN Micro termination plug">

## Overview

This tutorial shows how to connect and use [Zubax GNSS 2](/zubax_gnss_2) with [Pixhawk](http://pixhawk.org)
running APM or the native PX4 firmware.

Zubax GNSS 2 can be set up for use with any other [UAVCAN](http://uavcan.org)-enabled system in a very similar way.

### Parts needed

Aside from Zubax GNSS 2 itself and the Pixhawk it will be connected to, the following parts are needed:

* UAVCAN Micro to DF13 adapter cable
* UAVCAN Micro termination plug

The parts listed above can be purchased from [Zubax distributors](http://zubax.com/sales-network).
Alternatively, customers can choose to manufacture the needed cables/plugs on their own in order to suit some
custom needs, in which case they should refer to the relevant documentation for details.

## Configuring Zubax GNSS 2

<info>
If you're using PX4 flight software, Zubax GNSS 2 will be able to auto-configure itself, so this step can be skipped.
</info>

If you're using APM, the default configuration should be changed manually as follows:

* The parameter `uavcan.node_id` needs to be set manually
* Possibly, some functionality that is disabled by default needs to be enabled
(such as the time synchronization master or the air data sensor)

[Connect USB, open CLI](/usb_command_line_interface), then execute:

```
cfg set uavcan.node_id 50
```

This command will set the Node ID to 50.
You can use any other value as long as it doesn't conflict with other nodes.

Save the configuration into the non-volatile memory and then restart the device to apply new configuration:

```
cfg save
reboot
```

Configuration is complete.

## Configuring Pixhawk with APM firmware

<info>If you don't know what firmware you're using - you're using APM.</info>

UAVCAN driver is enabled in APM by default, but it is necessary to change some configuration parameters
to make APM listen to external UAVCAN-connected sensors.
The following chapters assume that [Mission Planner](http://planner.ardupilot.com/) is installed on the user's computer,
and that Pixhawk is otherwise properly configured.

Remember that it may be necessary to restart Pixhawk before the changes take full effect.

### GPS

In order to make APM receive measurements from an UAVCAN-interfaced GNSS receiver, set the parameter `GPS_TYPE` to 9.

<img src="mission_planner_gps_type_9.png" width=500 title="Enabling UAVCAN GPS via Mission Planner">

### Compass

In order to make APM receive measurements from an UAVCAN-interfaced compass, open the tab `INITIAL SETUP`,
then select `Mandatory Hardware` &rarr; `Compass`. On the displayed page:

* Check the checkbox `Enable`.
* In the `Orientation` frame, select the option `Manual`, `ROTATION_NONE`.
You may need to select a different rotation if the arrow printed on Zubax GNSS 2 is not aligned with
vehicle's longitudinal axis.

<img src="mission_planner_compass.png" width=500 title="Enabling external compass via Mission Planner">

Don't forget to perform compass calibration when done.

### Barometer

APM does not have proper support for external barometers, so proposed solution is a bit hackish, but it still works.
This modification is not required if external barometer is not needed.
Also, make sure that [the barometer is enabled on Zubax GNSS 2](/zubax_gnss_2#Configuration_parameters).

Power off the Pixhawk, extract its microSD card and mount it on a computer.
Create a file `etc/rc.txt` on the card and put the following script in it:

```bash
# uORB will be started again by the main init script later, it's OK
if uorb start
then
    echo "ext: uORB started"
    if uavcan start 1
    then
        echo "ext: UAVCAN started"
    else
        echo "ext: Could not start UAVCAN"
    fi
else
    echo "ext: Could not start uORB"
fi

# This delay allows UAVCAN to pick external sensors before internal ones
sleep 8
```

Insert the card back into Pixhawk.

Done, now the Pixhawk will be using barometer installed on Zubax GNSS 2,
provided that Zubax GNSS 2 was connected to the bus at the time of boot;
otherwise it will fall back to internal barometer.

## Configuring Pixhawk with PX4 firmware

Set the configuration parameter `UAVCAN_ENABLE` to 2, then reboot.

<info>All other GNSS drivers must be disabled.</info>

Please refer to the [Pixhawk documentation](http://pixhawk.org/firmware/apps/uavcan) for extra info.

## Connecting

Since Zubax GNSS 2 can be powered directly from the bus, the electrical connections are quite simple:

1. Connect Zubax GNSS 2 with Pixhawk using the appropriate cable.
In case you're using a non-redundant CAN interface (which is the only available option for Pixhawk v1),
only CAN1 must be used, leaving CAN2 empty.
2. Insert the termination plug into another connector of the used CAN interface on the Zubax GNSS 2.

Now the setup is ready to work.

## Links

* [Zubax GNSS 2 docs](/zubax_gnss_2)
* [Zubax GNSS 2 product page](http://zubax.com/product/zubax-gnss-2)
* [Where to buy parts](http://zubax.com/sales-network)

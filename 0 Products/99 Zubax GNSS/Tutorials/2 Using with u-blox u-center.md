# Using with u-blox u-center

This tutorial shows how to access the on-board GNSS receiver of [Zubax GNSS](/zubax_gnss)
via the auxiliary serial port using the
[u-center GNSS evaluation software from u-blox](http://www.u-blox.com/en/evaluation-tools-a-software/u-center/u-center.html).

## Setting up Zubax GNSS

First, connect to Zubax GNSS via the auxiliary serial port and power on; make sure CLI is available.

Then, execute the command `gnssbridge` via CLI.
In response, the device will print a message showing that it's about to get into bridge mode.
If the device is restarted after this command was executed, it will return to normal operation mode,
so make sure to not restart or power cycle it unless you want the bridge mode operation to stop.

The following shows the terminal output of the above steps:

```
ch> gnssbridge

RESET THE BOARD TO RESUME NORMAL OPERATION

GNSS driver terminated
```

The lines above will be immediately followed by raw data stream from the receiver,
which will appear as unreadable ASCII characters.

Make sure to close the terminal before continuing. Do not restart the device.

## Setting up u-blox u-center

<img src="u-center.png" title="u-blox u-center" class="thumbnail">

[u-blox u-center can be downloaded directly from u-blox.com](http://www.u-blox.com/en/evaluation-tools-a-software/u-center/u-center.html).

After installing u-center, perform the following steps:

1. Make sure the terminal is closed, and no other program has the serial port opened.
2. Start u-center.
3. Select `Receiver` &rarr; `Baudrate` &rarr; `115200`.
4. Select `Receiver` &rarr; `Port` &rarr; Your COM port.
5. Make sure it is connected now. Some data will be displayed on the panels.

Done!

While using u-center, keep in mind a few things:

* You can't change the baud rate. Attempting to do so will make the receiver inaccessible until the next power cycle.
* Avoid saving settings into the non-volatile memory of the receiver unless you know what you're doing.

<info>
Linux users: u-center runs nicely under Wine.
The serial port can be accessed via symlink at `~/.wine/dosdevices/`.
For instance: `ln -s /dev/ttyUSB0 ~/.wine/dosdevices/com5`
</info>

## Links

* [Zubax GNSS](/zubax_gnss)
* [Zubax GNSS product page](http://zubax.com/product/zubax-gnss)
* [u-center user guide](https://www.google.com/?q=u-blox+u-center+user+guide)

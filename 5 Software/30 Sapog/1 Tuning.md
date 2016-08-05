# Tuning PX4 Sapog

This tutorial covers the basics of how to configure and tune PX4 Sapog to maximize its performance with a given motor.

The tuning process requires to change configuration parameters of the device.
Depending on your setup, this can be done in a variety of ways:

* Via UAVCAN using the [UAVCAN GUI Tool](https://github.com/UAVCAN/gui_tool)
(requires a CAN adapter connected to your PC).
* Via serial <abbr title="Command Line Interface">CLI</abbr> using the command `cfg`.
Learn more [here](/sapog#Serial_CLI).
* Using other means provided by your setup.
For example, the QGroundControl ground station software allows you to alter configuration parameters remotely
via MAVLink, no extra hardware needed.

<info>
The device must be restarted in order for all configuration changes to take effect.
</info>

## Basic configuration

### Number of poles

It is recommended, but not mandatory, to specify the correct number of poles in the connected motor.
When this value is specified correctly,
Sapog will report correct <abbr title="Revolutions Per Minute">RPM</abbr> via UAVCAN and CLI interfaces.
If RPM measurements are not of interest, this parameter can be left at its default value -
it will not affect performance in any way.

The corrent number of poles can be obtained from the specification of your motor,
or it can be counted directly (number of poles equals the number of permanent magnets on the rotor).

Name of the relevant configuration parameter is `mot_num_poles`.

### Maximum current

It is recommended to configure the parameter `mot_i_max` correctly to avoid overloading the motor.
The maximum current allowed for the motor should be provided in the motor specification.

### Spinup settings

Some motors, especially high-KV motors with highly inertial loads, sometimes
cannot be started reliably with the default settings of the spinup algorithm.
If you're observing that the motor spinup is unreliable, it is recommended to
alter the following configuration parameters:

* Increment `mot_spup_cp_flt` once at a time until you've reached reliable spinup.
It is not recommended to exceed the value of 10.
* If a high voltage motor is used (nominal voltage exceeds 15V), it may be beneficial to
increase `mot_v_min` and `mot_v_spinup` to at least 10% and 20% of the nominal voltage,
respectively.
* If the motor stops shortly after spinup, further increase `mot_v_min` and possibly `mot_v_spinup`.

### Response characteristics

Sapog limits the maximum acceleration and deceleration rate of the motor to ensure reliable operation.
Better dynamic characteristics can be achieved by increasing the following configuration parameters:

* `mot_dc_slope` - number of full throttle ranges (from 0 to 1 inclusively) that the controller may
sweep in 1 second. In other words, if this parameter is set to 1, the motor may accelerate from
0% to 100% throttle in one second. If this parameter is set to 2, the motor may accelerate from
0% to 100% throttle in half a second, and so on.
* `mot_dc_accel` - if the setpoint changes by this value or less (in full range units, i.e. 0.1 is equivalent to 10%),
the controller will bypass the acceleration limiting ramp and apply the new throttle immediately.
This feature is particularly useful for applications where the throttle is changing mostly in a
very narrow range but low latency is required (e.g. multirotor applications).

## Advanced tuning

### Timing advance

In a nutshell, higher advance angle allows to increase the power output of the electric motor.
A collateral effect of increased advance angle is less reliable operation on low RPM.

In order to support both high advance angles and reliable operation on low RPM,
Sapog computes the advance angle dynamically as a linear function of commutation period,
which in turn is inversely proportional to RPM.

The following four parameters define the advance angle computation rules:

* `mot_tim_adv_min`, `mot_tim_adv_max` - minimum and maximum advance angles, in angular degrees electrical.
* `mot_tim_cp_min`,  `mot_tim_cp_max` - minimum and maximum commutation period of the interpolation range, in microseconds.

The logic is illustrated on the figure below:

<img src="timing_advance_interpolation.png" title="Timing advance interpolation logic">

The angles are specified in electrical degrees; one electrical degree is equivalent to 3 phase degrees.
For example, 90&deg; of phase advance is equivalent to 30&deg; of electrical advance.

The recommended procedure of tuning the advance angle settings is defined below.
You may skip it if you know what you're doing.

1. Find out the idle commutation period of your motor.
The commutation period (in seconds) can be derived from RPM using the following formula: `20 / (NumPoles * RPM)`,
where **NumPoles** is the number of magnetic poles in the rotor,
and **RPM** is the angular velocity of the rotor in revoltions per minute.

2. Set `mot_tim_cp_min` equal to the idle commutation period computed in the step #1.

3. Find out the commutation period when your motor is working at the nominal RPM.
Use the formula defined in the step #1 if necessary.

4. Set `mot_tim_cp_max` equal to the commutation period computed in the step #3.

5. Set `mot_tim_adv_max` to the desired advance angle at the nominal load.
This value typically can be found in the motor documentation.

Current RPM can be observed via UAVCAN message `uavcan.equipment.esc.Status`,
or via CLI using the command `stat` (use [DroneCode Probe](/dronecode_probe) to access the CLI).

### RPM governor mode

Sapog implements a closed-loop RPM control logic that can be used to maintain constant RPM of the rotor
under varying load.
This mode is especially useful for variable pitch propeller drives.

The RPM governor can be configured using the following parameters:

* `rpmctl_p`, `rpmctl_i`, `rpmctl_d` - terms **P**, **I**, **D** of the RPM PID controller, respectively.
RPM controller accepts RPM at the input and outputs the throttle value in the range
from -1.0 (full braking) through 0.0 (zero throttle) to 1.0 (full throttle).

* `mot_rpm_min` - minimum stable RPM of the rotor.
The setpoint will be clamped to be no less than this value, i.e. `Setpoint = max(mot_rpm_min, UnclampedSetpoint)`.

Note that the output of the RPM PID controller is limited by the acceleration ramp (see above).

### Number of restart attempts

If the controller could not start the motor after a specified number of attempts,
it will stop and lock up until the setpoint is reset to zero again.
The number of attempts can be configured via `mot_stop_thres`.

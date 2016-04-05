# Sapog BLDC Controller Firmware

Sapog is an advanced open source multiplatform BLDC motor controller firmware for electric aerial vehicles.

## Overview

### Design goals

The Sapog firmware has been designed with the following core design goals in mind.

#### High reliability

The firmware employs a reliable multi-point back EMF sensing method with least squares fitting that enables
precise and reliable tracking of the rotor position.
Health of the power stage is monitored during operation and at power on, and reported via
doubly redundant CAN bus.

#### Good response characteristics

<img src="sapog-dynamics.png" class="thumbnail"
     title="Dynamic characteristics captured with a 13x4.5 inch propeller">

Sapog has been designed with multirotor applications in mind, where good response characteristics are
critical.
This is achieved by the reliable rotor position tracking algorithm and capability of regenerative braking.

### Hardware requirements

The Sapog firmware can be used with any hardware based on the microcontroller STM32F105RCT with compatible
wiring.
The wiring diagram will be published soon.

## Self-diagnostics

The firmware maps its status and the hardware health onto the following set of health and mode codes.

### Operating modes

- `INITIALIZATION` - The firmware is initializing.
- `OPERATIONAL` - The firmware is operating.
- `SOFTWARE_UPDATE` - The firmware is updating itself via the bootloader.

### Health codes

- `OK` - This status code is reported when the firmware and the hardware are functioning normally.
- `CRITICAL` - This status code is reported if any of the following conditions are true:
    - The motor cannot be started.
    - The temperature sensor is not responding correctly.

### Power-on self test

Sapog performs a self test after powering on.
If the self test was successfull, the firmware will enter the normal operating mode.
If the self test was unsuccessful, detailed information will be printed to the CLI,
the firmware will abort initialization, and then it will reboot a few seconds later.
The reboot loop will continue indefinitely until the cause of the self test failure is removed.

The following components are tested during the self test:

- Power stage drivers and transistors.
- Back EMF sensing channels.
- Cross-phase short circuit (only if the motor is not connected).

## Configuration parameters

### Motor control settings

Duty cycle is defined in the range [0, 1]. All RPM refers to mechanical RPM.

#### High-level settings

##### `mot_v_min`

Minimum phase voltage needed for stable rotation of the motor.

Units: Volts.

##### `mot_dc_accel`

Maximum step change of the duty cycle.
If larger change is requested, slope pacing will be used.

Units: duty cycle units.

##### `mot_dc_slope`

If change of the duty cycle larger than `mot_dc_accel` is requested, the controller
will pace the duty cycle change at the rate defined by this configuration parameter.

Units: duty cycle units per second.
E.g. value 2 defines that the controller will pace the duty cycle from 0 to 1 in 0.5 seconds.

##### `mot_num_poles`

Number of magnetic poles in the motor.
Must be an even number.

##### `ctl_dir`

Direction of rotation: 1 - forward, 0 - reverse.

##### `mot_rpm_min`

Minimum mechanical RPM needed for stable rotation of the motor.

Units: RPM.

##### `mot_i_max`

Maximum DC motor current.

Units: Amperes.

##### `mot_i_max_p`

Motor current limiting factor, in the form of the duty cycle reduction per every Ampere above the limit.

Units: duty cycle units per Ampere.

##### `mot_lpf_freq`

Voltage and current low-pass filter corner frequency.

Units: Hertz.

##### `mot_stop_thres`

Number of unsuccessfull attemts to start the motor before locking up.

The lock can be removed by setting the target duty cycle or RPM to zero.

#### BLDC commutation settings

##### `mot_tim_adv`

Commutation advance angle.

Units: angular degrees.

##### `mot_blank_usec`

Blank time after commutation.

Units: microseconds.

##### `mot_bemf_win_den`

Refer to the implementation.

##### `mot_bemf_range`

Refer to the implementation.

##### `mot_zc_fails_max`

When this number of successive zero cross detection failures is reached, the motor will be stopped.

##### `mot_zc_dets_min`

When this number of successful zero crossings is detected, the motor is assumed to have reached
stable RPM.

##### `mot_comm_per_max`

Maximum commutation period.

Units: microseconds.

#### Spinup settings

##### `mot_spup_to_ms`

If the motor could not reach stable rotation in this time, spinup will be aborted.

Units: milliseconds.

##### `mot_spup_st_cp`

Initial commutation period during spinup.

Units: microseconds.

##### `mot_spup_en_cp`

Final commutation period during spinup.

Units: microseconds.

##### `mot_spup_gcomms`

After this number of good zero cross detections the spinup will be considered finished.

##### `mot_spup_dc_inc`

Duty cycle increment during spinup.

Units: duty cycle units.

#### Closed-loop RPM control settings

##### `rpmctl_p`

RPM to duty cycle PID controller - P coefficient.

##### `rpmctl_d`

RPM to duty cycle PID controller - D coefficient.

##### `rpmctl_i`

RPM to duty cycle PID controller - I coefficient.

### RCPWM input settings

##### `pwm_enable`

Whether to enable RCPWM input capture. Disabled by default.

##### `pwm_min_usec`

RCPWM pulse duration that matches zero setpoint.

Units: microseconds.

##### `pwm_max_usec`

RCPWM pulse duration that matches maximum setpoint.

Units: microseconds.

### UAVCAN node settings

See details at the [UAVCAN page](/uavcan) and at <http://uavcan.org>.

#### General

##### `uavcan_node_id`

Node ID of the local UAVCAN node.

#### ESC control

##### `esc_index`

Index of the current ESC.

##### `cmd_ttl_ms`

Command expiration time.

Units: milliseconds.

##### `cmd_start_dc`

The motor will not start if the initial duty cycle value was above this value.

#### Indication control

##### `light_index`

Index of the current ESC's RGB LED.

## UAVCAN interface

## RCPWM interface

## Serial CLI

## Indication



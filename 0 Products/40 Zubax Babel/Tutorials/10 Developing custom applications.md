# Developing custom applications #
Ok, you have your Zubax babel and want it to do something special. First of all you will need babel firmware source code, which can be found [here](https://github.com/Zubax/zubax_babel)
In order to build babel firmware *nix-environment will be needed.  If you use any kind of Linux - good for you, you probably already have everything needed(except for gnu arm toolchain). If (like me) you have only win machine, you will need:

- [git](https://git-scm.com/download/win)
- gnu utilities, which may be found [here](http://gnuwin32.sourceforge.net/)
- [Python 3+](https://www.python.org/downloads/)
- gnu arm toolchain. It is very version-dependant, so you should use [this version](https://launchpad.net/gcc-arm-embedded/4.9/4.9-2015-q3-update)

After you download and install everything make sure you have all these your environment variable PATH set up correctly and have access to all necessary utilities from console. For example, my PATH variable looks like this:

<img src="path.png" class="thumbnail" title="PATH">

Now its time to try to build the original firmware. Go to console and clone the repository

```git clone https://github.com/Zubax/zubax_babel```

Then follow [instructions from the repository](https://github.com/Zubax/zubax_babel/blob/master/firmware/src/board/board.hpp). If everything is fine, you will find file compound.elf in directory `/%reponame%/firmware/build/`. This is firmware in binary form, which may be loaded to the device with Drone code probe. 
You should try that. There are two ways of loading firmware to the device: 

- Using DroneCode probe(DCP)
- Using bootloader

## Loading firmware in windows environment ##
### Loading with DCP ###
Go to terminal and start gdb
`C:\Users\j3qq4hch>arm-none-eabi-gdb`
Then connect to DCP load your firmware and run it

```
(gdb) tar ext COM6
Remote debugging using COM6
(gdb) mon swdp_scan
Target voltage: 4.4V
Available Targets:
No. Att Driver
1  STM32F3
(gdb) file C:\\zubax_babel\\firmware\\build\\compound.elf
Reading symbols from C:\zubax_babel\firmware\build\compound.elf...warning: Loadable section "bootloader" outside of ELF segments
done.
(gdb) attach 1
Attaching to program: C:\zubax_babel\firmware\build\compound.elf, Remote target
0x0800d9fe in watchdogReset (id=id@entry=0) at zubax_chibios///zubax_chibios/platform/stm32/watchdog_stm32.cpp:139
139 if ((_mask & valid_bits_mask) == valid_bits_mask)
(gdb) load
Loading section bootloader, size 0x5571 lma 0x8000000
Loading section startup, size 0x1c0 lma 0x8008000
Loading section constructors, size 0x4 lma 0x80081c0
Loading section .padding1, size 0x1c lma 0x80081c4
Loading section .text, size 0x7c48 lma 0x80081e0
Loading section .data, size 0x90 lma 0x800fe28
Loading section .noinit, size 0x8 lma 0x800feb8
Start address 0x80081e0, load size 54321
Transfer rate: 16 KB/sec, 890 bytes/write.
(gdb) run
The program being debugged has been started already.
Start it from the beginning? (y or n) y
Starting program: C:\zubax_babel\firmware\build\compound.elf
```
### Loading with bootloader ###
coming soon

----------
## Loading firmware in *nix environment ##
### Loading with DCP ###
### Loading with bootloader ###
----------

## Tutorials ##

### Blink ###

A couple words about general code organisation must be said first.
Zubax Babel firmware uses ChibiOS and therefore this tutorial also relies on ChibiOS and its HAL in particular.
Firmware is written in C++, but it is OK to write in C too. 
As in any OS code is organised as threads which are executed in a pseudo-parallel way. Each thread is represented as separate endless function, which is called by the OS-scheduler according to its rules and desires. If you are interested how ChibiOS works (and even if not), it is highly recommended to read tutorial and manuals from [here](http://www.chibios.org/dokuwiki/doku.php?id=chibios:documentation:start). 

Finally, lets start.
We should begin with writing HELLO_WORLD for MCU - blinking an onboard LED. According to babel schematic one of the LEDs is connected to `pin8` of `PORTE`. Let’s blink it. Create blink function. Something like this:


```c
static THD_WORKING_AREA(waThread1, 128);
static THD_FUNCTION(blink_thread, arg) 
{   
    (void)arg;
    chRegSetThreadName("blinker"); 
    palSetPadMode(GPIOE, 8, PAL_MODE_OUTPUT_PUSHPULL);
    while (true) 
    {
        palSetPad(GPIOE,8);
        chThdSleepMilliseconds(100);
        palClearPad(GPIOE, 8);
        chThdSleepMilliseconds(100);
    }
}
```
Now find function ```int main()``` in ```zubax_babel\firmware\src\main.cpp```. This is program entry point. Comment it all and write your own version like this:

```c
int main()
{ 
    auto watchdog = app::init();	
    chThdCreateStatic(waThread1, sizeof(waThread1), NORMALPRIO+1, blink_thread,  NULL);
    while(1)
    {
        watchdog.reset();
    }
}
```
Now compile and load it and watch red LED blinking. 

---
### BREATH ###
Now we have blinking led, but I find it a little bit rough. Let’s make it glow. We will need PWM. According to babel schematic one of the LEDS is connected to channel4 of timer3.
In order to enable timer3 pwm generation ChibiOS must be configured a little bit. 


Find macro `HAL_USE_PWM` in `halconf.h` and make it `TRUE`

Find macro `STM32_PWM_USE_TIM3` in `mcuconf.h` and make it `TRUE`

Now add `breath_thread` to you code: 
```c
static PWMConfig pwmcfg =	//initialization structure for ChibiOS PWM hal 
{
    10000,        //10KHz PWM clock frequency.   
    255,          //255 ticks is pwm resolution
    NULL,
    {
        {PWM_OUTPUT_DISABLED, NULL},
        {PWM_OUTPUT_DISABLED, NULL},
        {PWM_OUTPUT_DISABLED, NULL},
        {PWM_OUTPUT_ACTIVE_HIGH, NULL}
    },
    /* HW dependent part.*/
    0,
    0
};

static THD_WORKING_AREA(waThread2, 255);
static THD_FUNCTION(breath_thread, arg) 
{
    (void)arg;
    uint8_t brightness = 0;
    chRegSetThreadName("breath");
    palSetPadMode(GPIOB, 1, PAL_MODE_ALTERNATE(2));
    pwmStart(&PWMD3, &pwmcfg);  			//Timer activation in PWM mode
    pwmEnableChannelI(&PWMD3, 3, 128);	//Brightness setting
    while (true) 
    {   
        while (brightness <= 250)
        {
            pwmEnableChannelI(&PWMD3, 3, brightness++);
            chThdSleepMilliseconds(3);
        }
        while (brightness >= 5)
        {
            pwmEnableChannelI(&PWMD3, 3, brightness--);
            chThdSleepMilliseconds(3);
        }
    }
}
```
And change your ```main()``` to start this thread: 
```c
int main()
{
    auto watchdog = app::init();	
    chThdCreateStatic(waThread1, sizeof(waThread1), NORMALPRIO+1, blink_thread,  NULL);
    chThdCreateStatic(waThread2, sizeof(waThread2), NORMALPRIO+1, breath_thread, NULL);
    while(1)
    {
        watchdog.reset();
    }
}
```    

Load it and watch green led blinking ON and OFF and red led smoothly chaging its brightness. Isn’t it fancy?

---
### Command line interface(CLI) ###
coming soon

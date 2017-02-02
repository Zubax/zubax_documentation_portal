# Developing custom applications #
Zubax Babel is a miniature USB-CAN adapter.  But beside its direct purpose it can also be used as a development board for custom applications. To start with this Babel firmware source code is needed. It can be found [here](https://github.com/Zubax/zubax_babel)
In order to build babel firmware *nix-environment will be needed.  If you use any kind of Linux -  you probably already have everything needed(except for gnu arm toolchain). If you have win machine, you will need:

- [git](https://git-scm.com/download/win)
- gnu utilities, which may be found [here](http://gnuwin32.sourceforge.net/)
- [Python 3+](https://www.python.org/downloads/)
- gnu arm toolchain. It is very version-dependant, so you should use [this version](https://launchpad.net/gcc-arm-embedded/4.9/4.9-2015-q3-update)

After you download and install everything make sure you have all these your environment variable PATH set up correctly and have access to all necessary utilities from console. For example, PATH variable should look like this:

<img src="path.png" class="thumbnail" title="PATH">

Now its time to try to build the original firmware. Go to console and clone the repository

`git clone https://github.com/Zubax/zubax_babel`

Then follow [instructions from the repository](https://github.com/Zubax/zubax_babel/blob/master/firmware/src/board/board.hpp). If everything is fine, you will find files `*****.application.bin` and `compound.elf` in directory `/%reponame%/firmware/build/`.  `compound.elf` includes application firmware and bootloader. Normally you should never avoid using bootloader and all further applications described here include it too. `compound.elf` may be loaded to the device with Drone code probe via SWD interface. `*****.application.bin` is application only in binary form and can be loaded to the device using bootloader. More details below


## Loading firmware ##
### Loading with DCP ###
Go to terminal and start gdb
`>arm-none-eabi-gdb`
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
Babel's firmware includes a bootloader, which can be used over USB, UART of CAN interfaces. Good description of it can be found [here](https://docs.zubax.com/zubax_babel#Bootloader)
In short: bootloader is activated each time Babel is reset and waits for commands for some time. It also checks if there is a valid application in flash memory. If bootloader receives no commands and finds valid application in flash, it passes control to the application. Otherwise Babel stays in bootloader waiting for commands. If you don't modify command line interface from original Babel's firmware, you can use script `flash_via_serial_bootloader.sh` to update firmware(note: this will only work in *nix-environmet). 
But if your application does not include any kind of command line interface and you have no way to reset Babel in software, there is another script to use bootloader: `bare_bootloader.py`. To use it you have to know Babel's name in system(e.x. COM3). You should first start script: `python bare_bootloader.py -p COM3 -f C:\tmp\application.bin` and then connect Babel to USB of your PC. Script will recognize it and upload the firmware. 
All scripts descrivbed may be found in `\zubax_chibios\tools` directory
Note: It is important to remember that hardware watchdog is activated in bootloader thus care must be taken to reset it in application. 

## Tutorials ##

### Blink (in C) ###

A couple words about general code organisation must be said first.
Zubax Babel firmware uses ChibiOS and therefore this tutorial also relies on ChibiOS and its HAL in particular.
Firmware is written in C++ and you should use C++ too . 
As in any OS code is organised as threads which are executed in a pseudo-parallel way. Each thread is represented as separate endless function, which is called by the OS-scheduler according to its rules and desires. It is highly recommended to read [ChibiOS tutorial and manuals](http://www.chibios.org/dokuwiki/doku.php?id=chibios:documentation:start). 

You should find a bootloader descriptor structure somewhere in the beginning of `main.cpp`. It will look like this:
```C++
namespace app
{
namespace
{
/**
 * This is the Brickproof Bootloader's app descriptor.
 * Details: https://github.com/PX4/Firmware/tree/nuttx_next/src/drivers/bootloaders/src/uavcan
 */
static const volatile struct __attribute__((packed))
{
    std::uint8_t signature[8]   = {'A','P','D','e','s','c','0','0'};
    std::uint64_t image_crc     = 0;
    std::uint32_t image_size    = 0;
    std::uint32_t vcs_commit    = GIT_HASH;
    std::uint8_t major_version  = FW_VERSION_MAJOR;
    std::uint8_t minor_version  = FW_VERSION_MINOR;
    std::uint8_t reserved[6]    = {0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF};
} _app_descriptor __attribute__((section(".app_descriptor")));
}
}
```
This structure is needed for proper bootloader operation and should not be deleted. This structure is what defines a valid application. It will be excluded from further code examples to make them shorter but you must be aware, that this structure must be present in `main.cpp`. With this said it is finally time to proceed to practice.

You should begin with writing HELLO_WORLD for MCU - blinking an onboard LED. According to Babel schematic one of the LEDs is connected to `pin8` of `PORTE`. Create a blink thread:

```c++
class BlinkerThread : public chibios_rt::BaseStaticThread<128>
{
    void main() override
    {
        setName("blinker");
        palSetPadMode(GPIOE, 8, PAL_MODE_OUTPUT_PUSHPULL);
        while (true)
        {
            palSetPad(GPIOE,8);
            chThdSleepMilliseconds(100);
            palClearPad(GPIOE, 8);
            chThdSleepMilliseconds(100);
        }
    }

public:
    virtual ~BlinkerThread() { }
} blinker_thread_;
```
And start it from `main()`
```c++
int main()
{  
  blinker_thread_.start(NORMALPRIO + 1);
  while(1){}
}
```
Build and flash the firmware. If everything is fine, you should see red led blinking.

---
### BREATH (basic PWM) ###
The easiest way to test PWM is to use another onboard LED which is connected to one of the MCU timers. According to Babel schematic one of the LEDS is connected to channel4 of timer3. Prior to using timer3 pwm generation ChibiOS must be configured. 
Find macro `HAL_USE_PWM` in `halconf.h` and make it `TRUE`.
Find macro `STM32_PWM_USE_TIM3` in `mcuconf.h` and make it `TRUE`.
Now add `breath_thread` to you code: 
```c++
static const PWMConfig pwmcfg = {
  10000, //10KHz PWM clock frequency.   
  255, //255 ticks is pwm resolution                                    
  NULL,
  {
    {PWM_OUTPUT_DISABLED, NULL},
    {PWM_OUTPUT_DISABLED, NULL},
    {PWM_OUTPUT_DISABLED, NULL},
    {PWM_OUTPUT_ACTIVE_HIGH, NULL}
  },
  0,
  0
};

 class BreatheThread : public chibios_rt::BaseStaticThread<128>
{
    void main() override
    {
    setName("breath");
    uint8_t brightness = 0;
    palSetPadMode(GPIOB, 1, PAL_MODE_ALTERNATE(2));
    pwmStart(&PWMD3, &pwmcfg);
    pwmEnableChannelI(&PWMD3, 3, 128);

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

public:
    virtual ~BreatheThread() { }
} breathe_thread_; 
```
And change your `main()` to start this thread: 
```c++
int main()
{  
  blinker_thread_.start(NORMALPRIO + 1);
  breathe_thread_.start(NORMALPRIO + 1);
  while(1){}
}
```    
Build firmware, flash it and if everything is fine you should  watch green led blinking ON and OFF and red led smoothly chaging its brightness. 

---
---

### Command line interface(CLI) ###
There is access to `USART1` and `USART3` on Babel PCB. `USART3` may be found on CAN pins. `USART1` is available on debug connector and dedicated edge pins. We will use `USART1` further, but there is not much difference since it is the same hardware. You can use dronecode probe to connect to `USART1` via debug connector or you can use any USB-UART adapter(IMPORTANT NOTE: using USB-RS232 adapter may damage your Babel) to connect via edge pads. 
<img src="dcp.jpg" class="thumbnail" title="usb-uart">
Connect its `RX` to `TX` of `USART1` and `TX` to `RX` of `USART1`

There are two ways to use USARTs in ChibiOS: relative high-level using Serial Driver and low-level using Uart Driver. In this tutorial Serial Driver will be used. First enable serial driver `SD1` associated with `USART1` by finding string  `#define STM32_SERIAL_USE_USART1    FALSE` and making it `#define STM32_SERIAL_USE_USART1    TRUE` in `mcuconf.h`
To test if it is working lets make HelloWorld routine, which will just send a string to serial interface every 0.5 sec.
```c++
char data[] = "Hello World !\r\n";
class HelloWorldThread : public chibios_rt::BaseStaticThread<128>
{
   void main() override
   {
      setName("Hello");
      while (true)
      {
         sdWrite(&SD1, (uint8_t *) data, strlen(data)); 
         chThdSleepMilliseconds(100);
      }
}

public:
    virtual ~HelloWorldThread() { }
} hello_world_thread_;
```
And change your `main()` to start this thread:

```c++
static SerialConfig uartCfg = //Init structure for serial driver. Only baudrate is crucial for now
{
    9600, // baudrate
    0,
    0,
    0
};

int main()
{  
    halInit();
    chSysInit();
    palSetPadMode(GPIOA, 9,  PAL_MODE_ALTERNATE(7)); //Config pin PA9 for uart use
    palSetPadMode(GPIOA, 10, PAL_MODE_ALTERNATE(7)); //Config pin PA10 for uart use
    sdStart(&SD1, &uartCfg);

	blinker_thread_.start(NORMALPRIO + 1);
    breathe_thread_.start(NORMALPRIO + 1);
    hello_world_thread_.start(NORMALPRIO + 1);
    while(1){}
}
```
You must see something like that in your terminal:
<img src="hello_world.png" class="thumbnail" title="Terminal">
If terminal is empty - check your connections and try again.

Now its time to read something from `SD1`. Lets write a simple thread, that reads one symbol from serial interface and writes it back. 
```c++
class LoopbackThread : public chibios_rt::BaseStaticThread<128>
{
    void main() override
    {
        setName("Loopback");
        uint8_t c;
        sdWrite(&SD1, (uint8_t *) "Give me something\r\n", strlen("Give me something\r\n")); 
        while (true) 
        {
            sdRead (&SD1, &c, 1);
            sdWrite(&SD1, (uint8_t *) "You gave me: ", strlen("You gave me: ")); 
            sdWrite(&SD1, &c, 1); 
            sdWrite(&SD1, (uint8_t *) "\r\n", 2); 
        }
    }
public:
    virtual ~LoopbackThread() { }
} loopback_thread_;
```
And change your `main()` to launch it instead of `hello_world_thread_`
```c++
static SerialConfig uartCfg = //Init structure for serial driver. Only baudrate is crucial for now
{
    9600, // baudrate
    0,
    0,
    0
};

int main()
{  
    halInit();
    chSysInit();
    palSetPadMode(GPIOA, 9,  PAL_MODE_ALTERNATE(7)); //Config pin PA9 for uart use
    palSetPadMode(GPIOA, 10, PAL_MODE_ALTERNATE(7)); //Config pin PA10 for uart use
    sdStart(&SD1, &uartCfg);

	blinker_thread_.start(NORMALPRIO + 1);
    breathe_thread_.start(NORMALPRIO + 1);
    //hello_world_thread_.start(NORMALPRIO + 1);
    loopback_thread_.start(NORMALPRIO + 1);
    while(1){}
}
```
Now open the terminal, flash the firmware and hit any button on the keyboard. You must see something like this:
<img src="loopback.png" class="thumbnail" title="loopback">
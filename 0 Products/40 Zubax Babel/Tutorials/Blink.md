# BLINK #

A couple words about general code organisation must be said first.
Zubax Babel firmware uses ChibiOS and therefore this tutorial also relies on ChibiOS and its HAL in particular.
Firmware is written in C++, but it is OK to write in C too. 
As in any OS code is organised as threads which are executed in a pseudo-parallel way. Each thread is represented as separate endless function, which is called by the OS-scheduler according to its rules and desires. If you are interested how ChibiOS works(and even if not), it is highly recommended to read tutorial and manuals from [here](http://www.chibios.org/dokuwiki/doku.php?id=chibios:documentation:start). 

Finally lets start.
We should begin with writing HELLOWORLD for MCU - blinking an onboard LED. According to BABEL schematic one of the LEDs is connected to pin8 of portE. Let’s blink it. Create blink function. Something like this:


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

Now find function `int main()` in zubax_babel\firmware\src\main.cpp. This is program entry point(kinda). Comment it all and write your own version like this:


    int main()
    { 
     auto watchdog = app::init();	
     chThdCreateStatic(waThread1, sizeof(waThread1), NORMALPRIO+1, blink_thread,  NULL);
     while(1)
    {
    	watchdog.reset();
    }
    }


Now load it and watch red LED blinking. 
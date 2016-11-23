# BREATH #


Now we have blinking led, but I find it a little bit rough. Let’s make it not just blink but breathe(like you know what). We will need PWM. According to babel schematic one of the LEDS is connected to channel4 of timer3.
In order to enable timer3 pwm generation ChibiOS must be configured a little bit. 


Find macro `HAL_USE_PWM` in halconf.h and make it `TRUE`

Find macro `STM32_PWM_USE_TIM3` in mcuconf.h and make it `TRUE`

Now add breath_thread to you code: 

    static PWMConfig pwmcfg =	//initialization structure for ChibiOS PWM hal 
     {
      10000,//10KHz PWM clock frequency.   */
      255, //255 ticks is pwm resolution
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
    static THD_FUNCTION(breath_thread, arg) {
    
    
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







And change your main() to start this thread:
  
      int main(){
     
      auto watchdog = app::init();	
       
      chThdCreateStatic(waThread1, sizeof(waThread1), NORMALPRIO+1, blink_thread,  NULL);
      chThdCreateStatic(waThread2, sizeof(waThread2), NORMALPRIO+1, breath_thread, NULL);
      
      while(1)
	    {
	    watchdog.reset();
	    }
    }
	    

Load it and watch green led blinking ON and OFF and red led smoothly chaging its brightness. Isn’t it fancy?



# Developing custom UAVCAN applications #

Lightweight protocol designed for reliable communication in aerospace and robotic applications via CAN bus.

In this tutorial creation of a custom UAVCAN-application will be shown. It is supposed that at this point you have everything needed to compile and flash firmware to Zubax Babel.
It is highly recommended to have a look at UAVCAN documentation, which may be found [here](http://uavcan.org/Specification/1._Introduction/)
First thing you need is UAVCAN library itself. It should be put to the firmware source code root directors(e.g. /zubax_babel/custom_app_template). Clone UAVCAN
```
cd C:\zubax_babel\custom_app_template 
git clone https://github.com/UAVCAN/libuavcan
cd libuavcan
git submodule update --init
```

In order to compile UAVCAN you should mention it in `Makefile`. Add following text to your `Makefile`

```
#
# UAVCAN library
# On CAN IRQ priority read this: http://forum.chibios.org/phpbb/viewtopic.php?f=25&t=3085
#

UDEFS += -DUAVCAN_STM32_TIMER_NUMBER=7          \
         -DUAVCAN_STM32_NUM_IFACES=1            \
         -DUAVCAN_STM32_CHIBIOS=1               \
         -DUAVCAN_CPP_VERSION=UAVCAN_CPP11      \
         -DUAVCAN_STM32_IRQ_PRIORITY_MASK=4

include libuavcan/libuavcan/include.mk
CPPSRC += $(LIBUAVCAN_SRC)
UINCDIR += $(LIBUAVCAN_INC)

include libuavcan/libuavcan_drivers/stm32/driver/include.mk
CPPSRC += $(LIBUAVCAN_STM32_SRC)
UINCDIR += $(LIBUAVCAN_STM32_INC)

$(info $(shell $(LIBUAVCAN_DSDLC) $(UAVCAN_DSDL_DIR)))
UINCDIR += dsdlc_generated
``` 
Make sure you have proper defines in `UDEFS`. For example, by default UAVCAN has 'DUAVCAN_STM32_NUM_IFACES' set to `2`. But in Babel there is only one CAN interface, so it should be `1`.
Now try to build it.

### Simple node that does nothing ###
Let's now build the simplest possible node that will do nothing but periodically sending its status.  

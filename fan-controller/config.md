# pwm_control.py
This program controls a PWM fan curve based on temp input from a DHT sensor module.

## Dependencies:
* RPi.GPIO
* rpi-hardware-pwm
* Adafruit_DHT

## Device Config:
* Add "dtoverlay=pwm-2chan" to /boot/config.txt (or /boot/firmware/usercfg.txt if using Ubuntu)

## Notes:
* You'll want to set your GPIO pins based on your specific configuration. These are set via variables in the .py file.
* PWM tach readings can be wildly inaccurate on RPi if you do not use a microcontroller. Do not rely on them; they are for reference only.

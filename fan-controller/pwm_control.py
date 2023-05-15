
# Import statements
import Adafruit_DHT
from rpi_hardware_pwm import HardwarePWM
import RPi.GPIO as GPIO
import time
import signal
import sys
import logging


# Configure GPIO Pins
pwm_chan = 0 # GPIO 12 and 18 are PWM 0 - GPIO 13 and 19 are PWM 1
fan_tach_pin = 23
dht_sensor_pin = 10
dht_sensor_type = Adafruit_DHT.DHT22


# Configure PWM frequency
pwm_freq = 25000


# Define fan curve
percent_at_20c = 20
percent_at_25c = 40
percent_at_30c = 60
percent_at_35c = 80
percent_at_40c = 100


# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
log_formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s')
log_stream_handler = logging.StreamHandler()
log_stream_handler.setFormatter(log_formatter)
logger.addHandler(log_stream_handler)


# Configure GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)


## Functions

def read_speed(n):

    global fan_tach_time
    global fan_tach_rpm

    dt = time.time() - fan_tach_time
    if dt < 0.005: return

    freq = 1 / dt
    fan_tach_rpm = (freq * 60) / 2
    fan_tach_time = time.time()

def cleanup(signum, frame):
    
    fan_pwm.stop()
    GPIO.cleanup()
    sys.exit(0)

def main():

    fan_pwm.start(100)

    while True:

        humidity, temp = Adafruit_DHT.read_retry(dht_sensor_type, dht_sensor_pin)

        if temp is not None and humidity is not None:
            if temp <= 20:
                duty_cycle = percent_at_20c
            elif temp <= 25:
                temp_delta_percent = (((temp - 25) + 5) * 2) / 10
                temp_range = percent_at_25c - percent_at_20c
                duty_cycle = round(temp_range * temp_delta_percent + percent_at_20c)
            elif temp <= 30:
                temp_delta_percent = (((temp - 30) + 5) * 2) / 10
                temp_range = percent_at_30c - percent_at_25c
                duty_cycle = round(temp_range * temp_delta_percent + percent_at_25c)
            elif temp <= 35:
                temp_delta_percent = (((temp - 35) + 5) * 2) / 10
                temp_range = percent_at_35c - percent_at_30c
                duty_cycle = round(temp_range * temp_delta_percent + percent_at_30c)
            elif temp <= 40:
                temp_delta_percent = (((temp - 40) + 5) * 2) / 10
                temp_range = percent_at_40c - percent_at_35c
                duty_cycle = round(temp_range * temp_delta_percent + percent_at_35c)
            else:
                duty_cycle = 100

            fan_pwm.change_duty_cycle(duty_cycle)

            time.sleep(3)
        
            logger.info(f"Temp(c): {round(temp, 2)} - Humidity (RH%): {round(humidity)} - Duty Cycle(%): {duty_cycle} - RPM: {round(fan_tach_rpm, 2)}")
        else:
            logger.info("Erroneous reading from DHT sensor. Setting fan to 100%. Trying again.")

            fan_pwm.change_duty_cycle(100)
            
            time.sleep(3)


# Configure signal handlers
signal.signal(signal.SIGTERM, cleanup)
signal.signal(signal.SIGINT, cleanup)


### These global vars are required so signal can cleanup with a handler

# Configure fan pwm
fan_pwm = HardwarePWM(pwm_chan, pwm_freq)


# Configure tach
fan_tach_time = time.time()
fan_tach_rpm = 0
GPIO.setup(fan_tach_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.add_event_detect(fan_tach_pin, GPIO.FALLING, read_speed)


# Main program execution
if __name__ == "__main__":
    main()

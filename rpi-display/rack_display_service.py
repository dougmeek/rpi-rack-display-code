from gpiozero import Button
import subprocess
import sys
import time
import logging
import signal

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

log_formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(name)s:%(message)s')

# log_file_handler = logging.FileHandler('logging.log')
# log_file_handler.setLevel(logging.ERROR)
# log_file_handler.setFormatter(log_formatter)
# logger.addHandler(log_file_handler)

log_stream_handler = logging.StreamHandler()
log_stream_handler.setFormatter(log_formatter)
logger.addHandler(log_stream_handler)


# Sets global variables
large_change_unit_threshold = 20
large_change_unit = 3
small_change_unit_threshold = 5
small_change_unit = 1
bl_power_file = "/sys/class/backlight/rpi_backlight/bl_power"
brightness_file = "/sys/class/backlight/rpi_backlight/brightness"

# Sets the GPIO pin for the button
button = Button(2)


# Gets the current power state of the screen
def _get_power_state():
    try:
        with open(bl_power_file, 'r') as f:
            state = bool(f.read())
            f.close()
    except FileNotFoundError as error:
        logger.error(error)
        sys.exit(1)
    logger.debug("Raw power state: %s (RPi reverse logic)" % state)

    # RPi screen uses backwards logic, thus 0 equals on and 1 equals off
    if state:
        powered_on = False
    else:
        powered_on = True
    
    logger.debug("Power state: %s" % powered_on)
    return powered_on

# Writes the new power state
def _write_power_state(powered_on):
    logger.debug("Desired power state: %s" % powered_on)

    # RPi screen uses backwards logic, thus 0 equals on and 1 equals off
    if powered_on:
        state = int(False)
    else:
        state = int(True)

    logger.debug("Setting raw power state data: %s (RPi reverse logic)" % state)
    try:
        with open(bl_power_file, 'w') as f:
            f.write(str(state))
    except FileNotFoundError as error:
        logger.error(error)
        sys.exit(1)

# Gets the current brightness level
def _get_brightness():
    try:
        with open(brightness_file, 'r') as f:
            raw_brightness = int(f.read())
    except FileNotFoundError as error:
        logger.error(error)
        sys.exit(1)

    logger.debug("Current raw brightness: %s" % raw_brightness)
    brightness = int(round(raw_brightness / 2.55))
    logger.debug("Current brightness: %s%%" % brightness)
    return brightness

# Writes the new brightness level
def _write_brightness(brightness):
    logger.debug("Desired brightness: %s%%" % brightness)
    raw_brightness = int(round(brightness * 2.55))
    logger.debug("Setting raw brightness: %s" % raw_brightness)
    try:
        with open(brightness_file, 'w') as f:
            f.write(str(raw_brightness))
    except FileNotFoundError as error:
        logger.error(error)
        sys.exit(1)

# Turns the screen on
def _screen_on():
    powered_on = _get_power_state()
    if not powered_on:
        _write_power_state(True)
    else:
        logger.info("Screen is already powered on")

# Turns the screen off
def _screen_off():
    powered_on = _get_power_state()
    if powered_on:
        _write_power_state(False)
    else:
        logger.info("Screen is already powered off")

# Sets a specific brightness given the `brightness` variable
def _screen_brightness(brightness, no_fade):

    # Turns the screen on if it's off
    if brightness > 5:
        _screen_on()
    
    # Fades the screen brightness unless no_fade=True
    if no_fade:
        _write_brightness(brightness)
    else:
        # Gets the current brightness value to create a delta for fading
        current = _get_brightness()

        # Creates the necessary deltas to calculate fading
        bright_delta = (brightness - current)
        logger.debug("Brightness delta: %s" % bright_delta)
        index_delta = abs(bright_delta)
        logger.debug("Index delta: %s" % index_delta)
        bright_index = 0

        # Loops through the deltas to create the fading effect
        logger.info("Setting the screen brightness to %s%%." % brightness)
        while index_delta > 0:
            if index_delta >= large_change_unit_threshold:
                change_unit = large_change_unit
            elif index_delta >= small_change_unit_threshold:
                change_unit = small_change_unit
            else:
                change_unit = 1
            index_delta -= change_unit
            if bright_delta < 0:
                bright_delta += change_unit
                bright_index -= change_unit
            else:
                bright_delta -= change_unit
                bright_index += change_unit
            
            _write_brightness(current + bright_index)
            time.sleep(0.05)

    # Turns off the display if the brightness is 0
    if not brightness or brightness <= 5:
        _screen_off()

# Takes input from the call and uses it to enact settings on the Pi display
def set_display(brightness, off, no_fade):
    if off:
        _screen_brightness(0, no_fade)
    else:
        _screen_brightness(brightness, no_fade)

def handler(signum, frame):
    sys.exit(0)

signal.signal(signal.SIGTERM, handler)
signal.signal(signal.SIGINT, handler)

def main():
    while True:
        button.wait_for_press()
        
        # Get current screen status
        current_brightness = _get_brightness()

        # Set screen brightness
        if current_brightness > 30:
            set_display(30, False, False)
        elif current_brightness <= 30 and current_brightness > 5:
            set_display(0, True, False)
        else:
            set_display(100, False, False)

        time.sleep(0.5)

if __name__ == "__main__":
    main()
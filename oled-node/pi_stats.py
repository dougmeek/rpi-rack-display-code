import time
import subprocess
import atexit
import signal
import sys

from board import SCL, SDA
import busio
from PIL import Image, ImageDraw, ImageFont
import adafruit_ssd1306
 
 
# Create the I2C interface.
i2c = busio.I2C(SCL, SDA)
 
# Create the SSD1306 OLED class.
disp = adafruit_ssd1306.SSD1306_I2C(128, 32, i2c)
 
# Leaving the OLED on for a long period of time can damage it
# Set these to prevent OLED burn in
REFRESH_INTERVAL = 5
DISPLAY_ON = 30 # on time in seconds - IMPORTANT: MUST BE A MULTIPLE OF REFRESH_INTERVAL

# Clear display.
disp.fill(0)
disp.show()
 
# Create blank image for drawing.
# Make sure to create image with mode '1' for 1-bit color.
width = disp.width
height = disp.height
image = Image.new("1", (width, height))
 
# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)
 
# Draw a black filled box to clear the image.
draw.rectangle((0, 0, width, height), outline=0, fill=0)
 
# Draw some shapes.
# First define some constants to allow easy resizing of shapes.
padding = -2
top = padding
bottom = height - padding
# Move left to right keeping track of the current x position for drawing shapes.
x = 0
 
 
# Load default font.
font = ImageFont.load_default()

# Turn off the screen when the script exits
def turnoffscreen():
    disp.fill(0)
    disp.show()

def handler(signum, frame):
    turnoffscreen()
    sys.exit(0)

atexit.register(turnoffscreen)
signal.signal(signal.SIGTERM, handler)
signal.signal(signal.SIGINT, handler)

# Set up runtime variables
i = 0
INITIAL_RUN = 1

while True:

    # Checking for beginning of minute to ensure that displays are synchronized
    current_seconds = time.gmtime().tm_sec
    if current_seconds == 1 or INITIAL_RUN == 1:

        # Execute display loop function for screen
        while i < (DISPLAY_ON):
            i += REFRESH_INTERVAL

            # Draw a black filled box to clear the image.
            draw.rectangle((0, 0, width, height), outline=0, fill=0)

            # Shell scripts for system monitoring from here:
            # https://unix.stackexchange.com/questions/119126/command-to-display-memory-usage-disk-usage-and-cpu-load
            cmd = "hostname | tr -d '\\n'"
            HostName = subprocess.check_output(cmd, shell=True).decode("utf-8")
            cmd = "hostname -I | cut -d' ' -f1"
            IP = subprocess.check_output(cmd, shell=True).decode("utf-8")
            cmd = "top -bn1 | grep load | awk '{printf \"CPU:%.2f\", $(NF-2)}'"
            CPU = subprocess.check_output(cmd, shell=True).decode("utf-8")
            cmd = "echo \"$(cat /sys/class/thermal/thermal_zone0/temp) / 1000\" | bc -l | awk '{printf \"Temp:%.1f\", $(NF)}'"
            Temp = subprocess.check_output(cmd, shell=True).decode("utf-8")
            cmd = "free -m | awk 'NR==2{printf \"Mem:%s/%s %.2f%%\", $3,$2,$3*100/$2 }'"
            MemUsage = subprocess.check_output(cmd, shell=True).decode("utf-8")
            cmd = 'df -h | awk \'$NF=="/"{printf "Disk:%d/%dGB %s", $3,$2,$5}\''
            Disk = subprocess.check_output(cmd, shell=True).decode("utf-8")
        
            # Write four lines of text.

            draw.text((x, top + 0), HostName + " " + IP, font=font, fill=255)
            draw.text((x, top + 8), CPU + " - " + Temp, font=font, fill=255)
            draw.text((x, top + 16), MemUsage, font=font, fill=255)
            draw.text((x, top + 25), Disk, font=font, fill=255)
    
            # Display image.
            disp.image(image)
            disp.show()
            time.sleep(REFRESH_INTERVAL)
    
        i = 0
        INITIAL_RUN = 0

        disp.fill(0)
        disp.show()
        time.sleep(0.9)
    time.sleep(0.9) # This prevents the time.gmtime() command from pegging the CPU to 100%
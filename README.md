# 3D Printed RPi Rack Display Code

The code in this repo manages the displays in the 3D printable RPi rack hosted here: [https://www.printables.com/model/97235-raspberry-pi-rackenclosure](https://www.printables.com/model/97235-raspberry-pi-rackenclosure)

## Basics

- In my rack, the RPi in the top section is the controller node for the OLEDs in the faceplates of the other blades. This is where I have the momentary buttons wired to GPIO. The RPi display button is on GPIO2 and the stats OLED button is on GPIO3.
- The OLED blades run a service that executes some Python code. You'll find these files under the oled-node subdirectory.
- The controller node must run a service for monitoring momentary button presses. You'll find these files under the oled-controller subdirectory.
- The controller node also runs a service for controlling the power state and brightness of the OEM RPi 7" display. The code for this service is under the rpi-display subdirectory.
- The momentary buttons are configured in a pull-down configuration. This means that one side of the button is wired to the GPIO pin and the other is wired to ground. If you need to choose different GPIO pins, these can be configured in their respective scripts.
- Your controller node will need SSH public keys installed on all OLED nodes from the account the service runs from (should be root).
- You'll need to update the racknode list in rack_oled_service.py. I've left some dummy names in the script to help guide you. You may use DNS or IP here.
- You'll want to update the .service files to point to the location of the Python scripts on your nodes.

*Note: The services need to run as root to properly function, especially the rack-display.service. This is a limitation in the way RPi handles screen brightness input.*

## How the OLED display services work

The service on the controller node listens for a button press on a GPIO pin. When this is detected, the service will perform the following tasks:

1. The script will SSH into the first node in the racknodes list and check the pi-stats.service status.
2. The script will then invert the boolean received from step one.
3. The script will SSH into all nodes in the racknodes list and start or stop the service based on the boolean value from step two.

If the displays are off, they will start immediately and then shut off after 30 seconds. After that, they will turn on at the beginning of every minute and then shut off after 30 seconds.

*Note: I recommend configuring NTP on your blades so that the start/stop times of the OLEDs are synchronized.*

## How the rack display service works

The service on the rack display node listens for a button press on a GPIO pin. When this is detected, the service will set the display in one of three states:

- 100%
- 30%
- 0%

You can configure these values in the main() function of the script. You can also add additional steps to set more than just three states.

***Disclaimer: I am not a software developer by trade and I'm certain this can be improved upon. Feel free to branch and modify as you wish. I offer no warranty or support for this code and I am not liable for any damages or loss associated with its use.***
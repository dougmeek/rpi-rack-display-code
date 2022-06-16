from gpiozero import Button
import time
import subprocess
import logging
from multiprocessing import Process
from multiprocessing import Pool
import signal
import sys

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

log_formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(name)s:%(message)s')
log_stream_handler = logging.StreamHandler()
log_stream_handler.setFormatter(log_formatter)
logger.addHandler(log_stream_handler)

# Sets the GPIO pin for the button
button = Button(3)

# Global variables
piuser = 'ubuntu' # This script requires that the nodes have the executing server's public SSH key installed on the user profile and the user must have root
statuscmd = 'sudo systemctl show pi-stats.service --property=ActiveState'
stopcmd = 'sudo systemctl stop pi-stats.service'
startcmd = 'sudo systemctl start pi-stats.service'

racknodes = [
    "blade-1.some.fqdn",
    "blade-2.some.fqdn",
    "blade-3.some.fqdn",
    "blade-4.some.fqdn",
    "blade-5.some.fqdn",
    "blade-6.some.fqdn",
    "blade-7.some.fqdn",
    "blade-8.some.fqdn"
]

bladecount = len(racknodes)

def get_service_status(pi_host):
    process = subprocess.run("ssh -o \"UserKnownHostsFile=/dev/null\" -o \"StrictHostKeyChecking=no\" {user}@{host} {cmd}".format(user=piuser, host=pi_host, cmd=statuscmd), shell=True, capture_output=True, encoding="utf-8")

    if process.stdout.strip():
        result_log = pi_host + ": " + process.stdout.strip()
        logger.debug("Service status: %s" % result_log)
    return process.stdout.strip()

def stop_service(pi_host):
    process = subprocess.run("ssh -o \"UserKnownHostsFile=/dev/null\" -o \"StrictHostKeyChecking=no\" {user}@{host} {cmd}".format(user=piuser, host=pi_host, cmd=stopcmd), shell=True, capture_output=True, encoding="utf-8")
    logger.debug("Stopping service on %s" % pi_host)
    if process.stdout.strip():
        result_log = pi_host + ": " + process.stdout.strip()
        logger.debug("Service stop result on %s" % result_log)
    return process.stdout

def start_service(pi_host):
    process = subprocess.run("ssh -o \"UserKnownHostsFile=/dev/null\" -o \"StrictHostKeyChecking=no\" {user}@{host} {cmd}".format(user=piuser, host=pi_host, cmd=startcmd), shell=True, capture_output=True, encoding="utf-8")
    logger.debug("Starting service on %s" % pi_host)
    if process.stdout.strip():
        result_log = pi_host + ": " + process.stdout.strip()
        logger.debug("Service start result on %s" % result_log)
    return process.stdout

def handler(signum, frame):
    sys.exit(0)

signal.signal(signal.SIGTERM, handler)
signal.signal(signal.SIGINT, handler)

def main():
    while True:
        # Wait for button input on GPIO pin
        button.wait_for_press()
        logger.info("Button pressed - executing toggle")

        # Get status of first node
        # It is necessary to target only one node for status, otherwise the displays may get out of sync
        status = get_service_status(racknodes[0])

        # Toggle logic
        if status == "ActiveState=active":
            logger.info("Desired state: stopped")
            # Execute toggle
            pool = Pool(bladecount)
            pool.map(stop_service, racknodes)
        else:
            logger.info("Desired state: started")
            # Execute toggle
            pool = Pool(bladecount)
            pool.map(start_service, racknodes)

        time.sleep(0.5)

if __name__ == '__main__':
    main()
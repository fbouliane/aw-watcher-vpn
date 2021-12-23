import logging
import platform
from datetime import datetime, timedelta, timezone
from time import sleep
import os
import psutil

from aw_core.models import Event
from aw_client import ActivityWatchClient

from .config import watcher_config

system = platform.system()
logger = logging.getLogger(__name__)


class Settings:
    def __init__(self, config_section):
        # Time without input before we're considering the user as AFK
        self.timeout = config_section["timeout"]
        # How often we should poll for input activity
        self.poll_time = config_section["poll_time"]


class OpenvpnWatcher:
    def __init__(self, testing=False):
        # Read settings from config
        configsection = "aw-watcher-openvpn"
        self.settings = Settings(watcher_config[configsection])

        self.client = ActivityWatchClient("aw-watcher-openvpn", testing=testing, host='10.0.1.80', port=5600)
        self.bucketname = "{}_{}".format(
            self.client.client_name, self.client.client_hostname
        )

    def send_heartbeat(self, openvpn_running: bool, timestamp: datetime, duration: float = 0):
        data = {"status": "running" if openvpn_running else "not-running"}
        e = Event(timestamp=timestamp, duration=duration, data=data)
        pulsetime = self.settings.timeout + self.settings.poll_time
        self.client.heartbeat(self.bucketname, e, pulsetime=pulsetime, queued=True)

    def run(self):
        logger.info("aw-watcher-openvpn started")

        # Initialization
        sleep(1)

        eventtype = "vpnstatus"
        self.client.create_bucket(self.bucketname, eventtype, queued=True)

        # Start afk checking loop
        with self.client:
            self.heartbeat_loop()

    def heartbeat_loop(self):
        afk = False
        while True:
            try:
                now = datetime.now(timezone.utc)
                process_names = [i.name() for i in psutil.process_iter(['name'])]
                vpn = False
                if 'nm-openconnect-service' in process_names or 'openvpn' in process_names:
                    vpn = True
                self.send_heartbeat(vpn, now)

                sleep(self.settings.poll_time)

            except KeyboardInterrupt:
                logger.info("aw-watcher-openvpn stopped by keyboard interrupt")
                break

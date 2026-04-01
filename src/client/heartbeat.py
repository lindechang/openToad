import threading
import time
import logging
from src.client.http_client import HttpClient
from src.client.config import ClientConfig

logger = logging.getLogger(__name__)

class HeartbeatService:
    def __init__(self, config: ClientConfig):
        self.config = config
        self.http_client = HttpClient(config.api_base, config.http_timeout)
        self._running = False
        self._thread: threading.Thread = None

    def start(self):
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()
        logger.info("Heartbeat service started")

    def stop(self):
        self._running = False
        if self._thread:
            self._thread.join(timeout=1)
        logger.info("Heartbeat service stopped")

    def _run(self):
        while self._running:
            try:
                self._send_heartbeat()
            except Exception as e:
                logger.error(f"Heartbeat failed: {e}")
            time.sleep(self.config.heartbeat_interval)

    def _send_heartbeat(self):
        data = {"instanceId": self.config.instance_id}
        self.http_client.post("/instance/heartbeat", data)
        logger.debug("Heartbeat sent")

import logging
from typing import Optional, Callable

from src.client.config import ClientConfig
from src.client.instance import InstanceManager
from src.client.heartbeat import HeartbeatService
from src.client.commander import CommanderService

logger = logging.getLogger(__name__)


class InstanceService:
    def __init__(self, config: Optional[ClientConfig] = None, on_command: Optional[Callable] = None):
        self.config = config or ClientConfig()
        self.instance_manager = InstanceManager(self.config)
        self.heartbeat_service = HeartbeatService(self.config)
        self.commander_service = CommanderService(self.config, on_command)
        self._started = False

    def start(self):
        if self._started:
            logger.warning("Service already started")
            return
        
        logger.info(f"Starting instance service for {self.config.instance_id}")
        
        self.instance_manager.register()
        logger.info(f"Instance registered: {self.config.instance_id}")
        
        self.heartbeat_service.start()
        
        self.commander_service.start()
        
        self._started = True
        logger.info("Instance service started successfully")

    def stop(self):
        self.heartbeat_service.stop()
        self.commander_service.stop()
        self._started = False
        logger.info("Instance service stopped")

    def bind_user(self, user_id: int):
        return self.instance_manager.bind_user(user_id)

    def get_status(self):
        return self.instance_manager.get_status()

    @property
    def instance_id(self) -> str:
        return self.config.instance_id
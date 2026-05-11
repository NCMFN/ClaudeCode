import logging
import json
import os
from datetime import datetime

class AgentLogger:
    """
    Logs inter-agent communications for traceability.
    """
    def __init__(self, log_dir: str = "logs"):
        self.log_dir = log_dir
        os.makedirs(self.log_dir, exist_ok=True)

        self.logger = logging.getLogger("MultiAgentFramework")
        self.logger.setLevel(logging.INFO)

        log_file = os.path.join(self.log_dir, f"framework_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
        file_handler = logging.FileHandler(log_file)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)

        if not self.logger.handlers:
            self.logger.addHandler(file_handler)

    def log_communication(self, sender: str, receiver: str, message: str, metadata: dict = None):
        """
        Log communication between agents.
        """
        log_entry = {
            "sender": sender,
            "receiver": receiver,
            "message": message,
            "metadata": metadata or {}
        }
        self.logger.info(json.dumps(log_entry))

    def log_event(self, event_type: str, details: str):
        """
        Log a general framework event.
        """
        log_entry = {
            "event": event_type,
            "details": details
        }
        self.logger.info(json.dumps(log_entry))

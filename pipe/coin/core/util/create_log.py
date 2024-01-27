import logging
from pathlib import Path


def log(name: str, log_location: str) -> logging.Logger:
    logger = logging.getLogger(name=name)
    if logger.hasHandlers():
        return logger

    logger.propagate = False
    logger.setLevel(logging.INFO)

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    try:
        file_handler = logging.FileHandler(filename=log_location)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except Exception as e:
        logger.error(f"Failed to create file handler due to: {e}")

    return logger


class SocketLogCustomer:
    def __init__(self, base_path: Path = None, file_name: str = None):
        if base_path:
            self.base_path = base_path
        else:
            self.base_path = (
                Path(__file__).parent.parent.parent / f"{file_name}" / "log"
            )

    def create_logger(self, log_name: str, log_type: str) -> logging.Logger:
        try:
            log_path = self.base_path / log_type / log_name
            log_path.parent.mkdir(parents=True, exist_ok=True)
            return log(log_name.split(".")[0], str(log_path))
        except Exception as e:
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to create or access the log file: {e}")
            return logger

    async def log_message(
        self, log_name: str, log_type: str, message: str, level: str = "info"
    ):
        logger = self.create_logger(log_name, log_type)
        log_func = getattr(logger, level, "info")
        log_func(message)

    async def connection(self, exchange_name: str, message: str):
        log_name = f"{exchange_name}_connection.log"
        await self.log_message(log_name, "connection", message)

    async def data_log(self, exchange_name: str, message: str):
        log_name = f"{exchange_name}_data.log"
        await self.log_message(log_name, "data", message)

    async def register_connection(self, message: str):
        log_name = "market_register.log"
        await self.log_message(log_name, "connection", message)

    async def error_log(self, error_type: str, message: str):
        log_name = f"{error_type}.log"
        await self.log_message(log_name, "error", message, level="error")

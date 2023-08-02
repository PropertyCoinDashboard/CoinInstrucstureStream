import logging
from pathlib import Path


def log(log_location: str, name: str):
    logger = logging.getLogger(name=name)
    if logger.hasHandlers():
        return logger  # Avoid duplicate handlers

    logger.propagate = False
    logger.setLevel(logging.INFO)

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    file_handler = logging.FileHandler(filename=log_location)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger


class SocketLogCustomer:
    path = Path(__file__)

    def create_logger(self, log_name: str, exchange_name: str, log_type: str):
        log_path = (
            self.path.parent.parent.parent
            / "streaming"
            / "log"
            / exchange_name
            / f"{exchange_name}_{log_type}.log"
        )
        log_path.parent.mkdir(parents=True, exist_ok=True)
        return log(str(log_path), log_name)

    async def log_message(
        self,
        log_name: str,
        exchange_name: str,
        log_type: str,
        message: str,
        level: str = "info",
    ):
        logger = self.create_logger(log_name, exchange_name, log_type)
        log_func = getattr(logger, level, "info")
        log_func(message)

    async def not_connection(self, log_name: str, message: str) -> None:
        self.log_message(log_name, log_name, "not_connection", message, level="error")

    async def connection(self, log_name: str, message: str):
        self.log_message(log_name, log_name, "connect", message)

    async def register_connection(self, log_name: str, message: str) -> None:
        self.log_message(log_name, log_name, "register", message)

    async def conn_logger(self, market: str, message: str) -> None:
        self.log_message(market, "total", "price_data_counting", str(message))

    async def error_logger(self, message: str) -> None:
        self.log_message(
            "error-logger", "total", "error_data_counting", message, level="error"
        )

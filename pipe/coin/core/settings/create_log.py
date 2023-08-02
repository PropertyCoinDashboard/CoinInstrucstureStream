"""
log
"""
import logging
from pathlib import Path


def log(log_location: str, name: str):
    # 로그 생성
    logger = logging.getLogger(name=name)
    logger.propagate = False

    # 로그의 출력 기준 설정
    logger.setLevel(logging.INFO)

    # log 출력 형식
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # log 출력
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    # log를 파일에 출력
    file_handler = logging.FileHandler(filename=log_location)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger


class SocketLogCustomer:
    path = Path(__file__)

    def create_logger(self, log_name: str, exchange_name: str, log_type: str):
        """
        주어진 이름으로 로거를 생성하는 함수.

        Args:
            log_name (str): 로거에 사용될 이름.
            exchange_name (str): 거래소 이름.

        Returns:
            logger: 주어진 이름으로 설정된 로거를 반환.
        """
        try:
            return log(
                f"{self.path.parent.parent}/streaming/log/{exchange_name}/{exchange_name}_{log_type}.log",
                log_name,
            )
        except (FileNotFoundError, FileExistsError):
            a: Path = self.path.parent.parent / "streaming" / "log" / exchange_name
            a.mkdir()

    def not_connection(self, log_name: str, meesge: str) -> None:
        logger = self.create_logger(
            log_name=f"{log_name}-not",
            exchange_name=log_name,
            log_type="not_connection",
        )
        logger.error(meesge)

    def connection(self, log_name: str, messge: str):
        logger = self.create_logger(
            log_name=f"{log_name}-connect",
            exchange_name=log_name,
            log_type="connect",
        )
        logger.info(messge)

    def register_connection(self, log_name: str, message: str) -> None:
        """
        market websocket register

        Args:
            message (_type_): register message
        """
        logger = self.create_logger(
            log_name=f"{log_name}-register",
            exchange_name=log_name,
            log_type="register",
        )
        logger.info(message)

    def conn_logger(self, market: str, messgae: str) -> None:
        conn_logger = self.create_logger(
            log_name=f"{market}-price-data",
            exchange_name="total",
            log_type="price_data_counting",
        )
        conn_logger.info(str(messgae))

    def error_logger(self, message: str) -> None:
        error_logger = self.create_logger(
            log_name="error-logger",
            exchange_name="total",
            log_type="error_data_counting",
        )
        print(error_logger)
        error_logger.error(message)

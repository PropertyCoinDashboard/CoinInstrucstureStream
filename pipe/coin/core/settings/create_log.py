"""
log
"""
import logging


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

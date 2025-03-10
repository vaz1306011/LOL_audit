import logging


def setup_logging():
    formatter = logging.Formatter(
        fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()  # 取得 root logger
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(handler)

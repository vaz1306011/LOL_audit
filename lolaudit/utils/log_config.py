import logging
import traceback


class TraceStyleFormatter(logging.Formatter):
    def format(self, record):
        level = f"[{record.levelname}]"
        time = self.formatTime(record, "%Y-%m-%d %H:%M:%S")

        header = f"{level} - {time}:"
        message = record.getMessage()

        if record.levelno >= logging.ERROR:
            stack = "".join(traceback.format_stack()[:-1])
            return f"{header}\n{stack}    {message}\n"
        else:
            location = f"{record.pathname}:{record.lineno}"
            return f"{header} {location}\n  {message}\n"


def setup_logging():
    formatter = TraceStyleFormatter()

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(handler)

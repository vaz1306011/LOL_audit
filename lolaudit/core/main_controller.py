# lolaudit/core/main_controller.py
from PySide6.QtCore import QObject, QThread, Signal

from lolaudit.config import ConfigKeys, ConfigManager
from lolaudit.core.match_manager import MatchManager


class MainController(QObject):
    update_signal = Signal(str)

    def __init__(self):
        super().__init__()
        self.config = ConfigManager("./config.json")

        self.match_manager = MatchManager(self.update_signal.emit)

        self.work_thread = QThread()
        self.moveToThread(self.work_thread)
        self.work_thread.started.connect(self.match_manager.start_main)
        self.work_thread.start()

    def start_matchmaking(self):
        self.match_manager.start_matchmaking()

    def stop_matchmaking(self):
        self.match_manager.stop_matchmaking()

    def set_accept_delay(self, value: int):
        self.match_manager.set_accept_delay(value)
        self.config.set_config(ConfigKeys.ACCEPT_DELAY, value)

    def set_auto_accept(self, value: bool):
        self.match_manager.set_auto_accept(value)
        self.config.set_config(ConfigKeys.AUTO_ACCEPT, value)

    def set_auto_rematch(self, value: bool):
        self.match_manager.set_auto_rematch(value)
        self.config.set_config(ConfigKeys.AUTO_REMATCH, value)

    def stop(self):
        self.match_manager.stop_main()
        self.work_thread.quit()
        self.work_thread.wait()

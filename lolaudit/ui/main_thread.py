from PySide6.QtCore import QObject, Signal

from lolaudit.core import MatchManager


class MainThread(QObject):
    update_signal = Signal(str)

    def __init__(self):
        super().__init__()
        self.lol_audit = MatchManager(self.update_signal.emit)

    def run(self):
        self.lol_audit.start_main()

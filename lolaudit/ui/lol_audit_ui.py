import logging

from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication, QMainWindow

from lolaudit.config import ConfigKeys
from lolaudit.core.main_controller import MainController
from lolaudit.ui import Tray, Ui_MainWindow
from lolaudit.utils import resource_path

logger = logging.getLogger(__name__)


class LolAuditUi(QMainWindow, Ui_MainWindow):
    def __init__(self, version):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle(f"LOL Audit v{version}")
        self.icon = QIcon(resource_path("./lol_audit.ico"))
        self.setWindowIcon(self.icon)
        self.setFixedSize(self.size())
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, True)

        self.controller = MainController()
        self.controller.update_signal.connect(self.__update)
        self.__init_ui()
        logger.info("UI 初始化完成")

    def __init_ui(self):
        cfg = self.controller.config
        self.accept_delay_value.setText(str(cfg.get_config(ConfigKeys.ACCEPT_DELAY)))
        self.accept_delay_value.textChanged.connect(self.controller.set_accept_delay)

        self.match_button.clicked.connect(self.__toggle_matchmaking_button)

        for key, widget, func in [
            (
                ConfigKeys.ALWAYS_ON_TOP,
                self.always_on_top_status,
                self.__set_always_on_top,
            ),
            (
                ConfigKeys.AUTO_ACCEPT,
                self.auto_accept_status,
                self.controller.set_auto_accept,
            ),
            (
                ConfigKeys.AUTO_REMATCH,
                self.auto_rematch_status,
                self.controller.set_auto_rematch,
            ),
        ]:
            status = bool(cfg.get_config(key))
            widget.setCheckable(True)
            widget.setChecked(status)
            widget.triggered.connect(func)
            if key == ConfigKeys.ALWAYS_ON_TOP:
                self.__set_always_on_top(status)

        self.tray = Tray(self, self.icon)
        self.tray.quit_action.triggered.connect(self.__exit_app)
        self.tray.show()

    def __update(self, text: str):
        if text == "未在列隊":
            self.match_button.setText("開始列隊")
            self.match_button.setEnabled(True)
        elif text.startswith("列隊中"):
            self.match_button.setText("停止列隊")
            self.match_button.setEnabled(True)
        else:
            self.match_button.setEnabled(False)
        self.label.setText(text)

    def __toggle_matchmaking_button(self):
        if self.match_button.text() == "開始列隊":
            self.controller.start_matchmaking()
        else:
            self.controller.stop_matchmaking()

    def __set_always_on_top(self, status: bool):
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, status)
        self.show()
        self.controller.config.set_config(ConfigKeys.ALWAYS_ON_TOP, status)

    def __exit_app(self):
        self.controller.stop()
        QApplication.quit()

    def closeEvent(self, event):
        event.ignore()
        self.hide()

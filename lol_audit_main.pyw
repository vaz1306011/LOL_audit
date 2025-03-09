import logging
import sys

from PySide6.QtCore import QObject, Qt, QThread, Signal
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication, QMainWindow

from lol_audit import LolAudit
from lol_audit_tray import LolAuditTray
from ui import Ui_MainWindow
from version import __version__

logger = logging.getLogger(__name__)


class Worker(QObject):
    update_signal = Signal(str)

    def __init__(self):
        super().__init__()
        self.lol_audit = LolAudit(self.update_signal.emit)

    def run(self):
        self.lol_audit.start_main()


class LolAuditUi(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)  # 設置 UI 佈局
        self.setWindowTitle(f"LOL Audit v{__version__}")
        self.icon = QIcon("./lol_audit.ico")
        self.setWindowIcon(self.icon)
        self.setFixedSize(self.size())
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, True)

        # 創建一個工作線程來運行 main 方法
        self.main_thread = Worker()
        self.main_thread.update_signal.connect(self.__update)

        # 創建線程執行 Worker.run 方法
        self.thread = QThread()
        self.main_thread.moveToThread(self.thread)
        self.thread.started.connect(self.main_thread.run)
        self.thread.start()

        self.__init_ui()

    def __init_ui(self):
        # 接受延遲
        self.accept_delay_value.setText(
            str(self.main_thread.lol_audit.get_accept_delay())
        )
        self.accept_delay_value.textChanged.connect(self.__set_accept_delay)

        # 列隊按鈕
        self.match_button.clicked.connect(self.__toggle_matchmaking_button)

        # 至頂開關
        self.always_on_top_status.setCheckable(True)
        self.always_on_top_status.setChecked(True)
        self.always_on_top_status.triggered.connect(self.__toggle_always_on_top)

        # 自動接受開關
        self.auto_accept_status.setCheckable(True)
        self.auto_accept_status.setChecked(self.main_thread.lol_audit.get_auto_accept())
        self.auto_accept_status.triggered.connect(self.__toggle_auto_accept)

        # 自動重新列隊開關
        self.auto_rematch_status.setCheckable(True)
        self.auto_rematch_status.setChecked(
            self.main_thread.lol_audit.get_auto_rematch()
        )
        self.auto_rematch_status.triggered.connect(self.__toggle_auto_rematch)

        # 系統托盤
        self.tray = LolAuditTray(self, self.icon)
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

    def __start_matchmaking(self):
        self.main_thread.lol_audit.start_matchmaking()

    def __stop_matchmaking(self):
        self.main_thread.lol_audit.stop_matchmaking()

    def __set_accept_delay(self, value):
        try:
            value = int(value)
        except ValueError:
            value = 0

        self.main_thread.lol_audit.set_accept_delay(value)

    def __toggle_matchmaking_button(self):
        if self.match_button.text() == "開始列隊":
            self.__start_matchmaking()
        else:
            self.__stop_matchmaking()

    def __toggle_always_on_top(self):
        self.setWindowFlag(
            Qt.WindowType.WindowStaysOnTopHint, self.always_on_top_status.isChecked()
        )
        self.show()

    def __toggle_auto_accept(self):
        self.main_thread.lol_audit.set_auto_accept(self.auto_accept_status.isChecked())

    def __toggle_auto_rematch(self):
        self.main_thread.lol_audit.set_auto_rematch(
            self.auto_rematch_status.isChecked()
        )

    def __exit_app(self):
        self.main_thread.lol_audit.stop_main()
        self.thread.quit()
        self.thread.wait()
        QApplication.quit()

    def closeEvent(self, event):
        event.ignore()
        self.hide()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    lol_audit_ui = LolAuditUi()
    lol_audit_ui.show()
    sys.exit(app.exec())

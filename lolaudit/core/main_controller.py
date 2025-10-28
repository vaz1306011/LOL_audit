from PySide6.QtCore import QObject, QThread, Signal

from lolaudit.config import ConfigKeys, ConfigManager
from lolaudit.core.gameflow import Gameflow
from lolaudit.core.match_manager import MatchManager


class MainController(QObject):
    ui_update = Signal(Gameflow, str)

    def __init__(self):
        super().__init__()
        self.config = ConfigManager("./config.json")
        self.match_manager = MatchManager()
        self.match_manager.gameflow_change.connect(self.__on_gameflow_change)

        self.work_thread = QThread()
        self.moveToThread(self.work_thread)
        self.work_thread.started.connect(self.match_manager.start_main)
        self.work_thread.start()

    def __on_gameflow_change(self, gameflow: Gameflow, data: dict):
        display_text = ""
        match gameflow:
            case Gameflow.LOADING:
                display_text = "讀取中"

            case Gameflow.NONE:
                display_text = "未在房間內"

            case Gameflow.LOBBY:
                display_text = "未在列隊"

            case Gameflow.PENALTY:
                try:
                    time_remaining = data["time_remaining"]
                except Exception as e:
                    display_text = f"懲罰時間獲取失敗: {e}\ndata:{data}"

                minute, second = divmod(time_remaining, 60)
                display_text = f"懲罰中，剩餘時間：{minute}:{second}"

            case Gameflow.MATCHMAKING:
                try:
                    time_in_queue = data["timeInQueue"]
                    estimated_time = data["estimatedTime"]
                except Exception as e:
                    display_text = f"匹配時間獲取失敗: {e}\ndata:{data}"

                tiqM, tiqS = divmod(time_in_queue, 60)
                etM, etS = divmod(estimated_time, 60)

                display_text = (
                    f"列隊中：{tiqM:02d}:{tiqS:02d}\n預計時間：{etM:02d}:{etS:02d}"
                )

            case Gameflow.WAITING_ACCEPT:
                try:
                    pass_time = data["pass_time"]
                    accept_delay = data["accept_delay"]
                except Exception as e:
                    display_text = f"等待確認時間獲取失敗: {e}\ndata:{data}"

                display_text = f"等待接受對戰 {pass_time}/{accept_delay}"

            case Gameflow.CHAMP_SELECT:
                display_text = "選擇英雄中"

            case Gameflow.IN_PROGRESS:
                display_text = "遊戲中"

            case Gameflow.RECONNECT:
                display_text = "重新連接中"

            case Gameflow.PRE_END_OF_GAME:
                display_text = "點讚畫面"

            case Gameflow.END_OF_GAME:
                display_text = "結算畫面"

            case Gameflow.UNKNOWN:
                try:
                    error = data["error"]
                except Exception as e:
                    display_text = f"未知狀態獲取失敗: {e}\ndata:{data}"

                display_text = f"未知狀態 {error}"

        self.ui_update.emit(gameflow, display_text)

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

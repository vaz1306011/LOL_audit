import logging
import threading
import time

import requests

import log_config
from league_client import LeagueClient

log_config.setup_logging()
logger = logging.getLogger(__name__)


class LolAudit:
    def __init__(self, output) -> None:
        self.__output = output
        self.__accept_delay = 3
        self.__auto_accept = True
        self.__auto_rematch = True
        self.__auto_start_match = True
        self.__client = LeagueClient()
        self.__main_flag = threading.Event()
        self.__is_on_penalty_flag = False

    def __is_playerResponsed(self) -> bool:
        mchmking_info: dict = self.__client.get_matchmaking_info()
        playerResponse = mchmking_info.get("readyCheck", {}).get("playerResponse")
        return playerResponse in ("Accepted", "Declined")

    def __in_lobby(self) -> None:
        mchmking_info: dict = self.__client.get_matchmaking_info()
        search_state = mchmking_info.get("searchState")
        match search_state:
            case None:
                self.__output("未在列隊")

            case "Error":
                if ptr := mchmking_info.get("penaltyTimeRemaining") > 0:
                    self.__is_on_penalty_flag = True
                    self.__output(f"懲罰時間剩餘{ptr}")
                else:
                    self.__output("matchmaking未知錯誤")

    def __in_matchmaking(self) -> None:
        mchmking_info: dict = self.__client.get_matchmaking_info()
        search_state = mchmking_info.get("searchState")
        match search_state:
            case "None":
                if self.__auto_start_match and self.__is_on_penalty_flag:
                    self.__client.start_matchmaking()
                    self.__is_on_penalty_flag = False

            case "Searching":
                time_in_queue = round(mchmking_info["timeInQueue"])
                tiqM, tiqS = divmod(time_in_queue, 60)
                estimated_time = round(mchmking_info["estimatedQueueTime"])
                # estimated_time = 5
                etM, etS = divmod(estimated_time, 60)

                self.__output(
                    f"列隊中：{tiqM:02d}:{tiqS:02d}\n預計時間：{etM:02d}:{etS:02d}"
                )

                if self.__auto_rematch and time_in_queue > estimated_time:
                    logger.info("等待時間過長")
                    self.__client.quit_matchmaking()
                    logger.info("退出列隊")
                    self.__client.start_matchmaking()
                    logger.info("重新列隊")

            case _:
                self.__output(f"未知matchmaking狀態:{search_state}")

    def __in_ready_check(self) -> None:
        mchmking_info: dict = self.__client.get_matchmaking_info()
        playerResponse = mchmking_info.get("readyCheck", {}).get("playerResponse")
        match playerResponse:
            case "None":
                if not self.__auto_accept:
                    return

                def ready_check_timer(accept_delay: int):
                    while True:
                        ready_check_data = self.__client.get_matchmaking_info()[
                            "readyCheck"
                        ]
                        if ready_check_data["state"] != "InProgress":
                            return
                        pass_time = round(ready_check_data["timer"])
                        if pass_time >= accept_delay:
                            break
                        yield pass_time

                for pass_time in ready_check_timer(self.__accept_delay):
                    if self.__is_playerResponsed():
                        break
                    self.__output(f"等待接受對戰 {pass_time}/{self.__accept_delay}")
                    time.sleep(0.5)
                else:
                    if not self.__is_playerResponsed():
                        self.__client.accept_match()

            case "Declined":
                self.__output("已拒絕對戰")

            case "Accepted":
                self.__output("已接受對戰")

            case _:
                self.__output(f"playerResponse未知狀態:{playerResponse}")

    def __main(self) -> None:
        while True:
            if self.__main_flag.is_set():
                logger.info("停止程序")
                break

            # if not self.__client.check_auth():
            #     self.__output("讀取中")
            #     self.__client.refresh_auth()
            #     continue
            try:
                gameflow = self.__client.get_gameflow()
            except requests.exceptions.MissingSchema:
                gameflow = {}

            match gameflow:
                case {}:
                    self.__output("讀取中")
                    self.__client.refresh_auth()

                case "None":
                    self.__output("未在房間內")

                case "Lobby":
                    self.__in_lobby()

                case "Matchmaking":
                    self.__in_matchmaking()

                case "ReadyCheck":
                    self.__in_ready_check()

                case "ChampSelect":
                    self.__output("選擇英雄中")

                case "InProgress":
                    self.__output("遊戲中")

                case "Reconnect":
                    self.__output("重新連接中")

                case "PreEndOfGame":
                    self.__output("點讚畫面")

                case "EndOfGame":
                    self.__output("結算畫面")

                case _:
                    self.__output(f"未知gameflow狀態:{gameflow}")
            time.sleep(0.5)

    def start_main(self) -> None:
        self.__main_flag.clear()
        main_thread = threading.Thread(target=self.__main)
        main_thread.daemon = True
        main_thread.start()

    def stop_main(self) -> None:
        self.__main_flag.set()

    def start_matchmaking(self) -> None:
        self.__client.start_matchmaking()

    def stop_matchmaking(self) -> None:
        self.__client.quit_matchmaking()

    def get_accept_delay(self) -> int:
        return self.__accept_delay

    def set_accept_delay(self, delay: int) -> None:
        self.__accept_delay = delay

    def get_auto_accept(self) -> bool:
        return self.__auto_accept

    def set_auto_accept(self, status: bool) -> None:
        self.__auto_accept = status

    def get_auto_rematch(self) -> bool:
        return self.__auto_rematch

    def set_auto_rematch(self, status: bool) -> None:
        self.__auto_rematch = status


if __name__ == "__main__":
    lol_audit = LolAudit(logger.info)
    lol_audit.start_main()

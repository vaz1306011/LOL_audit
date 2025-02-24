import threading
import time

from league_client import LeagueClient


class LolAudit:
    def __init__(self, output) -> None:
        self.__output = output
        self.__accept_delay = 3
        self.__auto_accept = True
        self.__auto_rematch = True
        self.__client = LeagueClient()
        self.__main_flag = threading.Event()
        self.__is_on_penalty_flag = False

    def __is_playerResponsed(self) -> bool:
        return self.__client.get_matchmaking_info().get("readyCheck", {}).get(
            "playerResponse"
        ) in ("Accepted", "Declined")

    def __matchmaking(self) -> None:
        mchmking_info: dict = self.__client.get_matchmaking_info()
        search_state = mchmking_info.get("searchState")
        match search_state:

            case "Searching":
                time_in_queue = round(mchmking_info["timeInQueue"])
                tiqM, tiqS = divmod(time_in_queue, 60)
                estimated_time = round(mchmking_info["estimatedQueueTime"])
                etM, etS = divmod(estimated_time, 60)

                self.__output(
                    f"列隊中：{tiqM:02d}:{tiqS:02d}\n預計時間：{etM:02d}:{etS:02d}"
                )

                if self.__auto_rematch and time_in_queue > estimated_time:
                    print("等待時間過長")
                    self.__client.quit_matchmaking()
                    print("退出列隊")
                    self.__client.start_matchmaking()
                    print("重新列隊")

            case "Error":
                if ptr := mchmking_info.get("penaltyTimeRemaining") > 0:
                    self.__is_on_penalty_flag = True
                    self.__output(f"懲罰時間剩餘{ptr}")
                else:
                    self.__output("matchmaking未知錯誤")

            case _:
                self.__output(f"未知matchmaking狀態:{search_state}")

    def __ready_check(self) -> None:
        mchmking_info: dict = self.__client.get_matchmaking_info()
        state = mchmking_info.get("readyCheck", {}).get("state")
        match state:
            case "InProgress":
                if not self.__auto_accept:
                    return

                while (
                    pass_time := round(
                        self.__client.get_matchmaking_info()["readyCheck"]["timer"]
                    )
                    < self.__accept_delay
                ):
                    if self.__is_playerResponsed():
                        break

                    self.__output(f"等待接受對戰 {pass_time}/{self.__accept_delay}")
                    time.sleep(0.5)
                else:
                    self.__client.accept_match()
                    self.__output("已接受對戰")

            case "Declined":
                self.__output("已拒絕對戰")

            case "Accepted":
                self.__output("已接受對戰")

            case _:
                self.__output(f"readycheck未知狀態:{state}")

    def __main(self) -> None:
        while True:
            if self.__main_flag.is_set():
                print("停止程序")
                break

            if not self.__client.check_auth():
                self.__output("讀取中")
                self.__client.refresh_auth()
                continue

            gameflow = self.__client.get_gameflow()
            match gameflow:
                case "None":
                    self.__output("未在房間內")

                case "Lobby":
                    self.__output("未在列隊")

                case "Matchmaking":
                    self.__matchmaking()

                case "ReadyCheck":
                    self.__ready_check()

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
    lol_audit = LolAudit(print)
    lol_audit.start_main()

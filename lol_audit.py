import threading
import time

from league_client import LeagueClient


class LolAudit:
    def __init__(self) -> None:
        self.__is_found = False
        self.__accept_delay = 3
        self.__auto_accept = True
        self.__auto_rematch = True
        self.__client = LeagueClient()
        self.__main_flag = threading.Event()

    def __main(self, output) -> None:
        while True:
            if self.__main_flag.is_set():
                print("停止程序")
                break

            if self.__client.get_phase() == "ChampSelect":
                output("選擇英雄中")

            status: dict = self.__client.get_matchmaking_info()

            match status.get("searchState"):
                case "Searching":
                    self.__is_found = False
                    time_in_queue = round(status["timeInQueue"])
                    tiqM, tiqS = divmod(time_in_queue, 60)
                    estimated_time = round(status["estimatedQueueTime"])
                    etM, etS = divmod(estimated_time, 60)

                    output(
                        f"列隊中 {tiqM:02d}:{tiqS:02d}\n預計時間：{etM:02d}:{etS:02d}"
                    )

                    if self.__auto_rematch and time_in_queue > estimated_time:
                        print("等待時間過長")
                        self.__client.quit_matchmaking()
                        print("退出列隊")
                        self.__client.start_matchmaking()
                        print("重新列隊")

                case "Found":
                    if self.__is_found:
                        continue
                    self.__is_found = True

                    print("找到對戰")
                    if self.__auto_accept:
                        for i in range(self.__accept_delay):
                            output(f"等待接受對戰 {i}/{self.__accept_delay}")
                            time.sleep(1)
                        self.__client.accept_match()
                        output("已接受對戰")

                case _:
                    output("未在列隊")

            time.sleep(0.5)

    def start_main(self, output) -> None:
        self.__main_flag.clear()

        main_thread = threading.Thread(target=self.__main, args=(output,))
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
    lol_audit = LolAudit()
    lol_audit.start_main(print)

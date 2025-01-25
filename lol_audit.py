import threading
import time
from os import system

from league_client import LeagueClient

ACCEPT_DELAY = 3
is_found = False


def main(event: threading.Event, update_label=None):
    client = LeagueClient()
    client.start_matchmaking()
    print("開始對戰")

    while True:
        if event.is_set():
            print("停止程序")
            break

        if client.get_phase() == "ChampSelect":
            print("選擇英雄中")
            break

        status: dict = client.get_matchmaking_info()

        match status.get("searchState"):
            case "Searching":
                is_found = False
                time_in_queue = round(status["timeInQueue"])
                tiqM, tiqS = divmod(time_in_queue, 60)
                estimated_time = round(status["estimatedQueueTime"])
                etM, etS = divmod(estimated_time, 60)
                print(f"列隊中 {tiqM:02d}:{tiqS:02d}/{etM:02d}:{etS:02d}")
                if time_in_queue > estimated_time:
                    print("等待時間過長")
                    client.quit_matchmaking()
                    print("退出列隊")
                    client.start_matchmaking()
                    print("重新列隊")

            case "Found":
                if is_found:
                    continue
                is_found = True

                print("找到對戰")
                for i in range(ACCEPT_DELAY):
                    print(f"等待接受對戰 {i}/{ACCEPT_DELAY}")
                    time.sleep(1)
                client.accept_match()
                print("接受對戰")

            case _:
                print("未在列隊")

        time.sleep(1)


if __name__ == "__main__":
    e = threading.Event()
    main(e)
    system("pause")

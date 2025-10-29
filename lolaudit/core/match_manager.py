import logging
import threading
import time

from PySide6.QtCore import QObject, Signal

from lolaudit.core.gameflow import Gameflow
from lolaudit.exceptions.summoner_exceptions import SummonerInfoError
from lolaudit.lcu import LeagueClient

logger = logging.getLogger(__name__)


class MatchManager(QObject):
    gameflow_change = Signal(Gameflow, dict)

    def __init__(self) -> None:
        super().__init__()
        self.__accept_delay = 3
        self.__auto_accept = True
        self.__auto_rematch = True
        self.__auto_start_match = True
        self.__client = LeagueClient()
        self.__main_flag = threading.Event()
        self.__is_on_penalty_flag = False

    def __wait_for_auth(self):
        logger.info("等待授權...")
        self.gameflow_change.emit(Gameflow.LOADING, {})
        while not self.__client.check_auth():
            self.__client.refresh_auth()
            continue
        logger.info("授權成功")

    def __wait_for_sunmmoner_info(self):
        logger.info(f"嘗試獲取召喚師狀態")
        while True:
            try:
                self.__client.load_summoner_info()
            except SummonerInfoError:
                pass
            except Exception as e:
                logger.warning(f"無法獲取召喚師狀態: {e}")
            else:
                break
        logger.info(
            f"召喚師狀態獲取成功\n  {self.__client.puuid}\n  {self.__client.gameName}#{self.__client.gameTag}"
        )

    def __main(self) -> None:
        self.__wait_for_auth()
        self.__wait_for_sunmmoner_info()

        while not self.__main_flag.is_set():

            gameflow = self.__client.get_gameflow()
            try:
                logger.info(f"gameflow: {gameflow}")
                match gameflow:
                    case {}:
                        self.__wait_for_auth()

                    case "None":
                        self.gameflow_change.emit(Gameflow.NONE, {})

                    case "Lobby":
                        self.__in_lobby()

                    case "Matchmaking":
                        self.__in_matchmaking()

                    case "ReadyCheck":
                        self.__in_ready_check()

                    case "ChampSelect":
                        self.__in_champ_select()

                    case "InProgress":
                        self.gameflow_change.emit(Gameflow.IN_PROGRESS, {})

                    case "Reconnect":
                        self.gameflow_change.emit(Gameflow.RECONNECT, {})

                    case "PreEndOfGame":
                        self.gameflow_change.emit(Gameflow.PRE_END_OF_GAME, {})

                    case "EndOfGame":
                        self.gameflow_change.emit(Gameflow.END_OF_GAME, {})

                    case _:
                        raise Exception(f"未知gameflow狀態:{gameflow}")
            except Exception as e:
                self.gameflow_change.emit(Gameflow.UNKNOWN, {"error": str(e)})

            time.sleep(0.5)
        else:
            logger.info("停止程序")

    def __in_lobby(self) -> None:
        mchmking_info: dict = self.__client.get_matchmaking_info()
        search_state = mchmking_info.get("searchState")
        logger.info(type(search_state))
        match search_state:
            case None:
                self.gameflow_change.emit(Gameflow.LOBBY, {})

            case "Error":
                if ptr := mchmking_info["penaltyTimeRemaining"] > 0:
                    self.__is_on_penalty_flag = True
                    self.gameflow_change.emit(Gameflow.PENALTY, {"timeRemaining": ptr})
                else:
                    raise Exception("matchmaking未知錯誤")

    def __in_matchmaking(self) -> None:
        mchmking_info: dict = self.__client.get_matchmaking_info()
        search_state = mchmking_info.get("searchState")
        logger.info(f"search_state: {search_state}")
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

                self.gameflow_change.emit(
                    Gameflow.MATCHMAKING,
                    {"timeInQueue": time_in_queue, "estimatedTime": estimated_time},
                )

                if self.__auto_rematch and time_in_queue > estimated_time:
                    logger.info("等待時間過長")
                    self.__client.quit_matchmaking()
                    logger.info("退出列隊")
                    self.__client.start_matchmaking()
                    logger.info("重新列隊")

            case _:
                raise Exception(f"未知matchmaking狀態:{search_state}")

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
                    self.gameflow_change.emit(
                        Gameflow.WAITING_ACCEPT,
                        {"pass_time": pass_time, "accept_delay": self.__accept_delay},
                    )
                    time.sleep(0.5)
                else:
                    if not self.__is_playerResponsed():
                        self.__client.accept_match()

            case "Declined":
                self.gameflow_change.emit(Gameflow.DECLINED, {})

            case "Accepted":
                self.gameflow_change.emit(Gameflow.ACCEPTED, {})

            case _:
                raise Exception(f"未知playerResponse狀態:{playerResponse}")

    def __in_champ_select(self):
        response = self.__client.get_champ_select_timer()
        adjustedTimeLeftInPhase = response["adjustedTimeLeftInPhase"] / 1000
        internalNowInEpochMs = response["internalNowInEpochMs"] / 1000
        remaining_time = (adjustedTimeLeftInPhase + internalNowInEpochMs) - time.time()
        self.gameflow_change.emit(
            Gameflow.CHAMP_SELECT, {"remaining_time": remaining_time}
        )

    def __is_playerResponsed(self) -> bool:
        mchmking_info: dict = self.__client.get_matchmaking_info()
        playerResponse = mchmking_info.get("readyCheck", {}).get("playerResponse")
        return playerResponse in ("Accepted", "Declined")

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

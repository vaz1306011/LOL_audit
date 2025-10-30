import logging
from typing import Optional

from PySide6.QtCore import QObject, Signal

from lolaudit.exceptions import (
    UnknownMatchmakingInfoError,
    UnknownPlayerResponseError,
    UnknownSearchStateError,
)
from lolaudit.lcu.league_client import LeagueClient
from lolaudit.models import Gameflow

logger = logging.getLogger(__name__)


class MatchManager(QObject):
    gameflow_change = Signal(Gameflow, dict)

    def __init__(self, client: LeagueClient) -> None:
        super().__init__()
        self.__client = client

        self.__accept_delay = 3
        self.__auto_accept = True
        self.__auto_rematch = True
        self.__auto_start_match = True
        self.__is_on_penalty_flag = False

    def in_lobby(self) -> int:
        mchmking_info: dict = self.__client.get_matchmaking_info()
        search_state = mchmking_info.get("searchState")
        match search_state:
            case None:
                return 0

            case "Error":
                if (ptr := mchmking_info["penaltyTimeRemaining"]) > 0:
                    self.__is_on_penalty_flag = True
                    return ptr
                else:
                    raise UnknownMatchmakingInfoError(mchmking_info)
            case _:
                raise UnknownSearchStateError(search_state)

    def in_matchmaking(self) -> dict:
        mchmking_info: dict = self.__client.get_matchmaking_info()
        search_state = mchmking_info.get("searchState")
        logger.info(f"search_state: {search_state}")
        match search_state:
            case "None":
                if self.__auto_start_match and self.__is_on_penalty_flag:
                    self.__client.start_matchmaking()
                    self.__is_on_penalty_flag = False
                return {}

            case "Searching":
                time_in_queue = round(mchmking_info["timeInQueue"])
                estimated_time = round(mchmking_info["estimatedQueueTime"])
                # estimated_time = 5

                if self.__auto_rematch and time_in_queue > estimated_time:
                    logger.info("等待時間過長")

                    logger.info("退出列隊")
                    self.__client.quit_matchmaking()

                    logger.info("重新列隊")
                    self.__client.start_matchmaking()

                return {"timeInQueue": time_in_queue, "estimatedTime": estimated_time}

            case _:
                raise UnknownSearchStateError(search_state)

    def in_ready_check(self) -> Optional[tuple[Gameflow, dict]]:
        mchmking_info: dict = self.__client.get_matchmaking_info()
        playerResponse = mchmking_info.get("readyCheck", {}).get("playerResponse")
        match playerResponse:
            case "None":
                if not self.__auto_accept:
                    return

                ready_check_data = self.__client.get_matchmaking_info()["readyCheck"]
                if ready_check_data["state"] != "InProgress":
                    return
                pass_time = round(ready_check_data["timer"])

                def __is_playerResponsed() -> bool:
                    mchmking_info: dict = self.__client.get_matchmaking_info()
                    playerResponse = mchmking_info.get("readyCheck", {}).get(
                        "playerResponse"
                    )
                    return playerResponse in ("Accepted", "Declined")

                if not __is_playerResponsed() and pass_time >= self.__accept_delay:
                    self.__client.accept_match()
                    return (Gameflow.ACCEPTED, {})

                return (
                    Gameflow.WAITING_ACCEPT,
                    {"pass_time": pass_time, "accept_delay": self.__accept_delay},
                )

            case "Accepted":
                return (Gameflow.ACCEPTED, {})

            case "Declined":
                return (Gameflow.DECLINED, {})

            case _:
                raise UnknownPlayerResponseError(playerResponse)

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

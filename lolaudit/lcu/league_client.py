import logging

import requests
import urllib3

from lolaudit.lcu import auth

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
logger = logging.getLogger(__name__)


class LeagueClient:
    def __init__(self):
        self.__auth = auth.get_auth_string()
        self.__client = requests.Session()
        self.__client.verify = False
        self.__client.headers.update({"Accept": "application/json"})

    def check_auth(self) -> bool:
        return self.__auth is not None

    def refresh_auth(self) -> None:
        self.__auth = auth.get_auth_string()

    def __get_request(self, url: str) -> dict:
        try:
            return self.__client.get(f"{self.__auth}/{url}", timeout=(3, 10)).json()
        except requests.exceptions.ConnectionError as e:
            logger.error(e)
            return {}

    def __post_request(self, url: str) -> None:
        try:
            self.__client.post(f"{self.__auth}/{url}", timeout=(3, 10))
        except requests.exceptions.ConnectionError as e:
            logger.error(e)

    def __delete_request(self, url: str) -> None:
        try:
            self.__client.delete(f"{self.__auth}/{url}", timeout=(3, 10))
        except requests.exceptions.ConnectionError as e:
            logger.error(e)

    def get_gameflow(self) -> dict:
        """
        gameflow_list = ['"None"'      , '"Lobby"'       , '"Matchmaking"',
                         '"ReadyCheck"', '"ChampSelect"' , '"InProgress"' ,
                         '"Reconnect"' , '"PreEndOfGame"', '"EndOfGame"' ,]
        """
        url = "lol-gameflow/v1/gameflow-phase"
        return self.__get_request(url)

    def get_matchmaking_info(self) -> dict:
        url = "lol-matchmaking/v1/search"
        return self.__get_request(url)

    def start_matchmaking(self) -> None:
        url = "lol-lobby/v2/lobby/matchmaking/search"
        self.__post_request(url)

    def quit_matchmaking(self) -> None:
        url = "lol-lobby/v2/lobby/matchmaking/search"
        self.__delete_request(url)

    def accept_match(self) -> None:
        url = "lol-matchmaking/v1/ready-check/accept"
        self.__post_request(url)

    def decline_match(self) -> None:
        url = "lol-matchmaking/v1/ready-check/decline"
        self.__post_request(url)

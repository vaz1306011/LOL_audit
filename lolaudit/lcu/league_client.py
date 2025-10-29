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
        self.me = None
        self.puuid = None
        self.gameName = None
        self.gameTag = None

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

    def check_auth(self) -> bool:
        return self.__auth is not None

    def refresh_auth(self) -> None:
        self.__auth = auth.get_auth_string()

    def load_summoner_info(self) -> None:
        self.me = self.__get_request("lol-chat/v1/me")
        self.puuid = self.me.get("puuid")
        self.gameName = self.me.get("gameName")
        self.gameTag = self.me.get("gameTag")
        if not (self.puuid and self.gameName and self.gameTag):
            raise SummonerInfoError

    def get_gameflow(self) -> dict:
        """
        gameflow_list = ['"None"'      , '"Lobby"'       , '"Matchmaking"',
                         '"ReadyCheck"', '"ChampSelect"' , '"InProgress"' ,
                         '"Reconnect"' , '"PreEndOfGame"', '"EndOfGame"' ,]
        """
        try:
            url = "lol-gameflow/v1/gameflow-phase"
            return self.__get_request(url)
        except requests.exceptions.MissingSchema:
            return {}

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

    def get_champ_select_timer(self) -> dict:
        url = "lol-champ-select/v1/session/timer"
        return self.__get_request(url)

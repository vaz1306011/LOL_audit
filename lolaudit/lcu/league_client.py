import logging
from typing import Optional

import requests
import urllib3

from lolaudit.exceptions import SummonerInfoError
from lolaudit.lcu import auth
from lolaudit.utils import BaseRequester

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
logger = logging.getLogger(__name__)


class LeagueClient(BaseRequester):
    def __init__(self):
        self.__auth = auth.get_auth_string()
        super().__init__(self.__auth)

        self.me = None
        self.puuid = None
        self.gameName = None
        self.gameTag = None

    def get_auth(self) -> Optional[str]:
        return self.__auth

    def check_auth(self) -> bool:
        return self.__auth is not None

    def refresh_auth(self) -> None:
        self.__auth = auth.get_auth_string()
        super().__init__(self.__auth)

    def load_summoner_info(self) -> None:
        self.me = self._get("lol-chat/v1/me")
        self.puuid = self.me.get("puuid")
        self.gameName = self.me.get("gameName")
        self.gameTag = self.me.get("gameTag")
        if not (self.puuid and self.gameName and self.gameTag):
            raise SummonerInfoError

    def get_gameflow(self) -> Optional[str]:
        """
        gameflow_list = ['"None"'      , '"Lobby"'       , '"Matchmaking"',
                         '"ReadyCheck"', '"ChampSelect"' , '"InProgress"' ,
                         '"Reconnect"' , '"PreEndOfGame"', '"EndOfGame"' ,]
        """
        try:
            url = "lol-gameflow/v1/gameflow-phase"
            return str(self._get(url))
        except requests.exceptions.MissingSchema:
            logger.warning("無法獲取遊戲流程")
            return None

    def get_matchmaking_info(self) -> dict:
        url = "lol-matchmaking/v1/search"
        return self._get(url)

    def start_matchmaking(self) -> None:
        url = "lol-lobby/v2/lobby/matchmaking/search"
        self._post(url)

    def quit_matchmaking(self) -> None:
        url = "lol-lobby/v2/lobby/matchmaking/search"
        self._delete(url)

    def accept_match(self) -> None:
        url = "lol-matchmaking/v1/ready-check/accept"
        self._post(url)

    def decline_match(self) -> None:
        url = "lol-matchmaking/v1/ready-check/decline"
        self._post(url)

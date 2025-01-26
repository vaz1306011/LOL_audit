import requests

import auth

requests.packages.urllib3.disable_warnings()


class LeagueClient:
    def __init__(self):
        self.__auth = auth.get_auth_string()
        self.__client = requests.Session()
        self.__client.verify = False
        self.__client.headers.update({"Accept": "application/json"})
        self.__client.timeout = 10

    def __get_request(self, url: str) -> requests.Response:
        return self.__client.get(f"{self.__auth}/{url}").json()

    def __post_request(self, url: str) -> None:
        self.__client.post(f"{self.__auth}/{url}")

    def __delete_request(self, url: str) -> None:
        self.__client.delete(f"{self.__auth}/{url}")

    def get_phase(self) -> requests.Response:
        """
        Lobby
        Matchmaking
        ReadyCheck
        ChampSelect
        """
        url = "lol-gameflow/v1/gameflow-phase"
        return self.__get_request(url)

    def get_matchmaking_info(self) -> requests.Response:
        url = "lol-matchmaking/v1/search"
        return self.__get_request(url)

    def get_team_info(self) -> requests.Response:
        url = "lol-matchmaking/v1/team"
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

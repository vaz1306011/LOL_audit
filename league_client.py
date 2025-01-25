import time

import requests

import auth

requests.packages.urllib3.disable_warnings()


class LeagueClient:
    def __init__(self):
        self.auth = auth.get_auth_string()
        self.client = requests.Session()
        self.client.verify = False
        self.client.headers.update({"Accept": "application/json"})
        self.client.timeout = 10

    def get_phase(self) -> requests.Response:
        """
        Lobby
        Matchmaking
        ReadyCheck
        ChampSelect
        """
        url = f"{self.auth}/lol-gameflow/v1/gameflow-phase"
        response = self.client.get(url)
        return response.json()

    def start_matchmaking(self) -> None:
        url = f"{self.auth}/lol-lobby/v2/lobby/matchmaking/search"
        self.client.post(url)

    def get_matchmaking_info(self) -> requests.Response:
        url = f"{self.auth}/lol-matchmaking/v1/search"
        response = self.client.get(url)
        return response.json()

    def quit_matchmaking(self) -> None:
        url = f"{self.auth}/lol-lobby/v2/lobby/matchmaking/search"
        self.client.delete(url)

    def accept_match(self) -> None:
        url = f"{self.auth}/lol-matchmaking/v1/ready-check/accept"
        self.client.post(url)

    def decline_match(self) -> requests.Response:
        url = f"{self.auth}/lol-matchmaking/v1/ready-check/decline"
        response = self.client.post(url)
        return response.json()

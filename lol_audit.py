import base64
import json
import time
from pathlib import Path

import requests
import urllib3
from genericpath import isfile

urllib3.disable_warnings()


class LeagueClient:
    def __init__(self, lockfile) -> None:
        with open(lockfile, "r") as f:
            data = f.read()
            data = data.split(":")
            # data[0] == 'LeagueClient'
            # data[1] ==  I dont't know
            # data[2] ==  Port number
            # data[3] ==  Authorization token
            # data[4] ==  Connecton method

            self.host = "127.0.0.1"
            self.port = data[2]
            self.authorization = "Basic " + base64.b64encode(
                ("riot:" + data[3]).encode(encoding="utf-8")
            ).decode("utf-8")
            self.connection_method = data[4]
            self.url_prefix = (
                self.connection_method + "://" + self.host + ":" + self.port
            )
            self.headers = {
                "Accept": "application/json",
                "Authorization": self.authorization,
            }

            """ Debug
            
            print("Host             : " + self.host)
            print("Port             : " + self.port)
            print("Connecton method : " + self.connection_method)
            print("Authorization    : " + self.authorization)
            print("\n")

            """

    def __requests_get(self, url, *args, **kwargs) -> requests.Response:
        return requests.get(
            url=self.url_prefix + url,
            *args,
            headers=self.headers,
            verify=False,
            **kwargs,
        )

    def __requests_post(self, url, *args, **kwargs) -> requests.Response:
        return requests.post(
            url=self.url_prefix + url,
            *args,
            headers=self.headers,
            verify=False,
            **kwargs,
        )

    @staticmethod
    def get_gamepath() -> Path | None:
        """獲取遊戲路徑

        Returns:
            Path | None: 遊戲路徑
        """
        import subprocess

        cmd = (
            'powershell "gps | where {$_.MainWindowTitle } | select Description,Id,Path'
        )
        proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
        for line in proc.stdout:
            program = line.decode(encoding="big5").rstrip()
            if program.startswith("League of Legends"):
                return (
                    Path(program[program.find("\\") - 2 :])
                    .parents[1]
                    .joinpath("LeagueClient")
                )
        else:
            return None

    def get_gameflow(self) -> str:
        """
        取得遊戲狀態

        return: 遊戲狀態(
            "None"      , "Lobby"       , "Matchmaking",
            "ReadyCheck", "ChampSelect" , "InProgress" ,
            "Reconnect" , "PreEndOfGame", "EndOfGame"
        )

        """
        # GET /lol-gameflow/v1/gameflow-phase HTTP/1.1
        response = self.__requests_get("/lol-gameflow/v1/gameflow-phase")
        return response.text.replace('"', "")

    def check_gameflow(self, gameflow: str) -> bool:
        """
        檢查遊戲狀態

        gameflow: 遊戲狀態(
            "None"      , "Lobby"       , "Matchmaking",
            "ReadyCheck", "ChampSelect" , "InProgress" ,
            "Reconnect" , "PreEndOfGame", "EndOfGame"
        )

        """
        return self.get_gameflow() == gameflow

    def wait_gameflow(self, gameflow: str, interval: float = 1) -> None:
        """
        等待遊戲狀態

        gameflow: 遊戲狀態(
            "None"      , "Lobby"       , "Matchmaking",
            "ReadyCheck", "ChampSelect" , "InProgress" ,
            "Reconnect" , "PreEndOfGame", "EndOfGame"
        )
        interval: 檢查間隔(秒)

        """
        while True:
            if self.check_gameflow(gameflow):
                return
            time.sleep(interval)

    def accept_matchmaking(self) -> None:
        """
        發送接受對戰請求

        """
        # POST /lol-matchmaking/v1/ready-check/accept HTTP/1.1
        self.__requests_post("/lol-matchmaking/v1/ready-check/accept")

    def get_team(self) -> list[dict]:
        """
        取得隊伍資料

        'assignedPosition': '',     (路線)
        'cellId': 0,                (不知道)
        'championId': 0,            (英雄ID)
        'championPickIntent': 0,    (想選的路)
        'playerType': 'PLAYER',     (玩家類型)
        'selectedSkinId': 11009,    (皮膚ID)
        'spell1Id': 11,             (召喚師技能1)
        'spell2Id': 4,              (召喚師技能2)
        'summonerId': 24194919,     (召喚師ID)
        'team': 1,                  (隊伍)
        'wardSkinId': -1            (皮膚ID)

        """
        # GET /lol-champ-select/v1/session HTTP/1.1
        return self.__requests_get("/lol-champ-select-legacy/v1/session").json()[
            "myTeam"
        ]

    def test(self, summonerId):
        return self.__requests_get(
            f"/lol-collections/v1/inventories/{summonerId}/champion-mastery"
        ).json()


if __name__ == "__main__":
    while True:
        path = LeagueClient.get_gamepath()
        if path is not None:
            print("\r" + " " * 20, end="")
            print("\r找到遊戲路徑")
            print(path)
            break
        else:
            print("\r" + " " * 20, end="")
            print("\r客戶端沒有執行或找不到路徑", end="")

        time.sleep(1)

    lockfile = path.joinpath("lockfile")
    client = LeagueClient(lockfile)
    print("遊戲狀態: " + client.get_gameflow())
    # with open("data.json", "w") as f:
    #     json.dump(client.test(24194919), f, indent=4)

    # while True:
    #     if client.check_gameflow("ChampSelect"):
    #         for player in client.get_team():
    #             print("=========================================")
    #             for key, val in player.items():
    #                 print(key, ":", val)

    #         break
    #     time.sleep(1)

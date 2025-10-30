import logging

import requests

logger = logging.getLogger(__name__)


class BaseRequester:
    def __init__(self, auth) -> None:
        self.__auth = auth
        self.__session = requests.Session()
        self.__session.verify = False
        self.__session.headers.update({"Accept": "application/json"})

    def _get(self, url: str) -> dict:
        try:
            return self.__session.get(f"{self.__auth}/{url}", timeout=(3, 10)).json()
        except requests.exceptions.ConnectionError:
            logger.warning(f"get request失敗: {url}")
            return {}

    def _post(self, url: str) -> None:
        try:
            self.__session.post(f"{self.__auth}/{url}", timeout=(3, 10))
        except requests.exceptions.ConnectionError:
            logger.warning(f"post request失敗: {url}")

    def _delete(self, url: str) -> None:
        try:
            self.__session.delete(f"{self.__auth}/{url}", timeout=(3, 10))
        except requests.exceptions.ConnectionError:
            logger.warning(f"delete request失敗: {url}")

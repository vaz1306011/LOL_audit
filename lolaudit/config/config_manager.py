import json
import platform
from pathlib import Path

from appdirs import user_config_dir
from PySide6.QtCore import QObject

from lolaudit.config.config_keys import ConfigKeys
from lolaudit.config.config_model import Config
from lolaudit.utils import resource_path


class ConfigManager(QObject):
    def __init__(self) -> None:
        self.__setting_path = self.get_config_path()
        self.setting = Config()
        self.load_config()

    def get_config_path(self) -> str:
        match platform.system():
            case "Windows":
                path = Path(user_config_dir("LOL_Audit"), "config.json")
                return str(path)
            case "Darwin":
                return resource_path("./config")
            case _:
                raise NotImplementedError("Unsupported platform")

    def load_config(self) -> None:
        try:
            with open(self.__setting_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.setting = Config(**data)
        except (FileNotFoundError, json.JSONDecodeError):
            self.save_config()

    def save_config(self) -> None:
        Path(self.__setting_path).parent.mkdir(parents=True, exist_ok=True)
        with open(self.__setting_path, "w", encoding="utf-8") as f:
            json.dump(self.setting.__dict__, f, ensure_ascii=False, indent=2)

    def set_config(self, key: ConfigKeys, value: object) -> None:
        if hasattr(self.setting, key.value):
            setattr(self.setting, key.value, value)
            self.save_config()
        else:
            raise AttributeError(f"Setting has no attribute '{key}'")

    def get_config(self, key: ConfigKeys) -> bool | int:
        if hasattr(self.setting, key.value):
            return getattr(self.setting, key.value)
        else:
            raise AttributeError(f"Setting has no attribute '{key}'")

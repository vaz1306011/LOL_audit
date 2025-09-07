import json
from dataclasses import dataclass

from PySide6.QtCore import QObject, Signal


# TODO: 儲存設定
@dataclass
class ConfigType:
    alwsay_on_top: bool = True
    backguard_startup: bool = True
    auto_accept: bool = True
    auto_rematch: bool = True
    accept_delay: int = 3


class ConfigKey:
    always_on_top = "alwsay_on_top"
    backguard_startup = "backguard_startup"
    auto_accept = "auto_accept"
    auto_rematch = "auto_rematch"
    accept_delay = "accept_delay"


class ConfigManager(QObject):
    def __init__(self, config_path: str) -> None:
        self.__setting_path = config_path
        self.setting = ConfigType()
        self.load_config()

    def load_config(self) -> None:
        try:
            with open(self.__setting_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.setting = ConfigType(**data)
        except (FileNotFoundError, json.JSONDecodeError):
            self.save_config()

    def save_config(self) -> None:
        with open(self.__setting_path, "w", encoding="utf-8") as f:
            json.dump(self.setting.__dict__, f, ensure_ascii=False, indent=2)

    def set_config(self, key: str, value: object) -> None:
        if hasattr(self.setting, key):
            setattr(self.setting, key, value)
            self.save_config()
        else:
            raise AttributeError(f"Setting has no attribute '{key}'")

    def get_config(self, key: str) -> bool | int:
        if hasattr(self.setting, key):
            return getattr(self.setting, key)
        else:
            raise AttributeError(f"Setting has no attribute '{key}'")

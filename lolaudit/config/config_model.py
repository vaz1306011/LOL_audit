from dataclasses import dataclass


@dataclass
class Config:
    alwsay_on_top: bool = True
    backguard_startup: bool = True
    auto_accept: bool = True
    auto_rematch: bool = True
    accept_delay: int = 3

import re
from typing import Optional

import psutil

# Regex
LCU_PORT_KEY = "--app-port="
LCU_TOKEN_KEY = "--remoting-auth-token="
PORT_REGEX = re.compile(r"--app-port=(\d+)")
TOKEN_REGEX = re.compile(r"--remoting-auth-token=(\S+)")
LEAGUE_PROCESSES = {"LeagueClientUx.exe", "LeagueClientUx"}


def get_auth_string() -> Optional[str]:
    stdout = ""
    for proc in psutil.process_iter(["name", "cmdline"]):
        name, cmdline = proc.info["name"], proc.info["cmdline"]

        if name in LEAGUE_PROCESSES:
            stdout = " ".join(cmdline)

    port_match = PORT_REGEX.search(stdout)
    port = port_match.group(1).replace(LCU_PORT_KEY, "") if port_match else "0"

    token_match = TOKEN_REGEX.search(stdout)
    token = (
        token_match.group(1).replace(LCU_TOKEN_KEY, "").replace('"', "")
        if token_match
        else ""
    )

    if not token:
        return None

    return f"https://riot:{token}@127.0.0.1:{port}"


if __name__ == "__main__":
    print(get_auth_string())

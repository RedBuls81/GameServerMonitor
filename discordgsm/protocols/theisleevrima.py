import time
from typing import TYPE_CHECKING

import opengsq

from discordgsm.protocols.protocol import Protocol

if TYPE_CHECKING:
    from discordgsm.gamedig import GamedigResult


class TheIsleEvrima(Protocol):
    pre_query_required = True
    name = "theisleevrima"

    _client_id = "xyza7891gk5PRo3J7G9puCJGFJjmEguW"
    _client_secret = "pKWl6t5i9NJK8gTpVlAxzENZ65P8hYzodV8Dqe5Rlc8"
    _deployment_id = "6db6bea492f94b1bbdfcdfe3e4f898dc"
    _grant_type = "client_credentials"
    _external_auth_type = ""
    _external_auth_token = ""
    _access_token = ""

    async def pre_query(self):
        TheIsleEvrima._access_token = await opengsq.EOS.get_access_token(
            client_id=self._client_id,
            client_secret=self._client_secret,
            deployment_id=self._deployment_id,
            grant_type=self._grant_type,
            external_auth_type=self._external_auth_type,
            external_auth_token=self._external_auth_token,
        )

    async def query(self):
        if not TheIsleEvrima._access_token:
            await self.pre_query()

        host, port = str(self.kv["host"]), int(str(self.kv["port"]))
        eos = opengsq.EOS(
            host, port, self._deployment_id, TheIsleEvrima._access_token, self.timeout
        )
        start = time.time()
        info = await eos.get_info()
        ping = int((time.time() - start) * 1000)

        # Credits: @dkoz https://github.com/DiscordGSM/GameServerMonitor/pull/54/files
        attributes = dict(info.get("attributes", {}))
        settings = dict(info.get("settings", {}))

        result: GamedigResult = {
            "name": attributes.get("SERVERNAME_s", "Unknown Server"),
            "map": attributes.get("MAP_NAME_s", "Unknown Map"),
            "password": attributes.get("PASSWORD_ENABLED_b", False),
            "numplayers": info.get("totalPlayers", 0),
            "numbots": 0,
            "maxplayers": settings.get("maxPublicPlayers", 0),
            "players": None,
            "bots": None,
            "connect": attributes.get("ADDRESS_s", "") + ":" + str(port),
            "ping": ping,
            "raw": info,
        }

        return result
import requests
import urllib3
import urllib3.exceptions
import logging
import time

logger = logging.getLogger(__name__)

# Ignore the Unverified HTTPS request warning.
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class Event:
    ENDPOINT = "liveclientdata/allgamedata"

    def __init__(self, ip: str = "127.0.0.1", port: int = 2999):
        self.ip = ip
        self.port = port
        self.previous_event_count: int = 0
        self.previous_game_time: int = 0
        self.game_data: dict | None = None
        self.new_events: list[str] = []

        # If the Event class initializes while a game is running
        # get all events up till that point, so that we don't send
        # events that have already happened.
        self._update_events()

    def _update_events(self):
        try:
            game_data = requests.get(
                f"https://{self.ip}:{self.port}/{Event.ENDPOINT}",
                verify=False,
            )
        except requests.exceptions.ConnectionError as e:
            # logger.exception(f"Unable to Connect to League Game. {e}")
            self.game_data = None
            time.sleep(3)
        else:
            logger.info("Connected to League Game")
            self.game_data = game_data.json()

    @property
    def events(self) -> list:
        if not self.game_data:
            return []
        return self.game_data["events"]["Events"]

    @property
    def event_count(self) -> int:
        return len(self.events)

    @property
    def game_time(self) -> int:
        if not self.game_data:
            return 0
        return self.game_data["gameData"]["gameTime"]

    def event_polling(self) -> list[str]:
        self.new_events = []
        self._update_events()
        if not self.game_data:
            logger.warning("Polling without game data")
            return []
        self.player_name = self.game_data["activePlayer"]["summonerName"]
        self.player_team = ""
        self.team_order_players = []
        self.team_chaos_players = []
        self.ally_team_players = []
        self.enemy_team_players = []

        # Populate team chaos and team order players lists
        # and figure out which team the player is on.
        for player in self.game_data["allPlayers"]:
            if player["team"] == "ORDER":
                self.team_order_players.append(player["summonerName"])
                if player["summonerName"] == self.player_name:
                    self.player_team = "ORDER"
            elif player["team"] == "CHAOS":
                self.team_chaos_players.append(player["summonerName"])
                if player["summonerName"] == self.player_name:
                    self.player_team = "CHAOS"

        # Populate ally and enemy team player lists.
        if self.player_team == "ORDER":
            self.ally_team_players = self.team_order_players
            self.enemy_team_players = self.team_chaos_players
        elif self.player_team == "CHAOS":
            self.ally_team_players = self.team_chaos_players
            self.enemy_team_players = self.team_order_players

        # Welcome announcement.
        if (
            self.game_time >= 26
            and self.previous_game_time < 26
            and self.game_time < 28
        ):
            self.new_events.append("Welcome")
        # Minions spawning soon.
        if (
            self.game_time >= 36
            and self.previous_game_time < 36
            and self.game_time < 38
        ):
            self.new_events.append("MinionsSpawningSoon")

        # Loop over all new events.
        for event_index in range(self.previous_event_count, self.event_count):
            event = self.events[event_index]
            event_name = event["EventName"]

            # Someone got first blood.
            if (
                event_name == "ChampionKill"
                and event_index < self.event_count - 1
                and self.events[event_index + 1]["EventName"] == "FirstBlood"
            ):
                event_index += 1
                self.new_events.append("FirstBlood")
            # Someone got a multikill.
            elif (
                event_name == "ChampionKill"
                and event_index < self.event_count - 1
                and self.events[event_index + 1]["EventName"] == "Multikill"
            ):
                multikill = self.events[event_index + 1]["KillStreak"]
                # Ally got a multikill.
                if event["KillerName"] in self.ally_team_players:
                    if multikill == 2:
                        self.new_events.append("AllyDoubleKill")
                    elif multikill == 3:
                        self.new_events.append("AllyTripleKill")
                    elif multikill == 4:
                        self.new_events.append("AllyQuadraKill")
                    elif multikill == 5:
                        self.new_events.append("AllyPentaKill")
                # Enemy got a multikill.
                elif event["KillerName"] in self.enemy_team_players:
                    if multikill == 2:
                        self.new_events.append("EnemyDoubleKill")
                    elif multikill == 3:
                        self.new_events.append("EnemyTripleKill")
                    elif multikill == 4:
                        self.new_events.append("EnemyQuadraKill")
                    elif multikill == 5:
                        self.new_events.append("EnemyPentaKill")
                event_index += 1
            # Someone got a kill.
            elif event_name == "ChampionKill":
                # Player got a kill.
                if event["KillerName"] == self.player_name:
                    self.new_events.append("PlayerKill")
                # Ally got a kill.
                elif event["KillerName"] in self.ally_team_players:
                    self.new_events.append("AllyKill")
                # Enemy got a kill.
                elif event["KillerName"] in self.enemy_team_players:
                    # Player was killed.
                    if event["VictimName"] == self.player_name:
                        self.new_events.append("PlayerDeath")
                    # Ally was killed.
                    else:
                        self.new_events.append("AllyDeath")
                # Someone got executed.
                else:
                    self.new_events.append("Executed")
            # A team scored an ace.
            elif event_name == "Ace":
                # Ally team scored an ace.
                if event["AcingTeam"] == self.player_team:
                    self.new_events.append("AllyAce")
                # Enemy team scored an ace.
                else:
                    self.new_events.append("EnemyAce")
            # A turret was killed.
            elif event_name == "TurretKilled":
                turret_name = event["TurretKilled"]
                # Ally team got a turret kill.
                if (
                    turret_name[7:9] == "T2"
                    and self.player_team == "ORDER"
                    or turret_name[7:9] == "T1"
                    and self.player_team == "CHAOS"
                ):
                    self.new_events.append("AllyTurretKill")
                # Enemy team got a turret kill.
                elif (
                    turret_name[7:9] == "T1"
                    and self.player_team == "ORDER"
                    or turret_name[7:9] == "T2"
                    and self.player_team == "CHAOS"
                ):
                    self.new_events.append("EnemyTurretKill")
            # A turret was killed.
            elif event_name == "InhibKilled":
                inhib_name = event["InhibKilled"]
                # Ally team got a turret kill.
                if (
                    inhib_name[9:11] == "T2"
                    and self.player_team == "ORDER"
                    or inhib_name[9:11] == "T1"
                    and self.player_team == "CHAOS"
                ):
                    self.new_events.append("AllyInhibitorKill")
                # Enemy team got a turret kill.
                elif (
                    inhib_name[9:11] == "T1"
                    and self.player_team == "ORDER"
                    or inhib_name[9:11] == "T2"
                    and self.player_team == "CHAOS"
                ):
                    self.new_events.append("EnemyInhibitorKill")
            # An inhibitor is respawning soon.
            elif event_name == "InhibRespawningSoon":
                inhib_name = event["InhibRespawningSoon"]
                # Ally team's inhibitor is respawning soon.
                if (
                    inhib_name[9:11] == "T1"
                    and self.player_team == "ORDER"
                    or inhib_name[9:11] == "T2"
                    and self.player_team == "CHAOS"
                ):
                    self.new_events.append("AllyInhibitorRespawningSoon")
                # Enemy team's inhibitor is respawning soon.
                elif (
                    inhib_name[9:11] == "T2"
                    and self.player_team == "ORDER"
                    or inhib_name[9:11] == "T1"
                    and self.player_team == "CHAOS"
                ):
                    self.new_events.append("EnemyInhibitorRespawningSoon")
            # An inhibitor has respawned.
            elif event_name == "InhibRespawned":
                inhib_name = event["InhibRespawned"]
                # Ally team's inhibitor has respawned.
                if (
                    inhib_name[9:11] == "T1"
                    and self.player_team == "ORDER"
                    or inhib_name[9:11] == "T2"
                    and self.player_team == "CHAOS"
                ):
                    self.new_events.append("AllyInhibitorRespawned")
                # Enemy team's inhibitor has respawned.
                elif (
                    inhib_name[9:11] == "T2"
                    and self.player_team == "ORDER"
                    or inhib_name[9:11] == "T1"
                    and self.player_team == "CHAOS"
                ):
                    self.new_events.append("EnemyInhibitorRespawned")
            # Minions have spawned.
            elif event_name == "MinionsSpawning":
                self.new_events.append("MinionsSpawning")
            # Game has ended.
            elif event_name == "GameEnd":
                # Victory
                if event["Result"] == "Win":
                    self.new_events.append("Victory")
                # Defeat
                elif event["Result"] == "Lose":
                    self.new_events.append("Defeat")
            # TODO: killing streaks
        self.previous_game_time = self.game_time
        self.previous_event_count = self.event_count
        logger.debug(self.new_events)
        return self.new_events

# League of Legends Announcer

Changes the default League of Legends announcer using Live Client Data API. Note that you need to mute the announcer in-game if you don't want overlapping sound.

## Build guide

Make sure to install the requirements before proceeding
```
pip install -r requirements.txt
```

To build and install on linux you can run run
```sh
make
sudo make install
```

or you can build the executable yourself using pyinstaller
```sh
pyinstaller cli.py --name "lol-announcer" --add-binary "announcer/sounds:announcer/sounds" --onefile --noconsole
```

On windows you may need to replace the colon with a semicolon
```sh
pyinstaller cli.py --name "lol-announcer" --add-binary "announcer/sounds;announcer/sounds" --onefile --noconsole
```

## Usage

To use just have the program open during a game of League of Legends.
It will automatically identify events in the game and will play the
appropriate sound for the event. You will need to mute the in game
announcer, so that you don't get any overlapping sounds.

## Create Sound Packs

The program comes bundled with a few sound packs. If you want to create your own,
You can use the creation tools in the app to generate a pack structure with everything
you need. if you prefer to do this manually, Keep reading for a short tutorial.

Sound Packs need to be placed in the following folders. these change depending
on your platform of choice.
Linux: `~/.config/lol-announcer/sounds/your_sound_pack`

Windows: `%APPDATA\lol-announcer\sounds\your_sound_pack`.

**All sounds in a soundpack should be processed. there is an option in app to do this for you.**

Each sound pack should contain a config.json with the following data.
```json
{
    "name": "Pack Name",
    "version": "1.0.0",
    "author": "Pack Author",
    "description": "Example Pack Description"
}
```
*Note that the version attribute is optional and not required. it is for internal use only*

you can find an example.json file in the root directory of the repository or by clicking [here](https://github.com/IHasPeks/peks-announcer/blob/master/exampleconfig.json "here.") The config.json should be placed with the following directories below
and each one should contain at least one audio file. You may add as many audio files as you
want, a random one will be played during that event.

Directory | Usage
---|---
PlayerFirstBlood | When you get the first kill in the game
PlayerKill | When you get a kill
PlayerDeath | When you die
PlayerDeathFirstBlood | When you die from a first blood
Executed | When you die without getting killed by an enemy
AllyAce | When your team gets an Ace
AllyKill | When your team gets a kill
AllyDeath | When your teammate dies
AllyDeathFirstBlood | When your teammate dies from a first blood
AllyFirstBlood | When your team gets the first kill in the game
AllyPentaKill | When your team gets a penta kill
AllyQuadraKill | When your team gets a quadra kill
AllyTripleKill | When your team gets a triple kill
AllyDoubleKill | When your team gets a double kill
AllyFirstBrick | When your team destroys the first turret
AllyTurretKill | When your team destroys a turret
AllyInhibitorKill | When your team destroys an inhibitor
AllyInhibitorRespawned | When your team's inhibitor respawns
AllyInhibitorRespawningSoon | When your team's inhibitor will respawn in 30 seconds
AllyDragonKill | When your team kills the dragon without stealing it
AllyDragonKillStolen | When your team kills the dragon by stealing it
AllyHeraldKill | When your team kills the herald without stealing it
AllyHeraldKillStolen | When your team kills the herald by stealing it
AllyBaronKill | When your team kills the baron without stealing it
AllyBaronKillStolen | When your team kills the baron by stealing it
EnemyAce | When the enemy team gets an ace
EnemyPentaKill | When the enemy gets a penta kill
EnemyQuadraKill | When the enemy gets a quadra kill
EnemyTripleKill | When the enemy gets a quadra kill
EnemyDoubleKill | When the enemy team gets a double kill
EnemyFirstBrick | When the enemy team destroys the first turret
EnemyTurretKill | When the enemy destroys a turret
EnemyInhibitorKill | When the enemy destroys an inhibitor
EnemyInhibitorRespawned | When the enemy's inhibitor respawns
EnemyInhibitorRespawningSoon | When the enemy's inhibitor will respawn in 30 seconds
EnemyDragonKill | When the enemy team kills the dragon without stealing it
EnemyDragonKillStolen | When the enemy team kills the dragon by stealing it
EnemyHeraldKill | When the enemy team kills the herald without stealing it
EnemyHeraldKillStolen | When the enemy team kills the herald by stealing it
EnemyBaronKill | When the enemy team kills the baron without stealing it
EnemyBaronKillStolen | When the enemy team kills the baron by stealing it
Victory | When you win
Defeat | When you lose
GameStart | At the start of the game
Welcome | At the start of the game, about 25 seconds in
MinionsSpawning | When minions spawn
MinionsSpawningSoon | When minions will spawn in 30 seconds

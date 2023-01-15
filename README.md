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

The program comes bundled with a sound pack. If you want to create your own
you will need to place them in `~/.config/lol-announcer/sounds/your_sound_pack`
on linux, and on windows in `%APPDATA\lol-announcer\sounds\your_sound_pack`.

Each sound pack should have the following directories and each one should
contain at least one audio file. You may add as many audio files as you
want, a random one will be played during that event.

Directory | Usage
---|---
FirstBlood | When someone gets the first kill in the game
PlayerKill | When you get a kill
PlayerDeath | When you die
Executed | When you die without getting killed by an enemy
AllyAce | When your team gets an Ace
AllyKill | When your team gets a kill
AllyDeath | When a teammate dies
AllyPentaKill | When your team gets a penta kill
AllyQuadraKill | When your team gets a quadra kill
AllyTripleKill | When your team gets a triple kill
AllyDoubleKill | When your team gets a double kill
AllyTurretKill | When your team destroys a turret
AllyInhibitorKill | When your team destroys an inhibitor
AllyInhibitorRespawned | When your team's inhibitor respawns
AllyInhibitorRespawningSoon | When your team's inhibitor will respawn in 30 seconds
EnemyAce | When the enemy team gets an ace
EnemyPentaKill | When the enemy gets a penta kill
EnemyQuadraKill | When the enemy gets a quadra kill
EnemyTripleKill | When the enemy gets a quadra kill
EnemyDoubleKill | When the enemy team gets a double kill
EnemyTurretKill | When the enemy destroys a turret
EnemyInhibitorKill | When the enemy destroys an inhibitor
EnemyInhibitorRespawned | When the enemy's inhibitor respawns
EnemyInhibitorRespawningSoon | When the enemy's inhibitor will respawn in 30 seconds
Victory | When you win
Defeat | When you lose
Welcome | At the start of the game, about 15 seconds in.
MinionsSpawning | When minions spawn
MinionsSpawningSoon | When minions will spawn in 30 seconds

# Pavlov WebRCON
- A WebUI for configuring a Pavlov Server down to specific mods per rotation (This is NOT a pavlov server)

### What problem does this solve?
- A Pavlov Server only lets you configure a rotation of Gamemode/Map pairs, all Mods in a Game.ini file must then be used in all these rotations (even if they don't make sense)
- This can make the player experience very poor
- Also, trying new/broken mods can be particularly frustrating, since you must edit the Game.ini file and restart the server OR Remove all unecessary mods via RCON which only allows you to remove one at a time

### What it does
- Has a WebUI where users can add Mods, Gamemodes & Maps to the local DB via their Mod.io UGC ID
- Users can then assemble 'profiles', where a profile is a single round of a combination of a Map, Gamemode & Mods
- An example rotation could look like:
  - Dust 2 On SND with No Gravity, No fall damage mods
  - Pavkart On Pavkart with No mods (as this breaks this gamemode)
  - Medical On PropHunt with Funny Taunt mods

### How it works
- Interacting with a Pavlov Server via RCON actually modifies the in-memory config, this config is re-read when the server rotates, so if the only config in the Game.ini is the Map/Mods/Gamemode of the target, then the server will obey

### Limitations
- Manual control via the Admin login on the webUI is required for rotating the server, this is due to the fact that the pavlov server does not have a signal of some sort that tells a listening party that the server is/did rotate

### Deploy
- This can be deployed in a Docker container, env variables defined in .env_example must be defined in order for it to find the pavlov server
- The Pavlov server must allow RCON on port defined in the `RCON_PORT` env variable

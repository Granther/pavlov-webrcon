# Pavlov WebRCON

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
- Interacting with a Pavlov Server via RCON actually modifies the in-memory config

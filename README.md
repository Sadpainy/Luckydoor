# LuckyDoor

![Android](https://img.shields.io/badge/Android-3DDC84?style=plastic&logo=android&logoColor=white&labelColor=555555)
![Build](https://img.shields.io/badge/Build-passing-brightgreen?style=plastic&labelColor=555555)
![Tests](https://img.shields.io/badge/Tests-passing-brightgreen?style=plastic&labelColor=555555)
![License](https://img.shields.io/badge/License-Apache%202.0-blue?style=plastic&logo=apache&logoColor=white&labelColor=555555)
![Python](https://img.shields.io/badge/Python-3776AB?style=plastic&logo=python&logoColor=white&labelColor=555555)

**A terminal-based, text-driven lucky draw game written in Python.** The player selects one of three doors and attempts to match the randomly generated "**lucky door**."

# Overview

**LuckyDoor is a single-player command-line game that revolves around probability and luck.** Each round, the player chooses a door from a fixed set of three options. The game generates a "**lucky door**" using a deterministic hash chain based on time, system entropy, and round-specific nonces. If the player's choice matches the lucky door, they win the round. Otherwise, a random penalty is applied.

# Gameplay

1. **Main Menu**: Select [1] Play, [2] History, [3] Clear History, or [Ctrl+C] to exit.
2. **Choose a Door**: Press 1 for Angel, 2 for Evil, or 3 for Lucky.
3. **Result**: The game reveals the lucky door and indicates whether you won or lost.
4. **Penalty (on loss)**: A random penalty is triggered.
5. **Next Action**: Press [R] to play again, [M] to return to the menu, [Q] to quit, or [H] to view history.

# Requirements

Python 3.8 or higher.

# Installation

1. ```Bash
   git clone https://github.com/Sadpainy/Luckydoor
   cd Luckydoor
   ```
   
2. Ensure Luckdoor.py is in your desired directory.
   ```bash
   ls -la
   ```

3. Run the game:
   ```bash
   python Luckdoor.py
   ```
   
# License

Apache License 2.0.

# Warning

Note: The game is designed to run on **Android terminals (Termux)** due to the hardcoded **/storage/emulated/0/Download** path for the FortuneFile penalty. On other platforms, this penalty will fail gracefully and report a `STATUS_PERMISSION_DENIED` error.

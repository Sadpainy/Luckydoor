# LuckyDoor

**A terminal-based, text-driven lucky draw game written in Python. The player selects one of three doors and attempts to match the randomly generated "lucky door." The application features a persistent history system, penalty mechanics, and a robust, pseudo-system-level status code architecture.**

# Overview

LuckyDoor is a single-player command-line game that revolves around probability and luck. Each round, the player chooses a door from a fixed set of three options. The game generates a "lucky door" using a deterministic hash chain based on time, system entropy, and round-specific nonces. If the player's choice matches the lucky door, they win the round. Otherwise, a random penalty is applied.

Despite its simple core gameplay, the application implements an extensive internal status code system inspired by Android's status_t and Windows NTSTATUS conventions, providing a structured and extensible error-handling framework.

# Features

· Three Door Choices: Angel, Evil, and Lucky.
· Randomized Lucky Door: Generated using a multi-layered hash chain (MD5, SHA-1, SHA-2 family).
· Penalty System: Three distinct penalties for losing rounds:
  · Lockdown: A 5-second countdown lock.
  · FortuneFile: Writes a luck report to a designated directory.
  · InstantExit: Immediately terminates the game.
· Persistent History: All game rounds are saved to a JSON file and can be viewed or cleared from the main menu.
· Robust Error Handling: A custom status code system with a @status_guard decorator to catch and translate exceptions.
· Cross-Platform Input: Supports both Windows (msvcrt) and Unix-like (termios, tty) terminals.

# Gameplay

1. Main Menu: Select [1] Play, [2] History, [3] Clear History, or [Ctrl+C] to exit.
2. Choose a Door: Press 1 for Angel, 2 for Evil, or 3 for Lucky.
3. Result: The game reveals the lucky door and indicates whether you won or lost.
4. Penalty (on loss): A random penalty is triggered.
5. Next Action: Press [R] to play again, [M] to return to the menu, [Q] to quit, or [H] to view history.

# Requirements

· Python 3.8 or higher.
· A terminal that supports ANSI escape sequences (for screen clearing).
· Standard library modules only (no external dependencies).

# Installation

1. ```Bash
   git clone https://github.com/Sadpainy/Luckydoor
   cd Luckydoor
   ```
   
2. Ensure Luckdoor.py is in your desired directory.

3. Run the game:
   ```bash
   python Luckdoor.py
   ```
   
# Configuration

The game uses several hardcoded constants and file paths:

· History File: luckydoor_records.json (stored in the current working directory).
· Fortune File Directory: /storage/emulated/0/Download (intended for Android environments).
· Fortune File Name: LuckyValue.
· Hash Algorithms: md5, sha1, sha224, sha256, sha384, sha512 (used in a 6-round hash chain).

# Architecture

The codebase is structured around a status code system and a singleton game state.

# License

Apache License 2.0.

**Note: The game is designed to run on Android terminals (e.g., Termux) due to the hardcoded /storage/emulated/0/Download path for the FortuneFile penalty. On other platforms, this penalty will fail gracefully and report a STATUS_PERMISSION_DENIED error.**

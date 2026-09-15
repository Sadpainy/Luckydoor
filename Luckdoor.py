from __future__ import annotations
import sys
import os
import time
import json
import random
import hashlib
import functools
import threading
import select
from typing import Any, Callable, Dict, Iterator, List, Optional, Tuple
from collections import OrderedDict

# Reference Android Linux Status_t Code. Define Wrapper "status_guard"
STATUS_NO_ERROR = 0x00000000
STATUS_UNKNOWN_ERROR = 0x80000000
STATUS_INVALID_OPERATION = 0x80000001
STATUS_PERMISSION_DENIED = 0x80000002
STATUS_TIMED_OUT = 0x80000003
STATUS_BAD_VALUE = 0x80000004
STATUS_BAD_TYPE = 0x80000005
STATUS_NO_INIT = 0x80000006
STATUS_NAME_NOT_FOUND = 0x80000007
STATUS_ALREADY_EXISTS = 0x80000008

STATUS_NAME_TABLE = OrderedDict(
    (
        (STATUS_NO_ERROR, "STATUS_NO_ERROR"),
        (STATUS_UNKNOWN_ERROR, "STATUS_UNKNOWN_ERROR"),
        (STATUS_INVALID_OPERATION, "STATUS_INVALID_OPERATION"),
        (STATUS_PERMISSION_DENIED, "STATUS_PERMISSION_DENIED"),
        (STATUS_TIMED_OUT, "STATUS_TIMED_OUT"),
        (STATUS_BAD_VALUE, "STATUS_BAD_VALUE"),
        (STATUS_BAD_TYPE, "STATUS_BAD_TYPE"),
        (STATUS_NO_INIT, "STATUS_NO_INIT"),
        (STATUS_NAME_NOT_FOUND, "STATUS_NAME_NOT_FOUND"),
        (STATUS_ALREADY_EXISTS, "STATUS_ALREADY_EXISTS"),
    )
)

STATUS_OFFSET_TABLE = OrderedDict(
    (
        ("STATUS_NO_ERROR_OFF", 0x00000000),
        ("STATUS_UNKNOWN_ERROR_OFF", 0x00000004),
        ("STATUS_INVALID_OPERATION_OFF", 0x00000008),
        ("STATUS_PERMISSION_DENIED_OFF", 0x0000000C),
        ("STATUS_TIMED_OUT_OFF", 0x00000010),
        ("STATUS_BAD_VALUE_OFF", 0x00000014),
        ("STATUS_BAD_TYPE_OFF", 0x00000018),
        ("STATUS_NO_INIT_OFF", 0x0000001C),
        ("STATUS_NAME_NOT_FOUND_OFF", 0x00000020),
        ("STATUS_ALREADY_EXISTS_OFF", 0x00000024),
    )
)

STATUS_ADDR_TABLE = OrderedDict(
    (
        ("STATUS_NO_ERROR_ADDR", 0x80000000 + 0x00000000),
        ("STATUS_UNKNOWN_ERROR_ADDR", 0x80000000 + 0x00000004),
        ("STATUS_INVALID_OPERATION_ADDR", 0x80000000 + 0x00000008),
        ("STATUS_PERMISSION_DENIED_ADDR", 0x80000000 + 0x0000000C),
        ("STATUS_TIMED_OUT_ADDR", 0x80000000 + 0x00000010),
        ("STATUS_BAD_VALUE_ADDR", 0x80000000 + 0x00000014),
        ("STATUS_BAD_TYPE_ADDR", 0x80000000 + 0x00000018),
        ("STATUS_NO_INIT_ADDR", 0x80000000 + 0x0000001C),
        ("STATUS_NAME_NOT_FOUND_ADDR", 0x80000000 + 0x00000020),
        ("STATUS_ALREADY_EXISTS_ADDR", 0x80000000 + 0x00000024),
    )
)

STATUS_ALL = (
    STATUS_NO_ERROR,
    STATUS_UNKNOWN_ERROR,
    STATUS_INVALID_OPERATION,
    STATUS_PERMISSION_DENIED,
    STATUS_TIMED_OUT,
    STATUS_BAD_VALUE,
    STATUS_BAD_TYPE,
    STATUS_NO_INIT,
    STATUS_NAME_NOT_FOUND,
    STATUS_ALREADY_EXISTS,
)

STATUS_SET = frozenset(STATUS_ALL)

DOORS = ("Angel", "Evil", "Lucky")
DOOR_COUNT = len(DOORS)
DOOR_INDEX_ANGEL = 0
DOOR_INDEX_EVIL = 1
DOOR_INDEX_LUCKY = 2

DOOR_CHOICES = (
    "[1] Angel",
    "[2] Evil",
    "[3] Lucky",
)

PENALTY_LOCK = 0
PENALTY_FILE = 1
PENALTY_EXIT = 2
PENALTY_COUNT = 3

PENALTY_NAMES = (
    "Lockdown",
    "FortuneFile",
    "InstantExit",
)

GAME_IDLE = 0
GAME_WAITING = 1
GAME_DONE = 2

RESULT_GOOD = "Good"
RESULT_BAD = "Bad"
RESULT_UNKNOWN = "Unknown"

DIVIDER_TEXT = "-" * 40
TITLE_TEXT = "LuckyDoor"
MENU_PROMPT_TEXT = "[1] = Play  [2] = History  [3] = Clear History  [Ctrl+C] = Exit"
CHOOSE_PROMPT_TEXT = "Choose a door:"
RESULT_PROMPT_TEXT = "[R] = Play Again  [M] = Menu  [Q] = Quit"
HISTORY_TITLE_TEXT = "History"
HISTORY_HEADER_TEXT = "No.  Date                 Choice     Lucky      Result"
HISTORY_EMPTY_TEXT = "No records found."
BACK_PROMPT_TEXT = "[Esc] = Back"
CLEAR_PROMPT_TEXT = "Clear all history? (Y/N)"
CLEAR_CONFIRM_TEXT = "[Y] = Confirm"
CLEAR_CANCEL_TEXT = "[N] = Cancel"
INVALID_INPUT_TEXT = "Invalid input."

CHOSEN_FMT = "You chose: {chosen}"
LUCKY_FMT = "Lucky door: {lucky}"
GOOD_TEXT = "Your luck is good today."
BAD_TEXT = "Your luck is bad today."
UNKNOWN_TEXT = "Unknown."

PENALTY_LOCK_FMT = "Locked for {seconds} seconds..."
PENALTY_LOCK_TICK_FMT = "{seconds}..."
PENALTY_LOCK_DONE_TEXT = "Lock released."
PENALTY_FILE_FMT = "Fortune file written: {path}"
PENALTY_FILE_FAIL_FMT = "Fortune file failed: {path}"
PENALTY_EXIT_TEXT = "Your luck ran out. Game over."

HISTORY_ROW_FMT = "{index:>3}  {timestamp:<20} {choice:<10} {lucky:<10} {result}"

KEY_CTRL_C = 3
KEY_ENTER = 13
KEY_ESCAPE = 27
KEY_SPACE = 32
KEY_ONE = 49
KEY_TWO = 50
KEY_THREE = 51
KEY_LOWER_Y = 121
KEY_UPPER_Y = 89
KEY_LOWER_N = 110
KEY_UPPER_N = 78
KEY_LOWER_R = 114
KEY_UPPER_R = 82
KEY_LOWER_M = 109
KEY_UPPER_M = 77
KEY_LOWER_Q = 113
KEY_UPPER_Q = 81
KEY_LOWER_H = 104
KEY_UPPER_H = 72
KEY_BACKSPACE = 127
KEY_BACKSPACE_ALT = 8

RECORDS_PATH = "luckydoor_records.json"
RECORDS_ENCODING = "utf-8"
RECORDS_INDENT = 2

FORTUNE_DIR = "/storage/emulated/0/Download"
FORTUNE_NAME = "LuckyValue"
FORTUNE_PATH = os.path.join(FORTUNE_DIR, FORTUNE_NAME)
FORTUNE_ENCODING = "utf-8"

TIME_SLEEP_INVALID = 0.4
TIME_SLEEP_FEEDBACK = 0.6
TIME_LOCK_SECONDS = 5
TIME_LOCK_TICK = 1.0

HASH_SALT_A = "luckydoor-alpha"
HASH_SALT_B = "luckydoor-beta"
HASH_SALT_C = "luckydoor-gamma"
HASH_SALT_D = "luckydoor-delta"
HASH_SALT_E = "luckydoor-epsilon"
HASH_SALT_F = "luckydoor-zeta"

HASH_ROUNDS = 6
HASH_ALGORITHMS = ("md5", "sha1", "sha224", "sha256", "sha384", "sha512")


def status_name(code: int) -> str:
    return STATUS_NAME_TABLE.get(int(code), "STATUS_UNKNOWN_ERROR")


def status_offset(code: int) -> int:
    value = int(code)
    if value in STATUS_SET:
        return STATUS_ALL.index(value) * 0x00000004
    return 0x00000004


def status_address(code: int) -> int:
    return 0x80000000 + status_offset(code)


def is_ok(code: int) -> bool:
    return int(code) == STATUS_NO_ERROR


def is_error(code: int) -> bool:
    return int(code) != STATUS_NO_ERROR


def status_guard(func: Callable[..., Any]) -> Callable[..., int]:
    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> int:
        try:
            result = func(*args, **kwargs)
        except MemoryError:
            return STATUS_UNKNOWN_ERROR
        except PermissionError:
            return STATUS_PERMISSION_DENIED
        except TimeoutError:
            return STATUS_TIMED_OUT
        except FileNotFoundError:
            return STATUS_NAME_NOT_FOUND
        except FileExistsError:
            return STATUS_ALREADY_EXISTS
        except KeyError:
            return STATUS_NAME_NOT_FOUND
        except ValueError:
            return STATUS_BAD_VALUE
        except TypeError:
            return STATUS_BAD_TYPE
        except AttributeError:
            return STATUS_NO_INIT
        except NotImplementedError:
            return STATUS_INVALID_OPERATION
        except Exception:
            return STATUS_UNKNOWN_ERROR
        if result is None:
            return STATUS_NO_ERROR
        if isinstance(result, bool):
            return STATUS_NO_ERROR if result else STATUS_UNKNOWN_ERROR
        if isinstance(result, int):
            return result
        return STATUS_NO_ERROR
    return wrapper


@status_guard
def emit(text: str) -> int:
    sys.stdout.write(str(text))
    sys.stdout.flush()
    return STATUS_NO_ERROR


@status_guard
def emit_line(text: str) -> int:
    sys.stdout.write(str(text))
    sys.stdout.write("\n")
    sys.stdout.flush()
    return STATUS_NO_ERROR


@status_guard
def emit_blank() -> int:
    sys.stdout.write("\n")
    sys.stdout.flush()
    return STATUS_NO_ERROR


@status_guard
def clear_screen() -> int:
    if os.name == "nt":
        os.system("cls")
    else:
        os.system("clear")
    return STATUS_NO_ERROR


@status_guard
def enable_ansi() -> int:
    if os.name == "nt":
        os.system("")
    return STATUS_NO_ERROR


@status_guard
def read_key() -> int:
    if os.name == "nt":
        import msvcrt
        ch = msvcrt.getch()
        if ch in (b"\x00", b"\xe0"):
            msvcrt.getch()
            return -1
        if ch == b"\x03":
            return KEY_CTRL_C
        if ch == b"\r":
            return KEY_ENTER
        try:
            return ord(ch.decode("utf-8"))
        except UnicodeDecodeError:
            return int(ch[0])
    else:
        import termios
        import tty
        fd = sys.stdin.fileno()
        old = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch = sys.stdin.read(1)
            if ch == "\x03":
                return KEY_CTRL_C
            if ch == "\x1b":
                sys.stdin.read(2)
                return KEY_ESCAPE
            if ch in ("\r", "\n"):
                return KEY_ENTER
            if ch == "\x7f":
                return KEY_BACKSPACE
            if ch == "\x08":
                return KEY_BACKSPACE_ALT
            return ord(ch)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old)
    return -1


@status_guard
def drain_input() -> int:
    try:
        while select.select([sys.stdin], [], [], 0)[0]:
            sys.stdin.read(1)
    except Exception:
        return STATUS_NO_ERROR
    return STATUS_NO_ERROR


class HistoryStore:
    def __init__(self, path: str = RECORDS_PATH) -> None:
        self.path = path
        self.records: List[Dict[str, Any]] = []
        self.lock = threading.RLock()

    @status_guard
    def load(self) -> int:
        with self.lock:
            if not os.path.exists(self.path):
                self.records = []
                return STATUS_NO_ERROR
            with open(self.path, "r", encoding=RECORDS_ENCODING) as handle:
                data = json.load(handle)
            if not isinstance(data, list):
                return STATUS_BAD_TYPE
            self.records = data
        return STATUS_NO_ERROR

    @status_guard
    def save(self) -> int:
        with self.lock:
            with open(self.path, "w", encoding=RECORDS_ENCODING) as handle:
                json.dump(self.records, handle, ensure_ascii=False, indent=RECORDS_INDENT)
        return STATUS_NO_ERROR

    @status_guard
    def append(self, record: Dict[str, Any]) -> int:
        if not isinstance(record, dict):
            return STATUS_BAD_TYPE
        with self.lock:
            self.records.append(record)
        return self.save()

    @status_guard
    def clear(self) -> int:
        with self.lock:
            self.records = []
            if os.path.exists(self.path):
                os.remove(self.path)
        return STATUS_NO_ERROR

    def is_empty(self) -> bool:
        with self.lock:
            return not self.records

    def rows(self) -> Iterator[Dict[str, Any]]:
        with self.lock:
            snapshot = tuple(self.records)
        return iter(snapshot)

    def __len__(self) -> int:
        with self.lock:
            return len(self.records)


HISTORY = HistoryStore()


def _hash_layer(raw: str, salt: str, algorithm: str) -> str:
    material = f"{salt}|{raw}|{salt}".encode("utf-8")
    hasher = hashlib.new(algorithm)
    hasher.update(material)
    return hasher.hexdigest()


def _hash_chain(seed: str, rounds: int = HASH_ROUNDS) -> str:
    raw = seed
    salts = (
        HASH_SALT_A,
        HASH_SALT_B,
        HASH_SALT_C,
        HASH_SALT_D,
        HASH_SALT_E,
        HASH_SALT_F,
    )
    for index in range(rounds):
        algorithm = HASH_ALGORITHMS[index % len(HASH_ALGORITHMS)]
        salt = salts[index % len(salts)]
        raw = _hash_layer(raw, salt, algorithm)
    return raw


def _hash_to_index(raw: str, modulo: int) -> int:
    if modulo <= 0:
        return 0
    digest = _hash_chain(raw, HASH_ROUNDS)
    return int(digest, 16) % modulo


def _hash_to_float(raw: str) -> float:
    digest = _hash_chain(raw, HASH_ROUNDS)
    value = int(digest, 16)
    return (value % 1000000) / 1000000.0


def _entropy_token() -> str:
    return str(random.SystemRandom().getrandbits(256))


def _time_token() -> str:
    return str(time.time_ns())


def generate_lucky_door(
    player_choice: int,
    round_index: int,
    nonce: Optional[str] = None,
    extra: Optional[str] = None,
) -> int:
    parts = (
        HASH_SALT_A,
        str(player_choice),
        str(round_index),
        _time_token(),
        _entropy_token(),
        HASH_SALT_B,
        nonce if nonce is not None else "",
        extra if extra is not None else "",
        HASH_SALT_C,
    )
    raw = "::".join(parts)
    return _hash_to_index(raw, DOOR_COUNT)


def generate_lucky_door_name(
    player_choice: int,
    round_index: int,
    nonce: Optional[str] = None,
    extra: Optional[str] = None,
) -> str:
    return DOORS[generate_lucky_door(player_choice, round_index, nonce, extra)]


def generate_penalty(
    player_choice: int,
    lucky_choice: int,
    round_index: int,
    nonce: Optional[str] = None,
    extra: Optional[str] = None,
) -> int:
    parts = (
        HASH_SALT_D,
        str(player_choice),
        str(lucky_choice),
        str(round_index),
        _time_token(),
        _entropy_token(),
        HASH_SALT_E,
        nonce if nonce is not None else "",
        extra if extra is not None else "",
        HASH_SALT_F,
    )
    raw = "::".join(parts)
    return _hash_to_index(raw, PENALTY_COUNT)


def generate_luck_percent(
    player_choice: int,
    lucky_choice: int,
    round_index: int,
    nonce: Optional[str] = None,
    extra: Optional[str] = None,
) -> float:
    parts = (
        HASH_SALT_B,
        str(player_choice),
        str(lucky_choice),
        str(round_index),
        _time_token(),
        _entropy_token(),
        HASH_SALT_C,
        nonce if nonce is not None else "",
        extra if extra is not None else "",
        HASH_SALT_D,
    )
    raw = "::".join(parts)
    return _hash_to_float(raw)


def door_index_by_name(name: str) -> int:
    try:
        return DOORS.index(str(name))
    except ValueError:
        return -1


def door_name_by_index(index: int) -> str:
    if 0 <= index < DOOR_COUNT:
        return DOORS[index]
    return RESULT_UNKNOWN


def door_choice_by_key(code: int) -> int:
    if code == KEY_ONE:
        return DOOR_INDEX_ANGEL
    if code == KEY_TWO:
        return DOOR_INDEX_EVIL
    if code == KEY_THREE:
        return DOOR_INDEX_LUCKY
    return -1


def penalty_name_by_index(index: int) -> str:
    if 0 <= index < PENALTY_COUNT:
        return PENALTY_NAMES[index]
    return RESULT_UNKNOWN


def make_nonce() -> str:
    return hashlib.sha256(_time_token().encode("utf-8")).hexdigest()


def luck_evaluation(percent: float) -> str:
    if percent >= 0.9:
        return "Extremely lucky."
    if percent >= 0.7:
        return "Very lucky."
    if percent >= 0.5:
        return "Above average."
    if percent >= 0.3:
        return "Below average."
    if percent >= 0.1:
        return "Very unlucky."
    return "Extremely unlucky."

class LuckyDoorGame:
    def __init__(self) -> None:
        self.state: int = GAME_IDLE
        self.round_index: int = 0
        self.player_choice: int = -1
        self.lucky_index: int = -1
        self.penalty_index: int = -1
        self.luck_percent: float = 0.0
        self.nonce: str = ""
        self.extra: str = ""
        self.start_time: float = 0.0
        self.end_time: float = 0.0
        self.lock = threading.RLock()

    @status_guard
    def new_round(self) -> int:
        with self.lock:
            self.round_index += 1
            self.player_choice = -1
            self.lucky_index = -1
            self.penalty_index = -1
            self.luck_percent = 0.0
            self.nonce = make_nonce()
            self.extra = hashlib.sha256(
                f"{self.round_index}:{self.nonce}".encode("utf-8")
            ).hexdigest()
            self.state = GAME_WAITING
            self.start_time = time.monotonic()
            self.end_time = self.start_time
        return STATUS_NO_ERROR

    @status_guard
    def choose(self, choice: int) -> int:
        with self.lock:
            if self.state != GAME_WAITING:
                return STATUS_INVALID_OPERATION
            if not (0 <= choice < DOOR_COUNT):
                return STATUS_BAD_VALUE
            self.player_choice = int(choice)
            self.lucky_index = generate_lucky_door(
                self.player_choice,
                self.round_index,
                self.nonce,
                self.extra,
            )
            self.luck_percent = generate_luck_percent(
                self.player_choice,
                self.lucky_index,
                self.round_index,
                self.nonce,
                self.extra,
            )
            self.state = GAME_DONE
            self.end_time = time.monotonic()
        return STATUS_NO_ERROR

    @status_guard
    def roll_penalty(self) -> int:
        with self.lock:
            if self.state != GAME_DONE:
                return STATUS_INVALID_OPERATION
            if self.is_win():
                return STATUS_INVALID_OPERATION
            self.penalty_index = generate_penalty(
                self.player_choice,
                self.lucky_index,
                self.round_index,
                self.nonce,
                self.extra,
            )
        return STATUS_NO_ERROR

    def is_waiting(self) -> bool:
        return self.state == GAME_WAITING

    def is_done(self) -> bool:
        return self.state == GAME_DONE

    def is_win(self) -> bool:
        if self.player_choice < 0 or self.lucky_index < 0:
            return False
        return self.player_choice == self.lucky_index

    def is_lose(self) -> bool:
        if self.player_choice < 0 or self.lucky_index < 0:
            return False
        return self.player_choice != self.lucky_index

    def elapsed(self) -> int:
        if self.state == GAME_WAITING:
            return int(time.monotonic() - self.start_time)
        return int(self.end_time - self.start_time)

    def chosen_name(self) -> str:
        return door_name_by_index(self.player_choice)

    def lucky_name(self) -> str:
        return door_name_by_index(self.lucky_index)

    def penalty_name(self) -> str:
        return penalty_name_by_index(self.penalty_index)

    def result_name(self) -> str:
        if self.is_win():
            return RESULT_GOOD
        if self.is_lose():
            return RESULT_BAD
        return RESULT_UNKNOWN

    def evaluation(self) -> str:
        return luck_evaluation(self.luck_percent)

    @status_guard
    def save(self) -> int:
        if self.state != GAME_DONE:
            return STATUS_INVALID_OPERATION
        record = OrderedDict(
            (
                ("timestamp", time.strftime("%Y-%m-%d %H:%M:%S")),
                ("choice", self.chosen_name()),
                ("lucky", self.lucky_name()),
                ("result", self.result_name()),
                ("penalty", self.penalty_name()),
                ("luck", round(self.luck_percent, 6)),
                ("duration", self.elapsed()),
            )
        )
        HISTORY.load()
        return HISTORY.append(record)

    @status_guard
    def reset(self) -> int:
        with self.lock:
            self.state = GAME_IDLE
            self.player_choice = -1
            self.lucky_index = -1
            self.penalty_index = -1
            self.luck_percent = 0.0
            self.nonce = ""
            self.extra = ""
            self.start_time = 0.0
            self.end_time = 0.0
        return STATUS_NO_ERROR


GAME = LuckyDoorGame()


@status_guard
def start_new_round() -> int:
    return GAME.new_round()


@status_guard
def choose_door(choice: int) -> int:
    return GAME.choose(choice)


@status_guard
def roll_penalty() -> int:
    return GAME.roll_penalty()


@status_guard
def save_round() -> int:
    return GAME.save()


@status_guard
def reset_round() -> int:
    return GAME.reset()


@status_guard
def apply_lockdown() -> int:
    remaining = TIME_LOCK_SECONDS
    emit_line(PENALTY_LOCK_FMT.format(seconds=TIME_LOCK_SECONDS))
    while remaining > 0:
        emit_line(PENALTY_LOCK_TICK_FMT.format(seconds=remaining))
        end_at = time.monotonic() + TIME_LOCK_TICK
        while time.monotonic() < end_at:
            time.sleep(0.05)
        remaining -= 1
    emit_line(PENALTY_LOCK_DONE_TEXT)
    time.sleep(TIME_SLEEP_FEEDBACK)
    return STATUS_NO_ERROR


@status_guard
def apply_fortune_file() -> int:
    percent = GAME.luck_percent * 100.0
    lines = (
        f"Luck Probability: {percent:.2f}%",
        f"Evaluation: {GAME.evaluation()}",
        f"Round: {GAME.round_index}",
        f"Choice: {GAME.chosen_name()}",
        f"Lucky: {GAME.lucky_name()}",
        f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}",
    )
    body = "\n".join(lines) + "\n"
    try:
        os.makedirs(FORTUNE_DIR, exist_ok=True)
        with open(FORTUNE_PATH, "w", encoding=FORTUNE_ENCODING) as handle:
            handle.write(body)
    except Exception:
        emit_line(PENALTY_FILE_FAIL_FMT.format(path=FORTUNE_PATH))
        time.sleep(TIME_SLEEP_FEEDBACK)
        return STATUS_PERMISSION_DENIED
    emit_line(PENALTY_FILE_FMT.format(path=FORTUNE_PATH))
    time.sleep(TIME_SLEEP_FEEDBACK)
    return STATUS_NO_ERROR


@status_guard
def apply_penalty() -> int:
    if GAME.penalty_index == PENALTY_LOCK:
        return apply_lockdown()
    if GAME.penalty_index == PENALTY_FILE:
        return apply_fortune_file()
    if GAME.penalty_index == PENALTY_EXIT:
        emit_line(PENALTY_EXIT_TEXT)
        time.sleep(TIME_SLEEP_FEEDBACK)
        return STATUS_PERMISSION_DENIED
    return STATUS_INVALID_OPERATION


@status_guard
def render_main_menu() -> int:
    clear_screen()
    emit_line(DIVIDER_TEXT)
    emit_line(TITLE_TEXT)
    emit_blank()
    emit_line(MENU_PROMPT_TEXT)
    emit_line(DIVIDER_TEXT)
    return STATUS_NO_ERROR


@status_guard
def render_history_header() -> int:
    clear_screen()
    emit_line(DIVIDER_TEXT)
    emit_line(HISTORY_TITLE_TEXT)
    emit_line(DIVIDER_TEXT)
    emit_line(HISTORY_HEADER_TEXT)
    emit_line(DIVIDER_TEXT)
    return STATUS_NO_ERROR


@status_guard
def render_history_empty() -> int:
    emit_line(HISTORY_EMPTY_TEXT)
    return STATUS_NO_ERROR


@status_guard
def render_history_row(index: int, record: Dict[str, Any]) -> int:
    timestamp = str(record.get("timestamp", ""))
    choice = str(record.get("choice", ""))
    lucky = str(record.get("lucky", ""))
    result = str(record.get("result", ""))
    line = HISTORY_ROW_FMT.format(
        index=index,
        timestamp=timestamp,
        choice=choice,
        lucky=lucky,
        result=result,
    )
    emit_line(line)
    return STATUS_NO_ERROR


@status_guard
def render_history_rows() -> int:
    if HISTORY.is_empty():
        render_history_empty()
        return STATUS_NO_ERROR
    for index, record in enumerate(HISTORY.rows(), start=1):
        render_history_row(index, record)
    return STATUS_NO_ERROR


@status_guard
def render_history_footer() -> int:
    emit_line(DIVIDER_TEXT)
    emit_line(BACK_PROMPT_TEXT)
    return STATUS_NO_ERROR


@status_guard
def show_history() -> int:
    HISTORY.load()
    render_history_header()
    render_history_rows()
    render_history_footer()
    while True:
        code = read_key()
        if code == KEY_CTRL_C:
            return STATUS_UNKNOWN_ERROR
        if code in (KEY_ESCAPE, KEY_ENTER):
            return STATUS_NO_ERROR
    return STATUS_NO_ERROR


@status_guard
def render_clear_header() -> int:
    clear_screen()
    emit_line(DIVIDER_TEXT)
    emit_line(CLEAR_PROMPT_TEXT)
    emit_blank()
    emit_line(CLEAR_CONFIRM_TEXT)
    emit_line(CLEAR_CANCEL_TEXT)
    emit_line(DIVIDER_TEXT)
    return STATUS_NO_ERROR


@status_guard
def clear_history() -> int:
    render_clear_header()
    while True:
        code = read_key()
        if code == KEY_CTRL_C:
            return STATUS_UNKNOWN_ERROR
        if code in (KEY_LOWER_Y, KEY_UPPER_Y):
            HISTORY.clear()
            return STATUS_NO_ERROR
        if code in (KEY_LOWER_N, KEY_UPPER_N):
            return STATUS_NO_ERROR
        if code == KEY_ESCAPE:
            return STATUS_NO_ERROR
    return STATUS_NO_ERROR


@status_guard
def render_choose_screen() -> int:
    clear_screen()
    emit_line(DIVIDER_TEXT)
    emit_line(TITLE_TEXT)
    emit_line(DIVIDER_TEXT)
    emit_line(CHOOSE_PROMPT_TEXT)
    emit_blank()
    for line in DOOR_CHOICES:
        emit_line(line)
    emit_line(DIVIDER_TEXT)
    return STATUS_NO_ERROR


@status_guard
def render_result_screen() -> int:
    clear_screen()
    emit_line(DIVIDER_TEXT)
    emit_line(TITLE_TEXT)
    emit_line(DIVIDER_TEXT)
    emit_line(CHOSEN_FMT.format(chosen=GAME.chosen_name()))
    emit_line(LUCKY_FMT.format(lucky=GAME.lucky_name()))
    emit_blank()
    if GAME.is_win():
        emit_line(GOOD_TEXT)
    elif GAME.is_lose():
        emit_line(BAD_TEXT)
    else:
        emit_line(UNKNOWN_TEXT)
    emit_line(DIVIDER_TEXT)
    emit_line(RESULT_PROMPT_TEXT)
    return STATUS_NO_ERROR


@status_guard
def render_invalid() -> int:
    emit_line(INVALID_INPUT_TEXT)
    return STATUS_NO_ERROR


@status_guard
def render_feedback(text: str) -> int:
    emit_line(text)
    return STATUS_NO_ERROR


@status_guard
def wait_choose_key() -> int:
    while True:
        code = read_key()
        if code == KEY_CTRL_C:
            return STATUS_UNKNOWN_ERROR
        if code == KEY_ESCAPE:
            return STATUS_UNKNOWN_ERROR
        choice = door_choice_by_key(code)
        if choice >= 0:
            result = GAME.choose(choice)
            if result == STATUS_NO_ERROR:
                return STATUS_NO_ERROR
            if result == STATUS_INVALID_OPERATION:
                return STATUS_UNKNOWN_ERROR
            render_invalid()
            time.sleep(TIME_SLEEP_INVALID)
            continue
        render_invalid()
        time.sleep(TIME_SLEEP_INVALID)
    return STATUS_NO_ERROR


@status_guard
def wait_result_key() -> int:
    while True:
        code = read_key()
        if code == KEY_CTRL_C:
            return STATUS_PERMISSION_DENIED
        if code == KEY_ESCAPE:
            return STATUS_UNKNOWN_ERROR
        if code in (KEY_LOWER_R, KEY_UPPER_R):
            return STATUS_NO_ERROR
        if code in (KEY_LOWER_M, KEY_UPPER_M):
            return STATUS_UNKNOWN_ERROR
        if code in (KEY_LOWER_Q, KEY_UPPER_Q):
            return STATUS_PERMISSION_DENIED
        if code in (KEY_LOWER_H, KEY_UPPER_H):
            show_history()
            render_result_screen()
            continue
        render_invalid()
        time.sleep(TIME_SLEEP_INVALID)
    return STATUS_NO_ERROR


@status_guard
def play_round() -> int:
    start_new_round()
    while GAME.is_waiting():
        render_choose_screen()
        emit("> ")
        code = wait_choose_key()
        if code == STATUS_UNKNOWN_ERROR:
            return STATUS_UNKNOWN_ERROR
        if code == STATUS_NO_ERROR:
            break
    save_round()
    if GAME.is_lose():
        roll_penalty()
        penalty_code = apply_penalty()
        if penalty_code == STATUS_PERMISSION_DENIED:
            return STATUS_PERMISSION_DENIED
    while GAME.is_done():
        render_result_screen()
        emit("> ")
        code = wait_result_key()
        if code == STATUS_NO_ERROR:
            return STATUS_NO_ERROR
        if code == STATUS_UNKNOWN_ERROR:
            return STATUS_UNKNOWN_ERROR
        if code == STATUS_PERMISSION_DENIED:
            return STATUS_PERMISSION_DENIED
    return STATUS_NO_ERROR


@status_guard
def play_loop() -> int:
    while True:
        code = play_round()
        if code == STATUS_NO_ERROR:
            continue
        if code == STATUS_UNKNOWN_ERROR:
            return STATUS_UNKNOWN_ERROR
        if code == STATUS_PERMISSION_DENIED:
            return STATUS_PERMISSION_DENIED
    return STATUS_NO_ERROR


@status_guard
def handle_main_key(code: int) -> int:
    if code == KEY_CTRL_C:
        return STATUS_PERMISSION_DENIED
    if code in (KEY_ONE, KEY_ENTER, KEY_SPACE):
        return STATUS_NO_ERROR
    if code == KEY_TWO:
        show_history()
        return STATUS_NO_INIT
    if code == KEY_THREE:
        clear_history()
        return STATUS_NO_INIT
    if code == KEY_ESCAPE:
        return STATUS_NO_INIT
    render_invalid()
    time.sleep(TIME_SLEEP_INVALID)
    return STATUS_NO_INIT


@status_guard
def main_menu_loop() -> int:
    enable_ansi()
    HISTORY.load()
    while True:
        render_main_menu()
        code = read_key()
        result = handle_main_key(code)
        if result == STATUS_PERMISSION_DENIED:
            return STATUS_PERMISSION_DENIED
        if result == STATUS_NO_ERROR:
            return STATUS_NO_ERROR
    return STATUS_NO_ERROR


@status_guard
def application_loop() -> int:
    enable_ansi()
    HISTORY.load()
    while True:
        code = main_menu_loop()
        if code == STATUS_PERMISSION_DENIED:
            clear_screen()
            return STATUS_NO_ERROR
        if code == STATUS_NO_ERROR:
            outcome = play_loop()
            if outcome == STATUS_PERMISSION_DENIED:
                clear_screen()
                return STATUS_NO_ERROR
            if outcome == STATUS_UNKNOWN_ERROR:
                continue
    return STATUS_NO_ERROR

@status_guard
def bootstrap() -> int:
    enable_ansi()
    HISTORY.load()
    return application_loop()


@status_guard
def entry_point() -> int:
    try:
        return bootstrap()
    except KeyboardInterrupt:
        clear_screen()
        return STATUS_NO_ERROR
    except Exception:
        clear_screen()
        return STATUS_UNKNOWN_ERROR


def iter_doors() -> Iterator[str]:
    return iter(DOORS)


def iter_door_choices() -> Iterator[str]:
    return iter(DOOR_CHOICES)


def iter_penalties() -> Iterator[str]:
    return iter(PENALTY_NAMES)


def iter_main_keys() -> Iterator[int]:
    return iter(
        (
            KEY_CTRL_C,
            KEY_ENTER,
            KEY_SPACE,
            KEY_ONE,
            KEY_TWO,
            KEY_THREE,
            KEY_ESCAPE,
        )
    )


def iter_choose_keys() -> Iterator[int]:
    return iter(
        (
            KEY_CTRL_C,
            KEY_ESCAPE,
            KEY_ONE,
            KEY_TWO,
            KEY_THREE,
        )
    )


def iter_result_keys() -> Iterator[int]:
    return iter(
        (
            KEY_CTRL_C,
            KEY_ESCAPE,
            KEY_LOWER_R,
            KEY_UPPER_R,
            KEY_LOWER_M,
            KEY_UPPER_M,
            KEY_LOWER_Q,
            KEY_UPPER_Q,
            KEY_LOWER_H,
            KEY_UPPER_H,
        )
    )


def iter_history_keys() -> Iterator[int]:
    return iter(
        (
            KEY_CTRL_C,
            KEY_ESCAPE,
            KEY_ENTER,
        )
    )


def iter_clear_keys() -> Iterator[int]:
    return iter(
        (
            KEY_CTRL_C,
            KEY_ESCAPE,
            KEY_LOWER_Y,
            KEY_UPPER_Y,
            KEY_LOWER_N,
            KEY_UPPER_N,
        )
    )


def door_status() -> int:
    if GAME.is_win():
        return STATUS_NO_ERROR
    if GAME.is_lose():
        return STATUS_UNKNOWN_ERROR
    return STATUS_NO_INIT


def door_address(index: int) -> int:
    return 0x80000000 + (index & 0x03) * 0x00000004


def door_offset(index: int) -> int:
    return (index & 0x03) * 0x00000004


def penalty_address(index: int) -> int:
    return 0x80000000 + (index & 0x03) * 0x00000004


def penalty_offset(index: int) -> int:
    return (index & 0x03) * 0x00000004


def round_signature() -> str:
    material = f"{GAME.round_index}:{GAME.nonce}:{GAME.extra}".encode("utf-8")
    return hashlib.sha256(material).hexdigest()


def verify_round() -> int:
    if GAME.state != GAME_DONE:
        return STATUS_INVALID_OPERATION
    if GAME.lucky_index < 0 or GAME.lucky_index >= DOOR_COUNT:
        return STATUS_BAD_VALUE
    if GAME.player_choice < 0 or GAME.player_choice >= DOOR_COUNT:
        return STATUS_BAD_VALUE
    return STATUS_NO_ERROR


def snapshot_round() -> Dict[str, Any]:
    return OrderedDict(
        (
            ("round", GAME.round_index),
            ("nonce", GAME.nonce),
            ("extra", GAME.extra),
            ("choice", GAME.chosen_name()),
            ("lucky", GAME.lucky_name()),
            ("result", GAME.result_name()),
            ("penalty", GAME.penalty_name()),
            ("luck", round(GAME.luck_percent, 6)),
            ("elapsed", GAME.elapsed()),
            ("signature", round_signature()),
        )
    )


def replay_hash(seed: str, rounds: int = HASH_ROUNDS) -> str:
    return _hash_chain(seed, rounds)


def replay_index(seed: str, modulo: int = DOOR_COUNT) -> int:
    return _hash_to_index(seed, modulo)


def replay_door(seed: str) -> str:
    return DOORS[replay_index(seed)]


def replay_penalty(seed: str) -> str:
    return PENALTY_NAMES[replay_index(seed, PENALTY_COUNT)]


def audit_round() -> int:
    code = verify_round()
    if code != STATUS_NO_ERROR:
        return code
    if round_signature() == "":
        return STATUS_UNKNOWN_ERROR
    return STATUS_NO_ERROR


def summarize_history() -> Dict[str, int]:
    total = 0
    good = 0
    bad = 0
    lock = 0
    file_penalty = 0
    exit_penalty = 0
    for record in HISTORY.rows():
        total += 1
        result = str(record.get("result", ""))
        penalty = str(record.get("penalty", ""))
        if result == RESULT_GOOD:
            good += 1
        elif result == RESULT_BAD:
            bad += 1
        if penalty == PENALTY_NAMES[PENALTY_LOCK]:
            lock += 1
        elif penalty == PENALTY_NAMES[PENALTY_FILE]:
            file_penalty += 1
        elif penalty == PENALTY_NAMES[PENALTY_EXIT]:
            exit_penalty += 1
    return OrderedDict(
        (
            ("total", total),
            ("good", good),
            ("bad", bad),
            ("lock", lock),
            ("file", file_penalty),
            ("exit", exit_penalty),
        )
    )


def format_summary() -> str:
    summary = summarize_history()
    return (
        f"Total: {summary['total']}  "
        f"Good: {summary['good']}  "
        f"Bad: {summary['bad']}  "
        f"Lock: {summary['lock']}  "
        f"File: {summary['file']}  "
        f"Exit: {summary['exit']}"
    )


def fortune_path() -> str:
    return FORTUNE_PATH


def fortune_exists() -> bool:
    return os.path.exists(FORTUNE_PATH)


def fortune_read() -> str:
    try:
        with open(FORTUNE_PATH, "r", encoding=FORTUNE_ENCODING) as handle:
            return handle.read()
    except Exception:
        return ""


def fortune_remove() -> int:
    try:
        if os.path.exists(FORTUNE_PATH):
            os.remove(FORTUNE_PATH)
    except Exception:
        return STATUS_PERMISSION_DENIED
    return STATUS_NO_ERROR


def run() -> int:
    return entry_point()


if __name__ == "__main__":
    sys.exit(run())


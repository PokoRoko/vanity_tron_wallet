from typing import TypedDict, Protocol
from bip_utils.bip.bip44_base.bip44_base import Bip44Base
from bip_utils.utils.mnemonic.mnemonic import Mnemonic
import re
from datetime import datetime
from re import Match, Pattern
import multiprocessing
import concurrent.futures
from bip_utils import (
    Bip39MnemonicGenerator,
    Bip39SeedGenerator,
    Bip44,
    Bip44Coins,
    Bip44Changes,
)

class Config(TypedDict):
    num_processes: int
    show_log: bool
    log_count: int
    is_included: bool
    keyword_included: str
    case_sensitive: bool
    use_leet: bool
    start_with: str | None
    end_with: str | None
    is_simetric: bool
    simetric_deep: int
    stop_on_found: bool


class StopEvent(Protocol):
    def is_set(self) -> bool: ...
    def set(self) -> None: ...


config: Config = {
    "num_processes": max(1, multiprocessing.cpu_count() - 1),  # Process count
    "show_log": True,  # Show progress or not
    "log_count": 10000,  # Show progress every N generations
    "is_included": True,  # Search for inclusion or not
    "keyword_included": "Bad",  # Keyword for search inclusion
    "case_sensitive": True,  # Register accuracy ! Dont work if "use_leet" is True
    "use_leet": False,  # Use leet or not
    "start_with": None,  # Start of address all addresses start with "T"
    "end_with": None,  # End of address
    "is_simetric": False,  # Symmetric matching or not
    "simetric_deep": 4,  # Symmetric matching depth
    "stop_on_found": True,  # Stop on first found wallet or not
}

LEET_MAP: dict[str, str] = {
    "a": "aA4",
    "b": "bB8",
    "e": "eE3",
    "i": "iIl1",
    "l": "lLi1",
    "o": "oO0",
    "s": "sS5",
    "t": "tT7",
    "z": "zZ2",
    "g": "gG9",
    "k": "kK",
    "p": "pP",
    "r": "rR",
    "n": "nN",
    "m": "mM",
    "c": "cC",
    "d": "dD",
    "y": "yY",
    "h": "hH",
    "v": "vV",
}


def has_palindrome_of_depth(s: str, depth: int, case_sensitive: bool = True) -> bool:
    if not case_sensitive:
        s = s.lower()
    n = len(s)

    def count_pairs(l: int, r: int) -> int:
        pairs = 0
        while l >= 0 and r < n and s[l] == s[r]:
            pairs += 1
            l -= 1
            r += 1
        return pairs

    # Odd centers: a(b)c(b)a
    for c in range(n):
        if count_pairs(c - 1, c + 1) >= depth:
            return True

    # Even centers: ab|ba
    for c in range(n - 1):
        if count_pairs(c, c + 1) >= depth:
            return True

    return False


def iterate(process_id: int, stop_event: StopEvent) -> dict[str, str] | None:
    i = 0
    while not stop_event.is_set():
        i += 1
        log_progress(process_id, i)
        # Generate new mnemonic and derive TRON address using BIP44 path m/44'/195'/0'/0/0
        mnemonic: Mnemonic = Bip39MnemonicGenerator().FromWordsNumber(12)
        seed_bytes: bytes = Bip39SeedGenerator(mnemonic).Generate()
        bip44_ctx: Bip44Base = Bip44.FromSeed(seed_bytes, Bip44Coins.TRON)
        acct: Bip44Base = (
            bip44_ctx.Purpose()
            .Coin()
            .Account(0)
            .Change(Bip44Changes.CHAIN_EXT)
            .AddressIndex(0)
        )

        address = acct.PublicKey().ToAddress()  # TRON Base58 address (starts with 'T')
        if address_matches_filters(address):
            return {
                "address": address,
                "seed_phrase": str(mnemonic),
                "private_key": acct.PrivateKey().Raw().ToHex(),
                "public_key": acct.PublicKey().RawUncompressed().ToHex(),
            }

    return None


def log_progress(process_id: int, attempts: int) -> None:
    """Logging progress of attempts every config['log_count'] attempts."""
    log_count: int = config["log_count"]
    if config["show_log"] and attempts % log_count == 0:
        print(
            f"{datetime.now().strftime(format='%H:%M:%S')} Process {process_id}: {attempts} total attempts"
        )


def address_matches_filters(address: str) -> bool:
    def char_class(ch: str) -> str:
        chars: str | None = LEET_MAP.get(ch.lower())
        if bool(config["use_leet"]) and chars:
            return f"[{chars}]"
        if not bool(config["case_sensitive"]):
            return f"[{ch.lower()}{ch.upper()}]"
        return f"[{ch}]"

    included: bool | None = None
    if bool(config["is_included"]):
        keyword_included: str = str(config["keyword_included"])
        pattern: str = "".join(char_class(ch) for ch in keyword_included)
        regex: Pattern[str] = re.compile(pattern)
        match: Match[str] | None = regex.search(address)
        if match is not None:
            included = True
        else:
            included = False

    is_symmetric: bool | None = None
    if bool(config["is_simetric"]):
        symmetric_depth: int = int(config["simetric_deep"])
        if has_palindrome_of_depth(
            s=address,
            depth=symmetric_depth,
            case_sensitive=bool(config["case_sensitive"]),
        ):
            is_symmetric = True
        else:
            is_symmetric = False

    starts_with: bool | None = None
    start_prefix: str | None = config.get("start_with")
    if start_prefix:
        if address.startswith(start_prefix):
            starts_with = True
        else:
            starts_with = False

    ends_with: bool | None = None
    end_suffix: str | None = config.get("end_with")
    if end_suffix:
        if address.endswith(end_suffix):
            ends_with = True
        else:
            ends_with = False

    return all(x is not False for x in (included, is_symmetric, starts_with, ends_with))


def main():
    with multiprocessing.Manager() as manager:
        stop_event: StopEvent = manager.Event()  # Create a common stop flag

        with concurrent.futures.ProcessPoolExecutor(
            max_workers=config["num_processes"]
        ) as executor:
            # Start parallel tasks with passing process number and stop flag
            num_workers: int = config["num_processes"]
            futures = [
                executor.submit(iterate, process_id=i + 1, stop_event=stop_event)
                for i in range(num_workers)
            ]

            for future in concurrent.futures.as_completed(futures):
                # Once one of the processes finds the desired wallet, end the program
                wallet: dict[str, str] | None = future.result()
                if wallet:
                    print("________________________________")
                    print("Found wallet!")
                    print("Address: " + wallet["address"])
                    print("Seed phrase: " + wallet["seed_phrase"])
                    print("Private key: " + wallet["private_key"])
                    print("Public key: " + wallet["public_key"])
                    print("________________________________")
                    if config["stop_on_found"]:
                        stop_event.set()
                        break


if __name__ == "__main__":
    main()

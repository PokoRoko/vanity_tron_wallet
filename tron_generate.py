from threading import Event
from pathlib import Path
from bip_utils.bip.bip44_base.bip44_base import Bip44Base
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

config = {
    "num_processes": max(1, multiprocessing.cpu_count() - 1),  # Process count
    "show_log": True,  # Show progress or not
    "log_count": 10000,  # Show progress every N generations
    "is_included": True,  # Search for inclusion or not
    "keyword_included": "BadBoy",  # Keyword for search inclusion
    "register_accuracy": True,  # Register accuracy ! Dont work if "use_leet" is True
    "use_leet": True,  # Use leet or not
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
    if not config["register_accuracy"]:
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


def iterate(process_id, stop_event) -> dict[str, str] | None:
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
        if find_possible_addresses(address):
            return {
                "address": address,
                "seed_phrase": str(mnemonic),
                "private_key": acct.PrivateKey().Raw().ToHex(),
                "public_key": acct.PublicKey().RawUncompressed().ToHex(),
            }

    return None


def log_progress(process_id, attempts):
    """Logging progress of attempts every 5000 attempts."""
    if config["show_log"] and attempts % config["log_count"] == 0:
        print(
            f"{datetime.now().strftime(format='%H:%M:%S')} Process {process_id}: {attempts} total attempts"
        )


def find_possible_addresses(address) -> list[str]:
    def char_class(ch: str) -> str:
        chars = LEET_MAP.get(ch.lower())
        if config["use_leet"] and chars:
            return f"[{chars}]"
        if config["register_accuracy"]:
            return f"[{ch.lower()}{ch.upper()}]"
        return f"[{ch}]"

    included = None
    if config["is_included"]:
        pattern: str = "".join(char_class(ch) for ch in str(config["keyword_included"]))
        regex: Pattern[str] = re.compile(pattern)
        matche: Match[str] | None = regex.search(address)
        if matche is not None:
            included = True
        else:
            included = False

    is_simetric = None
    if config["is_simetric"]:
        if has_palindrome_of_depth(
            s=address,
            depth=config["simetric_deep"],
            case_sensitive=not config["register_accuracy"],
        ):
            is_simetric = True
        else:
            is_simetric = False

    start_with = None
    if config["start_with"]:
        if address.startswith(config["start_with"]):
            start_with = True
        else:
            start_with = False

    end_with = None
    if config["end_with"]:
        if address.endswith(config["end_with"]):
            end_with = True
        else:
            end_with = False

    return False not in [included, is_simetric, start_with, end_with]


def main():
    with multiprocessing.Manager() as manager:
        stop_event: Event = manager.Event()  # Create a common stop flag

        with concurrent.futures.ProcessPoolExecutor(
            max_workers=config["num_processes"]
        ) as executor:
            # Start parallel tasks with passing process number and stop flag
            futures = [
                executor.submit(iterate, process_id=i + 1, stop_event=stop_event)
                for i in range(config["num_processes"])
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

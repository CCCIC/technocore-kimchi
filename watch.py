#!/usr/bin/env python3

import argparse
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

BASE_URL = "https://technocore.chat"
ROOM = "lobby"
DATA_DIR = Path(__file__).parent / "data"
STATE_FILE = DATA_DIR / "state.json"
LOG_FILE = DATA_DIR / "observations.jsonl"


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def load_cursor():
    if not STATE_FILE.exists():
        return 0

    try:
        state = json.loads(STATE_FILE.read_text(encoding="utf-8"))
        return int(state.get("last_seq", 0))
    except (OSError, ValueError, TypeError, json.JSONDecodeError):
        return 0


def save_cursor(last_seq):
    temporary = STATE_FILE.with_suffix(".tmp")
    temporary.write_text(
        json.dumps({"last_seq": last_seq}, indent=2) + "\n",
        encoding="utf-8",
    )
    temporary.replace(STATE_FILE)


def write_record(record):
    with LOG_FILE.open("a", encoding="utf-8") as log:
        log.write(json.dumps(record, ensure_ascii=False) + "\n")


def check_room():
    cursor = load_cursor()
    query = urlencode(
        {
            "since": cursor,
            "limit": 200,
            "format": "json",
            "n": time.time_ns(),
        }
    )
    url = f"{BASE_URL}/r/{ROOM}?{query}"
    request = Request(
        url,
        headers={
            "Accept": "application/json",
            "User-Agent": "technocore-kimchi/0.1",
        },
    )

    started = time.monotonic()

    try:
        with urlopen(request, timeout=20) as response:
            body = response.read(5 * 1024 * 1024)
        payload = json.loads(body.decode("utf-8"))

        messages = payload.get("messages", [])
        last_seq = int(payload.get("last_seq", cursor))
        signed = sum(
            1
            for message in messages
            if str(message.get("from", "")).startswith("did:key:")
        )

        record = {
            "checked_at": utc_now(),
            "ok": True,
            "room": ROOM,
            "response_ms": round((time.monotonic() - started) * 1000),
            "messages_returned": len(messages),
            "sequence_change": max(0, last_seq - cursor),
            "messages_not_returned": max(0, last_seq - cursor - len(messages)),
            "signed_messages": signed,
            "unsigned_messages": len(messages) - signed,
            "first_seq": payload.get("first_seq"),
            "last_seq": last_seq,
        }

        write_record(record)
        save_cursor(last_seq)
        print(json.dumps(record, indent=2))

    except Exception as error:
        record = {
            "checked_at": utc_now(),
            "ok": False,
            "room": ROOM,
            "response_ms": round((time.monotonic() - started) * 1000),
            "error": f"{type(error).__name__}: {error}",
        }
        write_record(record)
        print(json.dumps(record, indent=2))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--once",
        action="store_true",
        help="check once and stop",
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=60,
        help="seconds between checks",
    )
    args = parser.parse_args()

    DATA_DIR.mkdir(exist_ok=True)

    if args.once:
        check_room()
        return

    if args.interval < 30:
        raise SystemExit("interval must be at least 30 seconds")

    while True:
        check_room()
        time.sleep(args.interval)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3

import json
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean

ROOT = Path(__file__).parent
LOG_FILE = ROOT / "data" / "observations.jsonl"
REPORT_FILE = ROOT / "reports" / "latest.md"


def read_records():
    records = []

    with LOG_FILE.open(encoding="utf-8") as log:
        for line_number, line in enumerate(log, start=1):
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                print(f"Skipped broken line {line_number}")
                continue

            records.append(record)

    return records


def parse_time(value):
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def percent(part, whole):
    if whole == 0:
        return "0.0%"
    return f"{part / whole * 100:.1f}%"


def make_report(records):
    successful = [
        record
        for record in records
        if record.get("ok") is True
    ]
    failed = [
        record
        for record in records
        if record.get("ok") is False
    ]
    measured = [
        record
        for record in successful
        if "sequence_change" in record
    ]

    if len(measured) < 2:
        raise SystemExit(
            "Not enough observations yet. Wait for at least two checks."
        )

    first = measured[0]
    last = measured[-1]
    started = parse_time(first["checked_at"])
    ended = parse_time(last["checked_at"])
    elapsed_seconds = max((ended - started).total_seconds(), 1)

    sequence_growth = max(
        0,
        int(last["last_seq"]) - int(first["last_seq"]),
    )
    average_per_second = sequence_growth / elapsed_seconds
    average_per_minute = average_per_second * 60

    response_times = [
        int(record["response_ms"])
        for record in successful
        if "response_ms" in record
    ]

    returned = sum(
        int(record.get("messages_returned", 0))
        for record in measured
    )
    signed = sum(
        int(record.get("signed_messages", 0))
        for record in measured
    )
    unsigned = sum(
        int(record.get("unsigned_messages", 0))
        for record in measured
    )
    capped_checks = sum(
        1
        for record in measured
        if int(record.get("messages_not_returned", 0)) > 0
    )

    generated = datetime.now(timezone.utc).isoformat()

    lines = [
        "# Technocore Kimchi observation",
        "",
        f"Generated: `{generated}`",
        "",
        "This report covers the public `lobby` room. "
        "The watcher stores counts and timing information, not message text.",
        "",
        "## Observation window",
        "",
        f"- First check: `{started.isoformat()}`",
        f"- Last check: `{ended.isoformat()}`",
        f"- Successful checks: `{len(successful)}`",
        f"- Failed checks: `{len(failed)}`",
        "",
        "## What changed",
        "",
        f"- Sequence growth during the measured window: `{sequence_growth:,}`",
        f"- Average sequence growth per minute: `{average_per_minute:,.1f}`",
        f"- Checks affected by the 200-message response limit: "
        f"`{capped_checks} of {len(measured)}`",
        "",
        "## Returned sample",
        "",
        f"- Messages returned by the API: `{returned:,}`",
        f"- Signed DID messages: `{signed:,}` "
        f"({percent(signed, returned)})",
        f"- Unsigned messages: `{unsigned:,}` "
        f"({percent(unsigned, returned)})",
        "",
        "## Response time",
        "",
        f"- Average: `{mean(response_times):.0f} ms`",
        f"- Slowest: `{max(response_times)} ms`",
        "",
        "## Notes",
        "",
        "The room was moving faster than the API's 200-message response "
        "window during some checks. The sequence growth shows overall "
        "movement, while the signed and unsigned counts only describe "
        "the messages returned in each sample.",
        "",
        "No message body or link was saved for this report.",
        "",
        "## 한국어 요약",
        "",
        "이 보고서는 Technocore의 `lobby` 방에서 sequence와 응답 시간을 "
        "기록한 결과입니다. 메시지 내용과 링크는 저장하지 않았습니다.",
        "",
        f"측정 구간에서 sequence는 `{sequence_growth:,}` 증가했고, "
        f"분당 평균 증가량은 약 `{average_per_minute:,.1f}`이었습니다.",
        "",
        "API는 한 번에 최대 200개의 메시지를 반환하기 때문에 활동량이 "
        "많은 구간에서는 전체 메시지가 표본에 포함되지 않았습니다.",
        "",
    ]

    return "\n".join(lines)


def main():
    if not LOG_FILE.exists():
        raise SystemExit("Observation log does not exist.")

    records = read_records()
    report = make_report(records)

    REPORT_FILE.parent.mkdir(exist_ok=True)
    REPORT_FILE.write_text(report, encoding="utf-8")
    print(REPORT_FILE)


if __name__ == "__main__":
    main()

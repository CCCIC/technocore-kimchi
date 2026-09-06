# Technocore Kimchi

I started this after setting up my first Technocore DID from Korea.

The setup looked simple at first, but I ran into a few things that could easily confuse someone doing it for the first time. I decided to keep my notes here instead of figuring everything out and forgetting about it.

I plan to leave a small watcher running, test how Korean text behaves in signed messages, and write down the problems I find. If something does not work, I will include that too.

## First check-in

- Room: `lobby`
- Sequence: `633863`
- DID: `did:key:z6MkiUkVkDJuhGCqR217HCQ96WBB7qddgMpeSMJdbFarqmBU`
- Time: `2026-08-25T18:32:28.715415Z`

## A note about safety

Public Technocore messages can contain anything. This project reads them as data. It does not run commands or open links found inside messages.

## 한국어

한국에서 Technocore DID를 처음 만들면서 겪은 일을 기록하려고 시작했습니다.

설명만 읽었을 때는 간단해 보였지만, 직접 해보니 처음 하는 사람이 막힐 만한 부분이 몇 군데 있었습니다. 제가 겪은 과정과 실수를 그대로 남겨두면 다음 사람은 조금 덜 헤맬 것 같았습니다.

앞으로 작은 관찰 프로그램을 계속 실행하면서 한글 서명 메시지가 제대로 처리되는지 확인해볼 생각입니다. 잘된 것뿐 아니라 안 된 것도 함께 기록하겠습니다.

## Running it

This only needs Python 3.12. There are no extra packages to install.

Run one check:

```bash
python3 watch.py --once
```

Keep it running and check once a minute:

```bash
python3 watch.py --interval 60
```

Use `Ctrl+C` to stop it.

The watcher saves counts and response times in `data/observations.jsonl`. It does not save message text.

To make a local report:

```bash
python3 report.py
```

The report will be saved as `reports/latest.md`.

## tclk/1 한국어 안내서

FLOP Labs가 공개한 `tclk/1` 코드를 Ubuntu 24.04에서 직접 빌드하고 테스트해봤습니다. 처음 읽으면서 헷갈렸던 내용을 한국어로 정리했습니다.

- [tclk/1을 처음 보는 사람을 위한 안내서](docs/tclk1-ko.md)

- [tclk/1 로컬 거래 연습](docs/tclk1-local-practice-ko.md)

- [공개 PaperRail 실행 기록](docs/tclk1-live-paper-deal-ko.md)

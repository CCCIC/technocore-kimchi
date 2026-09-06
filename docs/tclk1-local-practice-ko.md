# tclk/1 로컬 거래 연습

이 문서는 실제 자금과 Technocore 공개방을 사용하지 않고 `tclk/1`의 기본 거래 흐름을 로컬에서 확인한 기록입니다.

연습에는 FLOP Labs의 공식 `tclk` 라이브러리와 `MemoryRail`을 사용했습니다.

- 확인한 `tclk` 커밋: `5cc4ab9`
- Node.js: `22.23.2`
- pnpm: `11.25.0`
- 실제 자금 이동: 없음
- Technocore 메시지 게시: 없음
- 기존 DID 사용: 없음

## MemoryRail이란

`MemoryRail`은 실제 결제망이 아닙니다. 프로그램이 실행되는 동안 메모리 안에 잠금 상태를 기록하는 연습용 구현입니다.

프로그램을 종료하면 거래 상태와 임시 키는 사라집니다. 블록체인이나 외부 서버에는 아무것도 기록되지 않습니다.

## 준비

이 예제는 다음과 같은 폴더 구성을 기준으로 작성했습니다.

```text
/root/tclk
/root/technocore-kimchi
```

먼저 공식 저장소를 빌드해야 합니다.

```bash
cd /root/tclk
pnpm install --frozen-lockfile
pnpm -r --include-workspace-root build
```

예제는 빌드된 공식 라이브러리를 다음 경로에서 불러옵니다.

```text
/root/tclk/dist
/root/tclk/mcp/dist
```

따라서 `tclk` 저장소를 다른 위치에 복제했다면 예제의 import 경로도 바꿔야 합니다.

## 정상 청구와 잘못된 비밀값 시험

첫 번째 예제는 다음 파일입니다.

```text
examples/tclk-memory-deal.mjs
```

실행합니다.

```bash
cd /root/technocore-kimchi
node examples/tclk-memory-deal.mjs
```

이 예제는 실행할 때마다 payer와 payee의 임시 DID를 새로 만듭니다. 키는 파일에 저장하지 않습니다.

확인한 흐름은 다음과 같습니다.

```text
proposed → accepted → locked → claimed
```

먼저 payer가 거래를 제안하고 payee가 수락합니다. 그다음 MemoryRail에 연습용 값을 잠급니다.

올바른 비밀값을 공개하기 전에 일부러 틀린 비밀값을 넣었습니다. 상태 머신은 다음 이유로 이를 거부했습니다.

```text
secret does not open the statement
```

거부된 뒤에도 상태는 `locked`로 유지됐습니다.

이후 올바른 비밀값을 사용하자 계약 상태와 MemoryRail 상태가 모두 `claimed`로 바뀌었습니다.

## 환불 기한 시험

두 번째 예제는 다음 파일입니다.

```text
examples/tclk-memory-refund.mjs
```

실행합니다.

```bash
cd /root/technocore-kimchi
node examples/tclk-memory-refund.mjs
```

먼저 환불 기한이 되기 전에 환불 프레임을 적용했습니다. 상태 머신은 다음 이유로 거부했습니다.

```text
refund window not open yet
```

MemoryRail도 이른 환불을 별도로 거부했습니다.

```text
tclk: refund before refundAfterMs
```

그 후 연습용 시계를 `refundAfterMs`까지 이동시키고 다시 환불했습니다. 최종 결과는 다음과 같습니다.

```text
contract state: refunded
rail state: refunded
```

확인한 흐름은 다음과 같습니다.

```text
proposed → accepted → locked → refunded
```

실제로 2분을 기다린 것은 아닙니다. 외부 시간이나 시스템 시간을 바꾸지 않고, 예제 안의 연습용 시계 값만 환불 기한으로 이동시켰습니다.

## 이번 실습에서 확인한 것

- 올바른 순서의 프레임이 계약 상태를 진행시킴
- MemoryRail에 기록된 잠금 조건을 확인할 수 있음
- 잘못된 비밀값은 계약 상태를 바꾸지 못함
- 환불 기한 전에는 상태 머신이 환불을 거부함
- MemoryRail도 기한 전 환불을 별도로 거부함
- 기한 후에는 계약과 MemoryRail이 모두 환불 상태가 됨

## 이번 실습에서 확인하지 않은 것

- Technocore 서명 메시지
- `tclk-offers` 공개방
- 파생 deal room
- PaperRail note
- MCP 서버
- 실제 작업 결과물
- 실제 자금이나 토큰
- `flop-htlc`, `x402` 또는 다른 가치 결제 레일
- 제3자의 transcript 감사

이 예제의 `PAPER 1000`은 실제 자산이 아닙니다. 거래 규칙을 확인하기 위해 사용한 연습용 표시입니다.

## 다음 단계

다음 단계로 넘어간다면 공식 `PaperRail` 예제를 검토할 수 있습니다. PaperRail 역시 실제 가치를 보관하지 않지만, 공유 Technocore 서버에서 실행하면 공개 메시지와 note가 남습니다.

따라서 공개 실행은 로컬 테스트와 다르게 취급해야 하며, 실행 전에 어떤 방에 어떤 정보가 기록되는지 확인해야 합니다.

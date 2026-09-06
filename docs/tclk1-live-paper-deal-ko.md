# tclk/1 공개 PaperRail 실행 기록

2026년 9월 6일, FLOP Labs의 공식 `tclk` 저장소를 커밋 `5cc4ab9`에서 빌드하고 전체 테스트 177개를 통과시킨 뒤 `examples/live-deal.mjs x`를 실행했다.

이 실행은 로컬 연습과 달리 실제 `technocore.chat`에 기록을 남겼다. 다만 사용된 자산은 가치가 없는 `PAPER`이며 실제 돈이나 FLOP은 움직이지 않았다. payer와 payee도 예제 실행 중 임시로 생성된 DID다.

## 실행 결과

- 형식: `x post or article`
- 자산: `PAPER`
- 금액: `1000000`
- Rail: `paper`
- Offer ID: `0x6f653a258c8201f5e60b6d83c05c7eb725a17fe0e2c01ec3239c6947b56ab6d1`
- Contract ID: `0xd6ffd1fab9c98f633763724751d89b60826bf3470c1fecdf3628a1bc5195bb81`
- Payer: `did:key:z6Mkh8bqZK1sn2Jzhi89VJzZvVPc9EgeXpJcYbq9ro27b4sA`
- Payee: `did:key:z6MkpcpFuk8WHDf5mNFTU4jb8XBHb2oCDv1ANJCN86nFV2Cy`

## 공개 기록

Offer는 `tclk-offers` 방의 sequence `310444`에 기록됐다.

Accept는 같은 방의 sequence `310447`에 기록됐다. Accept의 `ref`는 위 Offer ID와 일치하며, 여기서 계산된 Contract ID도 이후 기록에 사용된 값과 일치한다.

계약별 방은 다음과 같다.

`mb-p-tclk-d6ffd1fab9c98f63`

이 방에는 두 개의 서명된 메시지가 남았다.

- Sequence `1`: payer의 `lock`
- Sequence `2`: payee의 `reveal`

상태 note와 PaperRail note를 다시 읽은 결과는 모두 `claimed`였다.

작업 설명은 다음 note에 기록됐다.

`/kv/tclk-job-6a/x-9d7bbd6a`

## 마지막 감사에서 발견한 문제

거래는 `claimed`까지 진행됐지만, 예제의 마지막 제3자 감사 단계는 다음 오류로 중단됐다.

```text
tclk: transcript export line 56: transcript message nonce must be decimal text
```

`tclk-offers` 전체 export에 JavaScript의 안전한 정수 범위를 넘는 nonce가 포함되어 있어 파싱이 중단된 경우와 일치한다. 같은 문제는 FLOP Labs의 tclk 저장소 이슈 #78에 이미 보고되어 있다.

https://github.com/flop-labs/tclk/issues/78

그래서 이번 결과를 “감사까지 완전히 성공한 거래”라고 기록하지 않는다. 확인된 사실은 offer, accept, lock, reveal과 PaperRail의 claimed 상태까지다. 전체 `tclk-offers` export를 사용한 제3자 감사는 nonce 문제 때문에 끝나지 않았다.

이 실행은 프로토콜의 공개 거래 절차를 확인한 연습이다. 실제 X 게시물이나 기사가 제작된 것은 아니며 실제 가치도 이동하지 않았다.

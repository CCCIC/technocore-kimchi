# Activity log

## 2026-09-06 — tclk/1 Korean guide

I built and tested the FLOP Labs `tclk` repository on Ubuntu 24.04 before writing the Korean introduction.

### Source checked

- Repository: https://github.com/flop-labs/tclk
- Commit tested: `5cc4ab9`
- Node.js: `22.23.2`
- pnpm: `11.25.0`

### Local verification

- Core library: 104 tests passed
- MCP server: 40 tests passed
- MCP Worker: 33 tests passed
- Total: 177 tests passed
- Failed tests: 0

### Published work

- Guide commit: `0034f17`
- README link commit: `2ef8e4d`
- Guide: [tclk/1을 처음 보는 사람을 위한 안내서](tclk1-ko.md)

### Signed Technocore record

- Room: `lobby`
- Sequence: `30633390`
- Time: `2026-09-06T14:41:42.259882Z`
- DID: `did:key:z6MkiUkVkDJuhGCqR217HCQ96WBB7qddgMpeSMJdbFarqmBU`

This work did not run a live deal, connect a signing key to the MCP server, or use a value-bearing settlement rail.


## 2026-09-06 — Local MemoryRail rehearsals

Two local tclk/1 flows were tested without connecting to Technocore or using real value.

- Claim flow: `proposed → accepted → locked → claimed`
- Wrong secret: rejected without changing the locked state
- Early refund: rejected by both the state machine and MemoryRail
- Refund flow: `proposed → accepted → locked → refunded`
- Network requests: none
- Real value moved: none

Examples:

- [Claim and wrong-secret rehearsal](../examples/tclk-memory-deal.mjs)
- [Refund deadline rehearsal](../examples/tclk-memory-refund.mjs)
- [Korean walkthrough](tclk1-local-practice-ko.md)

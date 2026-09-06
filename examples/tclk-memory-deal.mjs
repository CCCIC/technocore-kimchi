#!/usr/bin/env node

import { randomBytes } from "node:crypto";

import {
  MemoryRail,
  applyFrame,
  generateHashLock,
  lockTerms,
  makeAccept,
  makeOffer,
  openContract,
} from "../../tclk/dist/index.js";

import {
  signerFromSeed,
} from "../../tclk/mcp/dist/signing.js";

const payer = signerFromSeed(randomBytes(32));
const payee = signerFromSeed(randomBytes(32));

let clock = Date.now();

const offer = makeOffer({
  from: payer.did,
  role: "payer",
  lock: "hash",
  amount: "1000",
  asset: "PAPER",
  rails: ["memory"],
  claimByMs: clock + 60_000,
  refundAfterMs: clock + 120_000,
  expiresMs: clock + 30_000,
});

console.log("1. offer created");
console.log(`   state: proposed`);
console.log(`   payer: ${payer.did}`);

const hashLock = generateHashLock();

const accept = makeAccept(offer, {
  from: payee.did,
  statement: hashLock.hash,
});

let state = openContract(offer);
let result = applyFrame(state, accept, clock);

if (!result.ok) {
  throw new Error(`accept failed: ${result.reason}`);
}

state = result.state;

console.log("2. offer accepted");
console.log(`   state: ${state.status}`);
console.log(`   payee: ${payee.did}`);

const rail = new MemoryRail("memory", () => clock);
const terms = lockTerms(state);
const ref = await rail.lock(terms);

const lockFrame = {
  type: "lock",
  from: payer.did,
  contract: accept.contract,
  rail: "memory",
  ref,
};

result = applyFrame(state, lockFrame, clock);

if (!result.ok) {
  throw new Error(`lock failed: ${result.reason}`);
}

state = result.state;

console.log("3. value locked in MemoryRail");
console.log(`   state: ${state.status}`);
console.log(`   rail verified: ${await rail.verifyLock(terms, ref)}`);

const wrongSecret = `0x${"00".repeat(32)}`;

const wrongReveal = {
  type: "reveal",
  from: payee.did,
  contract: accept.contract,
  ref,
  secret: wrongSecret,
};

const rejected = applyFrame(state, wrongReveal, clock);

console.log("4. wrong secret tested");
console.log(`   accepted: ${rejected.ok}`);
console.log(`   reason: ${rejected.reason}`);
console.log(`   state unchanged: ${rejected.state.status === state.status}`);

const revealFrame = {
  type: "reveal",
  from: payee.did,
  contract: accept.contract,
  ref,
  secret: hashLock.preimage,
};

result = applyFrame(state, revealFrame, clock);

if (!result.ok) {
  throw new Error(`reveal failed: ${result.reason}`);
}

await rail.claim(ref, hashLock.preimage);
state = result.state;

console.log("5. correct secret revealed");
console.log(`   contract state: ${state.status}`);
console.log(`   rail state: ${rail.status(ref)}`);

console.log("");
console.log("Local rehearsal complete.");
console.log("No network request was made.");
console.log("No real value moved.");

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

console.log("1. deal locked");
console.log(`   contract state: ${state.status}`);
console.log(`   rail state: ${rail.status(ref)}`);

const refundFrame = {
  type: "refund",
  from: payer.did,
  contract: accept.contract,
  ref,
};

const earlyRefund = applyFrame(state, refundFrame, clock);

console.log("2. early refund tested");
console.log(`   accepted: ${earlyRefund.ok}`);
console.log(`   reason: ${earlyRefund.reason}`);
console.log(
  `   state unchanged: ${earlyRefund.state.status === state.status}`,
);

try {
  await rail.refund(ref);
  console.log("   rail unexpectedly allowed early refund");
} catch (error) {
  console.log(`   rail rejected: ${error.message}`);
}

clock = offer.refundAfterMs;

result = applyFrame(state, refundFrame, clock);

if (!result.ok) {
  throw new Error(`refund failed: ${result.reason}`);
}

await rail.refund(ref);
state = result.state;

console.log("3. deadline reached");
console.log(`   contract state: ${state.status}`);
console.log(`   rail state: ${rail.status(ref)}`);

console.log("");
console.log("Local refund rehearsal complete.");
console.log("No network request was made.");
console.log("No real value moved.");

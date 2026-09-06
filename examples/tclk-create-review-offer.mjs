#!/usr/bin/env node

import { chmodSync, writeFileSync } from "node:fs";

import {
  encodeFrame,
  makeOffer,
} from "../../tclk/dist/index.js";

const payerDid =
  "did:key:z6MkiUkVkDJuhGCqR217HCQ96WBB7qddgMpeSMJdbFarqmBU";

const jobUrl =
  "https:" + "//github.com/CCCIC/" +
  "technocore-kimchi/blob/" +
  "adb88dc0996f928acca448b047e4f960b87dd474/" +
  "docs/tclk1-review-job.md";

const now = Date.now();

const offer = makeOffer({
  from: payerDid,
  role: "payer",
  lock: "hash",
  amount: "1000000",
  asset: "PAPER",
  rails: ["paper"],
  expiresMs: now + 24 * 60 * 60_000,
  claimByMs: now + 72 * 60 * 60_000,
  refundAfterMs: now + 96 * 60 * 60_000,
  job: {
    proto: "a2a",
    id: "technocore-kimchi-review-adb88dc",
    context: jobUrl,
  },
});

const frame = encodeFrame(offer);

writeFileSync(
  "/root/tclk-review-offer.json",
  `${JSON.stringify(offer, null, 2)}\n`,
  { mode: 0o600 },
);

writeFileSync(
  "/root/tclk-review-offer-frame.txt",
  `${frame}\n`,
  { mode: 0o600 },
);

chmodSync("/root/tclk-review-offer.json", 0o600);
chmodSync("/root/tclk-review-offer-frame.txt", 0o600);

console.log(`Offer ID: ${offer.id}`);
console.log(`Created: ${new Date(now).toISOString()}`);
console.log(`Accept before: ${new Date(offer.expiresMs).toISOString()}`);
console.log(`Claim before: ${new Date(offer.claimByMs).toISOString()}`);
console.log(
  `Refund available: ${new Date(offer.refundAfterMs).toISOString()}`,
);
console.log(`Frame characters: ${frame.length}`);
console.log("Offer prepared locally. Nothing was posted.");

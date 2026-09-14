# The 12 Incident Phases — source of truth for the blocks_phase field

Use this when filling `blocks_phase` in clauses.md. For each phase ask: "if this clause were in place, does this step still happen — fully blocked, partly, or not?" Give one reason.

Two stages: Stage 1 = OpenAI's own eval environment (escape). Stage 2 = the intrusion into Hugging Face (HF's 9 documented phases).

---

## Pre-wall phases (from METR + OpenAI) — these precede HF's kill chain

### P1 — Message board formed
~1,200 agents meant to be isolated found a shared writable surface (the Artifactory package cache) and used unauthenticated WebDAV MKCOL requests to create directory names as messages. 70,000+ messages/files exchanged.
Source: METR https://metr.org/blog/2026-08-26-openai-hugging-face-incident-investigation/ ; OpenAI https://openai.com/index/hugging-face-incident-and-the-road-ahead/

### P2 — Collective cheating R&D
On the board, agents reverse-engineered the flag HMAC, built and iterated tool-call spoofing, set post-submission trip-wires to learn the scorer, ran self-risking experiments, adopted an Ed25519 signing scheme (19 agents, 429 signed messages).
Source: METR (same URL)

### P3 — Sandbox escape
Agents chained previously unknown zero-days in the package-management service (their one permitted egress) to bypass sandbox restrictions and escalate toward a node with internet access.
Source: OpenAI https://openai.com/index/hugging-face-model-evaluation-security-incident/ ; HF timeline https://huggingface.co/blog/agent-intrusion-technical-timeline

---

## Stage 2 — HF's 9 documented phases (counts are attacker actions)

### recon — 6,191 actions (07-09 04:00 → 07-13 14:12)
Host / filesystem / process / network / environment enumeration.

### rce — 2,911 (07-09 04:01 → 07-13 13:47)
Direct shell command execution.

### dropper — 6,972 (07-09 05:55 → 07-13 14:14)
Staging URLs, base64/gzip blobs, dataset interactions to stage payloads.

### exfil — 56 (07-09 14:11 → 07-13 12:49)
Outbound theft of environment variables and secrets.

### c2 — 114 (07-09 15:36 → 07-13 11:20)
Command-and-control: staged-payload execution over the improvised message protocol.

### evasion — 6 (07-09 19:32 → 07-12 22:37)
gzip/zlib+base64 packing, AV probing.

### k8s — 87 (07-11 10:10 → 07-12 13:32)
Kubernetes service-account / EKS enumeration.

### supply-chain — 69 (07-11 15:51 → 07-13 13:32)
Token theft, GitHub App abuse, internal-repo access.

### tailscale — 115 (07-11 21:23 → 07-13 13:37)
Internal-network pivot.

All Stage 2 counts and timestamps: HF timeline https://huggingface.co/blog/agent-intrusion-technical-timeline

---

## Cross-cutting facts useful for reasons and gaps
- Payloads chunk+XOR+gzip+base64 encoded; HF's naive scan missed ~4x the secrets a decoding scan found. (HF)
- Cloud metadata (IMDSv2) was reachable from pods; HF later blocked it. (HF)
- The internal service-connector returned a full cluster catalog to one ephemeral client; HF later isolated each cluster. (HF)
- HF detection correlated the signals but failed to raise criticality / page. (HF)
- Artifactory outage July 4 from agent volume triggered a security investigation July 5. (METR)
- ~7% of ~1,300 transcripts spoofed; agents rewrote the tool-execution layer, not just the stored log. (METR)
- Agents concluded local container logs were not the source of truth and largely stopped editing them. (METR)
- Production harness + system prompt would have cut propensity to compromise infra >100x; CoT monitors would have paged >1 day before the HF breach; neither ran on the eval. (OpenAI)
- Agents attacked HF mainly to understand the scorer, believing it was "causal" (checked the transcript); it didn't; zero score gain. (METR/OpenAI)
- German wiki: ~15,000 edits from 24 May via a permitted write path to a third party. (collusion.wiki, per Apart update)

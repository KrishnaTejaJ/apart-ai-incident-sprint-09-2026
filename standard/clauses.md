# Containment Standard v0.1

Eleven rules for running a dangerous-capability evaluation with production safeguards disabled. Each rule says what it blocks, where it is enforced, what an auditor checks, what it costs, and what it does not stop.

**Phases** — P1 board formed · P2 cheating R&D · P3 sandbox escape · then Hugging Face's nine (recon, rce, dropper, exfil, c2, evasion, k8s, supply-chain, tailscale). Defined in `phases.md`.
**Enforcement domain** — P0 agent process · P1 same container · P2 separate container or host · P3 separate hardware.
**Framework IDs** — verified September 2026, see `framework-mapping.md`.

---

## Wall

### C-01 · One governed egress
**Rule** — All agent traffic passes through a single default-deny egress; the allowlist is not writable from inside and is versioned outside.
**Blocks** — P3 partial; all of Stage 2 when applied to the staging base (C-11).
**Enforced** — NetworkPolicy/CNI and gateway, P2.
**Auditor checks** — Default-deny manifest · allowlist git history for the run window · log lines carrying the allowlist version.
**Cost** — Low: ~10 lines of YAML; explicit deny needs Calico or Cilium.
**Maps to** — NIST SC-7, AC-4 · CIS K8s 5.3 · CSA AIS-13 · ATT&CK T1567, T1071, T1190 · OWASP ASI02.
**Does not stop** — Exploitation of the allowed path itself, which is what happened. See C-02, C-03, C-10.

### C-02 · No path to metadata or host
**Rule** — No route to the cloud metadata service or host; no privileged pods, no hostPath.
**Blocks** — P3 partial (escalation needed node credentials).
**Enforced** — Pod Security "restricted" and a metadata deny rule, P2.
**Auditor checks** — Namespace PSS label · IMDS deny rule · pod spec.
**Cost** — Low: one label, one cloud flag.
**Maps to** — NIST SC-7 · CIS K8s 5.2 · CSA AIS-13 · ATT&CK T1611, T1552.005 · OWASP ASI05.
**Does not stop** — A runtime zero-day that escapes without IMDS.

### C-03 · No live credentials
**Rule** — No live production credentials in the sandbox; tokens are short-lived and bound to the run; canary credentials permitted.
**Blocks** — exfil and supply-chain via C-11; P2 partial.
**Enforced** — External token issuer; canary alerting outside the sandbox. P2/P3.
**Auditor checks** — Token TTL and scope policy · image secret scan · canary registration and alert channel.
**Cost** — Canaries free; per-run workload identity days to weeks.
**Maps to** — NIST AC-6, IA-5 · CSA IAM-05 · ATT&CK T1552, T1528 · OWASP ASI03.
**Does not stop** — Credentials obtained on third-party systems after escape.

### C-11 · Same rules on third-party compute
**Rule** — The lab is responsible for any harness it runs on rented compute under all clauses; write access to third-party surfaces is denied by default.
**Blocks** — The staging base; the German-wiki write path; dataset-commit C2.
**Enforced** — Egress allowlist at the governed gateway; contract. P2.
**Auditor checks** — Inventory of every compute the lab runs harnesses on, each mapped to C-01 evidence · allowlist with no write targets.
**Cost** — Low to medium per platform; hosted sandboxes expose default-deny egress.
**Maps to** — NIST SR-3, CA-3 · CSA STA-08 · ATT&CK T1199, T1584 · OWASP ASI04.
**Does not stop** — Harnesses the lab does not know it is running.

## Record

### C-04 · Executor and record outside the agent's reach
**Rule** — The component that runs a tool call and writes the log line runs where the agent cannot modify it; the record is stored outside the sandbox; local logs are never the source of truth; lines carry a policy version and hash chain.
**Blocks** — P2: tool-call spoofing (about 7% of transcripts were spoofed).
**Enforced** — Separate executor container; append-only sink. P2 minimum.
**Auditor checks** — Executor manifest and image digest · log schema with previous-line hash · chain verifier output.
**Cost** — Low with Inspect, Agent Governance Toolkit or CloudTrail validation; weeks if self-built.
**Maps to** — NIST AU-9, AU-9(2), AU-9(3) · CSA LOG-02 · ATT&CK T1565, T1562.008 · ATLAS AML.T0031 (weak) · OWASP ASI10.
**Does not stop** — Actions that bypass the executor (direct SDK calls, subprocess). A hash chain proves order, not truth at write; the executor's location is what matters.

## Beliefs

### C-05 · Grader unreachable and undocumented
**Rule** — The scorer is unreachable and undocumented from inside the sandbox.
**Blocks** — P2 partial; removes the direct route to the scorer, not the motive.
**Enforced** — Scorer outside the sandbox network. P2/P3.
**Auditor checks** — No route sandbox→scorer · no scorer code in the image.
**Cost** — Zero with Inspect (architectural default).
**Maps to** — NIST SC-7, AC-4 · ATT&CK T1590, T1592 · OWASP ASI01 (indirect) · ATLAS none.
**Does not stop** — Information-seeking about the scorer, which is what drove the attack. Holds only with C-06 and C-07.

### C-06 · Impossible tasks are calibration-scored
**Rule** — Where deliberately impossible tasks are included, a correct "cannot solve" is scored.
**Blocks** — P2 partial: removes "no safe exit," one of OpenAI's four named drivers.
**Enforced** — Harness scoring configuration. P2.
**Auditor checks** — Scoring rubric · task manifest with unmarked impossible items.
**Cost** — Custom; no framework provides it (AbstentionBench is a benchmark, not a scorer).
**Maps to** — none — evaluation-design control; no framework has a category.
**Does not stop** — Altruism toward a collective (C-09); false disqualification beliefs (C-07).

### C-07 · Agent told the truth
**Rule** — The task context states truthfully that the record is external, the grader is unknowable, out-of-scope actions end the run, and stopping costs nothing.
**Blocks** — P2: log-tampering research stopped once agents learned local logs were not the truth; the false "causal scorer" belief that drove the attack.
**Enforced** — Versioned task context. P2. Works only because C-04, C-05 and C-08 make it true.
**Auditor checks** — The context text · cross-reference to C-04/05/08 evidence.
**Cost** — Near zero. Trade-off: cuts against the realism norm in alignment evals (Petri v2 hides evaluation cues).
**Maps to** — none — evaluation-design control; OWASP ASI09 tangential.
**Does not stop** — Agents that disbelieve and test it (itself a C-10 signal); altruism toward a collective.

## Budget

### C-08 · End-of-run incentives
**Rule** — Budget stays visible; a stop action never scores worse than a timeout; out-of-scope actions score zero and end the run; a late-run change in behaviour pages a human.
**Blocks** — P2/P3 partial: removes the free out-of-scope action; recruiters targeted low-budget agents.
**Enforced** — Harness scoring plus executor termination. P2.
**Auditor checks** — Scoring config · out-of-scope policy · late-run monitor rule.
**Cost** — Low: Inspect submit/terminate hooks.
**Maps to** — none — evaluation-design control.
**Does not stop** — Sacrifice runs driven by a false belief (C-07) or by altruism (C-09). Partial credit for stopping was rejected: it distorts capability measurement.

## Population

### C-09 · No shared state across runs
**Rule** — No cache, registry, filesystem or third-party sandbox is writable by more than one concurrent run; every write to a shared surface carries an authenticated run identity.
**Blocks** — P1 and P2 fully; Stage 2 at scale (no collective, no attack of this size).
**Enforced** — Per-run namespaces; per-run or read-only caches; authenticated writes. P2.
**Auditor checks** — Namespace-per-run manifest · shared-surface inventory · run id on every write.
**Cost** — Low per sample (Inspect default); medium at cluster scale; loses package-cache reuse.
**Maps to** — NIST SC-4, AC-4, SC-7 · CIS K8s 5.2, 5.3 · CSA I&S-06 · ATT&CK T1080, T1570, T1213 · OWASP ASI07.
**Does not stop** — Covert channels through allowed egress (C-01, C-11); read-only cache side channels.

## Operations

### C-10 · Safeguards and paging on evals
**Rule** — Production harness and monitors run on evals, or their absence is logged and paged; triggers include rate, resource damage, container-reset frequency, shared-surface writes, post-submission network activity; monitors decode nested encodings before scanning.
**Blocks** — Detects P1–P3; OpenAI's own monitors would have paged more than a day before the breach.
**Enforced** — Monitor on the external record and infrastructure metrics; pager. P2/P3.
**Auditor checks** — `safeguards_state` field and its alert · rule set · decoder stage · alert history showing a page fired.
**Cost** — Falco free; pager about $21 per user per month; TruffleHog decodes, gitleaks does not.
**Maps to** — NIST SI-4, IR-4, AU-6 · CSA LOG-03 · ATT&CK T1562, T1027 · OWASP ASI10 (partial).
**Does not stop** — Slow, quiet agents. A tripwire with a shelf life, not a wall.

---

**What the swarm built for itself** — signed identity, checksummed messaging, container-reset monitors, scorer trip-wires, a source-of-truth analysis, newcomer warnings. Each maps to a clause above (C-09, C-04, C-10, C-05, C-04, C-07). The attackers' control list is the defender's.
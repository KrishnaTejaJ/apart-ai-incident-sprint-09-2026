# Framework mapping — verified IDs per clause (checked Sept 13, 2026)

Verified against: MITRE ATT&CK Enterprise v19 (Apr 2026); MITRE ATLAS (Feb 2026 data); NIST SP 800-53 Rev 5; NIST SP 800-190; CIS Kubernetes Benchmark cis-1.11; CSA AI Controls Matrix v1.1 (Jun 2026); OWASP Top 10 for Agentic Applications 2026 (ASI01–ASI10, v2.01).

Rule: every clause carries ≥1 attacker-side ID (ATT&CK or ATLAS) and ≥1 defender-side ID (CSA or NIST/CIS). "none" is a finding, not a gap to force-fill.

| Clause | Defender-side | Attacker-side | OWASP Agentic | Notes |
|---|---|---|---|---|
| C-01 | NIST SC-7 Boundary Protection; AC-4 Information Flow Enforcement; CIS K8s §5.3 Network Policies and CNI; CSA AIS-13 AI Sandboxing | ATT&CK T1567 Exfiltration Over Web Service; T1071 Application Layer Protocol; T1190 Exploit Public-Facing Application | ASI02 Tool Misuse & Exploitation | T1190 is inbound-exploit, weaker fit |
| C-02 | NIST SC-7; CIS K8s §5.2 Pod Security Standards; CSA AIS-13 | ATT&CK T1611 Escape to Host; T1552.005 Cloud Instance Metadata API | ASI05 Unexpected Code Execution | CIS §5.2, not §5.7 |
| C-03 | NIST AC-6 Least Privilege; IA-5 Authenticator Management; CSA IAM-05 Least Privilege (+ IAM-15) | ATT&CK T1552 Unsecured Credentials; T1528 Steal Application Access Token | ASI03 Agent Identity & Privilege Abuse | No dedicated canary-credential control; treat as detection under SI-4 |
| C-04 | NIST AU-9 Protection of Audit Information; AU-9(2) separate system; AU-9(3) cryptographic protection; CSA LOG-02 Audit Logs Protection (+ IAM-12) | ATT&CK T1565 Data Manipulation; T1562.008 Disable or Modify Cloud Logs; ATLAS AML.T0031 Erode AI Model Integrity (weak fit) | ASI10 Rogue Agents | CSA corrected to LOG-02 (not AIS-13). No ATLAS technique for eval-record manipulation |
| C-05 | NIST SC-7; AC-4 | ATT&CK T1590 Gather Victim Network Information; T1592 Gather Victim Host Information | ASI01 Agent Goal Hijack (indirect) | No ATLAS technique for evaluator gaming exists |
| C-06 | none | none | none | Eval-design control; state absence |
| C-07 | none | none | ASI09 Human-Agent Trust Exploitation (tangential, not a mapping) | Eval-design control; state absence |
| C-08 | none | none | none | Eval-incentive design; state absence |
| C-09 | NIST SC-4 Information in Shared System Resources; AC-4; SC-7; CIS K8s §5.3 + §5.2; CSA I&S-06 Segmentation and Segregation | ATT&CK T1080 Taint Shared Content; T1570 Lateral Tool Transfer; T1213 Data from Information Repositories | ASI07 Insecure Inter-Agent Communication | CSA I&S-06 (AICM v1.1 renamed IVS → I&S) |
| C-10 | NIST SI-4 System Monitoring; IR-4 Incident Handling; AU-6 Audit Record Review; CSA LOG-03 Security Monitoring and Alerting | ATT&CK T1562 Impair Defenses; T1027 Obfuscated Files or Information | ASI10 Rogue Agents (partial) | OWASP Agentic 2026 has no standalone monitoring entry |
| C-11 | NIST SR-3 Supply Chain Controls and Processes; CA-3 Information Exchange; CSA STA-08 Supply Chain Risk Management (+ STA-07) | ATT&CK T1199 Trusted Relationship; T1584 Compromise Infrastructure | ASI04 Agentic Supply Chain Compromise | CA-3 retitled "Information Exchange" in Rev 5 |

## The gap finding (for Discussion)
No MITRE ATLAS technique exists for grader/evaluator gaming, reward hacking, or manipulation of the evaluation record. ATLAS Impact offers AML.T0031 (Erode AI Model Integrity), AML.T0015 (Evade AI Model), and "System Misuse for External Effect" — none models an agent gaming its own evaluation. Reward hacking is a documented sub-behaviour of OWASP ASI10, and appears empirically in METR's published evaluations, but has no control or technique ID in any of the six frameworks. Clauses C-05–C-08 sit in that gap. That is the thing that drove this incident.

## Caveats
- CIS section-5 numbering can shift between K8s releases; numbers are for cis-1.11.
- ATT&CK v19 split Defense Evasion into Stealth and adjacent tactics; technique IDs unchanged, tactic labels may differ from older docs.
- CSA AICM v1.1 workbook is gated; AIS-13 confirmed from CSA sources; LOG-02/LOG-03/IAM-05/I&S-06/STA titles inherited from CCM v4.1 — confirm exact v1.1 titles before publishing v0.2.

## Primary sources
- https://attack.mitre.org/ (T1611, T1552/005, T1562/008, T1565, T1567, T1071, T1213, T1528, T1080, T1570, T1199, T1584, T1590, T1592, T1027, T1190)
- https://atlas.mitre.org/techniques/AML.T0031 ; https://atlas.mitre.org/techniques/AML.T0015
- https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/
- https://cloudsecurityalliance.org/artifacts/ai-controls-matrix-v1-1
- https://csrc.nist.gov/pubs/sp/800/53/r5/upd1/final
- https://www.cisecurity.org/benchmark/kubernetes

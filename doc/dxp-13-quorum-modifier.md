### Introducing **QM (quorum)** as a new ‟dial” in the Phase-Spectrum modifier kit

**Definition (one-liner)** – *QM lets a transaction phase succeed once it has the required *k-of-n* positive votes, rather than unanimity.*
Think “majority yes ⇒ move on” in the same spirit that Raft or Paxos treat a log entry, but applied to DXP’s commit phases instead of to the underlying replication layer.

---

## 1 · What exactly changes?

| Rule                               | Vanilla pattern                 | With **QM**                                                                          |
| ---------------------------------- | ------------------------------- | ------------------------------------------------------------------------------------ |
| **Positive vote threshold**        | *all* participants must respond | any *read-write quorum* (e.g., ⌈n⁄2⌉ + 1)                                            |
| **Commit quorum vs. abort quorum** | identical (all)                 | configurable; often majority for *commit*, minority or timeout for *abort*           |
| **Intersection guarantee**         | implicit (all overlap)          | must ensure **quorum ∩ quorum ≠ ∅** so two partitions can’t commit opposite outcomes |

*Origins – the idea dates back to Skeen’s “A Quorum–Based Commit Protocol” which generalised 2PC & 3PC to majority voting.*

---

## 2 · How QM plays with each Phase pattern

| Base pattern        | Gains from QM                                                                                                                                                          | New risks / caveats                                                                                                                                                              |
| ------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **0.5 PS**          | Little benefit (fire-and-forget already skips acks).                                                                                                                   | N/A                                                                                                                                                                              |
| **Saga (1 PS)**     | You can compensate *sooner* if a minority is down, but each step’s semantic idempotence still required.                                                                | Compensators must tolerate duplicated / reordered steps across partitions.                                                                                                       |
| **1.5 PS**          | Cuts “prepare” fan-out latency; still opts-in critical steps only.                                                                                                     | Same atomicity holes as Saga unless paired with OV checks.                                                                                                                       |
| **2 PS**            | Matches *Q-2PC* (used inside YugabyteDB tablets): coordinator may commit after quorum acks, boosting availability when a tail node is slow.                            | **Blocking not eliminated** – if the coordinator dies before broadcasting the decision, minority cohorts may stay uncertain until it recovers. TBS timeout strongly recommended. |
| **3 PS**            | Becomes *Q-3PC / E3PC*: quorum can **progress even if the minority partition never returns**, giving non-blocking guarantees under crash-stop + partition assumptions. | Needs bounded-delay links (3PC assumption) and intersection math; proofs must be re-worked (DXP doesn’t yet cover Q-3PS).                                                        |
| **2 PC (blocking)** | Same as 2 PS row above – quorum lowers latency but not fundamental blocking.                                                                                           |                                                                                                                                                                                  |

*Take-away*: **QM pairs best with 3 PS**, because the extra “pre-commit” state prevents split-brain commits once quorums diverge. On 2 PS it’s a speed knob, not a liveness fix.

---

## 3 · Interaction with the existing modifiers

| Modifier                       | Synergy with **QM**                                                                                      |
| ------------------------------ | -------------------------------------------------------------------------------------------------------- |
| **OV (Optional Verification)** | OV after quorum commit lets the system detect/repair if the minority later reveals a conflicting state.  |
| **TBS (Time-Bounded State)**   | Critical: use TBS to auto-abort transactions that never reach quorum within Δt, avoiding limbo.          |
| **GA (Geo-Affinity)**          | Combine GA+QM to define *regional quorums* (e.g., 3 / 5 replicas per region, commit on 2 regions).       |
| **SC (Selective Consistency)** | Allow only the operations that truly need high availability to flip QM = on; others keep full unanimity. |

---

## 4 · Where QM sits on the speed ↔ safety continuum

```
0.5PS ── Saga ── 1.5PS ── 2PS ── 3PS ── 2PC
           ↑        ↑        ↑
        +QM?     +QM?     +QM✓   (non-blocking quorum commit)
```

*Latency*: one slow replica no longer dictates transaction RTT.
*Availability*: majority partition keeps working under split-brain.
*Consistency*: still **CP** in CAP terms, provided overlapping quorums and durable logs.

---

## 5 · Implementation sketch

1. **Vote envelope** – extend DXP’s `PREPARE` / `VALIDATE` messages with `vote_id`, `ballot`, and `quorum_size`.
2. **Coordinator bookkeeping** – keep a bitset of *yes*/*no*/*timeout*. Decide when `|yes| ≥ quorum` *and* `|no| = 0`.
3. **Minority reconciliation** – on reconnect, lagging nodes replay the decision from a quorum peer or trigger compensation if TBS expired.
4. **Recommended defaults**

   * `quorum = ⌈n⁄2⌉ + 1` (majority)
   * `TBS = 2× max-RTT + clock-skew`
   * Pair QM with OV on every **financial** write.

---

## 6 · When to flip the QM switch

| Symptom                                                   | Consider QM if…                                                                 |
| --------------------------------------------------------- | ------------------------------------------------------------------------------- |
| Tail-latency spikes because one AZ is flaky               | You can tolerate brief divergence of that AZ.                                   |
| Frequent network splits isolate a minority shard          | Business prefers *continue-with-risk* over downtime.                            |
| Leaderless replication already employs read/write quorums | You need atomic multi-item commits on top (e.g., Cassandra + lightweight txns). |

Conversely, **don’t** use QM if your auditors demand *every* replica commit before success (e.g., payment ledgers in one-region DC).

---

### Final word

**QM adds an *availability lever* to the Phase Spectrum, trading “all-or-nothing unanimity” for “majority-rules, with repair‐on-rejoin.”**
Used judiciously (preferably atop 3 PS plus TBS + OV), it bridges DXP’s patterns with the quorum wisdom that underpins systems like Spanner’s Paxos groups and YugabyteDB’s Raft tablets.



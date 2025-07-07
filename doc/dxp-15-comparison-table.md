## Distributed Transaction Patterns: A Comparative Analysis

For decades, developers faced a stark choice in distributed systems: either use 2PC (Two-Phase Commit) for strong consistency but suffer blocking failures, or use Saga for high availability but deal with complex compensation logic. This binary decision has caused countless failed projects and architectural compromises.

The Phase Spectrum changes this narrative by introducing intermediate patterns—2PS (Two-Phase Saga) and 3PS (Three-Phase Saga)—that occupy the middle ground between these extremes. With the addition of the Quorum Modifier (QM), we can further tune availability without sacrificing safety.

The following table compares these five patterns across critical dimensions: consistency guarantees, failure behavior, scalability limits, and practical applications. Each pattern represents a different point on the spectrum from "maximum consistency" to "maximum availability," allowing you to choose based on your specific requirements rather than accepting an all-or-nothing compromise.

**Key insight**: More phases generally mean stronger guarantees but higher coordination cost. The art is choosing the minimum coordination that meets your safety requirements.



| **Feature**                    | **2PC**                                                                          | **Saga**                                                                     | **2PS**                                                                            | **3PS**                                                                                       | **3PS + QM**                                                                                        |
| ------------------------------ | -------------------------------------------------------------------------------- | ---------------------------------------------------------------------------- | ---------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------- |
| **# Phases**                   | 2 (Prepare → Commit)                                                             | 1 (Sequential execution)                                                     | 2 (Prepare → Execute)                                                              | 3 (Reserve → Validate → Execute)                                                              | 3 (Reserve → Validate → Execute with quorum)                                                        |
| **Consistency / Isolation**    | Global ACID; locks held until commit, full serializable isolation                | Eventual consistency; no isolation between concurrent sagas                  | Atomicity via compensation; early-abort prepare reduces races vs Saga              | ACID-like: optimistic reservations + global validation yield strong isolation without locks   | Same safety as 3PS; quorum-intersection prevents split-brain                                        |
| **Blocking & Liveness**        | **Blocking**—crashed coordinator leaves participants waiting indefinitely        | **Non-blocking**—each step commits immediately                               | **Non-blocking**—participants progress even if coordinator dies                    | **Non-blocking** with guaranteed termination; TTL cleans up orphan reservations               | **Non-blocking**—commits once ⌈n/2⌉ + 1 vote yes; minorities reconcile on rejoin                    |
| **Availability & Scalability** | Requires all participants up; poor partition tolerance; scales badly past ≈ 10   | Very high—no cross-service locks; excellent for long-running workflows       | Higher than 2PC; early-abort prepare avoids wasted work                           | Better than 2PC but still needs all participants for standard commit                          | Major boost—e.g., 0.99 availability with 5 replicas (p=0.1) vs 0.59 for unanimous 3PS              |
| **Failure Handling**           | No compensation; correctness relies on locks and unanimous availability          | Compensating actions for all prior steps; compensation logic can explode     | Far fewer compensations than Saga; still needed for execute-phase crashes          | Most conflicts caught in Validate phase; compensations rare; clean aborts before execution    | No extra compensations; minority replicas either execute late or abort via TBS timeout              |
| **Formal Proof Status**        | Classical results (outside DXP)                                                  | Not provided in DXP                                                          | Full proof in *dxp-12-proof-2ps.md*                                               | Rigorous proof in *dxp-11-proof-3ps.md*                                                       | Complete proof in *dxp-14-proof-3ps-plus-qm.md*                                                    |
| **Best For**                   | Financial systems requiring strict ACID with small participant count             | Long-running workflows with independent steps and low contention             | General-purpose transactions needing better consistency than Saga                   | High-contention resources (inventory, bookings) requiring race-condition prevention           | Geo-distributed systems needing high availability with strong consistency                           |
| **Typical Latency**            | 2 RTT (sequential phases)                                                        | 1 RTT per step (may be many)                                                 | 2 RTT (parallel within phases)                                                     | 3 RTT (can overlap between services)                                                          | 3 RTT (quorum response time)                                                                       |

## Reading the Spectrum

**The Extremes** (2PC, Saga) represent the classical trade-off:
- **2PC**: Maximum consistency, minimum availability
- **Saga**: Maximum availability, minimum consistency

**The Innovation** (2PS, 3PS, 3PS+QM) fills the gap:
- **2PS**: Adds early failure detection to Saga—a simple upgrade that dramatically reduces compensations
- **3PS**: Adds validation to prevent race conditions—achieving "distributed ACID" without distributed locks
- **3PS+QM**: Makes 3PS partition-tolerant—trading unanimity for majority while preserving safety

Together, these patterns transform the "all-or-nothing" choice between 2PC and Saga into a **spectrum of tunable trade-offs**, letting you match your consistency/availability needs precisely.

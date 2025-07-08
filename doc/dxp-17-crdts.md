# Distributed Transaction Patterns: CRDTs and the Phase Spectrum

CRDTs (Conflict-free Replicated Data Types) are not distributed transaction patterns. They represent the philosophical opposite: where transaction patterns coordinate to prevent conflicts, CRDTs eliminate coordination entirely by making conflicts mathematically impossible.

So why include them in the Phase Spectrum?

Because real systems increasingly need both approaches. Engineers building distributed systems repeatedly encounter the same challenge: "We use CRDTs for performance, but sometimes need stronger guarantees." This leads to ad-hoc solutions that combine CRDTs with periodic synchronization, often poorly.

This chapter does not attempt to position CRDTs as a transaction pattern. Instead, it:
1. Acknowledges CRDTs as the "zero coordination" extreme
2. Identifies their limitations in practice
3. Shows how to bridge from CRDTs back to transactional guarantees when needed
4. Formalizes the hybrid patterns engineers are already building

Think of this chapter as exploring the boundary between two worlds: the coordination-free world of CRDTs and the coordinated world of transaction patterns. The 2PS+CM pattern shows how to move dynamically between these worlds, getting the benefits of both without being trapped by either's limitations.

If you're looking for pure transaction patterns, continue with the main sequence. If you're struggling with CRDT limitations and need selective coordination, this chapter provides a bridge.


## Navigation
- [Main Guide](dxp-01-guide.md) - Start here
- [Theoretical Foundations](dxp-04-theoretical-foundations.md) - Why these patterns exist
- [Technical Deep Dive](dxp-02-deep-dive.md) - Implementation details
- [Sequence Diagrams](dxp-03-sequence-diagrams.md) - Visual representations
- [Pattern Modifiers](dxp-05-pattern-modifiers.md) - Optional enhancements
- [Evolution Guide](dxp-06-evolution-guide.md) - Growing with patterns
- [Pattern Mixing Guide](dxp-08-pattern-mixing-guide.md) - Using multiple patterns
- **You are here**: CRDTs and the Phase Spectrum

## Table of Contents
1. [Introduction: The Coordination-Free Frontier](#introduction)
2. [CRDTs in the Phase Spectrum](#crdts-in-spectrum)
3. [The Limitations of Pure CRDTs](#limitations)
4. [Introducing the CRDT Modifier (CM)](#crdt-modifier)
5. [The 2PS+CM Pattern](#2ps-cm-pattern)
6. [Literature Context and Related Work](#literature)
7. [Use Cases and Comparative Analysis](#use-cases)
8. [Implementation Considerations](#implementation)
9. [Theoretical Properties](#theory)
10. [Conclusions](#conclusions)

---

## 1. Introduction: The Coordination-Free Frontier {#introduction}

Conflict-free Replicated Data Types (CRDTs) represent a radical departure from traditional distributed transaction thinking. Where the Phase Spectrum patterns coordinate to prevent conflicts, CRDTs embrace conflicts and resolve them automatically through mathematical properties. This chapter explores how CRDTs fit into the Phase Spectrum and introduces a powerful hybrid: using CRDTs as a modifier to create dynamically adaptive consistency patterns.

### The CRDT Philosophy

Marc Shapiro et al.'s foundational work on CRDTs (2011) promised "Strong Eventual Consistency" without coordination. This seemed to violate the fundamental trade-offs of distributed systems—how can you have both availability and consistency? The answer: by carefully constraining operations to those that commute and converge.

### The Missing Bridge

While CRDTs excel at coordination-free updates, real applications often need moments of stronger consistency. Current practice forces an all-or-nothing choice: either use CRDTs everywhere and accept their limitations, or use traditional transactions and lose availability. We propose a bridge: patterns that combine CRDT operations with optional phase-based coordination.

---

## 2. CRDTs in the Phase Spectrum {#crdts-in-spectrum}

### Positioning Pure CRDTs

In the Phase Spectrum, pure CRDTs occupy an extreme position:

```
0.5PS ─────── 1PS ─────── 1.5PS ─────── 2PS ─────── 3PS ─────── 2PC
  ↑
Pure CRDTs

Coordination:  NONE
Consistency:   Eventual (Strong Eventual)
Availability:  Maximum
Complexity:    Semantic (merge functions)
```

CRDTs are essentially "0 PS"—even less coordination than 0.5PS because they don't even require message delivery acknowledgment.

### The aci-D Analysis of CRDTs

Using our aci-D framework:
- **atomicity**: None in traditional sense; operations apply locally
- **consistency**: Strong Eventual Consistency (SEC)—all replicas converge
- **isolation**: Not applicable—all states are valid
- **Durability**: Local only until replication

This extreme position makes CRDTs perfect for specific scenarios but problematic for others.

---

## 3. The Limitations of Pure CRDTs {#limitations}

### Problem 1: Lack of Synchronization Points

Pure CRDTs provide no mechanism to ensure all replicas have seen specific updates. In collaborative editing, you can't implement "save and share" semantics where users know their changes are globally visible.

### Problem 2: Unbounded Metadata Growth

State-based CRDTs accumulate metadata (version vectors, tombstones) indefinitely. Without coordination to agree on garbage collection points, memory usage grows without bound. Preguiça et al. (2003) identified this in their work on Bayou, but CRDTs inherited the same challenge.

### Problem 3: No Global Invariants

CRDTs cannot enforce global invariants that require coordination. The classic example: maintaining a bank account balance ≥ 0 across concurrent withdrawals. Balegas et al.'s work on "Putting Consistency Back into Eventual Consistency" (2015) tried to address this with invariant-preserving CRDTs, but with limited success.

### Problem 4: No Explicit Durability

CRDTs offer no way to ensure updates are durably replicated to a quorum. A client writing to a CRDT has no guarantee beyond local persistence—problematic for operations with regulatory or business requirements.

---

## 4. Introducing the CRDT Modifier (CM) {#crdt-modifier}

### Definition

**CRDT Modifier (CM)**: A pattern modifier that replaces traditional state management with CRDT-based operations during non-coordinated phases, while preserving the base pattern's coordination phases.

### How CM Works

When applied to a base pattern:
1. **Local Operations**: Use CRDT semantics for immediate, conflict-free updates
2. **Coordination Phases**: Unchanged from base pattern
3. **State Reconciliation**: CRDT merge functions handle concurrent updates
4. **Checkpoint Creation**: Coordination phases create consistent snapshots

### Notation

Following our modifier syntax:
- `2PS+CM` = Two-Phase Saga with CRDT modifier
- `3PS+CM` = Three-Phase Saga with CRDT modifier
- `Saga+CM` = Saga with CRDT-based state

---

## 5. The 2PS+CM Pattern {#2ps-cm-pattern}

### Pattern Structure

The 2PS+CM pattern creates a hybrid that moves dynamically through the Phase Spectrum:

```
Timeline: ────────────────────────────────────────→

Mode:     CRDT Mode    │ 2PS Sync │    CRDT Mode    │ 2PS Sync │
                       ↑          ↑                  ↑          ↑
                    Trigger    Complete           Trigger   Complete

Spectrum: [0 PS] ─────→ [2 PS] ───→ [0 PS] ─────→ [2 PS] ──→ [0 PS]
```

### Phase Definitions

**Phase 0: CRDT Operations (Default)**
```go
func (s *State) LocalUpdate(op Operation) {
    // Apply CRDT operation immediately
    s.crdt.Apply(op)
    
    // Broadcast to other replicas (async)
    go s.broadcast(op)
    
    // Check if sync needed
    if s.shouldTriggerSync(op) {
        s.initiatePhase1()
    }
}
```

**Phase 1: Prepare Sync (On Trigger)**
```go
func (s *State) PrepareSync() error {
    // Snapshot current CRDT state
    snapshot := s.crdt.Snapshot()
    
    // Validate any invariants
    if err := s.validateGlobalInvariants(snapshot); err != nil {
        return err
    }
    
    // Prepare checkpoint
    s.checkpoint = snapshot
    return nil
}
```

**Phase 2: Execute Sync**
```go
func (s *State) ExecuteSync() error {
    // Coordinate with quorum
    agreed := s.coordinator.AgreeOnCheckpoint(s.checkpoint)
    
    // Persist durably
    s.durableStore.Save(agreed)
    
    // Garbage collect old CRDT metadata
    s.crdt.CompactBefore(agreed.Timestamp)
    
    return nil
}
```

### Trigger Conditions

The transition from CRDT mode to sync mode can be triggered by:

1. **Conflict Threshold**: Too many concurrent updates detected
2. **Time-Based**: Periodic checkpointing (e.g., every 5 minutes)
3. **Size-Based**: CRDT metadata exceeds threshold
4. **Application-Specific**: User clicks "save" or "commit"
5. **Invariant Risk**: Approaching constraint boundaries

---

## 6. Literature Context and Related Work {#literature}

### Bayou: The Pioneer (1994-1997)

Terry et al.'s Bayou system introduced many concepts we build upon:
- **Tentative vs. Committed Updates**: Similar to our CRDT vs. sync phases
- **Session Guarantees**: Provided via explicit sync in our model
- **Anti-Entropy**: Background synchronization resembles our Phase 0

However, Bayou predated CRDTs and used application-specific conflict resolution rather than mathematical convergence.

### RedBlue Consistency (2012)

Li et al.'s RedBlue consistency classified operations as:
- **Blue**: Commutative operations (like our CRDT phase)
- **Red**: Coordinated operations (like our sync phase)

Their static classification differs from our dynamic phase transitions, but the intuition is similar: not all operations need coordination.

### Lasp and Partisan (2015-2018)

Christopher Meiklejohn's work on Lasp showed how to build applications entirely with CRDTs, while acknowledging the need for "synchronization barriers" in practice. Our 2PS+CM pattern formalizes these ad-hoc barriers.

### Azure Cosmos DB's Bounded Staleness (2017)

Microsoft's Cosmos DB offers "bounded staleness consistency" where reads lag by at most K operations or T time. This inspired our trigger conditions—bounds that transition from CRDT to coordinated mode.

### Local-First Software (2019)

Kleppmann et al.'s local-first software principles advocate for CRDT-based applications with optional synchronization. Our pattern provides the missing formal framework for their vision.

---

## 7. Use Cases and Comparative Analysis {#use-cases}

### Comprehensive Use Case Analysis

| Use Case | Pure CRDT Limitations | 2PS+CM Advantages | Trigger Strategy |
|----------|----------------------|-------------------|------------------|
| **Collaborative Text Editing** | • Unbounded history growth<br>• No "save point" concept<br>• Can't prune old operations | • Checkpoint agreed document state<br>• Garbage collect history at checkpoints<br>• Explicit "document saved" semantics | Time-based (auto-save) or user-triggered |
| **Shopping Cart** | • Can't prevent overselling<br>• No point-in-time consistency<br>• Cart might never converge | • CRDT for adding/removing items<br>• 2PS at checkout for inventory check<br>• Guaranteed cart state at purchase | Checkout action triggers sync |
| **Mobile Offline Sync** | • No durability guarantees<br>• Can't confirm sync complete<br>• May lose data on device loss | • Local CRDT updates while offline<br>• 2PS sync on reconnection<br>• Explicit "synced to cloud" status | Network reconnection event |
| **Distributed Counters** | • Can't enforce upper bounds<br>• No atomic "read and reset"<br>• Divergence under partitions | • Increment via CRDT normally<br>• Sync when approaching limits<br>• Atomic reset via coordinated phase | Threshold-based (90% of limit) |
| **IoT Sensor Aggregation** | • Can't detect global thresholds<br>• No synchronized snapshots<br>• Alert timing uncertainties | • CRDT aggregation at edge<br>• Sync when anomalies detected<br>• Coordinated alert generation | Anomaly detection or periodic |
| **Social Media Reactions** | • Like counts may diverge<br>• No "final" count for analytics<br>• Can't prevent duplicate likes | • CRDT for real-time updates<br>• Periodic sync for analytics<br>• De-duplication during sync | Periodic (hourly) batches |
| **Multiplayer Game State** | • No authoritative state<br>• Can't resolve rule conflicts<br>• Cheating via state manipulation | • CRDT for movement/actions<br>• Sync for score updates<br>• Server validation in sync phase | Score changes or round endings |
| **Distributed Caching** | • No cache coherence points<br>• Can't guarantee fresh reads<br>• No TTL coordination | • CRDT for cache updates<br>• Sync for invalidation<br>• Coherent TTL management | Hot key detection or TTL expiry |

### Detailed Example: Collaborative Document Editing

**Pure CRDT Approach**:
```javascript
// Every character insertion is a CRDT operation
doc.insert(position, char, userId, vectorClock)
// Grows unbounded - includes all history forever
// No way to know when all users have seen an edit
```

**2PS+CM Approach**:
```javascript
// Phase 0: Local edits via CRDT
doc.localInsert(position, char)  // Immediate, no coordination

// Triggered by auto-save timer or user action
async function saveDocument() {
    // Phase 1: Prepare
    const snapshot = await doc.prepareCheckpoint()
    
    // Phase 2: Execute 
    const checkpoint = await coordinator.commitCheckpoint(snapshot)
    
    // Now can safely garbage collect
    doc.pruneHistoryBefore(checkpoint.timestamp)
    
    // UI shows "Document saved to cloud"
    showSavedIndicator()
}
```

---

## 8. Implementation Considerations {#implementation}

### State Management Architecture

```go
type CRDTModifiedState struct {
    // CRDT for normal operations
    crdt     CRDT
    
    // Coordination state
    phase    Phase
    checkpoint *Checkpoint
    
    // Triggers
    triggers []TriggerCondition
    
    // Metrics for trigger decisions
    metrics  struct {
        conflictRate   float64
        metadataSize   int64
        lastSync       time.Time
        operationCount int64
    }
}
```

### Trigger Implementation

```go
type TriggerCondition interface {
    ShouldTriggerSync(state *CRDTModifiedState) bool
}

type ConflictRateTrigger struct {
    threshold float64
}

func (t *ConflictRateTrigger) ShouldTriggerSync(state *CRDTModifiedState) bool {
    return state.metrics.conflictRate > t.threshold
}

type CompositeTrigger struct {
    triggers []TriggerCondition
    mode     TriggerMode // AND, OR, MAJORITY
}
```

### Network Protocol Extensions

The 2PS+CM pattern requires protocol extensions:

```protobuf
message CRDTOperation {
    bytes operation_data = 1;
    VectorClock clock = 2;
    bool triggers_sync = 3;  // Hint for sync coordination
}

message SyncRequest {
    bytes crdt_snapshot = 1;
    Timestamp as_of = 2;
    repeated string participants = 3;
}
```

### Failure Handling

Unlike pure 2PS, failure during sync doesn't lose data:

```go
func (s *State) HandleSyncFailure(err error) {
    // Revert to CRDT mode - no data loss
    s.phase = CRDTPhase
    
    // Operations continue to accumulate
    // Will retry sync later
    s.scheduleRetry()
    
    // Key: CRDT operations during failed sync are preserved
}
```

---

## 9. Theoretical Properties {#theory}

### Safety Properties

**Theorem 1: No Lost Updates**
Under 2PS+CM, no acknowledged update is lost:
- CRDT operations are locally durable immediately
- Sync phase ensures distributed durability
- Failure during sync preserves CRDT state

**Theorem 2: Convergence Preservation**
2PS+CM preserves CRDT convergence properties:
- Between syncs: Standard CRDT convergence
- At sync points: Global agreement via 2PS
- Post-sync: Convergence from agreed checkpoint

### Liveness Properties

**Bounded Synchronization**:
With appropriate triggers, sync phases occur within bounded time/operations:
- Time-based triggers ensure maximum staleness
- Size-based triggers prevent unbounded growth
- Application triggers provide semantic boundaries

### Consistency Model

2PS+CM provides a novel consistency model:

```
During CRDT phase: Strong Eventual Consistency (SEC)
During sync phase: Snapshot Consistency
Post-sync:        Checkpoint Consistency + SEC
```

This is stronger than pure SEC but weaker than linearizability—a pragmatic middle ground.

---

## 10. Conclusions {#conclusions}

### The Power of Hybrid Patterns

2PS+CM demonstrates that the Phase Spectrum isn't just about static patterns—it's a framework for understanding dynamic movement between consistency models. By treating CRDTs as a modifier rather than a complete solution, we get:

1. **Adaptive Consistency**: Applications can demand stronger guarantees precisely when needed
2. **Practical CRDTs**: Solutions to metadata growth and missing synchronization
3. **Clear Mental Model**: Developers understand "local updates" vs. "global sync"

### Generalizing the Approach

The CM modifier could apply to other patterns:
- `3PS+CM`: Reserve/Validate/Execute with CRDT-based reservations
- `Saga+CM`: Compensations over CRDT state
- `1.5PS+CM`: Critical operations coordinate, eventual use CRDTs

### Future Directions

1. **Formal Verification**: Prove convergence and safety properties in TLA+
2. **Optimal Triggers**: Machine learning for sync trigger conditions
3. **Compression Techniques**: Efficient checkpoint representation
4. **Standardization**: Protocol specifications for CRDT+coordination

### Final Thought

Pure CRDTs asked us to abandon coordination entirely. Pure transactions demand coordination for everything. Reality needs both—and the Phase Spectrum provides the vocabulary to describe these hybrid patterns. 2PS+CM shows that we can have our cake and eat it too: coordination-free operations when possible, coordinated checkpoints when necessary.

Just as the original Phase Spectrum revealed the hidden patterns between 2PC and Saga, adding CRDTs to the spectrum reveals the hidden patterns between coordination and convergence. The future isn't pure CRDTs or pure transactions—it's intelligent hybrids that adapt to application needs.

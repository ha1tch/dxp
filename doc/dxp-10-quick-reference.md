# The Phase Spectrum™ Quick Reference

## The Spectrum at a Glance

```
0.5PS ─────── 1PS ─────── 1.5PS ─────── 2PS ─────── 3PS ─────── 2PC
 ↓            ↓            ↓             ↓           ↓            ↓
Fire &      Saga      Mixed Saga    Two-Phase   Three-Phase   Two-Phase
Forget               Critical+Evt      Saga        Saga        Commit

FAST & LOOSE ←─────────────────────────────────────────→ SAFE & STRUCTURED
```

## Pattern Comparison Matrix

| Pattern | Phases | Blocking | Consistency | Best For | Avoid When |
|---------|--------|----------|-------------|----------|------------|
| **0.5PS** | 0.5 | Never | None | Analytics, Logs | Data loss unacceptable |
| **Saga** | 1 | Never | Eventual | Long workflows | High contention |
| **1.5PS** | 1.5 | Critical only | Mixed | Real systems | All ops equally critical |
| **2PS** | 2 | Between phases | Better | General purpose | Need full parallelism |
| **3PS** | 3 | Never | Strong-ish | High contention | Simple CRUD |
| **2PC** | 2 | Always | ACID | Financial critical | Microservices |

## aci-D Properties by Pattern

| Pattern | **a**tomicity | **c**onsistency | **i**solation | **D**urability |
|---------|---------------|------------------|---------------|----------------|
| 0.5PS   | ✗ | ✗ | ✗ | ✗ |
| Saga    | compensations | eventual | ✗ | ✓ |
| 1.5PS   | critical only | mixed | partial | ✓ |
| 2PS     | phase-level | improved | phase-level | ✓ |
| 3PS     | near-ACID | strong-ish | reservations | ✓ |
| 2PC     | ✓ | ✓ | ✓ | ✓ |

## Pattern Decision in 30 Seconds

```
START: What's your primary need?
│
├─ Need ACID guarantees?
│  ├─ YES: Can you tolerate blocking?
│  │  ├─ YES → 2PC
│  │  └─ NO → 3PS
│  └─ NO: Continue ↓
│
├─ Need to prevent race conditions?
│  ├─ YES: How much contention?
│  │  ├─ HIGH → 3PS
│  │  └─ MODERATE → 2PS
│  └─ NO: Continue ↓
│
├─ Mixed criticality operations?
│  ├─ YES → 1.5PS
│  └─ NO: Continue ↓
│
├─ Can tolerate data loss?
│  ├─ YES → 0.5PS
│  └─ NO → Saga
```

## Pattern Modifiers (Composable)

| Modifier | Symbol | Purpose | Use When |
|----------|---------|---------|----------|
| **OV** | ✓ | Optional Verification | Long delays between phases |
| **TBS** | ⏱ | Time-Bounded States | Prevent resource leaks |
| **GA** | 🌍 | Geographic Affinity | Multi-region deployment |
| **SC** | ⚡ | Selective Consistency | Mixed operation criticality |

**Composition**: `Pattern + Modifier₁ + Modifier₂ = Enhanced Pattern`

Example: `3PS + OV + TBS` = Three-Phase Saga with verification checkpoints and automatic expiration

## Key Metrics by Pattern

### 0.5PS (Fire-and-Forget)
- **Track**: Delivery rate (if possible)
- **Ignore**: Individual failures
- **Alert**: System-wide delivery < 95%

### Saga
- **Track**: Compensation rate
- **Target**: < 5% compensations
- **Alert**: Compensation failures

### 1.5PS (Mixed)
- **Track**: Critical success rate
- **Target**: Critical > 99.9%
- **Accept**: Eventual < 95%

### 2PS (Two-Phase)
- **Track**: Prepare success, Phase balance
- **Target**: Prepare ≈ Execute time
- **Alert**: Prepare timeouts > 1%

### 3PS (Three-Phase)
- **Track**: Validation failures, Conflicts
- **Target**: Validation success > 99%
- **Alert**: Resource leaks

## Common Anti-Patterns

| Anti-Pattern | Description | Instead Use |
|--------------|-------------|-------------|
| **Everything Saga** | Using Saga for high-contention resources | 2PS or 3PS for race prevention |
| **2PC Everywhere** | Blocking all operations unnecessarily | Mix patterns by criticality |
| **Silent Downgrade** | Falling back to weaker patterns without notice | Explicit pattern selection |
| **Compensation Cascade** | Complex compensation chains across patterns | Minimize cross-pattern dependencies |
| **Pattern Shopping** | Changing patterns based on load | Stable pattern selection |

## Performance Rules of Thumb

```
Latency (typical):
0.5PS: 1-10ms    (just queue)
Saga:  50-200ms  (sequential)
1.5PS: 50-100ms  (critical path)
2PS:   30-80ms   (2 phases)
3PS:   40-100ms  (3 phases, parallel)
2PC:   100-500ms (blocking)

Throughput (relative):
0.5PS: ████████████ Highest
Saga:  ████████░░░░ High
1.5PS: ████████░░░░ High
2PS:   ██████░░░░░░ Medium
3PS:   ██████░░░░░░ Medium
2PC:   ██░░░░░░░░░░ Low
```

## Quick Diagnosis Guide

| Symptom | Likely Pattern | Likely Issue | Quick Fix |
|---------|----------------|--------------|-----------|
| "Losing orders" | Saga | Race condition | → Upgrade to 2PS |
| "System slow" | 2PS | Prepare bottleneck | → Consider 3PS |
| "Deadlocks" | 2PC | Lock ordering | → Review or go 3PS |
| "Can't scale" | 2PC | Blocking | → Migrate to 2PS/3PS |
| "Overselling" | Saga | No isolation | → Add 2PS validation |
| "Complex rollbacks" | Any | Missing idempotency | → Add idempotency keys |

## Evolution Path

```
Your Journey: → → → → →

Start Simple        Add Safety         Handle Races       Optimize
    ↓                   ↓                  ↓                ↓
  Saga    →          2PS      →         3PS      →    Mixed Patterns
         Race?                 Contention?           Right tool/job
```

## Emergency Checklist

When things go wrong:

- [ ] Identify which pattern is failing
- [ ] Check pattern-specific metrics (see above)
- [ ] Look for pattern smells (high compensation rate? phase imbalance?)
- [ ] Consider immediate modifier (add TBS to prevent leaks?)
- [ ] Plan evolution (need stronger pattern?)

## Remember

1. **No perfect pattern** - only right pattern for the job
2. **Evolution is normal** - systems grow into new patterns
3. **Mix patterns** - different operations have different needs
4. **Modifiers first** - try modifiers before changing patterns
5. **Measure everything** - data drives pattern decisions

---

*The Phase Spectrum: From Fire-and-Forget to Distributed ACID*

For detailed explanations, see the [Main Guide](dxp-01-guide.md)
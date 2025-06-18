# Distributed Transaction Pattern Modifiers

## Table of Contents
1. [Introduction](#introduction)
2. [Understanding Pattern Modifiers](#understanding-modifiers)
3. [Optional Verification (OV)](#optional-verification)
4. [Time-Bounded States (TBS)](#time-bounded-states)
5. [Geographic Affinity (GA)](#geographic-affinity)
6. [Selective Consistency (SC)](#selective-consistency)
7. [Modifier Combinations](#modifier-combinations)
8. [Implementation Patterns](#implementation-patterns)
9. [Selection Guide](#selection-guide)
10. [Conclusions](#conclusions)

---

## 1. Introduction {#introduction}

While the base distributed transaction patterns (0.5PS through 3PS) provide the fundamental approaches to managing distributed transactions, real-world systems often need additional capabilities. Pattern modifiers are optional enhancements that can be applied to any base pattern to address specific requirements without changing the core transaction flow.

### What Are Pattern Modifiers?

Pattern modifiers are:
- **Composable**: Can be combined with any base pattern
- **Optional**: Applied only when needed
- **Focused**: Each addresses a specific concern
- **Non-invasive**: Don't change the fundamental pattern behavior

### Why Pattern Modifiers?

Instead of creating new patterns for every variation (leading to pattern explosion), modifiers allow you to:
- Start with a simple base pattern
- Add specific capabilities as needed
- Keep the conceptual model clean
- Avoid over-engineering

---

## 2. Understanding Pattern Modifiers {#understanding-modifiers}

### The Modifier Model

```
Base Pattern + Modifier(s) = Enhanced Pattern

Examples:
- 2PS + OV = Two-Phase Saga with Optional Verification
- 3PS + TBS = Three-Phase Saga with Time-Bounded States
- 1.5PS + GA + SC = Geographically-Aware Mixed-Consistency Saga
```

### Key Principles

1. **Modifiers enhance, not replace**: The base pattern's phases remain intact
2. **Modifiers are stackable**: Multiple modifiers can work together
3. **Modifiers are conditional**: Applied based on runtime or configuration needs
4. **Modifiers maintain aci-D properties**: They don't break the base pattern's guarantees

---

## 3. Optional Verification (OV) {#optional-verification}

### Overview

Optional Verification adds the ability to perform on-demand status checks between phases. Originally conceived as the "2.5PS" pattern, OV is better understood as a modifier that can enhance any multi-phase pattern.

### When to Use OV

- **Human approval workflows**: Long delays between preparation and execution
- **Batch processing**: Verify state before processing large batches
- **Unreliable networks**: Check participant health before critical operations
- **High-value transactions**: Extra verification for important operations

### How OV Works

```
Standard 2PS:
┌─────────┐      ┌─────────┐
│ Prepare │ ───> │ Execute │
└─────────┘      └─────────┘

2PS + OV:
┌─────────┐      ┌─────────────┐      ┌─────────┐
│ Prepare │ ───> │ Verify? (OV) │ ───> │ Execute │
└─────────┘      └─────────────┘      └─────────┘
                 (Conditional)
```

### Implementation Example

```go
type OptionalVerification struct {
    VerifyCondition func(txState *TransactionState) bool
    VerifyTimeout   time.Duration
    VerifyRetries   int
}

func (ov *OptionalVerification) Apply(ctx context.Context, coordinator Coordinator) error {
    if !ov.VerifyCondition(coordinator.GetState()) {
        return nil // Skip verification
    }
    
    // Perform verification
    for _, participant := range coordinator.GetParticipants() {
        status, err := participant.GetStatus(ctx)
        if err != nil || !status.Ready {
            return coordinator.Abort(ctx, "Verification failed")
        }
    }
    
    return nil
}
```

### OV with Different Base Patterns

#### 2PS + OV
- Verify all participants still hold valid reservations
- Useful when significant time passes between phases

#### 3PS + OV
- Additional verification before final execute phase
- Extreme safety for critical operations

#### 1.5PS + OV
- Selective verification only for critical operations
- Skip verification for eventual operations

### Best Practices

1. **Define clear verification conditions**: When should verification trigger?
2. **Set appropriate timeouts**: Balance safety with performance
3. **Handle verification failures gracefully**: Abort or retry?
4. **Log verification decisions**: For debugging and audit

---

## 4. Time-Bounded States (TBS) {#time-bounded-states}

### Overview

Time-Bounded States adds automatic expiration to intermediate states, preventing resource leaks and enabling self-healing systems.

### When to Use TBS

- **Resource scarcity**: Prevent indefinite resource locks
- **Failure recovery**: Automatic cleanup of abandoned transactions
- **SLA compliance**: Guarantee maximum transaction duration
- **Load management**: Prevent resource exhaustion

### How TBS Works

```
State Lifecycle with TBS:
┌─────────┐     ┌──────────┐     ┌───────────┐
│ Created │ ──> │ Reserved │ ──> │ Committed │
└─────────┘     └──────────┘     └───────────┘
                      │ 
                      │ Timeout
                      ↓
                ┌──────────┐
                │ Expired  │
                └──────────┘
```

### Implementation Example

```go
type TimeBoundedState struct {
    DefaultTTL      time.Duration
    ExtensionPolicy func(state *State) time.Duration
    CleanupFunc     func(ctx context.Context, state *State) error
}

type State struct {
    ID        string
    Phase     Phase
    Data      interface{}
    CreatedAt time.Time
    ExpiresAt time.Time
}

func (tbs *TimeBoundedState) WatchExpiration(ctx context.Context, store StateStore) {
    ticker := time.NewTicker(time.Second)
    defer ticker.Stop()
    
    for {
        select {
        case <-ticker.C:
            expired := store.GetExpiredStates(time.Now())
            for _, state := range expired {
                if err := tbs.CleanupFunc(ctx, state); err != nil {
                    log.Errorf("Cleanup failed for %s: %v", state.ID, err)
                }
            }
        case <-ctx.Done():
            return
        }
    }
}
```

### TBS Strategies

#### Fixed TTL
```go
// All states expire after fixed duration
tbs := &TimeBoundedState{
    DefaultTTL: 5 * time.Minute,
}
```

#### Progressive TTL
```go
// Longer TTL for later phases
tbs := &TimeBoundedState{
    DefaultTTL: 1 * time.Minute,
    ExtensionPolicy: func(state *State) time.Duration {
        switch state.Phase {
        case PhaseReserved:
            return 2 * time.Minute
        case PhaseValidated:
            return 5 * time.Minute
        default:
            return 1 * time.Minute
        }
    },
}
```

#### Adaptive TTL
```go
// TTL based on system load
tbs := &TimeBoundedState{
    ExtensionPolicy: func(state *State) time.Duration {
        load := getSystemLoad()
        if load > 0.8 {
            return 30 * time.Second // Aggressive cleanup under load
        }
        return 5 * time.Minute
    },
}
```

### Best Practices

1. **Set realistic TTLs**: Too short causes false timeouts, too long wastes resources
2. **Implement graceful cleanup**: Don't leave partial state
3. **Support TTL extension**: Allow active transactions to extend
4. **Monitor expiration rates**: High rates indicate problems

---

## 5. Geographic Affinity (GA) {#geographic-affinity}

### Overview

Geographic Affinity optimizes transaction processing for globally distributed systems by keeping operations close to their data.

### When to Use GA

- **Multi-region deployments**: Minimize cross-region latency
- **Data sovereignty requirements**: Keep data in specific regions
- **Performance optimization**: Reduce network round trips
- **Disaster recovery**: Regional failover capabilities

### How GA Works

```
Without GA:
┌─────────┐         ┌─────────┐         ┌─────────┐
│ US-East │ <-----> │ EU-West │ <-----> │ AP-South│
│ Service │ <-----> │ Service │ <-----> │ Service │
└─────────┘         └─────────┘         └─────────┘
     └──────────────────┘ └──────────────────┘
         High Latency         High Latency

With GA:
┌─────────┐         ┌─────────┐         ┌─────────┐
│ US-East │         │ EU-West │         │ AP-South│
│ Service │         │ Service │         │ Service │
└─────────┘         └─────────┘         └─────────┘
     │                   │                   │
┌─────────┐         ┌─────────┐         ┌─────────┐
│ US-East │         │ EU-West │         │ AP-South│
│  Data   │         │  Data   │         │  Data   │
└─────────┘         └─────────┘         └─────────┘
```

### Implementation Example

```go
type GeographicAffinity struct {
    RegionMapper    func(operation *Operation) string
    RegionEndpoints map[string][]string
    FallbackPolicy  FallbackPolicy
}

type FallbackPolicy int

const (
    NoFallback FallbackPolicy = iota
    NearestRegion
    AnyRegion
)

func (ga *GeographicAffinity) RouteOperation(op *Operation) (Participant, error) {
    region := ga.RegionMapper(op)
    endpoints := ga.RegionEndpoints[region]
    
    if len(endpoints) == 0 {
        switch ga.FallbackPolicy {
        case NearestRegion:
            region = ga.findNearestRegion(region)
            endpoints = ga.RegionEndpoints[region]
        case AnyRegion:
            endpoints = ga.getAllEndpoints()
        default:
            return nil, fmt.Errorf("no endpoints in region %s", region)
        }
    }
    
    // Load balance within region
    endpoint := endpoints[rand.Intn(len(endpoints))]
    return ga.connectToEndpoint(endpoint)
}
```

### GA Strategies

#### Regional Isolation
```go
// Each region handles its own transactions
ga := &GeographicAffinity{
    RegionMapper: func(op *Operation) string {
        return op.Metadata["region"]
    },
    FallbackPolicy: NoFallback,
}
```

#### Home Region with Failover
```go
// Prefer home region, failover to nearest
ga := &GeographicAffinity{
    RegionMapper: func(op *Operation) string {
        return op.User.HomeRegion
    },
    FallbackPolicy: NearestRegion,
}
```

#### Follow-the-Sun
```go
// Route based on time of day
ga := &GeographicAffinity{
    RegionMapper: func(op *Operation) string {
        hour := time.Now().UTC().Hour()
        switch {
        case hour >= 0 && hour < 8:
            return "ap-south"
        case hour >= 8 && hour < 16:
            return "eu-west"
        default:
            return "us-east"
        }
    },
}
```

### Best Practices

1. **Design region-aware data models**: Partition data by region when possible
2. **Implement smart routing**: Consider data locality, not just user location
3. **Handle cross-region transactions explicitly**: They're expensive
4. **Monitor regional performance**: Detect and fix hotspots

---

## 6. Selective Consistency (SC) {#selective-consistency}

### Overview

Selective Consistency allows different operations within a transaction to have different consistency guarantees based on their business importance.

### When to Use SC

- **Mixed-criticality operations**: Payment critical, analytics eventual
- **Performance optimization**: Relax consistency where acceptable
- **Cost optimization**: Reduce cross-region synchronization
- **User experience**: Fast response for non-critical operations

### How SC Works

```
Transaction with SC:
┌─────────────────────────────────────┐
│          Transaction T1             │
├─────────────────────────────────────┤
│ Op1: Payment     [Strong]     ✓    │
│ Op2: Inventory   [Strong]     ✓    │
│ Op3: Analytics   [Eventual]   ~    │
│ Op4: Email       [Best Effort] ?   │
└─────────────────────────────────────┘
```

### Implementation Example

```go
type SelectiveConsistency struct {
    DefaultLevel     ConsistencyLevel
    OperationLevels  map[string]ConsistencyLevel
    LevelStrategies  map[ConsistencyLevel]Strategy
}

type ConsistencyLevel int

const (
    BestEffort ConsistencyLevel = iota
    Eventual
    Strong
    Immediate
)

type Strategy interface {
    Execute(ctx context.Context, op *Operation) error
    Verify(ctx context.Context, op *Operation) error
}

func (sc *SelectiveConsistency) ProcessOperation(ctx context.Context, op *Operation) error {
    level := sc.DefaultLevel
    if opLevel, exists := sc.OperationLevels[op.Type]; exists {
        level = opLevel
    }
    
    strategy := sc.LevelStrategies[level]
    return strategy.Execute(ctx, op)
}
```

### SC Strategies

#### Strong Consistency Strategy
```go
type StrongStrategy struct{}

func (s *StrongStrategy) Execute(ctx context.Context, op *Operation) error {
    // Synchronous execution with confirmation
    result := make(chan error, 1)
    
    go func() {
        err := op.Execute()
        if err == nil {
            err = op.WaitForConfirmation(ctx)
        }
        result <- err
    }()
    
    select {
    case err := <-result:
        return err
    case <-ctx.Done():
        return ctx.Err()
    }
}
```

#### Eventual Consistency Strategy
```go
type EventualStrategy struct {
    RetryPolicy RetryPolicy
}

func (s *EventualStrategy) Execute(ctx context.Context, op *Operation) error {
    // Async execution with retries
    go func() {
        retry := 0
        for retry < s.RetryPolicy.MaxRetries {
            if err := op.Execute(); err == nil {
                return
            }
            retry++
            time.Sleep(s.RetryPolicy.BackoffDuration(retry))
        }
    }()
    
    return nil // Return immediately
}
```

#### Best Effort Strategy
```go
type BestEffortStrategy struct{}

func (s *BestEffortStrategy) Execute(ctx context.Context, op *Operation) error {
    // Fire and forget
    go op.Execute()
    return nil
}
```

### Best Practices

1. **Document consistency decisions**: Make trade-offs explicit
2. **Default to stronger consistency**: Relax only when justified
3. **Monitor consistency violations**: Track eventual consistency lag
4. **Provide consistency SLAs**: Set expectations for eventual operations

---

## 7. Modifier Combinations {#modifier-combinations}

### Common Combinations

#### High-Value Global Transactions: 3PS + OV + TBS + GA
```go
pattern := New3PS().
    WithOptionalVerification(highValueChecker).
    WithTimeBounds(5 * time.Minute).
    WithGeographicAffinity(regionalRouter)
```

Use case: International money transfers with human approval

#### Mixed Workload Systems: 1.5PS + SC + TBS
```go
pattern := New15PS().
    WithSelectiveConsistency(criticalityMapper).
    WithTimeBounds(adaptiveTTL)
```

Use case: E-commerce with mixed critical/analytical operations

#### Regional Services: 2PS + GA + TBS
```go
pattern := New2PS().
    WithGeographicAffinity(dataLocalityRouter).
    WithTimeBounds(regionalSLA)
```

Use case: Regional inventory management

### Modifier Interaction Matrix

| Base Pattern | +OV | +TBS | +GA | +SC |
|--------------|-----|------|-----|-----|
| 0.5PS | ❌ No phases | ✅ Cleanup | ✅ Regional | ✅ All best effort |
| Saga | ⚠️ Limited value | ✅ State cleanup | ✅ Regional flow | ✅ Mixed ops |
| 1.5PS | ✅ Critical only | ✅ Both phases | ✅ Regional split | ✅ Natural fit |
| 2PS | ✅ Between phases | ✅ Phase timeouts | ✅ Regional prepare | ✅ Phase-based |
| 3PS | ✅ Extra safety | ✅ All phases | ✅ Regional validate | ✅ Operation level |

---

## 8. Implementation Patterns {#implementation-patterns}

### Modifier Framework

```go
// Base modifier interface
type Modifier interface {
    Apply(ctx context.Context, pattern Pattern) Pattern
    Validate() error
}

// Composable pattern with modifiers
type ModifiablePattern struct {
    base      Pattern
    modifiers []Modifier
}

func (mp *ModifiablePattern) Execute(ctx context.Context, ops []*Operation) error {
    // Apply modifiers in order
    pattern := mp.base
    for _, modifier := range mp.modifiers {
        pattern = modifier.Apply(ctx, pattern)
    }
    
    return pattern.Execute(ctx, ops)
}
```

### Builder Pattern for Modifiers

```go
type PatternBuilder struct {
    base      Pattern
    modifiers []Modifier
}

func NewPatternBuilder(base Pattern) *PatternBuilder {
    return &PatternBuilder{base: base}
}

func (pb *PatternBuilder) WithOptionalVerification(config OVConfig) *PatternBuilder {
    pb.modifiers = append(pb.modifiers, NewOptionalVerification(config))
    return pb
}

func (pb *PatternBuilder) WithTimeBounds(ttl time.Duration) *PatternBuilder {
    pb.modifiers = append(pb.modifiers, NewTimeBoundedStates(ttl))
    return pb
}

func (pb *PatternBuilder) Build() Pattern {
    return &ModifiablePattern{
        base:      pb.base,
        modifiers: pb.modifiers,
    }
}

// Usage
pattern := NewPatternBuilder(New2PS()).
    WithOptionalVerification(ovConfig).
    WithTimeBounds(5 * time.Minute).
    WithGeographicAffinity(gaConfig).
    Build()
```

### Modifier Configuration

```yaml
# config.yaml
transaction_pattern:
  base: "2PS"
  modifiers:
    - type: "OptionalVerification"
      config:
        condition: "high_value"
        threshold: 10000
        timeout: "30s"
    
    - type: "TimeBoundedStates"
      config:
        default_ttl: "5m"
        phase_ttls:
          reserved: "2m"
          validated: "5m"
    
    - type: "GeographicAffinity"
      config:
        strategy: "home_region"
        fallback: "nearest"
    
    - type: "SelectiveConsistency"
      config:
        default: "eventual"
        overrides:
          payment: "strong"
          inventory: "strong"
          analytics: "best_effort"
```

---

## 9. Selection Guide {#selection-guide}

### Decision Tree for Modifiers

```
Start: Base Pattern Selected
    │
    ├─ Long delays between phases?
    │   └─ Yes → Add OV (Optional Verification)
    │
    ├─ Resource constraints?
    │   └─ Yes → Add TBS (Time-Bounded States)
    │
    ├─ Multi-region deployment?
    │   └─ Yes → Add GA (Geographic Affinity)
    │
    └─ Mixed operation criticality?
        └─ Yes → Add SC (Selective Consistency)
```

### Modifier Selection Matrix

| Requirement | Recommended Modifier | Reasoning |
|-------------|---------------------|-----------|
| Human approval workflows | OV | Verify state after delays |
| Resource scarcity | TBS | Prevent resource exhaustion |
| Global deployment | GA | Minimize cross-region latency |
| Mixed criticality | SC | Optimize per operation |
| Regulatory compliance | OV + TBS | Audit trail + guaranteed cleanup |
| High throughput | SC + GA | Reduce unnecessary consistency |
| Unreliable networks | OV + TBS | Verify + auto-cleanup |

### Anti-Patterns to Avoid

1. **Modifier Overload**: Don't add all modifiers "just in case"
2. **Conflicting Modifiers**: Some combinations don't make sense
3. **Premature Optimization**: Start simple, add modifiers as needed
4. **Ignoring Base Pattern**: Modifiers can't fix wrong pattern choice

---

## 10. Conclusions {#conclusions}

### Key Takeaways

1. **Modifiers enhance, not replace**: They add capabilities to base patterns
2. **Composability is powerful**: Mix and match for your needs
3. **Start simple**: Add modifiers when requirements emerge
4. **Document decisions**: Make modifier choices explicit

### The Power of Modifiers

Pattern modifiers transform the distributed transaction patterns from rigid prescriptions into flexible tools:

- **OV** adds safety nets for uncertain environments
- **TBS** adds self-healing properties
- **GA** adds geographic optimization
- **SC** adds business-aligned flexibility

### Future Directions

As distributed systems evolve, new modifiers may emerge:
- **Encryption modifiers** for security requirements
- **Audit modifiers** for compliance needs
- **ML-based modifiers** for adaptive behavior
- **Cost modifiers** for cloud spend optimization

### Final Thoughts

Pattern modifiers represent a mature approach to distributed transactions: start with a solid foundation (base pattern), then add specific capabilities (modifiers) based on actual requirements. This compositional approach leads to simpler, more maintainable systems that can evolve with changing needs.

Remember: The best pattern is not the most sophisticated one, but the simplest one that meets your requirements—with just the right modifiers applied.
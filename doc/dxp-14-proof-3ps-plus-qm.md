
## Formal Proof of 3PS+QM Correctness
### System Model Extension

To the base 3PS model, we add:
- **Quorum Size**: Q = ⌈n/2⌉ + 1 (majority)
- **Participants**: P = {p₁, p₂, ..., pₙ} where n ≥ 2Q - 1
- **Quorum**: Any subset S ⊆ P where |S| ≥ Q

#### Key Property (Quorum Intersection)
```
∀ Q₁, Q₂ where |Q₁| ≥ Q ∧ |Q₂| ≥ Q:
  Q₁ ∩ Q₂ ≠ ∅
```

### Compositional Properties to Prove

We must show that 3PS+QM:
1. **Preserves 3PS Safety**: No violation of base 3PS guarantees
2. **Adds Availability**: Can progress with Q participants
3. **Maintains Correctness**: No split-brain commits
4. **Enables Progress**: Minority failure doesn't block

---

## Theorem 1: Safety Preservation

**Statement**: 3PS+QM maintains all safety properties of base 3PS.

**Proof**:

The 3PS safety relies on:
- All validate → safe to execute
- Any invalidate → must abort

With QM, we modify to:
- Quorum validates → safe to execute  
- Quorum cannot validate → must abort

**Case 1: Quorum validates successfully**
```
Let V = {p ∈ P : Validate(p) = VALID} 
If |V| ≥ Q:
  - At least Q participants validated their reservations
  - By quorum intersection, any other quorum Q' must overlap with V
  - Overlapping participant saw consistent state
  - Safe to proceed to execute
```

**Case 2: Conflicting transactions**

Consider T₁ and T₂ competing for resource r:
```
Timeline:
t₁: T₁ reserves r (all participants)
t₂: T₂ reserves r (all participants)  
t₃: T₁ validation by quorum Q₁
t₄: T₂ validation by quorum Q₂
```

By quorum intersection: ∃p ∈ Q₁ ∩ Q₂

Participant p sees both reservations:
- p validates for at most one transaction
- At least one transaction fails to get quorum validation
- No double execution

Therefore, safety is preserved. □

---

## Theorem 2: Availability Under Partition

**Statement**: 3PS+QM can commit transactions when up to n-Q participants fail.

**Proof**:

Let F ⊂ P be failed participants where |F| ≤ n - Q.
Available participants A = P \ F where |A| ≥ Q.

**Progress through phases**:

1. **Reserve Phase**:
   ```
   Coordinator sends Reserve to all n
   Receives responses from A (|A| ≥ Q)
   Sufficient for quorum decision
   ```

2. **Validate Phase**:
   ```
   Q participants validate successfully
   |Q| ≥ ⌈n/2⌉ + 1 by definition
   Coordinator decides: PROCEED
   ```

3. **Execute Phase**:
   ```
   Execute sent to quorum Q
   All in Q execute
   Transaction commits
   ```

**Key**: Minority F never blocks progress.

Therefore, availability is improved. □

---

## Theorem 3: No Split-Brain Commits

**Statement**: Two conflicting transactions cannot both commit under network partition.

**Proof**:

Consider network partition creating P₁ and P₂ where P₁ ∪ P₂ = P.

**Case 1: Both partitions have quorum**
- Impossible: |P₁| ≥ Q ∧ |P₂| ≥ Q ⇒ |P₁| + |P₂| ≥ 2Q
- But 2Q > n (by definition of majority quorum)
- Contradiction

**Case 2: Only one partition has quorum**
- WLOG, let |P₁| ≥ Q and |P₂| < Q
- Only P₁ can achieve quorum validation
- P₂ cannot proceed past validation
- No split-brain

**Case 3: Neither partition has quorum**
- Neither can achieve Q validations
- Both abort
- No commits at all

Therefore, no split-brain commits possible. □

---

## Theorem 4: Consistency with Partial Execution

**Statement**: Resources remain consistent even when only quorum executes.

**Proof**:

**Scenario**: After quorum Q executes, minority M rejoins.

**Invariant to maintain**:
```
∀r ∈ Resources: Available(r) = Total(r) - Committed(r) ≥ 0
```

**On rejoin, minority M has three states**:

1. **Reserved but not validated**:
   - Reservation expired (by TBS)
   - No resource consumption
   - Consistent

2. **Validated but not executed**:
   - Must check with quorum for decision
   - If quorum executed: M executes too
   - If quorum aborted: M aborts
   - Deterministic reconciliation

3. **Partially executed** (if crash during execute):
   - Local transaction guarantees atomicity
   - Either fully executed or not at all
   - Check with quorum for final state

**Resource counting**:
- Quorum Q executed: resource consumed
- Minority M rejoins: either executes (same transaction) or aborts
- No double consumption

Therefore, consistency is maintained. □

---

## Theorem 5: Liveness Enhancement

**Statement**: 3PS+QM has stronger liveness than base 3PS.

**Proof**:

Define availability:
```
Availability(3PS) = P(all n participants available)
Availability(3PS+QM) = P(at least Q participants available)
```

For majority quorum Q = ⌈n/2⌉ + 1:
```
P(at least Q available) > P(all n available)
```

**Quantitative improvement** (assuming independent failure probability p):
- 3PS: (1-p)ⁿ
- 3PS+QM: Σᵢ₌Q..n C(n,i) × (1-p)ⁱ × pⁿ⁻ⁱ

For typical values (n=5, p=0.1):
- 3PS: 0.59 availability  
- 3PS+QM: 0.99 availability

Therefore, liveness is enhanced. □

---

## Theorem 6: Composability (QM preserves 3PS properties)

**Statement**: QM is a safe modifier that preserves 3PS correctness.

**Proof**:

We show QM transforms 3PS decision rules while preserving invariants:

**Original 3PS decision**:
```
decide(votes) = {
  if ∀v ∈ votes: v = YES then COMMIT
  else ABORT
}
```

**3PS+QM decision**:
```
decide_qm(votes) = {
  if |{v ∈ votes: v = YES}| ≥ Q then COMMIT
  else ABORT
}
```

**Preservation argument**:
1. Atomicity: Quorum decision is still all-or-nothing
2. Consistency: Validation logic unchanged, just vote counting
3. Isolation: Reservations still provide isolation
4. Durability: Local commits still durable

**Key insight**: QM only changes the decision threshold, not the fundamental protocol structure.

Therefore, QM is a safe compositional modifier. □

---

## Practical Considerations

### When Minority Rejoins

```python
def reconcile_minority(participant, transaction_id):
    quorum_state = query_quorum_for_decision(transaction_id)
    
    if quorum_state == COMMITTED:
        if participant.state == VALIDATED:
            participant.execute(transaction_id)
        elif participant.state == RESERVED:
            # Missed validation window
            participant.abort_reservation()
    else:  # ABORTED
        participant.abort_if_not_already()
```

### Configuration Constraints

For safety, enforce:
- n ≥ 2Q - 1 (ensures unique quorum)
- TBS timeout > max_validation_time + network_delay
- Persistent decision log at Q participants

---

## Conclusion

The 3PS+QM combination successfully:
1. **Preserves all 3PS safety properties** through quorum intersection
2. **Improves availability** to tolerate n-Q failures
3. **Prevents split-brain** through majority requirement
4. **Maintains consistency** through deterministic reconciliation
5. **Enhances liveness** significantly (proven quantitatively)

The composition is clean: QM modifies only the voting threshold while preserving the three-phase structure and guarantees of 3PS. This makes 3PS+QM a powerful pattern for systems requiring both strong consistency and high availability.

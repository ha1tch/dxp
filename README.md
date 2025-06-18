# Distributed Transaction Patterns (DXP)

A comprehensive framework for understanding and implementing distributed transaction patterns through a phase-based spectrum approach.

## Documentation Structure

The DXP documentation is organized as a progressive journey through distributed transaction patterns:

### Core Documents

- **[dxp-01-guide.md](https://github.com/ha1tch/dxp/blob/main/doc/dxp-01-guide.md)** - Main Guide  
  Start here. Introduces the phase spectrum (0.5 → 3 phases) and provides comprehensive coverage of all patterns.

- **[dxp-02-deep-dive.md](https://github.com/ha1tch/dxp/blob/main/doc/dxp-02-deep-dive.md)** - Technical Deep Dive  
  Implementation details, mathematical models, race condition analysis, and performance counter-intuitions.

- **[dxp-03-sequence-diagrams.md](https://github.com/ha1tch/dxp/blob/main/doc/dxp-03-sequence-diagrams.md)** - Visual Representations  
  Mermaid sequence diagrams showing each pattern in action using consistent e-commerce examples.

- **[dxp-04-theoretical-foundations.md](https://github.com/ha1tch/dxp/blob/main/doc/dxp-04-theoretical-foundations.md)** - Why These Patterns Exist  
  Explores the impossibility of ACID in microservices and introduces the aci-D framework.

### Advanced Topics

- **[dxp-05-pattern-modifiers.md](https://github.com/ha1tch/dxp/blob/main/doc/dxp-05-pattern-modifiers.md)** - Optional Enhancements  
  Composable modifiers (Optional Verification, Time-Bounded States, Geographic Affinity) that enhance any base pattern.

- **[dxp-06-evolution-guide.md](https://github.com/ha1tch/dxp/blob/main/doc/dxp-06-evolution-guide.md)** - Growing with Patterns  
  How systems naturally evolve through patterns and practical migration strategies.

- **[dxp-07-essentials.md](https://github.com/ha1tch/dxp/blob/main/doc/dxp-07-essentials.md)** - Essential Clarifications  
  Critical implementation details to prevent common errors. Read this before implementing.

## The Pattern Spectrum

```
0.5-Phase → 1-Phase → 1.5-Phase → 2-Phase → 3-Phase
(Fire & Forget) → (Saga) → (Mixed) → (2PS) → (3PS)
```

Each pattern makes different trade-offs between:
- Consistency guarantees
- Performance characteristics
- Failure handling
- Implementation complexity

## Quick Start

1. Read the [Main Guide](https://github.com/ha1tch/dxp/blob/main/doc/dxp-01-guide.md) for an overview
2. Review [Sequence Diagrams](https://github.com/ha1tch/dxp/blob/main/doc/dxp-03-sequence-diagrams.md) to visualize patterns
3. Check [Essential Clarifications](https://github.com/ha1tch/dxp/blob/main/doc/dxp-07-essentials.md) before implementing
4. Use the Pattern Selection Guide in the main document to choose your pattern

## Contact

Email: h@ual.fi

## License

Copyright 2025 h@ual.fi

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
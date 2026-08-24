# Theoretical Foundations

Load this reference only when a user asks for theoretical grounding or a maintainer is changing the skill's core definition.

No single established term fully defines minimum sufficient design. The skill combines a small core and several conditional tools while preserving their limits.

## Core Foundations

### Risk-driven design

George Fairbanks describes a risk-centric loop of identifying and prioritizing risks, selecting techniques that reduce them, and reassessing the remaining risk. MSD adopts proportional investment and feedback from this model. It does not require a complete architecture method or numeric risk score for every choice.

- [Just Enough Software Architecture](https://www.georgefairbanks.com/book/)
- [Risk-Centric Software Architecture](https://www.georgefairbanks.com/assets/pdf/Risk-centric-software-architecture-position-paper.pdf)

### Design by Contract

Design by Contract distinguishes caller obligations, implementation guarantees, and invariants. MSD uses these ideas to identify the non-negotiable floor of sufficiency. It does not require Eiffel, runtime assertions, or formal specification.

- [Eiffel: Design by Contract and Assertions](https://www.eiffel.org/doc/eiffelstudio/I2E-_Design_by_Contract_and_Assertions)

### Simple design

Kent Beck's design rules, as summarized by Martin Fowler, prioritize passing tests and expressing intent before removing duplication and minimizing elements. MSD adopts that ordering: fewer elements never outrank correctness and clarity.

- [Beck Design Rules](https://martinfowler.com/bliki/BeckDesignRules.html)

### YAGNI

YAGNI rejects capability and abstraction built only for predicted future demand. MSD uses it against speculative complexity, not against present reliability, compatibility, recovery, or verification requirements.

- [Yagni](https://martinfowler.com/bliki/Yagni.html)

## Conditional Tools

### Essential and accidental complexity

Fred Brooks distinguishes complexity inherent in the abstract software problem from complexity introduced by its representation. MSD uses the distinction to ask whether complexity is necessary and whether it sits with the right owner. The distinction does not supply a stopping rule by itself.

- [No Silver Bullet](https://worrydream.com/refs/Brooks_1986_-_No_Silver_Bullet.pdf)

### Evolutionary architecture and fitness functions

Evolutionary architecture supports guided, incremental change across multiple dimensions; fitness functions evaluate important architectural characteristics. MSD uses them when a durable property can be measured reliably. It does not require every design judgment to become an automated gate.

- [Building Evolutionary Architectures, second edition, sample chapter](https://www.thoughtworks.com/content/dam/thoughtworks/documents/books/bk_building_evolutionary_architectures_second_edition_free_chapter.pdf)

### Last responsible moment

Lean software development uses the last responsible moment to preserve options until a decision is necessary. MSD adopts delayed, reversible commitment when learning remains valuable. It does not endorse unlimited delay or waive current correctness guarantees.

- [The Software Development Pendulum](https://accu.org/conf-docs/PDFs_2007/Poppendieck-The_Software_Development_Pendulum.pdf)

## Background, Not Replacement Terms

Bounded rationality and satisficing explain why real decisions seek an adequate threshold under limited information, but they do not define the engineering threshold of sufficiency.

- [Herbert Simon's Nobel lecture](https://www.nobelprize.org/uploads/2018/06/simon-lecture.pdf)

Minimally viable architecture is adjacent because it focuses early product architecture on necessary decisions. MSD is broader: it also judges code, state, recovery, evidence, and later changes.

- [Minimally Viable Architecture](https://sei.cmu.edu/documents/6382/Minimally-Viable-Architecture-Architecture-Early-in-Development.pdf)

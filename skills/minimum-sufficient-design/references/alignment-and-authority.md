# Alignment and Authority

Load this reference only when an accepted decision, frozen contract, domain context, conflicting source, user-mentioned prior decision, or possible override affects the proposal.

## Retrieve Decision-Relevant Evidence

Read in this order, stopping when the decision frame is sufficiently supported:

1. explicit user scope and current project instructions;
2. frozen contracts and accepted decision records that govern the surface;
3. domain context and authoritative terminology;
4. relevant implementation and tests;
5. authorized runtime facts;
6. historical material, clearly labeled as history.

Target the retrieval. Do not assume a filename, directory layout, decision template, or permission model. A source's authority comes from current project governance, not from its format alone.

## Keep Evidence Types Distinct

- **Current constraint:** a rule or contract the proposal must obey now.
- **Domain language:** the shared meaning of business or technical concepts.
- **Current implementation:** what the code presently does; it may reveal drift but does not automatically supersede an accepted decision.
- **Runtime fact:** observed state within an authorized scope and time window.
- **Historical context:** why an earlier choice was made; it is not automatically current authority.

When two sources conflict, identify both, their apparent authority, and how the conflict changes the recommendation. Explicitly state which evidence, alignment, engineering-judgment, and authority gaps are closed or remain unresolved before recommending. Do not blend the sources into a convenient interpretation or treat a document type as authoritative without current governance evidence.

## Close the Four Kinds of Gap

### Evidence gap

Close it with safe, authorized retrieval at the level needed by the claim. If retrieval is unavailable, state the missing fact, the alternatives it separates, and the smallest input or authorization needed. Do not guess or retry indefinitely.

### Alignment gap

Close it when participants share the same problem, scope, constraints, terminology, and success criteria. They need not prefer the same solution.

### Engineering judgment

Close it by comparing decision-relevant evidence and giving a recommendation with costs, risks, and verification. The agent owns this work.

### Authority decision

Close it only when the accountable owner chooses a product preference, accepts residual risk, commits resources, or makes another responsibility-bearing decision. Evidence and recommendation should make that choice legible, but must not impersonate the owner.

## Resolve Decision Conflicts Explicitly

When a candidate conflicts with a current decision, pause only the affected design branch and present:

- the current decision and why it governs;
- the candidate and the exact point of conflict;
- the compatibility, migration, risk, or ownership impact;
- a recommendation to preserve, create a bounded exception, or explicitly supersede.

### Preserve

Use when the original constraints and evidence still hold. Adapt the candidate rather than weakening the governing decision silently.

### Bounded exception

Use when a narrow case genuinely differs and the exception can be precisely scoped, verified, and retired or reviewed. Record what remains governed by the original decision.

### Explicit supersession

Use when new evidence or changed scope invalidates the old choice. Define the replacement authority plus any migration, compatibility, recovery, and rollback obligations. Update the authoritative record before declaring the result frozen or implementation-ready.

If record changes are outside the current authority, continue only as far as allowed and leave the update as an explicit incomplete obligation.

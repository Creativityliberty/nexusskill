# Quality Gates Reference

Quality gates ensure each phase is complete before moving forward.
They prevent scope drift, missing artifacts, and premature execution.

---

## Gate Types

### Phase Gates (Between Missions)

Critical checkpoints between major project phases. Must PASS to proceed.

**Phase 1 → Phase 2 Gate: "Architecture Validated"**
```
Checklist:
├─ ☐ PRD document exists and covers: problem, users, features, success metrics
├─ ☐ Architecture decided and documented (tech stack, components, data flow)
├─ ☐ Data model defined (entities, relationships, key fields)
├─ ☐ Project scaffold created and running locally
├─ ☐ No unresolved blocking questions
└─ ☐ User has reviewed and approved direction
```

**Phase 2 → Phase 3 Gate: "Core Features Working"**
```
Checklist:
├─ ☐ Authentication working (sign up, sign in, sign out)
├─ ☐ Core CRUD operations functional
├─ ☐ Primary user flow works end-to-end
├─ ☐ Database populated with test/seed data
├─ ☐ Basic error handling in place
└─ ☐ No critical bugs in core flow
```

**Phase 3 → Launch Gate: "Ready for Users"**
```
Checklist:
├─ ☐ Deployed to production environment
├─ ☐ Tests passing (unit + integration)
├─ ☐ Payment flow working (if applicable)
├─ ☐ Landing/marketing page live
├─ ☐ Error tracking configured
├─ ☐ Basic documentation available
└─ ☐ User has done final review
```

### Task Gates (Within a Mission)

Lighter checkpoints between tasks. PARTIAL is acceptable.

```
Task Gate:
├─ ☐ Artifact produced?
├─ ☐ Artifact meets basic quality? (not empty, well-structured)
├─ ☐ Dependencies for next task satisfied?
└─ ☐ Any blockers identified?
```

---

## Gate Outcomes

### PASS ✅
All criteria met. Proceed to next phase/task.

### PARTIAL ⚠️
Some criteria met, no blockers. Proceed with acknowledged gaps.
Document what's missing and when it will be addressed.

### FAIL ❌
Critical criteria not met. Must fix before proceeding.
Identify specific failures and remediation steps.

---

## Artifact Quality Criteria

### Documentation Artifacts (PRD, Architecture, etc.)

**Minimum quality:**
- Has clear title and date
- Covers all required sections (not just headers)
- Specific to this project (not generic template)
- Actionable — a developer could start working from it

**High quality (aim for this):**
- Includes diagrams or visual aids
- Has concrete examples and user scenarios
- Addresses edge cases and failure modes
- Includes success metrics

### Code Artifacts

**Minimum quality:**
- Runs without errors
- Has basic error handling
- Follows project coding conventions
- Has at least smoke-test level testing

**High quality:**
- Comprehensive error handling
- Well-documented (comments + JSDoc/docstrings)
- Unit tests with >70% coverage
- Handles edge cases

### API Artifacts (OpenAPI spec, etc.)

**Minimum quality:**
- All endpoints documented
- Request/response schemas defined
- Authentication described

**High quality:**
- Examples for each endpoint
- Error response schemas
- Rate limiting documented
- Versioning strategy defined

---

## Gate Presentation Format

When presenting a gate check to the user:

```markdown
## Quality Gate: {Gate Name}

**Status: {PASS/PARTIAL/FAIL}**

| Criterion | Status | Notes |
|-----------|--------|-------|
| PRD complete | ✅ | Covers all sections |
| Architecture documented | ✅ | ADR written |
| Data model defined | ⚠️ | Missing indexes |
| Scaffold running | ✅ | Dev server starts |

{If PARTIAL or FAIL:}
**Action needed:**
- Define database indexes for performance
- ETA: Will address in Phase 2

**Recommendation:** Proceed (gap is non-blocking)
```

---

## Adaptive Gate Strictness

| Project Complexity | Gate Strictness |
|-------------------|----------------|
| 1-3 (Simple) | Minimal — just check artifacts exist |
| 4-6 (Medium) | Standard — check quality criteria |
| 7-10 (Complex) | Strict — full checklist, user approval required |

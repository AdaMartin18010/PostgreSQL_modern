# Translation Strategy for PostgreSQL_Formal

> **Document Status**: 🚧 Draft
> **Version**: v1.0
> **Last Updated**: 2026-04-07

---

## Overview

This document outlines the comprehensive strategy for translating the PostgreSQL_Formal knowledge base from Chinese to English, enabling international accessibility to this academic-grade formalized PostgreSQL documentation.

---

## Translation Scope

### Phase 1: High Priority (Core Documentation)

**Target Completion**: Q2 2026

| Category | Documents | Priority |
|----------|-----------|----------|
| Main Entry | README.md | P0 |
| Version Overview | 00-Version-Specific/README.md | P0 |
| PostgreSQL 17 Core | 8 Documents | P0 |
| PostgreSQL 18 Core | 12 Documents | P1 |

**PostgreSQL 17 Core Documents**:

1. VACUUM Memory Optimization
2. Incremental Backup
3. JSON_TABLE
4. MERGE Enhancements
5. Logical Replication Upgrades
6. pg_maintain Role
7. Monitoring & Diagnostics
8. Upgrade Guide

**PostgreSQL 18 Core Documents**:

1. AIO (Asynchronous I/O)
2. B-tree Skip Scan
3. UUIDv7
4. Virtual Generated Columns
5. Temporal Constraints
6. OAuth2 Integration
7. Parallel GIN Build
8. pg_upgrade Enhancements
9. pgvector
10. CloudNativePG
11. OpenTelemetry
12. LZ4 Compression

### Phase 2: Medium Priority (Theoretical Foundation)

**Target Completion**: Q3-Q4 2026

| Module | Documents | Est. Words |
|--------|-----------|------------|
| 01-Theory | 5 documents | ~50,000 |
| 04-Concurrency | 5 documents | ~60,000 |
| 02-Storage | 5 documents | ~55,000 |

Key documents:

- Relational Algebra Formalization
- Transaction Theory
- ACID Formalization
- MVCC Formal Specification
- Buffer Pool Formalization

### Phase 3: Lower Priority (Extended Modules)

**Target Completion**: 2027

| Module | Documents | Est. Words |
|--------|-----------|------------|
| 03-Query | 4 documents | ~40,000 |
| 05-Distributed | 4 documents | ~45,000 |
| 06-FormalMethods | 3 documents | ~35,000 |
| 07-PracticalCases | 12 documents | ~80,000 |
| 08-Performance | 4 documents | ~30,000 |
| 09-Tools | 4 documents | ~25,000 |
| 10-Visualization | 5 documents | ~35,000 |
| 11-Database-Centric-Architecture | 25+ documents | ~150,000 |

---

## Translation Principles

### 1. Technical Terminology

**Preserve English for**:

- Standard database acronyms: MVCC, WAL, ACID, SQL, API
- PostgreSQL-specific terms: VACUUM, TOAST, GIN, GiST, SP-GiST
- Computer science concepts: JIT, TLA+, Raft, 2PC/3PC

**Example**:

```
✅ "MVCC (Multi-Version Concurrency Control) ensures transaction isolation"
❌ "多版本并发控制 ensures transaction isolation"
```

### 2. Code Examples

**Rule**: Keep all code examples exactly as-is.

```sql
-- Original (Chinese comments allowed in code blocks)
SELECT * FROM pg_stat_activity;  -- 查询活动连接

-- Translated (keep code identical)
SELECT * FROM pg_stat_activity;  -- 查询活动连接
```

### 3. Mathematical Formulas

**Rule**: Preserve all mathematical notation.

```
Original: ∀t ∈ T: commit(t) → durable(t)
Translated: ∀t ∈ T: commit(t) → durable(t)
```

### 4. Writing Style

Follow technical writing best practices:

- **Clear**: One concept per sentence
- **Concise**: Remove redundant words
- **Accurate**: Precise technical terminology
- **Consistent**: Maintain terminology consistency

---

## Workflow

### Translation Management Options

| Platform | Pros | Cons | Recommendation |
|----------|------|------|----------------|
| **GitHub + PR** | Full control, free | Manual coordination | ✅ Recommended |
| **Crowdin** | Good UI, TM support | Cost for large projects | Optional |
| **GitLocalize** | Git integration | Limited features | Alternative |

### Recommended Workflow (GitHub-based)

```
┌─────────────────────────────────────────────────────────────┐
│  1. Fork & Branch                                             │
│     └── fork repo → create branch `translation/en/xxx`        │
│                                                               │
│  2. Translate                                                 │
│     └── translate document following guidelines               │
│                                                               │
│  3. Technical Review                                          │
│     └── reviewer checks accuracy & terminology                │
│                                                               │
│  4. Language Review                                           │
│     └── native speaker checks fluency                         │
│                                                               │
│  5. Merge                                                     │
│     └── merge to `main` → deploy to `en/` directory           │
└─────────────────────────────────────────────────────────────┘
```

### Quality Gates

1. **Pre-submission Checklist**:
   - [ ] All technical terms verified
   - [ ] Code blocks unchanged
   - [ ] Links updated to English versions
   - [ ] Glossary terms consistent

2. **Review Requirements**:
   - Minimum 1 technical reviewer (PostgreSQL expertise)
   - Minimum 1 language reviewer (native English)

3. **Automated Checks**:
   - Markdown linting
   - Link validation
   - Terminology consistency scan

---

## File Organization

```
PostgreSQL_Formal/
├── README.md                    # Chinese version (current)
├── README-en.md                 # English version
├── TRANSLATION_STRATEGY.md      # This file
├── TERMINOLOGY.md               # Bilingual glossary
├── CONTRIBUTING-TRANSLATION.md  # Translation guide
│
├── en/                          # English translations
│   ├── README.md
│   ├── 00-Version-Specific/
│   │   └── README.md
│   ├── 01-Theory/
│   ├── 02-Storage/
│   ├── 03-Query/
│   ├── 04-Concurrency/
│   ├── 05-Distributed/
│   ├── 06-FormalMethods/
│   ├── 07-PracticalCases/
│   ├── 08-Performance/
│   ├── 09-Tools/
│   ├── 10-Visualization/
│   ├── 11-Database-Centric-Architecture/
│   └── 99-Archive/
│
├── zh/                          # Chinese original (future)
│   └── (mirror current structure)
│
└── (current Chinese structure preserved)
```

---

## Terminology Management

### Glossary Maintenance

- **Location**: `TERMINOLOGY.md`
- **Format**: Markdown table (Chinese | English | Notes)
- **Updates**: Contribute new terms via PR

### Terminology Workflow

```
New Term Encountered
        ↓
Check TERMINOLOGY.md
        ↓
    ┌───┴───┐
  Exists   New
    ↓        ↓
  Use it   Propose addition
              ↓
           PR to update
           TERMINOLOGY.md
```

---

## Synchronization Strategy

### Handling Source Updates

| Scenario | Action | Frequency |
|----------|--------|-----------|
| Minor fix (typo) | Update translation within 1 week | As needed |
| Content addition | Batch update monthly | Monthly |
| Major restructuring | Re-evaluate translation scope | As needed |

### Version Tracking

Each translated document includes:

```markdown
<!-- Translation Metadata -->
> **Source Version**: v1.2 (2026-03-15)
> **Translated**: 2026-04-01
> **Translator**: @username
> **Reviewer**: @reviewer
```

---

## Progress Tracking

### Phase 1 Progress

| Document | Status | Translator | Reviewer | Completion |
|----------|--------|------------|----------|------------|
| README-en.md | 🚧 In Progress | TBD | TBD | 0% |
| 00-Version-Specific/README-en.md | ⏳ Pending | - | - | 0% |
| PG17/01-VACUUM | ⏳ Pending | - | - | 0% |
| ... | ... | ... | ... | ... |

---

## Resources

### For Translators

- **Style Guide**: Follow Google Technical Writing guidelines
- **PostgreSQL Docs**: <https://www.postgresql.org/docs/>
- **Community**: PostgreSQL mailing lists, Discord

### Reference Materials

- Original Chinese documentation
- PostgreSQL official English documentation
- Academic papers (cited in original documents)

---

## Community

### How to Join

1. Read [CONTRIBUTING-TRANSLATION.md](CONTRIBUTING-TRANSLATION.md)
2. Join discussions in GitHub Issues (label: `translation`)
3. Pick an unassigned document and comment to claim

### Communication Channels

- **GitHub Issues**: Task tracking, questions
- **Discussions**: General translation discussions
- **PR Comments**: Line-specific feedback

---

## License

All translations maintain the same license as the original content.

---

**Document maintained by**: PostgreSQL_Formal Translation Team
**Last reviewed**: 2026-04-07

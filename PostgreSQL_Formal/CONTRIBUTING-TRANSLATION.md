# Translation Contribution Guide

> **Document Status**: 🚧 Draft
> **Version**: v1.0
> **Last Updated**: 2026-04-07

---

## Welcome, Translators

Thank you for your interest in translating PostgreSQL_Formal! This guide will help you get started and ensure high-quality translations that maintain the academic rigor of the original content.

---

## Table of Contents

1. [Getting Started](#getting-started)
2. [Translation Workflow](#translation-workflow)
3. [Quality Requirements](#quality-requirements)
4. [Review Process](#review-process)
5. [Style Guidelines](#style-guidelines)
6. [Tools & Resources](#tools--resources)
7. [FAQ](#faq)

---

## Getting Started

### Prerequisites

Before you begin, please ensure you have:

- **GitHub Account**: For forking and submitting PRs
- **PostgreSQL Knowledge**: Understanding of core PostgreSQL concepts
- **Technical Writing Skills**: Ability to write clear, accurate English prose
- **Time Commitment**: Documents vary from 2,000 to 20,000+ words

### First Steps

1. **Read the Strategy**: Review [TRANSLATION_STRATEGY.md](TRANSLATION_STRATEGY.md)
2. **Check the Glossary**: Familiarize yourself with [TERMINOLOGY.md](TERMINOLOGY.md)
3. **Join the Community**: Watch the repository for translation-related issues
4. **Claim a Document**: Comment on an open translation issue to claim it

### Translation Priority Matrix

| Priority | Documents | Skill Level | Est. Time |
|----------|-----------|-------------|-----------|
| P0 | README, Version Overview | Intermediate | 4-8 hrs |
| P1 | PG17/18 Core (20 docs) | Advanced | 8-16 hrs each |
| P2 | Theory modules | Expert | 16-24 hrs each |
| P3 | Extended modules | Intermediate | 4-12 hrs each |

---

## Translation Workflow

### Step 1: Claim a Document

1. Check the [Translation Tracking Issue](https://github.com/luyatshimbalanga/PostgreSQL_modern/issues) for available documents
2. Comment on the issue with: `"I'd like to translate [document path]"`
3. Wait for maintainer assignment (usually within 24 hours)
4. Create a tracking comment in the format:

   ```markdown
   ## Translation: [Document Name]
   - **Assignee**: @your-username
   - **Status**: 🚧 In Progress
   - **Started**: YYYY-MM-DD
   - **Estimated Completion**: YYYY-MM-DD
   ```

### Step 2: Setup Your Environment

```bash
# Fork and clone the repository
git clone https://github.com/YOUR-USERNAME/PostgreSQL_modern.git
cd PostgreSQL_modern

# Create a feature branch
git checkout -b translation/en/document-name

# Create the directory structure if needed
mkdir -p PostgreSQL_Formal/en/XX-ModuleName
```

### Step 3: Translate

#### Document Structure

Each translated document should include:

```markdown
# Document Title

> **Source**: [Original Chinese Document](./path/to/original.md)
> **Source Version**: v1.2 (2026-03-15)
> **Translated**: YYYY-MM-DD
> **Translator**: @your-username
> **Technical Reviewer**: @reviewer-username
> **Language Reviewer**: @native-speaker-username

---

[Content]

---

## Translation Notes

<!-- Optional: document-specific translation decisions -->
- Term X: Chose translation Y because Z
```

#### Translation Checklist

Before submitting, verify:

- [ ] **Terminology**: All technical terms match [TERMINOLOGY.md](TERMINOLOGY.md)
- [ ] **Code Blocks**: Unchanged from original
- [ ] **Math Formulas**: Unchanged from original
- [ ] **Links**: Updated to point to English versions where available
- [ ] **Images**: References work correctly
- [ ] **Formatting**: Markdown renders correctly
- [ ] **Headers**: Hierarchy preserved
- [ ] **Tables**: Formatting preserved

### Step 4: Self-Review

Use this quality checklist:

| Aspect | Check |
|--------|-------|
| Accuracy | Technical meaning preserved? |
| Completeness | Nothing omitted or added? |
| Fluency | Natural English flow? |
| Consistency | Terms used consistently? |
| Formatting | Markdown structure intact? |

### Step 5: Submit PR

```markdown
## Translation: [Document Title]

**Source**: [link to original Chinese document]
**Word Count**: ~X,XXX words

### Checklist
- [x] Read TRANSLATION_STRATEGY.md
- [x] Checked TERMINOLOGY.md for all technical terms
- [x] Code blocks preserved unchanged
- [x] Math formulas preserved unchanged
- [x] Links updated appropriately
- [x] Self-review completed

### Notes for Reviewers
[Any special considerations or questions]
```

---

## Quality Requirements

### Must-Haves

1. **Technical Accuracy**: Preserve exact technical meaning
2. **Terminology Consistency**: Use glossary terms consistently
3. **Code Integrity**: Never modify code examples
4. **Link Validity**: All internal links must resolve

### Should-Haves

1. **Fluent English**: Natural reading flow
2. **Consistent Style**: Match existing translations
3. **Proper Formatting**: Clean Markdown structure
4. **Complete Coverage**: Translate all content including captions

### Nice-to-Haves

1. **Improved Clarity**: Restructure for better understanding
2. **Additional Context**: Add helpful explanations where needed
3. **Cross-References**: Link to related English documents

### Quality Levels

| Level | Description | Acceptance |
|-------|-------------|------------|
| A+ | Fluent, accurate, well-formatted | Immediate merge |
| A | Accurate, minor language issues | Minor fixes, then merge |
| B | Accurate, needs language polish | Revision requested |
| C | Inaccurate or incomplete | Resubmission required |

---

## Review Process

### Two-Stage Review

```
┌─────────────────────────────────────────────────────────────┐
│  Stage 1: Technical Review                                    │
│  ├── Reviewer: PostgreSQL expert                              │
│  ├── Focus: Technical accuracy, terminology                   │
│  └── Outcome: Approve / Request changes                       │
│                                                               │
│  Stage 2: Language Review                                     │
│  ├── Reviewer: Native English speaker                         │
│  ├── Focus: Fluency, style, clarity                           │
│  └── Outcome: Approve / Request changes                       │
│                                                               │
│  Final: Merge                                                 │
└─────────────────────────────────────────────────────────────┘
```

### Review Timeline

| Stage | Timeframe | Expected Feedback |
|-------|-----------|-------------------|
| Initial Triage | 1-2 days | Assignment confirmation |
| Technical Review | 3-5 days | Technical corrections |
| Language Review | 3-5 days | Language improvements |
| Final Merge | 1-2 days | - |

### Reviewer Guidelines

**For Technical Reviewers**:

- Verify PostgreSQL terminology accuracy
- Check that concepts are correctly conveyed
- Ensure code examples are unchanged
- Validate mathematical formulas

**For Language Reviewers**:

- Check for natural English flow
- Verify consistent style with existing translations
- Suggest improvements for clarity
- Note any awkward phrasing

---

## Style Guidelines

### Writing Style

**Do**:

- Use active voice where appropriate
- Keep sentences clear and direct
- Use parallel structure in lists
- Define acronyms on first use

**Don't**:

- Use overly complex sentence structures
- Translate idioms literally
- Add subjective commentary
- Change technical meanings for flow

### Examples

**Good Translation**:

```markdown
MVCC maintains multiple versions of data to enable concurrent
access without locking. When a transaction modifies a row,
PostgreSQL creates a new version rather than overwriting
the existing data.
```

**Avoid**:

```markdown
MVCC is a very complicated mechanism that uses many versions
of data. It is used for concurrency. When transactions want
to change rows, PostgreSQL makes new versions instead of
changing old ones. This is very good for performance!
```

### Formatting Conventions

**Headers**:

```markdown
# Main Title (H1)
## Section (H2)
### Subsection (H3)
#### Details (H4)
```

**Code Blocks**:

```markdown
```sql
-- Comments in code can remain Chinese
SELECT * FROM table;
```

```

**Tables**:
```markdown
| Column 1 | Column 2 | Column 3 |
|----------|----------|----------|
| Value 1  | Value 2  | Value 3  |
```

---

## Tools & Resources

### Recommended Tools

| Tool | Purpose | Link |
|------|---------|------|
| VS Code | Markdown editing | <https://code.visualstudio.com/> |
| Markdownlint | Markdown linting | VS Code extension |
| Vale | Prose linting | <https://vale.sh/> |
| Grammarly | Grammar checking | <https://grammarly.com/> |

### Reference Resources

- [Google Technical Writing Course](https://developers.google.com/tech-writing)
- [PostgreSQL Official Documentation](https://www.postgresql.org/docs/)
- [Microsoft Writing Style Guide](https://docs.microsoft.com/en-us/style-guide/)

### Internal Resources

- [TRANSLATION_STRATEGY.md](TRANSLATION_STRATEGY.md) - Overall strategy
- [TERMINOLOGY.md](TERMINOLOGY.md) - Bilingual glossary
- [Original Chinese README](README.md) - Reference for tone/style

---

## FAQ

### Q: Can I translate part of a document?

A: We prefer complete document translations to maintain consistency. For very long documents, coordinate with maintainers to split into sections.

### Q: What if I find an error in the original Chinese text?

A: Note it in your PR description. We'll fix the Chinese version first, then you can update your translation.

### Q: How do I handle Chinese-specific concepts without English equivalents?

A: Use the closest English technical term and add a brief explanation. Update TERMINOLOGY.md with your decision.

### Q: Can I use machine translation as a starting point?

A: Machine translation is permitted as a first draft, but you must:

- Thoroughly review and correct all output
- Ensure technical accuracy
- Rewrite for natural flow
- Take full responsibility for the final quality

### Q: How are translators credited?

A: Translators are:

- Listed in the document header metadata
- Added to CONTRIBUTORS.md
- Mentioned in release notes for significant contributions

### Q: What if I need to abandon a translation mid-way?

A: No problem! Just comment on your tracking issue so others can pick it up. Your partial work may still be useful as a starting point.

### Q: Can I suggest changes to the glossary?

A: Absolutely! Propose additions or modifications via PR to TERMINOLOGY.md with rationale.

---

## Code of Conduct

All contributors must adhere to our [Code of Conduct](./CODE_OF_CONDUCT.md). Key points:

- Be respectful and constructive in all interactions
- Accept feedback gracefully
- Help maintain a welcoming environment
- Focus on the content, not the person

---

## Recognition

### Translator Tiers

| Tier | Contribution | Recognition |
|------|--------------|-------------|
| 🥉 Contributor | 1-3 documents | Listed in CONTRIBUTORS.md |
| 🥈 Active Translator | 4-9 documents | Named in release notes |
| 🥇 Core Translator | 10+ documents | Repository collaborator role |

### Hall of Fame

Outstanding translators will be featured in our README and recognized in project communications.

---

## Contact

- **General Questions**: Open a [GitHub Discussion](https://github.com/luyatshimbalanga/PostgreSQL_modern/discussions)
- **Translation Coordination**: Comment on the [Translation Tracking Issue](https://github.com/luyatshimbalanga/PostgreSQL_modern/issues)
- **Private Inquiries**: Email the maintainers (see repository profile)

---

## Quick Reference Card

```
┌─────────────────────────────────────────────────────────────┐
│  TRANSLATION QUICK START                                     │
├─────────────────────────────────────────────────────────────┤
│  1. Read: TRANSLATION_STRATEGY.md                           │
│  2. Check: TERMINOLOGY.md                                    │
│  3. Claim: Comment on tracking issue                         │
│  4. Branch: translation/en/document-name                    │
│  5. Translate: Following this guide                          │
│  6. Review: Use quality checklist                            │
│  7. Submit: PR with template                                 │
└─────────────────────────────────────────────────────────────┘
```

---

**Thank you for helping make PostgreSQL_Formal accessible to the global community!**

*PostgreSQL_Formal Translation Team*

# Knowledge QA Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Deliver project 3 as a runnable, bounded knowledge QA Agent with verifiable citations and offline evidence.

**Architecture:** Local JSON knowledge tools feed a model-selected search/read/finish loop. Live and offline decision providers share one interface. CLI prints answer and Trace.

**Tech Stack:** Python 3.7+ standard library, unittest.

**Spec:** `docs/01-requirements.md`

## Global Constraints

- Cover all six required acceptance scenarios.
- Provide at least three input/output/Trace examples.
- Stop clearly on tool failure and step limit.
- Mark Mock evidence as process-only.

## Review Focus

- Empty question returns a missing-information result.
- Unknown document ID cannot become an answer.
- Fabricated quote cannot become an answer.
- Search with no hits gets one follow-up query.
- Changed document text changes cited answer.

### Task 1: Knowledge tools and loop

**Files:** `data/documents.json`, `src/tools.py`, `src/agent.py`, `tests/test_agent.py`

- [x] Write failing tests for six acceptance paths, citation validation, step limit.
- [x] Run tests and observe missing implementation.
- [x] Implement local search/read and bounded action loop.
- [x] Run tests to green.

### Task 2: Decision providers and CLI

**Files:** `src/models.py`, `src/cli.py`, `.env.example`, `requirements.txt`

- [x] Add live JSON decision adapter and labeled offline policy.
- [x] Add reproducible CLI entry and options.
- [x] Run CLI paths.

### Task 3: Evidence and handoff

**Files:** `examples/*`, `README.md`, `docs/01-requirements.md` through `docs/05-retrospective.md`

- [x] Generate actual inputs, outputs, traces, and test log.
- [x] Document tradeoffs, AI usage, limits and submission gap.
- [x] Verify complete test suite and examples.

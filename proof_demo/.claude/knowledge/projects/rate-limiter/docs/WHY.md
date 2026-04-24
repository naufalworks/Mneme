---
name: rate-limiter-origin
description: Why rate-limiter exists
type: project
created: 2026-04-24T13:47:54.311748
---

# Why rate-limiter Exists

Prevent API abuse

## Created For

This project was created to support `auth-service`.

## Causal Chain

The sequence of events that led to this project:

1. auth had no rate limiting
2. attacks detected
3. rate-limiter created

## How to Apply

When modifying `rate-limiter`, consider:

- Impact on `auth-service` (this project was created for it)
- The original reason for creation: Prevent API abuse
- Whether changes align with the project's purpose

## Metadata

- **Created**: 2026-04-24
- **Crystallized**: 2026-04-24T13:47:54.311767

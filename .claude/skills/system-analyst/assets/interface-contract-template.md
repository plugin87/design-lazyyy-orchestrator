# Interface contract — [boundary name]

| Item | Value |
|---|---|
| Boundary type | HTTP API / storage layer / third-party integration / message queue |
| Consumer | [who calls it] |
| Provider | [who implements it] |
| Version | [v1] |
| Traces to | [requirement IDs] |

---

## 1. Cross-cutting rules

| Element | Value |
|---|---|
| Transport | [HTTPS, TLS ≥ 1.2] |
| Authentication | [scheme; what happens when absent or expired] |
| Content type | [application/json] |
| Client timeout | [seconds] — **and what the client does when it fires** |
| Retry policy | [which status codes, backoff schedule, maximum attempts] |
| Idempotency | [key source — mandatory for any write a client can retry] |
| Rate limit | [limit, window, and the client's backoff behaviour] |
| Clock authority | [server receipt time vs client time, for ordering] |
| Versioning | [how a breaking change ships without breaking old clients] |
| Deprecation | [notice period and how consumers are told] |

The timeout row is the one usually left blank and the case that always occurs.
"No answer" is not the same state as "error response".

## 2. Operations

Repeat per operation.

### 2.1 [Operation name]

**Purpose** — one line.

**Request** `[METHOD] [path]`

| Field | Type | Required | Constraint | Notes |
|---|---|---|---|---|
| | | | | |

```json
{ }
```

**Success response** — `[status code]`

| Field | Type | Always present | Notes |
|---|---|---|---|
| | | | |

```json
{ }
```

**Errors**

| Status | Code | Meaning | Client retries? | Client action |
|---|---|---|---|---|
| 400 | | | No | Quarantine and surface |
| 401 | | | After refresh | Refresh token, then retry once |
| 409 | | | No | Apply the conflict rule (see §3) |
| 429 | | | Yes | Backoff per the Retry-After header |
| 5xx | | | Yes | Backoff, bounded attempts, then queue |
| — | timeout | No response | Yes | Treat as unknown, retry idempotently |

**Idempotency** — key: [field]. Repeating the same key returns [the original
result / 200 with the existing record], never a duplicate.

**Traces to** — [requirement IDs]

## 3. Conflict handling

Applies to any write that two clients can make independently.

| Entity | Strategy | Losing case, stated explicitly |
|---|---|---|
| | last-write-wins by server receipt / append-only / per-field merge / user resolution | |

"We use LWW" is not testable. "If the same item is completed on two devices
while both are offline, the union applies and the earlier timestamp is
retained" is.

## 4. Failure behaviour

| Failure | Client behaviour | User-visible? | Data outcome |
|---|---|---|---|
| Provider unreachable | | | |
| Partial batch applied | | | |
| Payload too large | | | |
| Auth expired mid-sync | | | |
| Provider returns malformed data | | | |

## 5. Data contract stability

| Field | May change without a version bump? |
|---|---|
| | Adding optional fields: yes. Removing, renaming, retyping, or changing meaning: no |

## 6. Test hooks

How this boundary is exercised without the real provider: [fake / recorded
fixtures / contract tests]. Anything that can only be tested against
production is a design defect.

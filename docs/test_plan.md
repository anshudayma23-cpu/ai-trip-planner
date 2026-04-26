# AI Travel Planner — Test Plan & Edge Cases

> **Version:** 1.0  
> **Date:** April 25, 2026  
> **Run these tests after completing each sub-phase before moving to the next.**

---

## Testing Strategy

After each sub-phase, run the corresponding test section below. Each section contains:
- **Unit Tests** — isolated function-level checks
- **Edge Cases** — unusual inputs that break naive implementations
- **Integration Checks** — verify the component works within the graph

> **Rule:** Do NOT proceed to the next sub-phase until all tests in the current section pass.

---

## Sub-Phase 1A — Project Scaffolding & Config

### Unit Tests

| # | Test | Command | Expected |
|---|------|---------|----------|
| 1 | Dependencies install | `pip install -r requirements.txt` | Exit code 0, no errors |
| 2 | Config loads with valid `.env` | `python -c "from src.config import settings; print(settings)"` | Prints config dict |
| 3 | Config fails without `.env` | Delete `.env`, run config import | Raises clear error with missing key name |

### Edge Cases

| # | Scenario | Input | Expected Behavior |
|---|----------|-------|-------------------|
| 1 | Missing `.env` file | No `.env` exists | Raise `FileNotFoundError` or `ValueError` with message: "Create .env from .env.example" |
| 2 | Partial `.env` | Only `GOOGLE_API_KEY` set, `TAVILY_API_KEY` missing | Raise error naming the missing key |
| 3 | Empty API key | `GOOGLE_API_KEY=""` | Raise error: "GOOGLE_API_KEY cannot be empty" |
| 4 | Extra whitespace in key | `OPENAI_API_KEY= sk-abc ` | Strip whitespace, load correctly |

---

## Sub-Phase 1B — Graph State & Skeleton

### Unit Tests

| # | Test | Expected |
|---|------|----------|
| 1 | `AgentState` can be instantiated with all fields | No TypedDict errors |
| 2 | `TravelConstraints` accepts valid data | All fields populate correctly |
| 3 | Graph compiles without errors | `workflow.compile()` returns a runnable graph |
| 4 | Graph runs with minimal state | `graph.invoke({"user_request": "test", "revision_count": 0, "status": "init"})` returns state unchanged |
| 5 | All 6 placeholder nodes execute | Status field passes through all nodes |

### Edge Cases

| # | Scenario | Input | Expected Behavior |
|---|----------|-------|-------------------|
| 1 | Empty `user_request` | `""` | Graph still runs (orchestrator handles in 1C) |
| 2 | Missing optional fields | State without `constraints`, `research_notes` | Placeholders handle `None` / empty lists gracefully |
| 3 | Extra unknown fields in state | `{"user_request": "test", "unknown_field": 123}` | Graph ignores extra fields, no crash |

---

## Sub-Phase 1C — Orchestrator Agent (Intent Parser)

### Unit Tests

| # | Test | Input | Expected Output |
|---|------|-------|-----------------|
| 1 | Standard request | `"Plan a 5-day trip to Japan. Tokyo + Kyoto. $3,000 budget. Love food and temples, hate crowds."` | `{"destination_country": "Japan", "cities": ["Tokyo", "Kyoto"], "duration_days": 5, "budget_usd": 3000, "preferences": ["food", "temples"], "avoidances": ["crowds"]}` |
| 2 | Single city | `"3 days in Paris, $1500, love art"` | `cities: ["Paris"]`, `preferences: ["art"]` |
| 3 | No explicit budget | `"5 days in Italy, Rome and Florence, love history"` | Should infer a reasonable default budget (e.g., $2000–$5000) |
| 4 | No avoidances | `"4 days Tokyo, $2000, love anime and food"` | `avoidances: []` (empty, not null) |
| 5 | Multiple avoidances | `"...hate crowds, long walks, and spicy food"` | `avoidances: ["crowds", "long walks", "spicy food"]` |

### Edge Cases

| # | Scenario | Input | Expected Behavior |
|---|----------|-------|-------------------|
| 1 | Gibberish input | `"asdfghjkl 12345"` | Return error state or sensible fallback, NOT crash |
| 2 | Non-English input | `"日本に5日間旅行を計画して"` | Attempt to parse; if unable, set `error` in state |
| 3 | Very long input | 2000+ character travel essay | Parse correctly without truncation issues |
| 4 | Conflicting constraints | `"1-day trip to 10 cities"` | Parse as-is; Review Agent catches in Phase 3 |
| 5 | No destination | `"Plan a vacation for $500"` | Infer or set `error`: "No destination specified" |
| 6 | Zero/negative budget | `"Trip to Japan, $0 budget"` | Parse `budget_usd: 0`; Budget Agent handles in Phase 3 |
| 7 | Ambiguous cities | `"Visit Paris, Texas"` | Parse `cities: ["Paris"]`, `destination_country: "USA"` or `"France"` (either is acceptable if consistent) |
| 8 | Budget in different currency | `"5 days Japan, ¥300,000 budget"` | Convert to USD or flag for Budget Agent |

### Integration Check
```bash
# Run the full graph — only orchestrator is real, rest are placeholders
python -m src.main "Plan a 5-day trip to Japan. Tokyo + Kyoto. $3,000 budget."
# Verify: constraints are populated, status updated, no crash
```

---

## Sub-Phase 2A — Search Tool Integration

### Unit Tests

| # | Test | Input | Expected |
|---|------|-------|----------|
| 1 | Basic search works | `"best temples in Kyoto"` | Returns list of 3–5 text snippets |
| 2 | Results are strings | Any query | Each item in list is `str`, not dict |
| 3 | Empty query | `""` | Returns empty list, no crash |

### Edge Cases

| # | Scenario | Input | Expected Behavior |
|---|----------|-------|-------------------|
| 1 | Invalid API key | `TAVILY_API_KEY="invalid"` | Raise clear auth error, not generic 500 |
| 2 | Network timeout | Simulate slow network | Return empty list after timeout, log warning |
| 3 | Rate limit hit | Rapid-fire 50 queries | Graceful backoff or queued retry |
| 4 | Non-English query | `"京都の寺院"` | Returns results (possibly English), no crash |
| 5 | Very long query | 500+ char query string | Truncate or handle; return results |

---

## Sub-Phase 2B — Destination Research Agent

### Unit Tests

| # | Test | Input Constraints | Expected |
|---|------|-------------------|----------|
| 1 | Japan food+temples | `cities: ["Tokyo","Kyoto"], prefs: ["food","temples"]` | Notes mention specific temples AND food spots |
| 2 | Paris art+cafes | `cities: ["Paris"], prefs: ["art","cafes"]` | Notes mention museums (Louvre, etc.) AND cafe areas |
| 3 | Crowd avoidance | `avoidances: ["crowds"]` | At least 1 note includes timing tips (e.g., "go early") |
| 4 | Query count | 2 cities × 2 prefs + 2 cities × 1 avoidance | Exactly 6 search queries generated |

### Edge Cases

| # | Scenario | Input | Expected Behavior |
|---|----------|-------|-------------------|
| 1 | Unknown city | `cities: ["Xyzville"]` | Search returns sparse results; agent returns what it finds, no crash |
| 2 | No preferences | `preferences: []` | Agent generates generic "top things to do in {city}" queries |
| 3 | Many cities (5+) | `cities: ["Tokyo","Kyoto","Osaka","Nara","Hiroshima"]` | All cities get research notes (may be shorter per city) |
| 4 | Contradictory preferences | `preferences: ["nightlife"], avoidances: ["crowds"]` | Agent notes the tension; suggests off-peak nightlife |
| 5 | Search tool returns empty | All Tavily calls fail | Agent returns partial notes from LLM knowledge, sets warning |

### Integration Check
```bash
# Run: Orchestrator → Research → (placeholders)
# Verify: research_notes populated with relevant content
python -m src.main "3 days in Paris, $1500, love museums"
```

---

## Sub-Phase 2C — Logistics Agent

### Unit Tests

| # | Test | Input | Expected |
|---|------|-------|----------|
| 1 | Night allocation | 5 days, 2 cities | 2–3 nights per city, total = duration - 1 (or duration) |
| 2 | Day count matches | `duration_days: 5` | Exactly 5 `DayPlan` entries |
| 3 | All cities present | `cities: ["Tokyo","Kyoto"]` | Both appear in daily_plans |
| 4 | Day structure complete | Any input | Every day has non-empty morning, afternoon, evening |
| 5 | Intercity transport exists | 2+ cities | At least 1 transport entry |
| 6 | Costs are positive | Any input | All `estimated_cost_usd` values > 0 |

### Edge Cases

| # | Scenario | Input | Expected Behavior |
|---|----------|-------|-------------------|
| 1 | Single city, no transport | `cities: ["Tokyo"], duration: 3` | No intercity_transport, 3 day plans in Tokyo |
| 2 | 1-day trip | `duration_days: 1, cities: ["Tokyo"]` | Exactly 1 day plan, 0 nights accommodation |
| 3 | Many cities, few days | `cities: ["A","B","C","D"], duration: 3` | Agent prioritizes top cities or suggests reducing |
| 4 | Very long trip | `duration_days: 30, cities: ["Tokyo"]` | 30 unique day plans (content may repeat, but structure valid) |
| 5 | No research notes available | `research_notes: []` | Agent uses LLM knowledge to fill, sets warning |
| 6 | Research notes are vague | Notes like "Tokyo is nice" | Agent still produces structured plan from LLM knowledge |

### Integration Check
```bash
# Run: Orchestrator → Research → Logistics → (placeholders)
# Verify: daily_plans has correct day count, accommodation splits make sense
python -m src.main "5 days Japan, Tokyo + Kyoto, $3000, food and temples"
```

---

## Sub-Phase 2D — Wire Research + Logistics into Graph

### Integration Tests (3 different requests)

| # | Request | Verify |
|---|---------|--------|
| 1 | `"5-day Japan, Tokyo + Kyoto, $3000, food + temples, avoid crowds"` | 5 days, both cities, food/temple mentions |
| 2 | `"3-day Paris, $1500, museums and cafes"` | 3 days, Paris only, museum mentions |
| 3 | `"7-day Thailand, Bangkok + Chiang Mai, $2000, beaches + street food"` | 7 days, both cities, beach/food mentions |

### Edge Cases

| # | Scenario | Expected |
|---|----------|----------|
| 1 | Run same request twice | Both runs produce valid output (no stale state) |
| 2 | Run requests back-to-back | No state leakage between invocations |
| 3 | Research agent returns very long notes | Logistics agent handles large context without truncation |

---

## Sub-Phase 3A — Budget Agent

### Unit Tests

| # | Test | Input | Expected |
|---|------|-------|----------|
| 1 | Correct total | Accommodation=$620, Transport=$240, Activities=$200 | `estimated_spend = sum of all categories` |
| 2 | Green status | spend=$2650, budget=$3000 | `status: "green"` |
| 3 | Yellow status | spend=$2800, budget=$3000 | `status: "yellow"`, has warnings |
| 4 | Red status | spend=$3500, budget=$3000 | `status: "red"`, has savings suggestions |
| 5 | Category breakdown | Any input | Breakdown has: accommodation, transport, food, activities |
| 6 | Currency conversion | JPY input | Correctly converts to USD |

### Edge Cases

| # | Scenario | Input | Expected Behavior |
|---|----------|-------|-------------------|
| 1 | Zero budget | `budget_usd: 0` | Status "red", suggest free activities |
| 2 | Very high budget | `budget_usd: 100000` | Status "green", large buffer noted |
| 3 | Missing cost data | Some activities have no cost estimate | Agent estimates or flags as unknown |
| 4 | All costs are zero | Every activity cost = 0 | Status "green", but flag as suspicious |
| 5 | Negative costs | An activity has `cost: -50` | Treat as 0 or flag data error |
| 6 | Currency not in rate table | `from_currency: "XYZ"` | Fallback to 1.0 rate with warning |

### Integration Check
```bash
# Run: Orchestrator → Research → Logistics → Budget → (placeholder review) → END
# Verify: budget_report populated with valid breakdown
python -m src.main "5 days Japan, $3000"
```

---

## Sub-Phase 3B — Review Agent (QA Checklist)

### Unit Tests

| # | Test | Setup | Expected Verdict |
|---|------|-------|------------------|
| 1 | Perfect plan | 5 days, both cities, budget green, preferences met | **PASS**, score ≥ 90 |
| 2 | Missing city | 5 days but only Tokyo (Kyoto missing) | **FAIL**, `failed_checks: ["cities_covered"]` |
| 3 | Wrong day count | 4 daily_plans for a 5-day trip | **FAIL**, `failed_checks: ["duration_fit"]` |
| 4 | Over budget | budget status = "red" | **FAIL**, `failed_checks: ["budget_ok"]` |
| 5 | No food activities | Preferences = ["food"] but no food in plan | **FAIL**, `failed_checks: ["preferences_met"]` |
| 6 | Incomplete day | Day 3 missing evening activity | **FAIL**, `failed_checks: ["completeness"]` |
| 7 | Crowded plan | Avoidance = "crowds", plan has peak-hour crowded spots | **FAIL**, `failed_checks: ["avoidances_respected"]` |

### Edge Cases

| # | Scenario | Input | Expected Behavior |
|---|----------|-------|-------------------|
| 1 | All checks fail | Every constraint violated | Returns all 7 in `failed_checks`, score near 0 |
| 2 | Budget exactly at limit | spend == budget (100%) | PASS (yellow zone is still passing) |
| 3 | Preferences partially met | 50% match (below 60% threshold) | FAIL on preferences_met |
| 4 | Preferences fully met | 100% match | PASS, score boost |
| 5 | Empty daily_plans | `daily_plans: []` | FAIL on duration_fit, completeness |
| 6 | Null budget report | `budget_report: None` | FAIL on budget_ok (treat missing as failed) |

---

## Sub-Phase 3C — Feedback Loop & Synthesizer

### Unit Tests

| # | Test | Setup | Expected |
|---|------|-------|----------|
| 1 | PASS routes to synthesizer | `qa_result.verdict = "PASS"` | Router returns `"synthesizer"` |
| 2 | Budget fail routes to budget | `failed_checks: ["budget_ok"]` | Router returns `"budget"` |
| 3 | Duration fail routes to logistics | `failed_checks: ["duration_fit"]` | Router returns `"logistics"` |
| 4 | Preference fail routes to research | `failed_checks: ["preferences_met"]` | Router returns `"research"` |
| 5 | Max revisions forces synthesizer | `revision_count: 3` | Router returns `"synthesizer"` regardless of verdict |
| 6 | Revision counter increments | After each loop | `revision_count` increases by 1 |

### Edge Cases

| # | Scenario | Setup | Expected Behavior |
|---|----------|-------|-------------------|
| 1 | Infinite loop prevention | QA always fails | Stops after 3 revisions, returns best-effort itinerary |
| 2 | Multiple failures at once | `failed_checks: ["budget_ok", "duration_fit"]` | Routes to highest-priority fix (budget first) |
| 3 | Fix introduces new failure | Budget fix causes logistics failure | Next loop catches and fixes logistics |
| 4 | Synthesizer with incomplete data | Some state fields still `None` | Produces partial itinerary with "N/A" sections, no crash |
| 5 | Synthesizer output format | Valid complete state | Returns markdown-formatted, human-readable itinerary |

### Integration Tests (End-to-End)

| # | Request | Special Condition | Verify |
|---|---------|-------------------|--------|
| 1 | `"5 days Japan, $3000, food+temples"` | Normal | PASS on first review, clean itinerary |
| 2 | `"5 days Japan, $500, luxury hotels"` | Impossible budget | Feedback loop triggers, final plan has budget adjustments |
| 3 | `"1 day, 5 cities, $100"` | Unrealistic | Handles gracefully, reduces scope or flags |
| 4 | `"10 days Bali, $5000, surfing"` | Single city, long trip | 10 unique day plans, no city-coverage issues |
| 5 | `"3 days Europe, Paris+Rome+London"` | Many cities, few days | Logistics optimizes or suggests reducing cities |

---

## Sub-Phase 4A — FastAPI Backend

### Unit Tests

| # | Test | Action | Expected |
|---|------|--------|----------|
| 1 | Server starts | `uvicorn src.api.routes:app` | No errors, listening on port |
| 2 | POST `/api/plan` | Valid JSON body | Returns 202 with `session_id` |
| 3 | POST `/api/plan` invalid body | `{}` or missing `query` | Returns 422 validation error |
| 4 | GET `/api/plan/{id}` found | Valid session ID | Returns itinerary or processing status |
| 5 | GET `/api/plan/{id}` not found | Random UUID | Returns 404 |
| 6 | GET `/api/plan/{id}/status` | During processing | Returns `"processing"` with current agent name |
| 7 | WebSocket connects | `/ws/plan/{id}` | Connection established, receives messages |

### Edge Cases

| # | Scenario | Input | Expected Behavior |
|---|----------|-------|-------------------|
| 1 | Concurrent requests | 5 simultaneous POST requests | All get unique session IDs, all process correctly |
| 2 | Very long query | 5000-char request body | Accepted (or 413 if limit enforced) |
| 3 | Empty query string | `{"query": ""}` | Returns 400 with "Query cannot be empty" |
| 4 | Special characters in query | `{"query": "<script>alert('xss')</script>"}` | Sanitized, no injection |
| 5 | WebSocket to unknown session | `/ws/plan/nonexistent-id` | Close connection with error message |
| 6 | Pipeline crash mid-execution | LLM key invalid during run | Status becomes "failed" with error message |
| 7 | Poll before completion | GET status immediately after POST | Returns "processing", not 500 |

---

## Sub-Phase 4B — Frontend UI

### Visual Tests (Manual)

| # | Test | Action | Expected |
|---|------|--------|----------|
| 1 | Page loads | Open `index.html` | Dark theme renders, input card visible |
| 2 | Submit request | Type and click submit | Loading animation starts, stepper activates |
| 3 | Agent progress | Watch stepper during processing | Steps light up sequentially: Parsing → Researching → ... |
| 4 | Itinerary renders | Wait for completion | Day cards appear with timeline layout |
| 5 | Budget display | Check budget section | Donut/bar chart with category breakdown |
| 6 | QA badge | Check score badge | Green/yellow/red pill with score number |
| 7 | Mobile responsive | Resize to 375px width | Layout stacks vertically, no overflow |
| 8 | Empty state | Page load before any request | Shows hero section, no broken UI |

### Edge Cases

| # | Scenario | Expected Behavior |
|---|----------|-------------------|
| 1 | Server offline | Display "Unable to connect" error, not blank page |
| 2 | WebSocket disconnects mid-stream | Show partial progress + "Connection lost" message |
| 3 | Very long itinerary (30 days) | Scrollable, no layout breakage |
| 4 | Special characters in itinerary | `"Café René"`, `"¥3000"` | Renders correctly, no encoding issues |
| 5 | Double-click submit | Prevents duplicate submissions (disable button) |
| 6 | Browser back/forward | State preserved or gracefully reset |

---

## Sub-Phase 4C — Integration, Polish & Deployment

### Smoke Tests

| # | Test | Action | Expected |
|---|------|--------|----------|
| 1 | Full E2E: input to display | Submit request from UI → see itinerary | Complete flow works under 60 seconds |
| 2 | Docker build | `docker build -t trip-planner .` | Build succeeds |
| 3 | Docker run | `docker run -p 8000:8000 trip-planner` | App accessible at `localhost:8000` |
| 4 | Cached response | Submit same request twice | Second response is instant (cached) |
| 5 | LLM fallback | Invalidate Gemini API key | Falls back to Groq (Llama 3) |

### Edge Cases

| # | Scenario | Expected Behavior |
|---|----------|-------------------|
| 1 | All LLM providers down | Returns "Service temporarily unavailable" with retry suggestion |
| 2 | Redis/cache unavailable | Falls through to live execution, no crash |
| 3 | Disk full (Docker) | Container logs error, doesn't corrupt state |
| 4 | Simultaneous users (10+) | All get results, no race conditions |
| 5 | `.env` missing in Docker | Container exits with clear error message |

---

## Test Execution Checklist

Use this checklist to track progress across sub-phases:

| Sub-Phase | Unit Tests | Edge Cases | Integration | Status |
|-----------|:----------:|:----------:|:-----------:|:------:|
| 1A | ☐ 3/3 | ☐ 4/4 | — | ☐ |
| 1B | ☐ 5/5 | ☐ 3/3 | — | ☐ |
| 1C | ☐ 5/5 | ☐ 8/8 | ☐ 1/1 | ☐ |
| 2A | ☐ 3/3 | ☐ 5/5 | — | ☐ |
| 2B | ☐ 4/4 | ☐ 5/5 | ☐ 1/1 | ☐ |
| 2C | ☐ 6/6 | ☐ 6/6 | ☐ 1/1 | ☐ |
| 2D | ☐ 3/3 | ☐ 3/3 | — | ☐ |
| 3A | ☐ 6/6 | ☐ 6/6 | ☐ 1/1 | ☐ |
| 3B | ☐ 7/7 | ☐ 6/6 | — | ☐ |
| 3C | ☐ 6/6 | ☐ 5/5 | ☐ 5/5 | ☐ |
| 4A | ☐ 7/7 | ☐ 7/7 | — | ☐ |
| 4B | ☐ 8/8 | ☐ 6/6 | — | ☐ |
| 4C | ☐ 5/5 | ☐ 5/5 | — | ☐ |

# AI Travel Planner — Agent Interaction Diagrams

This document visualizes how the 5 agents interact and share information through the LangGraph state machine.

## 1. System Workflow (Flowchart)
This diagram shows the path a travel request takes through the specialized agents.

```mermaid
graph TD
    User([User Request]) --> ORC[Orchestrator Agent]
    
    subgraph "Planning Loop"
        ORC -->|Parsed Constraints| RES[Research Agent]
        RES -->|Attractions & Food| LOG[Logistics Agent]
        LOG -->|Daily Schedule| BUD[Budget Agent]
        BUD -->|Cost Validation| REV[Review Agent]
    end

    REV -->|Feedback: Failed QA| LOG
    REV -->|Feedback: Over Budget| BUD
    REV -->|Feedback: Missing Info| RES
    
    REV -->|Passed QA| SYN[Synthesizer]
    SYN --> Final([Final Itinerary])

    style ORC fill:#f9f,stroke:#333,stroke-width:2px
    style REV fill:#ff9,stroke:#333,stroke-width:2px
    style Final fill:#9f9,stroke:#333,stroke-width:4px
```

---

## 2. Shared State Concept
All agents read from and write to a single **Shared State Object**. Think of it as a shared document that grows as the agents work.

```mermaid
classDiagram
    class AgentState {
        +String user_request
        +Dict constraints
        +List research_notes
        +List daily_plans
        +Dict budget_report
        +Dict qa_feedback
        +Int revision_count
        +String status
    }
    
    AgentState <|-- Orchestrator : Writes Constraints
    AgentState <|-- Research : Writes Notes
    AgentState <|-- Logistics : Writes Plans
    AgentState <|-- Budget : Writes Costs
    AgentState <|-- Review : Writes Feedback
```

---

## 3. The "Review -> Fix" Feedback Loop (Sequence)
This shows how the Review Agent forces other agents to self-correct until the plan is perfect.

```mermaid
sequenceDiagram
    participant O as Orchestrator
    participant L as Logistics
    participant B as Budget
    participant R as Reviewer
    
    O->>L: Here is the research, build a plan.
    L->>B: Here is the plan, check costs.
    B->>R: Here is the total cost ($3,500).
    Note over R: Reviewer checks against<br/>User Budget ($3,000)
    R-->>B: FAIL: Over budget by $500!
    B->>L: Need cheaper hotels in Tokyo.
    L->>B: Plan updated with hostels.
    B->>R: New total: $2,850.
    R-->>O: PASS: Plan is ready.
```

---

## 4. Hub-and-Spoke Communication (State-Centric)
This diagram highlights that agents don't talk directly; they all interact with the **Central State Hub**.

```mermaid
graph LR
    subgraph "LangGraph State Hub"
        STATE[(Shared AgentState)]
    end

    ORC[Orchestrator] <-->|Writes Constraints| STATE
    RES[Research] <-->|Appends Notes| STATE
    LOG[Logistics] <-->|Writes Schedule| STATE
    BUD[Budget] <-->|Checks Costs| STATE
    REV[Review] <-->|Checks Everything| STATE

    style STATE fill:#f1f5f9,stroke:#64748b,stroke-width:4px
    style ORC fill:#e0f2fe,stroke:#0ea5e9
    style RES fill:#f0fdf4,stroke:#22c55e
    style LOG fill:#fefce8,stroke:#eab308
    style BUD fill:#fff1f2,stroke:#f43f5e
    style REV fill:#faf5ff,stroke:#a855f7
```


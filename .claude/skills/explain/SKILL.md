---
name: explain
description: Explain code or files using real-world analogies and ASCII diagrams. Use when user asks to explain, understand, or visualize code.
argument-hint: [file-or-topic]
allowed-tools: Read, Glob, Grep
---

# Explain Code with Analogies and Diagrams

Explain the code or concept specified in `$ARGUMENTS` using:

1. **Real-world analogies** that make complex concepts intuitive
2. **ASCII diagrams** that visualize the structure and flow

## Process

### Step 1: Understand the Code
- Read the specified file(s) or explore the relevant code
- Identify the core purpose, components, and relationships
- Note any complex patterns or architectures

### Step 2: Create a Real-World Analogy
- Find a relatable real-world scenario that mirrors the code's behavior
- Map each code component to something tangible (e.g., a restaurant, factory, library)
- Explain how data flows like physical objects in the analogy

**Example analogies:**
- API Gateway → Restaurant host (routes customers to tables)
- Load Balancer → Traffic cop (directs cars to open lanes)
- Cache → Sticky notes on your desk (quick access to frequent info)
- Queue → Line at a coffee shop (first come, first served)
- Database → Filing cabinet (organized storage and retrieval)
- Middleware → Security checkpoint (inspects everything passing through)

### Step 3: Draw ASCII Diagrams
Create clear ASCII art showing:
- Component relationships
- Data flow direction (use arrows: →, ←, ↓, ↑)
- Boundaries and layers (use boxes: ┌─┐ │ └─┘)
- Interactions between parts

**Diagram styles to use:**

**Flow diagram:**
```
┌─────────┐     ┌─────────┐     ┌─────────┐
│  Input  │────▶│ Process │────▶│ Output  │
└─────────┘     └─────────┘     └─────────┘
```

**Layered architecture:**
```
┌─────────────────────────────────┐
│         Presentation            │
├─────────────────────────────────┤
│         Business Logic          │
├─────────────────────────────────┤
│         Data Access             │
└─────────────────────────────────┘
```

**Component interaction:**
```
    ┌───────────┐
    │  Client   │
    └─────┬─────┘
          │ request
          ▼
    ┌───────────┐
    │  Server   │◀────┐
    └─────┬─────┘     │
          │           │ cache hit
          ▼           │
    ┌───────────┐     │
    │  Database │─────┘
    └───────────┘
```

### Step 4: Explain Step-by-Step
Walk through the code flow using both the analogy and diagram:
1. Start with the entry point
2. Explain each step in plain English
3. Reference both the analogy and the diagram
4. Highlight key decision points or branches

## Output Format

Structure your explanation as:

```
## Overview
[One sentence summary]

## The Analogy: [Analogy Name]
[2-3 paragraph explanation using the real-world comparison]

## Architecture Diagram
[ASCII diagram]

## How It Works
[Step-by-step walkthrough referencing the analogy]

## Key Components
| Component | Purpose | Analogy |
|-----------|---------|---------|
| ...       | ...     | ...     |

## Summary
[Key takeaways in bullet points]
```

## Tips
- Use simple, everyday analogies (kitchen, library, postal service, etc.)
- Keep diagrams clean and readable (max 80 chars wide)
- Explain technical terms when first introduced
- Connect abstract concepts to concrete actions

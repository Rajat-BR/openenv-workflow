# FlowForge: Evaluating AI Agents in Real-World Workflows

FlowForge is a system for evaluating whether AI agents can reliably execute multi-step real-world tasks using tools.

As AI evolves from simple chat interfaces to action-based agents—such as booking flights, scheduling meetings, and updating databases—it becomes critical to verify not just what the AI says, but what it actually does.

FlowForge focuses on measuring the **correctness and reliability of AI actions**.

---

## Core Methodology

The system evaluates an AI agent through the following process:

1. **Task Assignment**  
   The AI is given a real-world objective.

2. **Tool Selection**  
   The AI selects the required APIs (tools) and determines the execution order.

3. **Execution**  
   FlowForge executes the selected tools.

4. **Verification**  
   The system checks whether:
   - the correct tools were used  
   - the order was correct  
   - the inputs were accurate  

5. **Scoring**  
   The AI receives a score based on performance.

---

## Technical Components: APIs as Tools

In FlowForge, APIs act as tools that the AI must use to complete tasks:

| API           | Function                      |
|---------------|-------------------------------|
| flight_api    | Books airline travel          |
| calendar_api  | Schedules meetings            |
| email_api     | Sends communications          |
| database_api  | Stores structured information |

---

## Task Complexity Levels

AI agents are evaluated across different levels of complexity:

- **Easy**: Single-step tasks  
  (e.g., scheduling a meeting)

- **Medium**: Multi-step tasks  
  (e.g., booking a flight and sending an email)

- **Hard**: Full workflows  
  (e.g., book flight → schedule meeting → store data → send email)

---

## Scoring & Evaluation Criteria

Performance is graded between **0 and 1** based on:

- **Tool Selection** — correct APIs used  
- **Logical Sequencing** — correct order of execution  
- **Data Accuracy** — correct parameters provided  
- **Efficiency** — no unnecessary or incorrect steps  

---

## Example Scenario

**Task:** Schedule a meeting and send an email  

- **1.0 (Perfect):**  
  `calendar_api → email_api`  

- **Partial Credit:**  
  correct tools but wrong order  

- **Low Score:**  
  missing steps or incorrect tools  

---

## Key Insight

When tested with real AI models, we observed that agents often:
- add unnecessary steps  
- use incorrect tools  
- break logical ordering  

FlowForge is designed to detect and penalize these behaviors, ensuring that only correct and efficient workflows receive full scores.

---

## Running the Project

### Option 1: Run with Docker (Recommended)

```bash
docker build -t flowforge .
docker run flowforge
```

---

### Option 2: Run Locally (Optional)

```bash
pip install -r requirements.txt
python inference.py
```
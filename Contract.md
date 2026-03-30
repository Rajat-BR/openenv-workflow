# 📜 OpenEnv Workflow Contract

This file defines the strict interface rules for all components.

All team members MUST follow this. 

---

## 🔧 APIs (Allowed)

Only these APIs are allowed:

- flight_api
- calendar_api
- email_api
- database_api

---

## 📥 API Parameters (STRICT)

Each API must receive EXACT parameters:

- flight_api:
  - from_city (str)
  - to_city (str)

- calendar_api:
  - date (str)
  - time (str)

- email_api:
  - to (str)

- database_api:
  - data (str)

---

## 🔗 System Flow

User Input
→ Inference (generate workflow)
→ Environment (execute APIs)
→ Grader (compare with expected)
→ Score

---

## 🚨 Critical Rules

- API names MUST NOT change
- Parameter names MUST NOT change
- Workflow format MUST remain consistent
- All modules must follow this contract

---

## 🧪 Validation Expectations

System must:
- Not crash on invalid input
- Return score = 0 for garbage input
- Give partial scores for partial correctness
- Be deterministic (same input → same output)


---

End of Contract
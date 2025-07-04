# 🛒 Shop Agent: Context-Aware Multi-Agent Product Recommender (CrewAI)

This project implements a **multi-agent AI system** using the [CrewAI](https://github.com/joaomdmoura/crewAI) framework to assist users in making optimized shopping decisions on Indian e-commerce platforms. The system comprises two specialized agents: one for precise product discovery and another for comparative decision-making based on multi-factor scoring.

---

## 📌 Project Overview

### 🔹 Agents

#### 🕵️‍♂️ item_find Agent – *"{target_item} Parametric Hunter"*
- **Goal**: Find products that best match user-defined specifications from `{item_details}`.
- **Priority Criteria**:
  1. ≥90% attribute match
  2. Availability guarantees
  3. Verified buyer media
- **Backstory**: Built upon Zalando's precision search infrastructure with advanced fuzzy matching algorithms.

#### ⚖️ compare_agent – *"{target_item} Decision Optimizer"*
- **Goal**: Analyze and rank items from the item_find agent using a weighted scoring system.
- **Scoring Factors**:
  - 40% feature compliance
  - 30% cost (price + shipping)
  - 20% delivery reliability
  - 10% review authenticity
- **Backstory**: Powered Consumer Reports' decision guides with a “Triple-Layer Filter” system.

---

## 📂 Tasks

### 🔍 `item_find_task`
- **Description**: Search Indian e-commerce sites for `{target_item}` using `{item_details}`.
- **Agent**: `item_find`
- **Expected Output**: A JSON list of matched products (price, link, etc.)  
- **Output File**: `output/results.json`

### 📊 `item_compare_task`
- **Description**: Compare search results and generate decision insights.
- **Agent**: `compare_agent`
- **Expected Output**:
  - Best Value
  - Fastest Solution
  - Premium Choice
  - Comparison Matrix
  - Fraud Risk Indicators  
- **Output File**: `output/final_decision.md`

---

## ⚙️ Tech Stack

- [CrewAI](https://github.com/joaomdmoura/crewAI)
- Python 3.10+
- Open-source LLM (e.g., OpenHermes, Llama2)
- JSON/Markdown outputs
- Local runtime (configurable for remote hosting)

---

## ▶️ How to Run

1. **Clone the Repository**
   ```bash
   git clone https://github.com/your-username/shop-agent-crewai.git
   cd shop-agent-crewai
   ```

2. **Update `.env` File**

   Create or edit the `.env` file and add your compatible API keys:

   ```
   GEMINI_API_KEY=your_api_key_here
   ```

3. **Run the Agent Workflow**

   Make sure you're in the correct folder and your environment is activated (if applicable), then run:

   ```bash
   crewai run
   ```

   This will execute the two-agent system to find and evaluate the best products.

---

## 📁 Output Files

- `output/results.json`: Raw search results from `item_find_agent`
- `output/final_decision.md`: Structured decision report from `compare_agent`

---

## 🚀 Future Work

- Add **context-passing mechanisms** like shared memory, agent history logs, and vector store-based context recall.
- Introduce more agents such as:
  - **Budget Agent** for lowest-cost suggestions
  - **Fraud Detection Agent** for seller validation
  - **User Feedback Agent** to adapt based on preferences
- Enable **dynamic goal switching** and **multi-agent memory tracing**

---
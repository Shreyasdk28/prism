# Smart Shopping Assistant

This project implements a smart shopping assistant using **crewAI** to help users find products based on their preferences, compare items, and manage long-term shopping memories.

---

## 🛠️ Features

### 1. Intelligent Product Search  
Find products based on detailed user descriptions  
(e.g., *"wireless earbuds, black, budget around $100, with noise cancellation"*).

### 2. Preference Extraction  
Automatically parse user inputs to extract:
- **Budget**
- **Color**
- **Features**

### 3. Memory Management  
- **Short‑term memory**: Stores recent session data.  
- **Long‑term memory**: Saves and retrieves user preferences for specific product categories.  
- **Episodic Memory (via Qdrant)**: Stores each shopping "episode" for historical context and future analysis.

### 4. Agent‑Based Architecture  
Leverages crewAI to orchestrate specialized agents:
| Agent                   | Responsibility |
|-------------------------|----------------|
| Memory Query Agent      | Queries past shopping memories |
| Preference Extraction Agent | Extracts structured preferences from natural language |
| Item Find Agent         | Uses Google Shopping to find products |
| Compare Agent           | Compares identified items |
| Markdown Parser Agent   | Parses markdown output |
| Database Agent          | Interacts with the preference database |

### 5. Extensible Tools  
Integrates with external tools like:
- **ComposioToolSet** (for SERPAPI search)  
- **GoogleShoppingTool**

---

## 📁 Project Structure

```

.
├── config/
│   ├── agents.yaml
│   └── tasks.yaml
├── shop\_agent/
│   ├── **init**.py
│   ├── crew\.py
│   ├── main.py
│   ├── memory.py
│   ├── models/
│   │   └── model.py
│   └── tools/
│       ├── **init**.py
│       ├── custom\_tool.py
│       ├── db\_tool.py
│       └── vector\_tools.py
└── .env

````

---

## ⚙️ Setup and Installation

### Prerequisites
- Python 3.9+
- pip package manager

### Steps
1. **Clone the repository:**
   ```bash
   git clone <your-repository-url>
   cd smart-shopping-assistant

2. **Install crewAI:**
   Follow crewAI docs (subject to change).

3. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   Create a `.env` file based on `.env.example`, e.g.:

   ```env
   COMPOSIO_API_KEY="your_composio_api_key_here"
   # Add others as needed
   ```

5. **Configure Agents and Tasks:**
   Customize `config/agents.yaml` and `config/tasks.yaml` for desired behavior.

---

## ▶️ How to Run

Run the main script or use crewAI CLI:

```bash
python shop_agent/main.py
# or
Crewai run
```

The assistant will prompt for:

* **username**
* **product category**
* **specific needs**

**Example Interaction:**

```
👤 Enter your username: john_doe
💡 Session started (UUID: <generated-uuid>)

Product category (e.g., wireless earbuds) or type 'exit' to quit: wireless earbuds
Describe your needs (color, budget, must-have features):
black, budget around $150, noise cancellation, good battery life

📝 Parsed preferences: {
  'budget': 150,
  'color': 'black',
  'features': ['noise_cancellation', 'good battery life'],
  'raw_input': 'black, budget around $150, noise cancellation, good battery life'
}

🔍 Searching for wireless earbuds with specs...
🔖 Final Recommendations:
1. **Sony WF-1000XM4**
   - Price: $120
   - Features: noise cancellation, excellent battery life, black
2. **Bose QuietComfort Earbuds II**
   - Price: $145
   - Features: world‑class noise cancellation, comfortable fit, black

✅ Preferences saved.
🔍 Retrieved preferences: { … }

✅ Completed in X.Xs

Type another product category or ‘exit’ to quit.

👋 Goodbye!
🧠 Short‑term memory cleared.
```

---

## 📈 Extending the Project

* **Add more tools:** Integrate with review sites, comparison services, etc.
* **Enhance parsing:** Improve `parse_user_details` for nuance recognition.
* **Improve comparisons:** Add deeper logic, score weighting, etc.
* **Add UI:** Web or desktop front-end for user-friendly experience.
* **Expand memory:** Experiment with other vector DBs or knowledge bases.

---


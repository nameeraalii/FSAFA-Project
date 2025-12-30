# Forensic Position Sizing Engine 🔍📊

A **forensic accounting–driven portfolio positioning system** that translates earnings quality and financial distress signals into **deterministic position sizing and execution-ready trade recommendations**, with **local AI explanations powered by Ollama**.

This project bridges **forensic accounting** and **portfolio management**, moving beyond screening models to an **actionable, explainable allocation framework**.

---

## 🚀 Key Highlights

- Uses **forensic accounting models** to assess manipulation and distress risk  
- Converts forensic risk into **long / hold / short signals**
- Applies **position sizing discipline with diversification constraints**
- Outputs **execution-ready share-level recommendations**
- Integrates **local LLM (Ollama)** strictly for **interpretability**, not decision-making
- Fully **transparent, auditable, and deterministic**

---

## 🧠 Forensic Models Used

- **Beneish M-Score** — Earnings manipulation risk  
- **Sloan Accruals** — Earnings quality and accrual aggressiveness  
- **Piotroski F-Score** — Fundamental strength  
- **Altman Z-Score** — Bankruptcy / distress risk  

These are normalized and combined into a **Composite Forensic Risk Score (FRS)**.

---

## ⚙️ How the Engine Works

1. **Input**
   - Multi-year financial statements (CSV / Excel)
   - Portfolio size
   - Stock price
   - Current portfolio weight

2. **Forensic Risk Computation**
   - Individual forensic scores computed per year
   - Scores normalized to a common risk scale
   - Combined into a single **FRS**

3. **Signal & Position Sizing**
   - FRS mapped to **LONG / HOLD / SHORT**
   - Position adjustment calculated using a deterministic sizing function
   - Diversification caps enforced

4. **Execution Layer**
   - Target portfolio weight
   - Target exposure (₹)
   - Exact shares to buy / sell

5. **AI Interpretation (Optional Layer)**
   - Local LLM (Ollama) explains:
     - Forensic diagnostics
     - Position sizing logic
     - Final recommendation
   - AI **never alters scores or trades**

---

## 🏗️ Architecture

```

Financial Statements
↓
Forensic Models (Python)
↓
Composite Forensic Risk Score (FRS)
↓
Position Sizing Engine (Deterministic)
↓
Execution Engine (Shares to Trade)
↓
AI Explanation Layer (Ollama – Local, Optional)

````

> **Design Principle:**  
> Deterministic logic for decisions, AI only for explanation.

---

## 🧪 Tech Stack

- **Python**
- **Streamlit** (UI)
- **Pandas / NumPy**
- **Ollama** (Local LLM)

No cloud APIs. No black boxes.

---

## ▶️ How to Run

### 1. Start Ollama (Local LLM)
```bash
ollama serve
````

Ensure a model is available:

```bash
ollama pull llama3
```

### 2. Run the App

```bash
streamlit run app.py
```
---

## 🎓 Academic & Practical Contribution

* Moves forensic models from **screening tools** to **portfolio construction inputs**
* Integrates accounting risk into **formal position sizing**
* Maintains **explainability and auditability**
* Suitable for:

  * Academic projects / capstones
  * Investment research prototypes
  * Risk and forensic analytics demonstrations

---

## ⚠️ Disclaimer

This project is for **educational and research purposes only**.
It does **not** constitute investment advice or a recommendation to trade securities.

---

## 📌 Author Note

This system is intentionally designed to ensure:

* **No AI-driven trading decisions**
* **Clear separation between analytics and interpretation**
* **Robustness under imperfect real-world financial data**

---

⭐ If you find this project interesting, feel free to star the repository!

```

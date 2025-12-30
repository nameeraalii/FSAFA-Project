import requests
import json

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3"


def _ollama_generate(prompt, temperature=0.2):
    payload = {
        "model": MODEL,
        "prompt": prompt,
        "stream": True,
        "options": {
            "temperature": temperature
        }
    }

    try:
        response = requests.post(
            OLLAMA_URL,
            json=payload,
            stream=True,
            timeout=120
        )
        response.raise_for_status()

        output = []
        for line in response.iter_lines():
            if line:
                data = json.loads(line.decode("utf-8"))  # ✅ FIX
                if "response" in data:
                    output.append(data["response"])

        return "".join(output).strip()

    except requests.exceptions.RequestException as e:
        return (
            "⚠️ **Ollama is unavailable**\n\n"
            "Your forensic and portfolio engine is still running correctly.\n\n"
            "Ensure Ollama is running:\n"
            "`ollama serve`\n\n"
            f"Error: {str(e)}"
        )


# ============================================================
# AI EXPLANATIONS (INTERPRETATION ONLY)
# ============================================================
def ai_explain_forensic_scores(m, sloan, f, z, frs):
    prompt = f"""
Explain the following forensic accounting indicators conservatively.
Do NOT give investment advice.

Beneish M-Score: {m:.2f}
Sloan Accruals: {sloan:.3f}
Piotroski F-Score: {int(f)}/9
Altman Z-Score: {z:.2f}
Composite Forensic Risk Score (FRS): {frs:.2f}

Focus on earnings quality, financial stability, and manipulation risk.
"""
    return _ollama_generate(prompt)


def ai_explain_positioning(frs, signal, current_w, target_w):
    prompt = f"""
Explain why a forensic-driven position sizing engine produced
the following output.

Forensic Risk Score (FRS): {frs:.2f}
Signal: {signal}
Current portfolio weight: {current_w:.2%}
Target portfolio weight: {target_w:.2%}

Focus on diversification, risk control, and discipline.
"""
    return _ollama_generate(prompt)


def ai_final_recommendation(signal, shares):
    prompt = f"""
Write a short, professional investment committee note.

Signal: {signal}
Shares to trade: {shares}

Do not mention AI or predictions.
Keep tone execution-focused and conservative.
"""
    return _ollama_generate(prompt)

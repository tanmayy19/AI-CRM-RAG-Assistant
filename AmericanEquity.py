from flask import Flask, render_template, request, session, jsonify
import pandas as pd
import markdown
import sqlite3
import re
from openai import OpenAI

app = Flask(__name__)
app.secret_key = "qwertyuiop"

# =========================================================
# 🔑 OPENAI CLIENT
# =========================================================
import os
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# =========================================================
# DATABASE LOADING + CACHING
# =========================================================

def load_dataframes():
    conn = sqlite3.connect("AmericanEquity.db")

    accounts = pd.read_sql_query("SELECT * FROM accounts", conn)
    products = pd.read_sql_query("SELECT * FROM products", conn)
    sales_teams = pd.read_sql_query("SELECT * FROM sales_teams", conn)
    pipeline = pd.read_sql_query("SELECT * FROM sales_pipeline", conn)
    interactions = pd.read_sql_query("SELECT * FROM interactions", conn)

    conn.close()

    # Date parsing
    if "timestamp" in interactions.columns:
        interactions["timestamp"] = pd.to_datetime(interactions["timestamp"], errors="coerce")

    for date_col in ["close_date", "engage_date"]:
        if date_col in pipeline.columns:
            pipeline[date_col] = pd.to_datetime(pipeline[date_col], errors="coerce")

    return accounts, products, sales_teams, pipeline, interactions


_data = None
def get_data():
    global _data
    if _data is None:
        _data = load_dataframes()
    return _data


# =========================================================
# SMART RETRIEVAL HELPERS (Option A)
# =========================================================

def retrieve_accounts(question):
    accounts, _, _, _, _ = get_data()

    # fuzzy matching against account_name
    q = question.lower()
    matches = accounts[accounts["account"].str.lower().str.contains(q, na=False)]

    if matches.empty:
        # try partial word matching
        for _, row in accounts.iterrows():
            name = row["account"]
            if any(part in q for part in name.lower().split()):
                return accounts[accounts["account"] == name]

    return matches


def retrieve_contact_interactions(question):
    _, _, _, _, interactions = get_data()
    q = question.lower()

    # Try fuzzy match
    matches = interactions[interactions["contact_name"].str.lower().str.contains(q, na=False)]

    # If no direct match, try partial name matching
    if matches.empty:
        for _, row in interactions.iterrows():
            parts = str(row["contact_name"]).lower().split()
            if any(p in q for p in parts):
                matches = interactions[interactions["contact_name"] == row["contact_name"]]
                break

    return matches.sort_values("timestamp", ascending=False)


def retrieve_sales_team(question):
    _, _, sales_teams, _, _ = get_data()
    q = question.lower()

    # Match managers
    managers = sales_teams["manager"].unique().tolist()
    for m in managers:
        if m.lower() in q:
            return sales_teams[sales_teams["manager"] == m]

    # Match sales agents
    for _, row in sales_teams.iterrows():
        if row["sales_agent"].lower() in q:
            return sales_teams[sales_teams["sales_agent"] == row["sales_agent"]]

    # default: return entire table
    return sales_teams


def retrieve_pipeline(question):
    _, _, _, pipeline, _ = get_data()
    q = question.lower()

    # "open opportunities"
    if "open" in q:
        return pipeline[pipeline["deal_stage"].str.lower().isin(["engaging", "prospecting"])]

    # "closed deals"
    if "closed" in q or "won" in q:
        return pipeline[pipeline["deal_stage"].str.lower() == "won"]

    # return entire table if unsure
    return pipeline


def retrieve_products(question):
    _, products, _, _, _ = get_data()
    return products


# =========================================================
# LLM INTENT CLASSIFIER (GPT-4.1)
# =========================================================

def classify_intent(message):
    prompt = f"""
You are an intent classifier for a CRM AI assistant.

User message:
\"\"\"{message}\"\"\"

Classify into ONE of the following intents:

- account_info
- contact_interaction
- sales_hierarchy
- product_info
- pipeline_info
- best_deal
- followup
- general_question

Respond with ONLY the label.
"""

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=10,
        temperature=0
    )
    return response.choices[0].message.content.strip()


# =========================================================
# MAIN RAG ANSWER GENERATION (GPT-4.1)
# =========================================================

def generate_rag_answer(question, retrieved_data, memory):
    """
    retrieved_data = dict of:
      { "accounts": df, "interactions": df, "sales": df, ... }
    memory = session-based conversation memory
    """

    context_blocks = []

    for key, df in retrieved_data.items():
        if df is not None and not df.empty:
            context_blocks.append(f"=== {key.upper()} DATA ===\n{df.to_string(index=False)}")

    if memory:
        context_blocks.append(f"=== CONVERSATION MEMORY ===\n{memory}")

    full_context = "\n\n".join(context_blocks)

    prompt = f"""
You are an AI assistant for a CRM dataset. 
You MUST answer using ONLY the structured data provided below.
Do not hallucinate or make up facts. Use natural language, bullet points when clear.

USER QUESTION:
{question}

CONTEXT DATA:
{full_context}

Provide a concise, accurate answer grounded ONLY in the above data.
"""

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=300
    )

    return response.choices[0].message.content.strip()


# =========================================================
# CHAT ENGINE
# =========================================================

@app.route("/")
def home():
    session.clear()
    return render_template("index.html", history=[])


@app.route("/chat", methods=["POST"])
def chat():
    msg = request.json.get("message", "").strip()

    if "memory" not in session:
        session["memory"] = ""

    # 1. CLASSIFY INTENT
    intent = classify_intent(msg)

    # 2. SMART RETRIEVAL (Option A)
    retrieved = {
        "accounts": None,
        "interactions": None,
        "sales_team": None,
        "pipeline": None,
        "products": None,
    }

    if intent == "account_info":
        retrieved["accounts"] = retrieve_accounts(msg)

    elif intent == "contact_interaction":
        retrieved["interactions"] = retrieve_contact_interactions(msg)

    elif intent == "sales_hierarchy":
        retrieved["sales_team"] = retrieve_sales_team(msg)

    elif intent == "product_info":
        retrieved["products"] = retrieve_products(msg)

    elif intent == "pipeline_info":
        retrieved["pipeline"] = retrieve_pipeline(msg)

    elif intent == "best_deal":
        # retrieve only won deals
        _, _, _, pipeline, _ = get_data()
        retrieved["pipeline"] = pipeline[pipeline["deal_stage"].str.lower() == "won"]

    elif intent == "followup":
        # Give model full memory + partial retrieval
        retrieved["accounts"] = retrieve_accounts(msg)
        retrieved["interactions"] = retrieve_contact_interactions(msg)

    else:
        # fallback only memory
        retrieved = {}

    # 3. GENERATE RAG ANSWER
    answer = generate_rag_answer(msg, retrieved, session["memory"])

    # 4. UPDATE MEMORY
    session["memory"] += f"\nUser: {msg}\nBot: {answer}\n"

    # 5. RETURN CLEAN HTML
    return jsonify({"html": markdown.markdown(answer)})


@app.route("/clear", methods=["POST"])
def clear_chat():
    session.clear()
    return {"status": "cleared"}


if __name__ == "__main__":
    app.run(debug=True)

# 🤖 AI CRM RAG Assistant

An AI-powered CRM assistant built using Flask, SQLite, and OpenAI GPT-4.1-mini.  
It uses Retrieval-Augmented Generation (RAG) to answer CRM questions with accurate, database-grounded insights — no hallucinations.

------------------------------------------------------------

## ✨ Features

- 💬 Conversational AI Chatbot  
- 🧠 Intent Classification (accounts, pipeline, interactions, sales hierarchy, products)  
- 📚 RAG Retrieval Layer (structured + accurate)  
- ⚡ Fast GPT-4.1-mini responses  
- 🎨 Modern UI with Bootstrap + Dark Mode  
- 🔎 Autocomplete suggestions + quick prompts  
- 🗂️ CSV-to-SQLite automated import system  

------------------------------------------------------------

## 🛠️ Tech Stack

**Backend:** Python, Flask, SQLite, Pandas, OpenAI API  
**Frontend:** HTML, Bootstrap 5, JavaScript  
**Database Tables:** accounts, products, sales_pipeline, sales_teams, interactions  

------------------------------------------------------------

## 📁 Project Structure

AI-CRM-RAG-Assistant/
- AmericanEquity.py  
- Import_csvs.py  
- AmericanEquity.db  
- templates/index.html  
- static/AE.png  
- static/image.png  
- accounts.csv  
- products.csv  
- interactions.csv  
- sales_pipeline.csv  
- sales_teams.csv  
- data_dictionary.csv  
- requirements.txt  
- README.md  

------------------------------------------------------------

## 🔌 Key Code Snippets

**Intent Classification:**
response = client.chat.completions.create(model="gpt-4.1-mini", messages=[{"role":"user","content":prompt}])

**Filter Open Opportunities:**
pipeline[pipeline["deal_stage"].str.lower().isin(["engaging", "prospecting"])]

------------------------------------------------------------

## 🚀 How to Run the Project

1. Install dependencies:
pip install -r requirements.txt

2. Load CSV files into SQLite:
python Import_csvs.py

3. Add your OpenAI API key in AmericanEquity.py:
OPENAI_API_KEY = "your-key-here"

4. Start Flask server:
python AmericanEquity.py

5. Open browser:
http://127.0.0.1:5000

------------------------------------------------------------

## 🧪 Example Queries

- Show open opportunities  
- Show best deal  
- List accounts and industries  
- Show sales hierarchy  
- Show recent interactions  

------------------------------------------------------------

## 🤔 Why OpenAI Over Cohere & Perplexity?

**Cohere:**  
- Weak structured retrieval  
- Inconsistent formatting  

**Perplexity:**  
- Great for open Q&A  
- Not built for CRM/SQL-style reasoning  

**OpenAI (Final Choice):**  
- Best accuracy for structured data  
- Fast + cheap with GPT-4.1-mini  
- Works perfectly with RAG  

------------------------------------------------------------

## ✅ Conclusion

This project demonstrates how LLMs + RAG + Flask can build a production-ready CRM assistant that delivers real-time, accurate, data-driven insights through an elegant and intuitive interface.


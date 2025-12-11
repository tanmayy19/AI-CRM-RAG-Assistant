# American Equity AI Sales Assistant  
An AI-powered CRM assistant built using **Flask**, **SQLite**, and **OpenAI (GPT-4.1 Mini)** that answers sales, account, and pipeline questions using structured company data.

This project was developed as a **Capstone Project** to demonstrate real-world AI application design, Retrieval-Augmented Generation (RAG), and intelligent query handling.

---

## 🚀 Features

### 🔹 Natural Language Chatbot  
Ask questions like:
- *“Show open opportunities”*
- *“List accounts and industries”*
- *“Who is managing this sales agent?”*
- *“What is the best closed deal?”*

### 🔹 Intent Classification  
Uses GPT-4.1-mini to classify questions into:
- Account info  
- Pipeline info  
- Sales hierarchy  
- Product details  
- Contact interactions  
- Best deal  
- General questions  

### 🔹 Retrieval Layer  
Smart fuzzy-search and partial matching over SQLite tables:
- `accounts`
- `sales_pipeline`
- `products`
- `sales_teams`
- `interactions`

### 🔹 RAG (Retrieval-Augmented Generation)
The system passes:
- Retrieved rows  
- Conversation history  
- User question  

to the LLM for grounded, non-hallucinated answers.

### 🔹 Clean Front-End UI  
Built with:
- Bootstrap 5  
- Custom chat bubbles  
- Autocomplete suggestions  
- Dark mode  
- “Bot is thinking…” indicator  

---

## 🗂 Project Structure


# PayPilot AI 🛒💳
> **An AI-Powered Shopping and Payment Assistant**

PayPilot AI is an intelligent shopping companion that guides users seamlessly from product discovery to checkout. It helps buyers discover verified tech products, compare technical specifications side-by-side, analyze deals through an AI Purchase Advisor, and prepares transactions for fast PayPal checkout.

---

## 📁 Project Architecture

```
PayPilot-AI/
│
├── backend/
│   ├── main.py            # FastAPI REST API, routing & AI shopping assistant endpoints
│   ├── database.py        # SQLite schema, products catalog, orders & payment ledger
│   └── requirements.txt   # FastAPI, Uvicorn, Pydantic, Requests
│
├── frontend/
│   ├── index.html         # Modern Fintech/E-commerce UI, sidebar & PayPal entry point
│   ├── style.css          # Executive dark navy theme, gradient typography & responsive grid
│   └── script.js          # Async client, live search, comparison matrix & AI chat
│
├── .env                   # Local runtime environment configuration
├── .env.example           # Environment template
├── .gitignore             # Standard git ignore definitions
└── README.md              # Project documentation
```

---

## ✨ Features

### 1. 🧭 Main Dashboard (Overview)
- **Heading**: *"Shop Smarter with PayPilot AI"*
- **Subtitle**: *"Your intelligent shopping companion, from discovery to checkout."*
- **AI Shopping Search Bar**: Interactive query input with real-time catalog search and popular category chips.
- **Recommended Products**: Clean product cards displaying star ratings, category tags, original and discounted prices, spec badges, and comparison toggles.
- **Product Comparison Preview**: Side-by-side matrix displaying pricing, ratings, and technical specs.
- **AI Purchase Advisor Highlights**: Algorithmic deal analysis showing price drops, savings percentages, and purchase tips.
- **PayPal Checkout Entry Point**: Clean PayPal entry point modal with order summary and estimated tax.

### 2. 🤖 AI Shopping Assistant
- Real-time conversational interface connected to the live catalog.
- Answers questions about specs, feature differences, budget picks, and deals.
- Powered by Google Gemini 1.5 (when `GEMINI_API_KEY` is provided) or the built-in local catalog reasoning engine.

### 3. ⚖️ Product Comparison Matrix
- Compare up to 4 products side-by-side.
- Compares battery life, connectivity, processors, display specs, and value ratings.

### 4. 💡 Purchase Advisor
- Analyzes current market discounts and user reviews.
- Highlights savings and provides transparent buying recommendations.

### 5. 📦 My Orders
- Tracks user purchase orders, delivery statuses (`Delivered`, `In Transit`), and purchase dates.

### 6. 💳 Payment History
- Verified transaction log displaying transaction IDs, order references, payment amounts, and PayPal checkout entries.

---

## 🚀 Quick Start Guide

### 1. Install Dependencies
```bash
pip install -r backend/requirements.txt
```

### 2. Run the Application
Start the FastAPI server:
```bash
python -m uvicorn backend.main:app --reload --port 8000
```

### 3. Open in Browser
Visit:
```
http://localhost:8000
```
- Interactive API Swagger documentation: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 📡 REST API Reference

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/health` | Service health status check |
| `GET` | `/api/overview` | Overall catalog, orders, and payment statistics |
| `GET` | `/api/products` | Retrieve products (supports `?category=` and `?q=`) |
| `GET` | `/api/products/{id}` | Retrieve specific product details |
| `POST` | `/api/compare` | Compare products by array of IDs (`product_ids: [1, 2]`) |
| `GET` | `/api/advisor/deals` | Retrieve active deal insights and price drops |
| `GET` | `/api/orders` | Retrieve user order history |
| `GET` | `/api/payments` | Retrieve payment transaction history |
| `POST` | `/api/ai/shopping-assistant` | AI shopping assistant conversational endpoint |
| `GET` | `/api/ai/history` | Retrieve recent assistant conversation history |

---

## 🧪 Testing the Application

### 1. Verify Health & Backend
```bash
curl http://127.0.0.1:8000/api/health
```
Expected output:
```json
{"status":"healthy","service":"PayPilot-AI Shopping Assistant","version":"1.0.0"}
```

### 2. Test Shopping Search
```bash
curl "http://127.0.0.1:8000/api/products?q=headphones"
```

### 3. Test Product Comparison
```bash
curl -X POST http://127.0.0.1:8000/api/compare \
     -H "Content-Type: application/json" \
     -d '{"product_ids": [1, 2]}'
```

### 4. Test AI Shopping Assistant
```bash
curl -X POST http://127.0.0.1:8000/api/ai/shopping-assistant \
     -H "Content-Type: application/json" \
     -d '{"message": "Compare Sony XM5 vs Bose headphones"}'
```

---

## 🛡️ License
MIT License. Built for hackathon demonstration.

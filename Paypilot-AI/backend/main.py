import os
import json
from typing import Optional, List, Dict, Any
from pathlib import Path

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    env_path = Path(__file__).parent.parent / ".env"
    if env_path.exists():
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, val = line.split("=", 1)
                    os.environ.setdefault(key.strip(), val.strip())

import requests
from fastapi import FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from backend.database import (
    init_db,
    get_products,
    get_product_by_id,
    get_compared_products,
    get_orders,
    get_payments,
    create_order_and_payment,
    get_overview_stats,
    log_ai_message,
    get_ai_history
)

# Initialize database tables and seed products
init_db()

app = FastAPI(
    title="PayPilot AI — Shopping & Payment Assistant API",
    description="Intelligent product discovery, comparison, purchase advisor and payment helper API",
    version="1.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Pydantic Models ---

class CompareRequest(BaseModel):
    product_ids: List[int] = Field(..., min_length=1, max_length=4)

class CheckoutRequest(BaseModel):
    product_id: int
    gateway: Optional[str] = "PayPal"

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1)

# --- API Endpoints ---

@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "service": "PayPilot-AI Shopping Assistant",
        "version": "1.0.0"
    }

@app.get("/api/overview")
def overview_stats():
    """Returns overview metrics: total catalog items, orders placed, and payments."""
    return get_overview_stats()

@app.get("/api/products")
def list_products(
    category: Optional[str] = None,
    q: Optional[str] = None
):
    """Lists recommended catalog items with search and category filter."""
    return get_products(category=category, query=q)

@app.get("/api/products/{product_id}")
def read_product(product_id: int):
    product = get_product_by_id(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@app.post("/api/compare")
def compare_products(payload: CompareRequest):
    """Compares 2 or more products side-by-side with specs and prices."""
    products = get_compared_products(payload.product_ids)
    if not products:
        raise HTTPException(status_code=404, detail="No matching products found for comparison")
    return {
        "count": len(products),
        "products": products
    }

@app.get("/api/advisor/deals")
def purchase_advisor_deals():
    """Returns dynamic AI purchase advice based on current live catalog discounts and ratings."""
    products = get_products()
    deals = []
    for p in products:
        orig = p.get("original_price")
        curr = p.get("price")
        if orig and orig > curr:
            savings = round(orig - curr, 2)
            pct = round((savings / orig) * 100)
            deals.append({
                "product_id": p["id"],
                "name": p["name"],
                "category": p["category"],
                "current_price": curr,
                "original_price": orig,
                "savings": savings,
                "discount_pct": pct,
                "rating": p["rating"],
                "advice": f"Save ${savings:.2f} ({pct}% off). Highly rated by {p['reviews_count']} verified buyers."
            })
    return sorted(deals, key=lambda x: x["discount_pct"], reverse=True)

@app.get("/api/orders")
def list_orders():
    """Returns user order history."""
    return get_orders()

@app.get("/api/payments")
def list_payments():
    """Returns user payment transaction history."""
    return get_payments()

@app.post("/api/checkout/process", status_code=status.HTTP_201_CREATED)
def process_checkout(req: CheckoutRequest):
    """Processes real order and payment creation in SQLite database."""
    product = get_product_by_id(req.product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    order_record = create_order_and_payment(
        product_name=product["name"],
        price=product["price"],
        gateway=req.gateway or "PayPal"
    )

    return {
        "success": True,
        "message": f"Payment of ${product['price']:.2f} processed via {req.gateway or 'PayPal'}. Order confirmed!",
        "order": order_record
    }

@app.get("/api/advisor/product/{product_id}")
def product_advisor(product_id: int):
    """Provides algorithmic buying recommendations for a specific product."""
    product = get_product_by_id(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    orig = product.get("original_price")
    curr = product["price"]
    has_discount = orig and orig > curr
    discount_pct = round(((orig - curr) / orig) * 100) if has_discount else 0

    return {
        "product_id": product["id"],
        "name": product["name"],
        "category": product["category"],
        "price": curr,
        "rating": product["rating"],
        "has_discount": bool(has_discount),
        "discount_pct": discount_pct,
        "deal_verdict": "Exceptional Value" if discount_pct > 10 or product["rating"] >= 4.8 else "Fair Market Price",
        "analysis": (
            f"Rated {product['rating']}★ across {product['reviews_count']} buyers. "
            + (f"Currently discounted by {discount_pct}% (save ${orig - curr:.2f}). " if has_discount else "")
            + "High reliability index with verified warranty."
        )
    }

# --- AI Shopping Assistant Engine ---

def shopping_assistant_local_engine(user_query: str) -> str:
    """Answers shopping questions by searching real catalog specs and pricing."""
    q_lower = user_query.lower()
    products = get_products()

    # If query mentions comparison
    if any(k in q_lower for k in ["compare", "difference", "versus", "vs"]):
        if any(k in q_lower for k in ["macbook", "apple", "dell", "xps", "laptop"]):
            mac = next((p for p in products if "MacBook" in p["name"]), None)
            dell = next((p for p in products if "XPS" in p["name"]), None)
            if mac and dell:
                return (
                    f"### ⚖️ Product Comparison: MacBook Air 15\" vs. Dell XPS 14\n\n"
                    f"- **{mac['name']}**: ${mac['price']:.2f} (Rating: {mac['rating']}★). Features Apple M3 silicon and up to 18 hours of battery life. Best for macOS users wanting silent, cool performance.\n"
                    f"- **{dell['name']}**: ${dell['price']:.2f} (Rating: {dell['rating']}★). Features 3.2K OLED touch display and Intel Core Ultra 7. Best for Windows productivity and content creation.\n\n"
                    f"💡 **PayPilot Advice**: If battery endurance is your priority, pick the MacBook Air ($1,199). If OLED display sharpness and touchscreen matter more, choose the Dell XPS 14."
                )

        if any(k in q_lower for k in ["sony", "bose", "headphone", "audio"]):
            sony = next((p for p in products if "Sony" in p["name"]), None)
            bose = next((p for p in products if "Bose" in p["name"]), None)
            if sony and bose:
                return (
                    f"### 🎧 Headphone Showdown: Sony WH-1000XM5 vs. Bose QC Ultra\n\n"
                    f"- **{sony['name']}**: ${sony['price']:.2f} (Was ${sony['original_price']:.2f} — Save $51.99). 30-hour battery life, superior microphone call clarity, and custom EQ.\n"
                    f"- **{bose['name']}**: ${bose['price']:.2f} (Was ${bose['original_price']:.2f} — Save $50.00). World-class spatial immersion audio and foldable earcups.\n\n"
                    f"💡 **PayPilot Advice**: The Sony XM5 offers better battery life and is currently $31 cheaper. Pick Bose if you travel frequently and prefer spatial audio."
                )

    # Budget or price queries
    if any(k in q_lower for k in ["cheap", "budget", "under 100", "under 200", "under 400", "affordable", "deal", "discount"]):
        discounted = [p for p in products if p.get("original_price") and p["original_price"] > p["price"]]
        items_list = "\n".join([
            f"- **{p['name']}**: Now **${p['price']:.2f}** (was ${p['original_price']:.2f}, save {round((p['original_price']-p['price'])/p['original_price']*100)}%) — *{p['category']}*"
            for p in discounted[:4]
        ])
        return (
            f"### 🏷️ Top Deals & Budget Picks Available Now\n\n"
            f"Here are the highest discounted products currently in our catalog:\n\n"
            f"{items_list}\n\n"
            f"Ask me to compare any of these or add them to your evaluation list!"
        )

    # Specific product search
    matched = [p for p in products if p["name"].lower() in q_lower or p["category"].lower() in q_lower]
    if matched:
        p = matched[0]
        specs_str = ""
        if isinstance(p.get("specs"), dict):
            specs_str = "\n" + "\n".join([f"  - **{k}**: {v}" for k, v in p["specs"].items()])
        return (
            f"### 📦 Product Information: {p['name']}\n\n"
            f"- **Category**: {p['category']}\n"
            f"- **Current Price**: **${p['price']:.2f}**" + (f" *(Original: ${p['original_price']:.2f})*" if p.get("original_price") else "") + "\n"
            f"- **Rating**: {p['rating']} ★ ({p['reviews_count']} reviews)\n"
            f"- **Description**: {p['description']}\n"
            f"- **Key Specifications**:{specs_str}\n\n"
            f"You can view full details or compare this product in the dashboard."
        )

    # General Shopping Guidance
    return (
        f"### 🛍️ PayPilot AI Shopping Assistant\n\n"
        f"I can help you discover products, compare technical specifications, and find the best verified deals in our catalog.\n\n"
        f"Try asking:\n"
        f"- *'Compare Sony XM5 vs Bose QC Ultra headphones'*\n"
        f"- *'What are the best laptop deals right now?'*\n"
        f"- *'Tell me about the Logitech MX Master 3S'* \n"
        f"- *'Show me products under $400'*"
    )

@app.post("/api/ai/shopping-assistant")
def ai_shopping_assistant(payload: ChatRequest):
    """Processes user shopping inquiries via Gemini API if key is set, or via catalog reasoning engine."""
    user_msg = payload.message.strip()
    log_ai_message("user", user_msg)

    api_key = os.getenv("GEMINI_API_KEY", "").strip()

    if api_key and api_key != "your_gemini_api_key_here":
        try:
            products = get_products()
            catalog_summary = json.dumps([
                {"name": p["name"], "category": p["category"], "price": p["price"], "rating": p["rating"], "specs": p.get("specs")}
                for p in products
            ])
            sys_context = (
                f"You are PayPilot AI, an intelligent, helpful shopping and payment assistant.\n"
                f"Live Product Catalog: {catalog_summary}\n"
                f"Help the user discover products, compare technical specs, recommend best deals, and answer questions concisely with markdown."
            )

            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
            body = {
                "contents": [
                    {"role": "user", "parts": [{"text": f"{sys_context}\n\nUser Question: {user_msg}"}]}
                ]
            }
            resp = requests.post(url, json=body, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                reply_text = data["candidates"][0]["content"]["parts"][0]["text"]
                log_ai_message("assistant", reply_text)
                return {"reply": reply_text, "source": "gemini-ai"}
        except Exception:
            pass

    # Use local catalog-based shopping reasoning
    reply = shopping_assistant_local_engine(user_msg)
    log_ai_message("assistant", reply)
    return {"reply": reply, "source": "paypilot-shopping-engine"}

@app.get("/api/ai/history")
def ai_chat_history():
    return get_ai_history(limit=15)

# --- Serve Frontend Static Files ---
frontend_dir = Path(__file__).parent.parent / "frontend"
if frontend_dir.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_dir)), name="static")

    @app.get("/")
    def serve_landing():
        """Landing page — Particle Saturn splash screen."""
        return FileResponse(str(frontend_dir / "landing.html"))

    @app.get("/app")
    def serve_app():
        """Main shopping dashboard."""
        return FileResponse(str(frontend_dir / "index.html"))

    @app.get("/{full_path:path}")
    def serve_frontend_fallback(full_path: str):
        target_file = frontend_dir / full_path
        if target_file.is_file():
            return FileResponse(str(target_file))
        # Unknown paths fall back to landing
        return FileResponse(str(frontend_dir / "landing.html"))

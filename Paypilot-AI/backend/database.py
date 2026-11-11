import sqlite3
import os
import json
from datetime import datetime
from typing import List, Dict, Any, Optional

DB_PATH = os.path.join(os.path.dirname(__file__), "paypilot.db")

def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def init_db():
    """Initializes shopping tables and seeds demo products and orders if empty."""
    with get_connection() as conn:
        cursor = conn.cursor()

        # Products catalog table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                price REAL NOT NULL,
                original_price REAL,
                rating REAL DEFAULT 4.5,
                reviews_count INTEGER DEFAULT 120,
                description TEXT,
                specs TEXT,
                badge TEXT,
                in_stock INTEGER DEFAULT 1
            )
        """)

        # Orders table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_number TEXT NOT NULL,
                product_name TEXT NOT NULL,
                price REAL NOT NULL,
                status TEXT DEFAULT 'Delivered',
                order_date TEXT NOT NULL,
                payment_method TEXT DEFAULT 'PayPal'
            )
        """)

        # Payment transactions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                transaction_id TEXT NOT NULL,
                order_number TEXT NOT NULL,
                amount REAL NOT NULL,
                currency TEXT DEFAULT 'USD',
                status TEXT DEFAULT 'Completed',
                gateway TEXT DEFAULT 'PayPal',
                timestamp TEXT NOT NULL
            )
        """)

        # AI Shopping assistant conversations table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ai_conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.commit()

        # Check if products exist; seed if empty
        cursor.execute("SELECT COUNT(*) as count FROM products")
        if cursor.fetchone()["count"] == 0:
            seed_initial_data(conn)

def seed_initial_data(conn: sqlite3.Connection):
    cursor = conn.cursor()

    demo_products = [
        (
            "Sony WH-1000XM5 Wireless Headphones",
            "Audio",
            348.00,
            399.99,
            4.8,
            2450,
            "Industry-leading noise cancellation with 2 processors, 8 microphones, and 30-hour battery life.",
            json.dumps({"Battery": "30 hrs", "Weight": "250g", "Connectivity": "Bluetooth 5.2 / 3.5mm", "ANC": "Auto NC Optimizer"}),
            "Best Seller"
        ),
        (
            "Bose QuietComfort Ultra Headphones",
            "Audio",
            379.00,
            429.00,
            4.7,
            1820,
            "World-class spatial audio with custom immersion mode and luxurious lightweight earcups.",
            json.dumps({"Battery": "24 hrs", "Weight": "252g", "Connectivity": "Bluetooth 5.3", "ANC": "CustomTune Tech"}),
            "Top Soundstage"
        ),
        (
            "Apple MacBook Air 15\" (M3 Chip)",
            "Laptops",
            1199.00,
            1299.00,
            4.9,
            3410,
            "Super slim 15.3-inch Liquid Retina display with 18-hour battery life and blazing fast M3 processing.",
            json.dumps({"CPU": "Apple M3 (8-core)", "Memory": "16GB Unified", "Storage": "512GB SSD", "Display": "15.3\" Liquid Retina"}),
            "Editor's Choice"
        ),
        (
            "Dell XPS 14 OLED Laptop",
            "Laptops",
            1399.00,
            1599.00,
            4.6,
            960,
            "Stunning 3.2K InfinityEdge OLED touch display with Intel Core Ultra 7 processor and CNC aluminum body.",
            json.dumps({"CPU": "Intel Ultra 7 155H", "Memory": "16GB LPDDR5x", "Storage": "1TB NVMe", "Display": "14.5\" 3.2K OLED"}),
            "Premium Build"
        ),
        (
            "Dell UltraSharp 27\" 4K USB-C Hub Monitor (U2723QE)",
            "Monitors",
            519.00,
            629.99,
            4.8,
            1540,
            "IPS Black technology with 2000:1 contrast ratio, 98% DCI-P3 color gamut, and 90W USB-C power delivery.",
            json.dumps({"Resolution": "3840 x 2160 (4K UHD)", "Panel": "IPS Black", "Refresh Rate": "60Hz", "Ports": "USB-C, DP 1.4, HDMI, RJ45"}),
            "Productivity Pick"
        ),
        (
            "Logitech MX Master 3S Wireless Mouse",
            "Peripherals",
            99.99,
            109.99,
            4.9,
            8920,
            "Ergonomic precision mouse with 8,000 DPI track-on-glass sensor and whisper-quiet clicks.",
            json.dumps({"Sensor": "8,000 DPI Darkfield", "Battery": "Up to 70 days", "Scroll Wheel": "MagSpeed Electromagnetic", "Multi-Device": "Flow 3 devices"}),
            "Top Ergonomic"
        ),
        (
            "Keychron Q1 Pro Wireless Custom Mechanical Keyboard",
            "Peripherals",
            199.00,
            219.00,
            4.7,
            750,
            "Full aluminum CNC body with QMK/VIA key remapping, hot-swappable switches, and double-gasket acoustic design.",
            json.dumps({"Layout": "75%", "Switches": "Keychron K Pro Red", "Connectivity": "Bluetooth 5.1 / Type-C", "Body": "Full CNC Aluminum"}),
            "Enthusiast Choice"
        ),
        (
            "Apple Watch Series 9 GPS 45mm",
            "Wearables",
            329.00,
            429.00,
            4.8,
            4120,
            "Powerful S9 SiP with Double Tap gesture, brighter display, and comprehensive health sensors.",
            json.dumps({"Chip": "S9 SiP with 64-bit dual-core", "Water Resistance": "50m swimproof", "Sensors": "ECG, SpO2, Heart Rate", "Battery": "18-36 hrs"}),
            "Popular Deal"
        )
    ]

    cursor.executemany("""
        INSERT INTO products (name, category, price, original_price, rating, reviews_count, description, specs, badge)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, demo_products)

    # Seed demo order history
    demo_orders = [
        ("ORD-98214", "Sony WH-1000XM5 Wireless Headphones", 348.00, "Delivered", "2026-10-24", "PayPal"),
        ("ORD-89420", "Logitech MX Master 3S Wireless Mouse", 99.99, "Delivered", "2026-10-18", "PayPal"),
        ("ORD-77192", "Apple Watch Series 9 GPS 45mm", 329.00, "In Transit", "2026-10-29", "PayPal")
    ]

    cursor.executemany("""
        INSERT INTO orders (order_number, product_name, price, status, order_date, payment_method)
        VALUES (?, ?, ?, ?, ?, ?)
    """, demo_orders)

    # Seed demo payment transactions
    demo_payments = [
        ("PAY-558912", "ORD-98214", 348.00, "USD", "Completed", "PayPal", "2026-10-24 14:22:10"),
        ("PAY-441208", "ORD-89420", 99.99, "USD", "Completed", "PayPal", "2026-10-18 09:15:44"),
        ("PAY-339102", "ORD-77192", 329.00, "USD", "Completed", "PayPal", "2026-10-29 18:40:02")
    ]

    cursor.executemany("""
        INSERT INTO payments (transaction_id, order_number, amount, currency, status, gateway, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, demo_payments)

    conn.commit()

# --- Product Queries ---

def get_products(category: Optional[str] = None, query: Optional[str] = None) -> List[Dict[str, Any]]:
    with get_connection() as conn:
        cursor = conn.cursor()
        sql = "SELECT * FROM products WHERE in_stock = 1"
        params = []

        if category and category.lower() != "all":
            sql += " AND category = ?"
            params.append(category)

        if query:
            sql += " AND (name LIKE ? OR category LIKE ? OR description LIKE ?)"
            term = f"%{query}%"
            params.extend([term, term, term])

        sql += " ORDER BY rating DESC, id ASC"
        cursor.execute(sql, params)
        rows = [dict(row) for row in cursor.fetchall()]
        for r in rows:
            if isinstance(r.get("specs"), str):
                try:
                    r["specs"] = json.loads(r["specs"])
                except Exception:
                    pass
        return rows

def get_product_by_id(product_id: int) -> Optional[Dict[str, Any]]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM products WHERE id = ?", (product_id,))
        row = cursor.fetchone()
        if not row:
            return None
        item = dict(row)
        if isinstance(item.get("specs"), str):
            try:
                item["specs"] = json.loads(item["specs"])
            except Exception:
                pass
        return item

def get_compared_products(ids: List[int]) -> List[Dict[str, Any]]:
    if not ids:
        return []
    with get_connection() as conn:
        cursor = conn.cursor()
        placeholders = ",".join("?" for _ in ids)
        cursor.execute(f"SELECT * FROM products WHERE id IN ({placeholders})", ids)
        rows = [dict(row) for row in cursor.fetchall()]
        for r in rows:
            if isinstance(r.get("specs"), str):
                try:
                    r["specs"] = json.loads(r["specs"])
                except Exception:
                    pass
        return rows

# --- Orders and Payments ---

def get_orders() -> List[Dict[str, Any]]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM orders ORDER BY id DESC")
        return [dict(row) for row in cursor.fetchall()]

def get_payments() -> List[Dict[str, Any]]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM payments ORDER BY id DESC")
        return [dict(row) for row in cursor.fetchall()]

def create_order_and_payment(product_name: str, price: float, gateway: str = "PayPal") -> Dict[str, Any]:
    """Creates a real order and transaction record in SQLite."""
    import random
    from datetime import datetime

    order_num = f"ORD-{random.randint(10000, 99999)}"
    tx_id = f"PAY-{random.randint(100000, 999999)}"
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    today_str = datetime.now().strftime("%Y-%m-%d")

    with get_connection() as conn:
        cursor = conn.cursor()

        # Insert order
        cursor.execute("""
            INSERT INTO orders (order_number, product_name, price, status, order_date, payment_method)
            VALUES (?, ?, ?, 'Confirmed', ?, ?)
        """, (order_num, product_name, float(price), today_str, gateway))
        order_id = cursor.lastrowid

        # Insert payment
        cursor.execute("""
            INSERT INTO payments (transaction_id, order_number, amount, currency, status, gateway, timestamp)
            VALUES (?, ?, ?, 'USD', 'Completed', ?, ?)
        """, (tx_id, order_num, float(price), gateway, now_str))
        payment_id = cursor.lastrowid

        conn.commit()

        return {
            "order_id": order_id,
            "order_number": order_num,
            "product_name": product_name,
            "price": float(price),
            "status": "Confirmed",
            "order_date": today_str,
            "transaction_id": tx_id,
            "gateway": gateway,
            "payment_status": "Completed",
            "timestamp": now_str
        }

# --- Overview Stats ---

def get_overview_stats() -> Dict[str, Any]:
    with get_connection() as conn:
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) as total_products FROM products")
        products_count = cursor.fetchone()["total_products"] or 0

        cursor.execute("SELECT COUNT(*) as total_orders, SUM(price) as total_spent FROM orders")
        order_stats = cursor.fetchone()

        cursor.execute("SELECT COUNT(*) as completed_payments FROM payments WHERE status = 'Completed'")
        payments_count = cursor.fetchone()["completed_payments"] or 0

        return {
            "total_products": products_count,
            "total_orders": order_stats["total_orders"] or 0,
            "total_spent": round(order_stats["total_spent"] or 0.0, 2),
            "completed_payments": payments_count
        }

# --- AI Chat History ---

def log_ai_message(role: str, content: str):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO ai_conversations (role, content) VALUES (?, ?)", (role, content))
        conn.commit()

def get_ai_history(limit: int = 15) -> List[Dict[str, Any]]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT role, content, timestamp FROM ai_conversations ORDER BY id DESC LIMIT ?", (limit,))
        rows = cursor.fetchall()
        return [dict(row) for row in reversed(rows)]

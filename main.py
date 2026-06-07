from fastmcp import FastMCP
import psycopg2
import os

CATEGORIES_PATH = os.path.join(os.path.dirname(__file__), "categories.json")

mcp = FastMCP("ExpenseTracker")

# PostgreSQL connection config
DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "user": "test",
    "password": "test",
    "dbname": "mydb"
}


def get_conn():
    return psycopg2.connect(**DB_CONFIG)


def init_db():
    with get_conn() as conn:
        with conn.cursor() as c:
            c.execute("""
                CREATE TABLE IF NOT EXISTS expenses(
                    id SERIAL PRIMARY KEY,
                    date DATE NOT NULL,
                    amount NUMERIC NOT NULL,
                    category TEXT NOT NULL,
                    subcategory TEXT DEFAULT '',
                    note TEXT DEFAULT ''
                )
            """)
        conn.commit()


init_db()


@mcp.tool()
def add_expense(date, amount, category, subcategory="", note=""):
    """Add a new expense entry to the database."""
    with get_conn() as conn:
        with conn.cursor() as c:
            c.execute("""
                INSERT INTO expenses(date, amount, category, subcategory, note)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id
            """, (date, amount, category, subcategory, note))

            new_id = c.fetchone()[0]
        conn.commit()

    return {"status": "ok", "id": new_id}


@mcp.tool()
def list_expenses(start_date, end_date):
    """List expense entries within an inclusive date range."""
    with get_conn() as conn:
        with conn.cursor() as c:
            c.execute("""
                SELECT id, date, amount, category, subcategory, note
                FROM expenses
                WHERE date BETWEEN %s AND %s
                ORDER BY id ASC
            """, (start_date, end_date))

            rows = c.fetchall()
            cols = [desc[0] for desc in c.description]

    return [dict(zip(cols, row)) for row in rows]


@mcp.tool()
def summarize(start_date, end_date, category=None):
    """Summarize expenses by category within a date range."""
    with get_conn() as conn:
        with conn.cursor() as c:

            query = """
                SELECT category, SUM(amount) AS total_amount
                FROM expenses
                WHERE date BETWEEN %s AND %s
            """
            params = [start_date, end_date]

            if category:
                query += " AND category = %s"
                params.append(category)

            query += " GROUP BY category ORDER BY category ASC"

            c.execute(query, params)

            rows = c.fetchall()
            cols = [desc[0] for desc in c.description]

    return [dict(zip(cols, row)) for row in rows]


@mcp.resource("expense://categories", mime_type="application/json")
def categories():
    """Return categories JSON file dynamically."""
    with open(CATEGORIES_PATH, "r", encoding="utf-8") as f:
        return f.read()


"""from fastmcp import FastMCP
import os
import sqlite3
import random

mcp = FastMCP(name = "Demo Server")

@mcp.tool
def roll_dice(n_dice:int = 1)-> list[int]:
    return [random.randint(1,6) for _ in range(n_dice)]

@mcp.tool 
def add_numbers(a:float, b:float)->float:
    return a+b

if __name__ == "__main__":
    mcp.run()"""

if __name__ == "__main__":
    mcp.run(transport="http", host ="0.0.0.0", port= 8000)
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sqlite3
import pandas as pd
import os

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_NAME = "companies.db"

class Company(BaseModel):
    rd_spend: float
    administration: float
    marketing_spend: float
    state: str
    profit: float

def init_db():
    """Initialize database and load CSV data if needed"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS companies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            rd_spend REAL,
            administration REAL,
            marketing_spend REAL,
            state TEXT,
            profit REAL
        )
    ''')
    
    cursor.execute("SELECT COUNT(*) FROM companies")
    if cursor.fetchone()[0] == 0:
        csv_file = '1000_Companies.csv'
        if os.path.exists(csv_file):
            df = pd.read_csv(csv_file)
            df.columns = ['rd_spend', 'administration', 'marketing_spend', 'state', 'profit']
            df.to_sql('companies', conn, if_exists='append', index=False)
    
    conn.commit()
    conn.close()

@app.on_event("startup")
async def startup_event():
    init_db()

@app.get("/ventures")
async def get_ventures():
    """Get all companies/ventures from database"""
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT * FROM companies", conn)
    conn.close()
    return df.to_dict(orient='records')

@app.get("/metrics")
async def get_metrics():
    """Get summary metrics"""
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT * FROM companies", conn)
    conn.close()
    
    total_profit = float(df['profit'].sum())
    total_spend = float(df['rd_spend'].sum() + df['administration'].sum() + df['marketing_spend'].sum())
    efficiency = round((total_profit / total_spend * 100), 2) if total_spend > 0 else 0
    top_state = df.groupby('state')['profit'].sum().idxmax()
    
    return {
        "total_records": len(df),
        "avg_profit": float(df['profit'].mean()),
        "total_profit": total_profit,
        "avg_rd_spend": float(df['rd_spend'].mean()),
        "efficiency_ratio": efficiency,
        "top_state": top_state
    }

@app.post("/ventures")
async def add_venture(company: Company):
    """Add a new company/venture to database"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO companies (rd_spend, administration, marketing_spend, state, profit)
        VALUES (?, ?, ?, ?, ?)
    ''', (company.rd_spend, company.administration, company.marketing_spend, 
          company.state, company.profit))
    conn.commit()
    conn.close()
    return {"status": "success", "message": "Venture added successfully"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)

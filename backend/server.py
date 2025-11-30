from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import pymysql
import sqlparse

# -----------------------------
# MODEL AND DATABASE SETUP
# -----------------------------
MODEL_NAME = "google/flan-t5-small"

# Load tokenizer and model
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME)

# MySQL connection details (edit if you use password)
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "chin2022021060",          # <-- put your MySQL password here if needed
    "database": "company_db" # must match your created DB name
}

# -----------------------------
# FASTAPI INITIALIZATION
# -----------------------------
app = FastAPI(title="NL2SQL - Week6 Prototype")

# Allow frontend (port 8080) to talk to backend (port 8000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      # For demo, allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------
# REQUEST MODEL
# -----------------------------
class QueryRequest(BaseModel):
    nl_query: str

# -----------------------------
# HELPER FUNCTIONS
# -----------------------------
def validate_sql(sql_text):
    """Allow only SELECT queries and basic SQL syntax."""
    parsed = sqlparse.parse(sql_text)
    if not parsed:
        raise ValueError("Invalid SQL syntax.")
    first_token = parsed[0].token_first(skip_cm=True)
    if not first_token or first_token.normalized.upper() != "SELECT":
        raise ValueError("Only SELECT statements are allowed.")
    return sql_text.strip().rstrip(";")

def fix_common_errors(sql_text):
    """Simple keyword correction for demo schema."""
    sql_text = sql_text.replace("employee ", "employees ")
    sql_text = sql_text.replace("Employee ", "employees ")
    sql_text = sql_text.replace("department", "dept")
    return sql_text

def run_sql(query):
    """Execute the SQL query on MySQL and return rows."""
    connection = pymysql.connect(**DB_CONFIG, cursorclass=pymysql.cursors.DictCursor)
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(query)
            rows = cursor.fetchall()
    return rows

# -----------------------------
# MAIN ROUTE
# -----------------------------
@app.post("/nl_to_sql")
def nl_to_sql(req: QueryRequest):
    nl_query = req.nl_query.strip()
    if not nl_query:
        raise HTTPException(status_code=400, detail="Empty query.")

    # -----------------------------
    # TOKENIZATION + ENCODING STEP
    # -----------------------------
    tokens = tokenizer.tokenize(nl_query)
    encoded = tokenizer.encode(nl_query, return_tensors="pt")

    print(f"Tokens: {tokens}")  # visible in backend console
    print(f"Encoded IDs: {encoded.tolist()}")

    # Generate SQL using model
    prompt = f"Translate English to SQL: {nl_query}"
    outputs = model.generate(**tokenizer(prompt, return_tensors="pt"), max_length=128)
    generated_sql = tokenizer.decode(outputs[0], skip_special_tokens=True)

    # Fix & validate
    generated_sql = fix_common_errors(generated_sql)
    if "SELECT" not in generated_sql.upper():
        generated_sql = "SELECT * FROM employees;"  # fallback query

    try:
        clean_sql = validate_sql(generated_sql)
        result = run_sql(clean_sql)
        if not result:
            result = [{"message": "No matching records found"}]
    except Exception as e:
        return {"nl_query": nl_query, "generated_sql": generated_sql, "error": str(e)}

    # Return everything (good for debugging)
    return {
        "nl_query": nl_query,
        "tokens": tokens,
        "generated_sql": clean_sql,
        "result": result
    }

# -----------------------------
# RUN COMMAND (for reference)
# -----------------------------
# uvicorn server:app --reload

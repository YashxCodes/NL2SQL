from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import pymysql

app = FastAPI()

# CORS setup to allow frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load tokenizer + model
tokenizer = AutoTokenizer.from_pretrained("model/fine_tuned_model")
model = AutoModelForSeq2SeqLM.from_pretrained("model/fine_tuned_model")

# Update with your MySQL credentials
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "your_mysql_password",
    "database": "company_db"
}

class Query(BaseModel):
    question: str

@app.post("/nl_to_sql")
def nl_to_sql(query: Query):
    try:
        inputs = tokenizer(query.question, return_tensors="pt")
        outputs = model.generate(**inputs, max_length=128, num_beams=4)
        sql = tokenizer.decode(outputs[0], skip_special_tokens=True)

        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute(sql)
        result = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        cursor.close()
        conn.close()

        return {"sql": sql, "result": [dict(zip(columns, row)) for row in result]}
    except Exception as e:
        return {"sql": sql, "error": str(e)}

# 📚 Book Management System

A feature-rich **Book Management System** built with **FastAPI** and **PostgreSQL**.  
Includes CRUD operations, import/export (JSON & CSV), JWT authentication, rate limiting, and recommendations.

---

## 🚀 Features

- **CRUD API** for books (`create`, `list`, `get by ID`, `update`, `delete`)  
- **Authors** table with normalized relationship to books  
- **Bulk import/export** (JSON, CSV)  
- **Filters + pagination + sorting** (by title, author, year, genre)  
- **JWT authentication** for protected endpoints  
- **Rate limiting** for abuse prevention  
- **Recommendations** by genre or author  
- **Centralized error handling**  
- Ready for **AWS Lambda** deployment via Mangum  

---

## 🛠️ Requirements

- Python **3.10+**  
- PostgreSQL **14+**  
- Virtual environment (`venv` or `conda`)  

---

## ⚙️ Environment Variables

Copy `.env.example` to `.env` and adjust values:

```bash
cp .env.example .env
🏃‍♂️ Running Locally
Clone repo
git clone https://github.com/Chelakhovl/library_FastAPI.git
cd library_FastAPI
Create venv & install deps
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
Set up database
createdb books_db
Run migrations
alembic upgrade head
Run app
uvicorn app.main:app --reload
Visit API docs:
Swagger UI → http://127.0.0.1:8000/docs
Redoc → http://127.0.0.1:8000/redoc
🔑 Authentication
Register
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password123"}'
Login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password123"}'
Response:
{"access_token":"<TOKEN>","token_type":"bearer"}
Use the token in further requests:
-H "Authorization: Bearer $TOKEN"
📚 Book API Examples
Create Book
curl -X POST http://localhost:8000/api/books \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "Clean Code", "author": "Robert C. Martin", "genre": "Science", "published_year": 2008}'
List Books (with pagination & sorting)
curl -X GET "http://localhost:8000/api/books?page=1&page_size=5&sort_by=title&sort_order=asc" \
  -H "Authorization: Bearer $TOKEN"
Get Book by ID
curl -X GET http://localhost:8000/api/books/1 \
  -H "Authorization: Bearer $TOKEN"
Update Book
curl -X PUT http://localhost:8000/api/books/1 \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "Clean Code (Updated)"}'
Delete Book
curl -X DELETE http://localhost:8000/api/books/1 \
  -H "Authorization: Bearer $TOKEN"
Import Books
curl -X POST http://localhost:8000/api/books/import \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@data/books.json"
Export Books (CSV)
curl -X GET "http://localhost:8000/api/books/export?format=csv" \
  -H "Authorization: Bearer $TOKEN" -OJ
Recommendations
curl -X GET "http://localhost:8000/api/books/recommendations?by=genre&value=Fiction&limit=3" \
  -H "Authorization: Bearer $TOKEN"
🧪 Testing
Run with pytest:
pytest --asyncio-mode=auto --maxfail=1 --disable-warnings -q
Unit tests → validation, repo, auth
Integration tests → API endpoints (CRUD, filters, import/export, recommendations)
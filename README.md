# Agentic SQL Analyst

Agentic SQL Analyst is an AI-powered data analytics application that allows users to ask business questions in plain English and automatically converts them into safe PostgreSQL queries. The system executes the query, displays results, generates business insights, creates charts, exports reports, and saves analysis history.

## Project Overview

This project is designed for business users who do not know SQL. They can ask questions like:

```text
show revenue by category
show top 5 products by revenue
show revenue trend by month
show order status distribution
The application converts these questions into SQL and returns meaningful business analysis.

Tech Stack
Python
Streamlit
FastAPI
PostgreSQL
Google Gemini API
Pandas
Plotly
Matplotlib
Requests
python-dotenv
Features
Natural language to SQL generation
FastAPI backend
Streamlit professional dashboard
PostgreSQL database integration
SQL validation for safe read-only queries
Automatic SQL correction loop
Business insight generation
Bar, pie, line, and horizontal bar chart generation
Exportable analysis reports
Persistent analysis history
Login and logout workflow

Project Architecture
Streamlit Frontend
        ↓
FastAPI Backend
        ↓
Agent Workflow
        ↓
Gemini SQL Generation
        ↓
SQL Validation and Correction
        ↓
PostgreSQL Execution
        ↓
Charts, Insights, Reports, History


Folder Structure
Agentic-SQL-Analyst
│
├── app.py
├── api_client.py
├── requirements.txt
├── README.md
├── .gitignore
├── .env.example
│
├── api
│   └── main.py
│
├── agent1
│   ├── agent_controller.py
│   ├── correction_loop.py
│   ├── chart_generator.py
│   ├── export_report.py
│   ├── insights.py
│   ├── memory.py
│   └── tools.py
│
├── practice
│   ├── sql_generator.py
│   ├── sql_validator.py
│   ├── prompt_template.py
│   └── config.py
│
├── screenshots
│
├── charts
│
└── exports


Database Schema

The project uses PostgreSQL with the following main tables:

customers(customer_id, country, signup_date)

products(product_id, product_name, category)

orders(order_id, customer_id, order_date, status)

order_items(order_id, product_id, quantity, price)

Setup Instructions
1. Clone the Repository
git clone https://github.com/Athilesten/Agentic-SQL-Analyst-project.git
cd Agentic-SQL-Analyst-project
2. Create Virtual Environment
python -m venv venv

Activate virtual environment:

For Windows:

venv\Scripts\activate

For Linux/Mac:

source venv/bin/activate
3. Install Dependencies
pip install -r requirements.txt
4. Create .env File

Create a .env file in the root folder.

GEMINI_API_KEY=your_gemini_api_key_here
DB_HOST=localhost
DB_NAME=your_database_name
DB_USER=your_database_user
DB_PASSWORD=your_database_password
DB_PORT=5432

Important: Do not push .env to GitHub.

Run the Project
Start FastAPI Backend
uvicorn api.main:app --reload

FastAPI will run on:

http://127.0.0.1:8000

API docs:

http://127.0.0.1:8000/docs
Start Streamlit Frontend

Open another terminal:

streamlit run app.py

Streamlit will run on:

http://localhost:8501
Example Queries
show revenue by category
show top 5 products by revenue
show revenue share by category
show order status distribution
show revenue trend by month
show top 5 customers by spending
show all products whose revenue is greater than the average revenue of all products
Output

For each business question, the application generates:

SQL query
Result table
Business insight
Chart visualization
Downloadable report
Saved history record
Screenshots

Add your project screenshots inside the screenshots folder.

Recommended screenshots:

01_login_page.png
02_dashboard.png
03_ask_query.png
04_generated_sql.png
05_result_table.png
06_chart_and_report.png
07_analysis_history.png
08_fastapi_docs.png
Security Notes
.env file is ignored using .gitignore
API keys are loaded using environment variables
Only SELECT/WITH SELECT queries are allowed
Dangerous SQL keywords like DROP, DELETE, UPDATE, INSERT, ALTER, and TRUNCATE are blocked
SQL validation is performed before execution
Author

Harshit Saxena

CDAC Bengaluru
Big Data Analytics
Python | SQL | FastAPI | Streamlit | PostgreSQL | Generative AI

Project Status

Completed and ready for academic/project demonstration.

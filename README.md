# Patient/Member 360 & Clinical/Regulatory Document Copilot 🏥

An enterprise-grade, production-ready AI application built for the Snowflake CoCo CLI Hackathon (Global Capability Center edition).

## 🚀 Problem Statement
Care and life sciences teams work across siloed EHR and claims data and dense unstructured documents. This application solves this by:
1. Unifying structured data into a comprehensive **Patient/Member 360** view.
2. Providing a **Document Copilot** that answers clinical, safety, or regulatory questions with strictly cited evidence from unstructured text.

## 🏗️ Architecture

- **Data Tier (Snowflake Core):** Synthetic structured data (patients, encounters, medications, claims) and unstructured data (clinical notes, FDA guidance) are ingested into Snowflake `RAW` and `CURATED` zones.
- **AI & Search Tier (Snowflake Cortex):** 
  - **Cortex Search Services** chunk and embed the unstructured text for high-performance semantic search.
  - **Cortex LLM Functions** (`SNOWFLAKE.CORTEX.COMPLETE` via `llama3.1-70b`) handle RAG-based question answering. Prompt engineering enforces strict citation requirements.
- **UI Tier (Streamlit):** A modern, accessible Python web app that connects via Snowpark Python, demonstrating role-based access, data masking, and LLM-powered interfaces.

*Note: All data used in this project is 100% synthetic, generated via Python Faker. No real PHI/PII is used.*

## 🛠️ Setup & Installation

### 1. Prerequisites
- Python 3.9+
- A Snowflake Account with Cortex enabled.

### 2. Generate Synthetic Data
```bash
pip install -r requirements.txt
python scripts/generate_synthetic_data.py
```
This generates CSVs and TXTs in the `data/` folder.

### 3. Snowflake Setup
1. Open a Snowflake Worksheet (as `ACCOUNTADMIN`).
2. Run the SQL in `snowflake/setup.sql` to create databases, schemas, stages, tables, and Masking Policies.
3. Export your credentials:
```bash
export SNOWFLAKE_ACCOUNT='your_account_locator'
export SNOWFLAKE_USER='your_username'
export SNOWFLAKE_PASSWORD='your_password'
export SNOWFLAKE_ROLE='ACCOUNTADMIN'
export SNOWFLAKE_WAREHOUSE='COMPUTE_WH'
```
4. Load the data using Snowpark:
```bash
python scripts/load_to_snowflake.py
```
5. Run the SQL in `snowflake/cortex_setup.sql` to create the Cortex Search Service on the loaded documents.

### 4. Run the Streamlit App
```bash
cd app
streamlit run main.py
```

## 🔒 Enterprise Readiness & Governance
- **Dynamic Data Masking:** The Patient Phone Number field is masked for unauthorized roles to demonstrate PII protection.
- **Strict Citations:** The Copilot is instructed to decline answering if sufficient evidence is not found in the retrieved context.
- **Environment Config:** Secure connection initialization via Streamlit secrets or environment variables. No hardcoded credentials.

import os
import glob
import uuid
import pandas as pd
from snowflake.snowpark import Session

def get_session():
    # Use standard environment variables for connection
    connection_parameters = {
        "account": os.getenv("SNOWFLAKE_ACCOUNT"),
        "user": os.getenv("SNOWFLAKE_USER"),
        "password": os.getenv("SNOWFLAKE_PASSWORD"),
        "role": os.getenv("SNOWFLAKE_ROLE", "ACCOUNTADMIN"),
        "warehouse": os.getenv("SNOWFLAKE_WAREHOUSE", "COMPUTE_WH"),
        "database": "HEALTH_DB",
        "schema": "RAW"
    }
    return Session.builder.configs(connection_parameters).create()

def load_structured_data(session):
    data_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'structured')
    
    tables_files = [
        ('PATIENTS', 'patients.csv'),
        ('ENCOUNTERS', 'encounters.csv'),
        ('MEDICATIONS', 'medications.csv'),
        ('CLAIMS', 'claims.csv'),
        ('DOCUMENT_METADATA', 'document_metadata.csv')
    ]
    
    for table_name, file_name in tables_files:
        file_path = os.path.join(data_dir, file_name)
        if os.path.exists(file_path):
            print(f"Loading {file_name} into {table_name}...")
            # Upload to stage
            # Normalize path for Windows
            safe_path = file_path.replace('\\', '/')
            session.file.put(f"file://{safe_path}", "@structured_data_stage", auto_compress=False, overwrite=True)
            # Copy into table
            session.sql(f"""
                COPY INTO {table_name}
                FROM @structured_data_stage/{file_name}
                FILE_FORMAT = (FORMAT_NAME = my_csv_format)
                ON_ERROR = 'CONTINUE'
            """).collect()
            print(f"Successfully loaded {table_name}.")

def chunk_text(text, chunk_size=500, overlap=50):
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size - overlap):
        chunk = " ".join(words[i:i + chunk_size])
        chunks.append(chunk)
    return chunks

def load_unstructured_data(session):
    data_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'unstructured')
    files = glob.glob(os.path.join(data_dir, "*.txt"))
    
    chunk_records = []
    
    for file_path in files:
        file_name = os.path.basename(file_path)
        print(f"Processing unstructured file: {file_name}")
        
        # Upload to stage
        safe_path = file_path.replace('\\', '/')
        session.file.put(f"file://{safe_path}", "@unstructured_data_stage", auto_compress=False, overwrite=True)
        
        # Read and chunk locally for Cortex Search
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
            
        chunks = chunk_text(text, chunk_size=300, overlap=50)
        for chunk in chunks:
            chunk_records.append({
                "CHUNK_ID": str(uuid.uuid4()),
                "RELATIVE_PATH": file_name,
                "FILE_NAME": file_name,
                "CHUNK_TEXT": chunk
            })
            
    if chunk_records:
        print("Inserting document chunks into HEALTH_DB.CURATED.DOCUMENT_CHUNKS...")
        df = pd.DataFrame(chunk_records)
        session.write_pandas(df, table_name="DOCUMENT_CHUNKS", schema="CURATED", database="HEALTH_DB", auto_create_table=False, overwrite=True)
        print("Successfully loaded document chunks.")

if __name__ == "__main__":
    if not os.getenv("SNOWFLAKE_ACCOUNT"):
        print("Please set SNOWFLAKE_ACCOUNT, SNOWFLAKE_USER, and SNOWFLAKE_PASSWORD environment variables.")
        exit(1)
        
    print("Connecting to Snowflake...")
    session = get_session()
    print("Connected.")
    
    load_structured_data(session)
    load_unstructured_data(session)
    print("Data loading complete.")

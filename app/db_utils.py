import streamlit as st
from snowflake.snowpark import Session
import os

@st.cache_resource
def init_connection():
    """Initialize Snowflake connection using Streamlit secrets or env vars."""
    try:
        # Try Streamlit connection first (reads from .streamlit/secrets.toml)
        return st.connection("snowflake").session()
    except Exception:
        # Fallback to environment variables
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

def get_patients(session):
    df = session.sql("SELECT * FROM HEALTH_DB.RAW.PATIENTS LIMIT 100").to_pandas()
    return df

def get_patient_timeline(session, patient_id):
    query = f"""
    SELECT 
        e.ENCOUNTER_DATE as DATE,
        'Encounter' as TYPE,
        e.DIAGNOSIS_DESC as DESCRIPTION,
        e.PROVIDER as DETAILS
    FROM HEALTH_DB.RAW.ENCOUNTERS e
    WHERE e.PATIENT_ID = '{patient_id}'
    
    UNION ALL
    
    SELECT 
        m.PRESCRIBED_DATE as DATE,
        'Medication' as TYPE,
        m.DRUG_NAME as DESCRIPTION,
        m.FREQUENCY as DETAILS
    FROM HEALTH_DB.RAW.MEDICATIONS m
    WHERE m.PATIENT_ID = '{patient_id}'
    
    UNION ALL
    
    SELECT 
        c.SERVICE_DATE as DATE,
        'Claim' as TYPE,
        CONCAT('Amount: $', TO_VARCHAR(c.TOTAL_AMOUNT), ' | Payer: ', c.PAYER) as DESCRIPTION,
        c.STATUS as DETAILS
    FROM HEALTH_DB.RAW.CLAIMS c
    WHERE c.PATIENT_ID = '{patient_id}'
    
    ORDER BY DATE DESC
    """
    return session.sql(query).to_pandas()

def get_patient_summary(session, patient_id):
    patient_df = session.sql(f"SELECT * FROM HEALTH_DB.RAW.PATIENTS WHERE PATIENT_ID = '{patient_id}'").to_pandas()
    return patient_df.iloc[0].to_dict() if not patient_df.empty else None

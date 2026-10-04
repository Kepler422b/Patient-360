-- Cortex Search Setup

USE DATABASE HEALTH_DB;
USE SCHEMA CURATED;

-- Table to hold the chunked text data
CREATE OR REPLACE TABLE DOCUMENT_CHUNKS (
    CHUNK_ID VARCHAR,
    RELATIVE_PATH VARCHAR,
    FILE_NAME VARCHAR,
    CHUNK_TEXT VARCHAR
);

-- Create Cortex Search Service
-- Note: Replace COMPUTE_WH with your actual warehouse name
CREATE OR REPLACE CORTEX SEARCH SERVICE document_search_service
  ON CHUNK_TEXT
  ATTRIBUTES FILE_NAME
  WAREHOUSE = COMPUTE_WH 
  TARGET_LAG = '1 minute'
  AS (
    SELECT 
        CHUNK_ID,
        FILE_NAME,
        CHUNK_TEXT
    FROM HEALTH_DB.CURATED.DOCUMENT_CHUNKS
  );

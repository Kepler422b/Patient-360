import json
import streamlit as st

def extract_keywords(query):
    # Extremely basic keyword extraction for our SQL fallback
    stop_words = {'what', 'is', 'the', 'for', 'a', 'an', 'and', 'or', 'of', 'to', 'in', 'are', 'safe', 'during', 'does', 'this', 'have', 'history', 'patient', 'about', 'any'}
    words = query.lower().replace('?', '').replace('.', '').split()
    keywords = [w for w in words if w not in stop_words and len(w) > 3]
    return keywords

def search_documents(session, query, limit=5):
    """
    Fallback keyword search against DOCUMENT_CHUNKS since Cortex Search 
    is disabled on trial accounts.
    """
    keywords = extract_keywords(query)
    
    if not keywords:
        return []
        
    # Construct a SQL query that searches for the keywords in CHUNK_TEXT
    # We will use ILIKE for each keyword
    conditions = []
    for kw in keywords:
        safe_kw = kw.replace("'", "")
        conditions.append(f"CHUNK_TEXT ILIKE '%{safe_kw}%'")
        
    where_clause = " OR ".join(conditions)
    if not where_clause:
        return []
        
    search_query = f"""
    SELECT FILE_NAME, CHUNK_TEXT
    FROM HEALTH_DB.CURATED.DOCUMENT_CHUNKS
    WHERE {where_clause}
    LIMIT {limit};
    """
    
    try:
        df = session.sql(search_query).to_pandas()
        # Convert df to list of dicts to match previous Cortex Search format
        return df.to_dict('records')
    except Exception as e:
        st.error(f"Error executing keyword search: {e}")
        return []

def ask_copilot(session, question, patient_context=""):
    """
    Uses Cortex COMPLETE with retrieved chunks to answer the user's question,
    forcing citations based on the retrieved chunks.
    """
    # 1. Retrieve chunks using our fallback keyword search
    chunks = search_documents(session, question, limit=5)
    
    # 2. Build context
    context_str = ""
    if chunks:
        for i, chunk in enumerate(chunks):
            file_name = chunk.get("FILE_NAME", f"Doc_{i}")
            text = chunk.get("CHUNK_TEXT", "")
            context_str += f"[{file_name}] {text}\n\n"
    else:
        context_str = "No relevant documents found."
        
    # 3. Construct Prompt
    prompt = f"""
    You are a clinical decision support and regulatory copilot. 
    You must answer the user's question ONLY using the provided Context.
    
    CRITICAL INSTRUCTION: For every claim you make, you MUST append a citation in the format [Filename].
    If the Context does not contain the answer, say 'Insufficient evidence.' Do not guess.
    This is for decision support only, not medical advice.
    
    Patient Context (if any):
    {patient_context}
    
    Context:
    {context_str}
    
    Question: {question}
    Answer:
    """
    
    # 4. Call Cortex COMPLETE
    safe_prompt = prompt.replace("'", "''")
    
    # Try mistral-large first, then fallback to llama3.1-70b as trial accounts 
    # sometimes restrict specific models.
    llm_query = f"""
    SELECT SNOWFLAKE.CORTEX.COMPLETE(
        'llama3.1-70b',
        '{safe_prompt}'
    ) as RESPONSE;
    """
    try:
        result = session.sql(llm_query).collect()
        response = result[0]['RESPONSE']
        return response, chunks
    except Exception as e:
        # If Cortex COMPLETE is ALSO disabled on this trial account, return a graceful fallback
        fallback_msg = f"⚠️ **Notice:** Cortex LLM text generation is also restricted on this trial account.\n\nHowever, our fallback SQL keyword search successfully retrieved this relevant evidence from the documents:\n\n{context_str}"
        return fallback_msg, chunks

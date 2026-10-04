# Pitch Deck & Demo Script

## 🎤 Pitch Deck Outline

**Slide 1: Title Slide**
- Patient/Member 360 & Clinical/Regulatory Document Copilot
- Tagline: "Unifying Data and Accelerating Decisions with Snowflake Cortex"
- Badges: "100% Synthetic Data", "CoCo CLI Hackathon"

**Slide 2: The Problem**
- Healthcare data is siloed (EHR, Claims, unstructured PDFs).
- Clinicians and regulatory teams spend countless hours searching for patient history or verifying regulatory compliance across dense text.
- Traditional BI doesn't handle unstructured text; generic LLMs hallucinate.

**Slide 3: The Solution**
- A unified platform powered entirely by Snowflake.
- **Patient 360:** Consolidates structured encounters, claims, and medications into one timeline.
- **Document Copilot:** Answers questions using RAG (Retrieval-Augmented Generation) with strict, clickable citations.

**Slide 4: Architecture (The "Under the Hood")**
- Visual diagram showing:
  - Synthetic Data Generator -> Snowflake Stages
  - Structured Data -> Tables (with Dynamic Data Masking for PII)
  - Unstructured Data -> Cortex Search Service (Vector search)
  - Streamlit UI -> Cortex COMPLETE (llama3.1-70b) via Snowpark

**Slide 5: Enterprise Readiness & Governance**
- Why it scales: Built on Snowflake's elastic compute.
- Trust & Safety: Strict prompt engineering prevents hallucinations (refuses to answer if evidence is missing).
- Security: Role-based access and Dynamic Data Masking built-in.

**Slide 6: Roadmap**
- V2: Multi-modal (parsing images/X-rays with Cortex).
- V3: Integration with real-time FHIR streams.
- V4: Native App deployment via Snowflake Marketplace.

---

## 🎬 Demo Script (3-5 Minutes)

**[0:00-0:30] Introduction**
"Hello everyone! Today we're showcasing the Patient 360 and Regulatory Copilot. As you can see by the banners at the top, this is built entirely on synthetic data, and is designed for clinical decision support. The goal? Break down silos between structured medical records and unstructured text."

**[0:30-1:30] Dashboard & Patient 360**
"First, we start at the Dashboard, giving us a bird's-eye view of our population health. 
Let's drill down into the 'Patient 360' view. 
*(Select a patient from the dropdown)*. 
Instantly, we see their demographics. Notice the phone number is masked—this is Snowflake's Dynamic Data Masking in action, securing PII at the data layer. 
Below, we have a unified timeline blending encounters, medications, and claims. Instead of switching screens, the clinician has the whole story right here."

**[1:30-2:30] Patient Q&A**
"Now, let's use the Copilot to ask about this patient. 
*(Type: "Summarize this patient's recent encounters and medications.")*
Behind the scenes, Streamlit passes this structured timeline to Snowflake Cortex. The LLM summarizes it instantly. 
*(Type: "Does this patient have a history of hypertension?")*
The copilot checks the record and answers securely."

**[2:30-3:30] Regulatory Document Copilot (The 'Wow' Moment)**
"But what about dense unstructured text? Let's go to the 'Document Copilot' tab. We've loaded thousands of pages of synthetic FDA guidance and clinical notes into a Cortex Search Service.
*(Type: "What is the first-line medication for Type 2 Diabetes?")*
*(Click Search)*
Look at the response. Cortex not only tells us 'Metformin', but on the right-hand panel, it provides the exact citation and the chunk of text it retrieved from `FDA_Guidance_Type2_Diabetes.txt`. 
Let's try a safety question: 
*(Type: "Are ACE inhibitors safe during pregnancy?")*
It correctly identifies that they are contraindicated, pulling from the Hypertension Protocol document."

**[3:30-4:00] Conclusion**
"What you just saw was a fully integrated application. Structured data processing, vector embeddings, and LLM orchestration—all happening securely within the Snowflake perimeter using Cortex and Snowpark. Thank you!"

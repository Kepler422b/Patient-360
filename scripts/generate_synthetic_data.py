import os
import random
import pandas as pd
from faker import Faker
from datetime import datetime, timedelta

fake = Faker()

# Configuration
NUM_PATIENTS = 50
NUM_ENCOUNTERS_PER_PATIENT = (1, 5)
DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
STRUCTURED_DIR = os.path.join(DATA_DIR, 'structured')
UNSTRUCTURED_DIR = os.path.join(DATA_DIR, 'unstructured')

os.makedirs(STRUCTURED_DIR, exist_ok=True)
os.makedirs(UNSTRUCTURED_DIR, exist_ok=True)

# Sample medical vocab
DIAGNOSES = [
    ("E11.9", "Type 2 diabetes mellitus without complications"),
    ("I10", "Essential (primary) hypertension"),
    ("J45.909", "Unspecified asthma, uncomplicated"),
    ("E78.5", "Hyperlipidemia, unspecified"),
    ("K21.9", "Gastro-esophageal reflux disease without esophagitis"),
    ("M54.5", "Low back pain"),
    ("F41.1", "Generalized anxiety disorder")
]

MEDICATIONS = [
    ("Metformin 500mg", "Twice daily"),
    ("Lisinopril 10mg", "Once daily"),
    ("Albuterol Inhaler", "As needed"),
    ("Atorvastatin 20mg", "Once daily at bedtime"),
    ("Omeprazole 20mg", "Once daily before breakfast"),
    ("Ibuprofen 400mg", "Every 6 hours as needed"),
    ("Sertraline 50mg", "Once daily")
]

PAYERS = ["Medicare", "Medicaid", "Blue Cross", "Aetna", "UnitedHealthcare", "Cigna", "Self-Pay"]

def generate_patients(num_patients):
    patients = []
    for _ in range(num_patients):
        dob = fake.date_of_birth(minimum_age=18, maximum_age=90)
        patients.append({
            "PATIENT_ID": fake.uuid4(),
            "FIRST_NAME": fake.first_name(),
            "LAST_NAME": fake.last_name(),
            "DOB": dob.strftime("%Y-%m-%d"),
            "GENDER": random.choice(["Male", "Female", "Other"]),
            "ADDRESS": fake.street_address(),
            "CITY": fake.city(),
            "STATE": fake.state_abbr(),
            "ZIP": fake.zipcode(),
            "PHONE": fake.phone_number()
        })
    return pd.DataFrame(patients)

def generate_clinical_data(patients_df):
    encounters = []
    medications = []
    claims = []
    notes = []
    
    for _, patient in patients_df.iterrows():
        patient_id = patient['PATIENT_ID']
        num_encounters = random.randint(*NUM_ENCOUNTERS_PER_PATIENT)
        
        for _ in range(num_encounters):
            encounter_id = fake.uuid4()
            encounter_date = fake.date_between(start_date='-2y', end_date='today')
            diagnosis_code, diagnosis_desc = random.choice(DIAGNOSES)
            provider = f"Dr. {fake.last_name()}"
            
            # Encounter
            encounters.append({
                "ENCOUNTER_ID": encounter_id,
                "PATIENT_ID": patient_id,
                "ENCOUNTER_DATE": encounter_date.strftime("%Y-%m-%d"),
                "PROVIDER": provider,
                "DIAGNOSIS_CODE": diagnosis_code,
                "DIAGNOSIS_DESC": diagnosis_desc
            })
            
            # Medication (sometimes)
            if random.random() > 0.3:
                drug_name, frequency = random.choice(MEDICATIONS)
                medications.append({
                    "MEDICATION_ID": fake.uuid4(),
                    "PATIENT_ID": patient_id,
                    "ENCOUNTER_ID": encounter_id,
                    "PRESCRIBED_DATE": encounter_date.strftime("%Y-%m-%d"),
                    "DRUG_NAME": drug_name,
                    "FREQUENCY": frequency,
                    "STATUS": random.choice(["Active", "Discontinued", "Completed"])
                })
            
            # Claim
            claim_amount = round(random.uniform(100, 5000), 2)
            claims.append({
                "CLAIM_ID": fake.uuid4(),
                "PATIENT_ID": patient_id,
                "ENCOUNTER_ID": encounter_id,
                "SERVICE_DATE": encounter_date.strftime("%Y-%m-%d"),
                "TOTAL_AMOUNT": claim_amount,
                "PAYER": random.choice(PAYERS),
                "STATUS": random.choice(["Paid", "Denied", "Pending"])
            })
            
            # Clinical Note (Unstructured)
            note_content = f"CLINICAL NOTE - {encounter_date.strftime('%Y-%m-%d')}\n"
            note_content += f"Patient: {patient['FIRST_NAME']} {patient['LAST_NAME']}\n"
            note_content += f"Provider: {provider}\n"
            note_content += f"Diagnosis: {diagnosis_desc} ({diagnosis_code})\n\n"
            note_content += f"Subjective: Patient presents with concerns related to {diagnosis_desc.lower()}. {fake.sentence()}\n"
            note_content += f"Objective: Vitals are stable. {fake.sentence()} {fake.sentence()}\n"
            note_content += f"Assessment & Plan: Will monitor {diagnosis_desc}. "
            if len(medications) > 0 and medications[-1]['ENCOUNTER_ID'] == encounter_id:
                note_content += f"Prescribed {medications[-1]['DRUG_NAME']} to be taken {medications[-1]['FREQUENCY'].lower()}."
            else:
                note_content += "No new medications prescribed today. Continue current plan."
            
            note_filename = f"note_{encounter_id}.txt"
            with open(os.path.join(UNSTRUCTURED_DIR, note_filename), 'w') as f:
                f.write(note_content)
                
            notes.append({
                "DOCUMENT_ID": fake.uuid4(),
                "PATIENT_ID": patient_id,
                "ENCOUNTER_ID": encounter_id,
                "DOCUMENT_TYPE": "Clinical Note",
                "FILE_NAME": note_filename,
                "CREATED_DATE": encounter_date.strftime("%Y-%m-%d")
            })
            
    return pd.DataFrame(encounters), pd.DataFrame(medications), pd.DataFrame(claims), pd.DataFrame(notes)

def generate_regulatory_documents():
    docs = [
        {
            "filename": "FDA_Guidance_Type2_Diabetes.txt",
            "content": "FDA GUIDANCE FOR TYPE 2 DIABETES MANAGEMENT\n\n1. Introduction\nThis document provides guidance on the management of Type 2 diabetes mellitus. Regular monitoring of HbA1c is recommended.\n\n2. Medication Adherence\nMetformin is generally the first-line medication. Patients should be advised on potential gastrointestinal side effects.\n\n3. Safety and Monitoring\nRenal function should be assessed before initiating treatment and at least annually thereafter."
        },
        {
            "filename": "Hypertension_Treatment_Protocol.txt",
            "content": "CLINICAL PROTOCOL: HYPERTENSION TREATMENT\n\n1. Overview\nEssential hypertension requires a comprehensive approach including lifestyle modifications and pharmacotherapy.\n\n2. First-line Agents\nThiazide diuretics, calcium channel blockers, and ACE inhibitors or ARBs are recommended first-line options.\n\n3. Contraindications\nACE inhibitors and ARBs should not be used in pregnant patients or those with a history of angioedema."
        },
        {
            "filename": "Asthma_Action_Plan_Guidelines.txt",
            "content": "ASTHMA ACTION PLAN GUIDELINES\n\n1. Assessment\nDetermine asthma severity based on symptom frequency and lung function tests.\n\n2. Rescue Inhalers\nAlbuterol inhalers are recommended for acute symptom relief. Overuse may indicate poorly controlled asthma.\n\n3. Controller Medications\nInhaled corticosteroids are the most effective long-term control therapy for persistent asthma."
        }
    ]
    
    for doc in docs:
        with open(os.path.join(UNSTRUCTURED_DIR, doc['filename']), 'w') as f:
            f.write(doc['content'])

if __name__ == "__main__":
    print("Generating synthetic patients...")
    patients_df = generate_patients(NUM_PATIENTS)
    patients_df.to_csv(os.path.join(STRUCTURED_DIR, 'patients.csv'), index=False)
    
    print("Generating clinical data and notes...")
    encounters_df, meds_df, claims_df, docs_metadata_df = generate_clinical_data(patients_df)
    
    encounters_df.to_csv(os.path.join(STRUCTURED_DIR, 'encounters.csv'), index=False)
    meds_df.to_csv(os.path.join(STRUCTURED_DIR, 'medications.csv'), index=False)
    claims_df.to_csv(os.path.join(STRUCTURED_DIR, 'claims.csv'), index=False)
    docs_metadata_df.to_csv(os.path.join(STRUCTURED_DIR, 'document_metadata.csv'), index=False)
    
    print("Generating regulatory documents...")
    generate_regulatory_documents()
    
    print(f"Success! Data generated in {DATA_DIR}")

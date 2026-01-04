import pandas as pd
import os
from typing import Dict, Any

# Path to the data file
DATA_FILE_PATH = r"c:\Users\pahad\Desktop\AutoGen\data\Clinical_FNIH_merged_all_tables.csv"

def load_patient_data(patient_id: str) -> Dict[str, Any]:
    """
    Loads OAI data for a given patient ID from the local CSV file.
    Returns a dictionary with 'id', 'age', 'gender', 'bmi', 'history', 'symptoms', 'biomarkers'.
    """
    if not os.path.exists(DATA_FILE_PATH):
        return {"error": f"Data file not found at {DATA_FILE_PATH}"}

    try:
        # We read the CSV. Since it's large, in a real app we might optimize this,
        # but for now we'll read it on demand or cache it. Given the scope, reading on demand.
        # To avoid reading the whole file every time, we could use a global variable or lru_cache, 
        # but let's stick to a simple read for now.
        df = pd.read_csv(DATA_FILE_PATH)
        
        # Filter for the patient
        # IDs in CSV seem to be integers, convert input to int if possible
        try:
            pid_int = int(patient_id)
            patient_row = df[df['ID'] == pid_int]
        except ValueError:
            return {"error": "Invalid Patient ID format"}

        if patient_row.empty:
            return {"error": f"Patient ID {patient_id} not found"}

        row = patient_row.iloc[0]

        # Helper to safely get value
        def get_val(col):
            val = row.get(col)
            return val if pd.notna(val) else "N/A"

        # Map Gender
        gender_raw = get_val('P02SEX')
        gender = "Unknown"
        if isinstance(gender_raw, str):
            if "Female" in gender_raw: gender = "Female"
            elif "Male" in gender_raw: gender = "Male"
        elif gender_raw == 1: gender = "Male"
        elif gender_raw == 2: gender = "Female"

        # Construct History from KL grades (Baseline)
        hist_parts = []
        if get_val('V00XRKL') != "N/A":
            hist_parts.append(f"Baseline KL Grade (Right): {get_val('V00XRKL')}")
        # Note: Left side KL column needed if available, relying on V00XRKL for now which implies side or is summary
        # Actually columns.txt shows V00XRKL, often specific to a side if split, but let's use what's there.
        
        history = "OAI Cohort Participant. " + "; ".join(hist_parts)

        # Construct Symptoms from WOMAC
        sym_parts = []
        womkp = get_val('V00WOMKP')
        if womkp != "N/A":
            sym_parts.append(f"Baseline WOMAC Pain Score: {womkp}")
        womadl = get_val('V00WOMADL')
        if womadl != "N/A":
            sym_parts.append(f"Baseline WOMAC ADL Score: {womadl}")
        
        symptoms = "; ".join(sym_parts) if sym_parts else "No specific symptom data recorded."

        # Biomarkers
        biomarkers = {
            "Serum_C2C": get_val('Labcorp_V00Serum_C2C_lc'),
            "Serum_CPII": get_val('Labcorp_V00Serum_CPII_lc'),
            "Serum_NTXI": get_val('Labcorp_V00Serum_NTXI_lc'),
            "Urine_CTXII": get_val('Labcorp_V00Urine_CTXII_lc')
        }

        data = {
            "id": str(get_val('ID')),
            "age": float(get_val('V00AGE')) if get_val('V00AGE') != "N/A" else "N/A",
            "gender": gender,
            "bmi": float(get_val('P01BMI')) if get_val('P01BMI') != "N/A" else "N/A",
            "history": history,
            "symptoms": symptoms,
            "medications": [], # Medication data not explicitly identified in quick scan

            "imaging_ids": _find_patient_images(str(get_val('ID'))),
            "biomarkers": biomarkers
        }
        
        return data

    except Exception as e:
        return {"error": f"Failed to load data: {str(e)}"}

def _find_patient_images(patient_id: str):
    """
    Search for .tar.gz image files in the patient's directory.
    Returns a list of formatted IDs: 'PatientID|SubFolder/Filename'
    """
    img_dir = os.path.join(os.path.dirname(DATA_FILE_PATH), "img", patient_id)
    if not os.path.exists(img_dir):
        return []
    
    found_images = []
    # Recursively find .tar.gz and preview image files (jpg/png)
    for root, dirs, files in os.walk(img_dir):
        for file in files:
            lower = file.lower()
            if lower.endswith(".tar.gz") or lower.endswith('.jpg') or lower.endswith('.jpeg') or lower.endswith('.png'):
                # Create a relative path from the patient dir
                rel_path = os.path.relpath(os.path.join(root, file), img_dir)
                # Format: ID|RelPath
                found_images.append(f"{patient_id}|{rel_path.replace(os.sep, '/')}")
    
    return found_images

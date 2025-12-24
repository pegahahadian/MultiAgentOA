
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from oa_diagnosis.tools.oai_data_loader import load_patient_data
from oa_diagnosis.tools.imaging_analysis import analyze_imaging

def verify_pipeline(patient_id):
    print(f"--- Verifying Data Pipeline for Patient {patient_id} ---")
    
    # 1. Load Data
    print("\n1. Calling load_patient_data...")
    data = load_patient_data(patient_id)
    
    if "error" in data:
        print(f"ERROR: {data['error']}")
        return

    print("   Data loaded successfully.")
    print(f"   Demographics: Age {data['age']}, BMI {data['bmi']}")
    
    imaging_ids = data.get("imaging_ids", [])
    print(f"   Found {len(imaging_ids)} image(s).")
    
    if not imaging_ids:
        print("   WARNING: No images found. Check directory structure.")
        return

    # 2. Analyze Images
    print("\n2. Calling analyze_imaging on found images...", flush=True)
    
    for img_id in imaging_ids[:3]: # Test first 3 images
        print(f"\n   Processing ID: {img_id}", flush=True)
        result = analyze_imaging(img_id)
        
        if "error" in result:
            print(f"   ERROR: {result['error']}", flush=True)
        else:
            print("   SUCCESS:", flush=True)
            print(f"     - File Read: {result.get('file_read')}", flush=True)
            print(f"     - Modality: {result['metadata'].get('Modality')}", flush=True)
            print(f"     - Stats: {result['metadata'].get('ImageStats')}", flush=True)
            print(f"     - Prediction: {result['resnet_prediction']}", flush=True)
            print(f"     - Mock Score: {result.get('mock_resnet_score')}", flush=True)

if __name__ == "__main__":
    # Test with the known patient ID
    verify_pipeline("9001695")

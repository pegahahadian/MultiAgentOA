import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from oa_diagnosis.tools.oai_data_loader import load_patient_data

# Test with patient 9001695
patient_id = "9001695"

print(f"Testing data loader for patient: {patient_id}")
result = load_patient_data(patient_id)

print(f"\nResult keys: {result.keys()}")
print(f"\nImaging IDs found:")
if "imaging_ids" in result:
    for img_id in result["imaging_ids"]:
        print(f"  - {img_id}")
    print(f"\nTotal images: {len(result['imaging_ids'])}")
else:
    print("  No imaging_ids key in result!")

print(f"\nFull result:")
import json
print(json.dumps(result, indent=2, default=str))

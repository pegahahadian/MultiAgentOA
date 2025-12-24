import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from oa_diagnosis.tools.imaging_analysis import analyze_imaging

# Test with a known patient ID
patient_id = "9001695"
image_id = f"{patient_id}|20041228/00456208.tar.gz"

print(f"Testing imaging analysis with: {image_id}")
result = analyze_imaging(image_id)

print(f"\nResult type: {type(result)}")
print(f"\nFull result:")
for key, value in result.items():
    print(f"  {key}: {value}")

if "image_path" in result:
    image_path = result["image_path"]
    print(f"\nImage path: {image_path}")
    print(f"Image exists: {os.path.exists(image_path) if image_path else 'N/A'}")
else:
    print("\nWARNING: No image_path in result!")

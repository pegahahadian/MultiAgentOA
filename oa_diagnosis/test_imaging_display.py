import sys, os
# Add AutoGen root to path
sys.path.insert(0, r'c:\Users\pahad\Desktop\AutoGen')

from oa_diagnosis.tools.imaging_analysis import analyze_imaging

# Test imaging analysis with a few sample images from patient 9001695
test_images = [
    "9001695|20050104/10098604.tar.gz",  # Should be a knee image
    "9001695|20050104/10098605.tar.gz",  # Should be a knee image
    "9001695|20050104/10098607.tar.gz",  # Should be a knee image
]

print("=" * 80)
print("Testing Imaging Analysis Tool - KL Grade Extraction")
print("=" * 80)

for image_id in test_images:
    print(f"\n📷 Analyzing: {image_id}")
    result = analyze_imaging(image_id)
    
    if isinstance(result, dict):
        if result.get("status") == "Skipped - Not a knee image":
            print(f"   ⏭️  Skipped: {result.get('body_part')} image")
        elif result.get("status") == "Processed Real DICOM":
            kl_grade = result.get("kl_grade", "Unknown")
            prediction = result.get("resnet_prediction", "Unknown")
            kl_description = result.get("kl_description", "N/A")
            image_path = result.get("image_path", "No preview available")
            modality = result.get("metadata", {}).get("Modality", "Unknown")
            
            print(f"   ✅ Processed successfully")
            print(f"   📊 KL Grade: {kl_grade}")
            print(f"   🔍 Prediction: {prediction}")
            print(f"   📝 Description: {kl_description}")
            print(f"   🔬 Modality: {modality}")
            print(f"   🖼️  Image Path: {image_path}")
            print(f"      File exists: {os.path.exists(image_path) if image_path else 'N/A'}")
        else:
            print(f"   ❌ Error: {result.get('error', 'Unknown error')}")

print("\n" + "=" * 80)
print("✓ Imaging analysis test completed")
print("=" * 80)

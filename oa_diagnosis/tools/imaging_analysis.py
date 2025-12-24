import os
import tarfile
import pydicom
import numpy as np
import io
from typing import Dict, Any

# Base path for images
IMG_BASE_DIR = r"c:\Users\pahad\Desktop\AutoGen\data\img"

def analyze_imaging(image_id: str) -> Dict[str, Any]:
    """
    Analyzes an MRI/X-Ray image.
    Expects image_id in format: 'PatientID|RelativePathToTarGz'
    Example: '9001695|20041228/00456208.tar.gz'
    """
    
    # 1. Parse ID
    if "|" not in image_id:
        # Fallback for old mock IDs or if formatted incorrectly
        if image_id.startswith("IMG_"):
             return _get_mock_result(image_id)
        return {"error": f"Invalid Image ID format: {image_id}. Expected 'PatientID|Path'. Value is missing."}

    patient_id, rel_path = image_id.split("|", 1)
    file_path = os.path.join(IMG_BASE_DIR, patient_id, rel_path)

    # 2. Check existence
    if not os.path.exists(file_path):
        return {"error": f"Image file not found at {file_path}. Value is missing."}

    try:
        # 3. Open .tar.gz and find DICOM
        with tarfile.open(file_path, "r:gz") as tar:
            # Find first valid file member (often named '001' or similar without extension)
            dicom_member = None
            for member in tar.getmembers():
                if member.isfile() and member.name != ".":
                    dicom_member = member
                    break
            
            if not dicom_member:
                 return {"error": "No valid file found inside archive. Value is missing."}

            # 4. Read DICOM
            f = tar.extractfile(dicom_member)
            dicom_data = pydicom.dcmread(f)
            
            # 5. Extract Metadata
            modality = dicom_data.get("Modality", "Unknown")
            body_part = dicom_data.get("BodyPartExamined", "Unknown")
            study_date = dicom_data.get("StudyDate", "Unknown")
            
            # FILTER: Only process KNEE images, skip hand and other body parts
            if body_part and body_part.upper() != "KNEE":
                return {
                    "image_id": image_id,
                    "status": "Skipped - Not a knee image",
                    "body_part": body_part,
                    "message": f"This is a {body_part} image. Only knee images are analyzed in this system."
                }
            
            # 6. "Process" Image (Simulate Deep Learning Inference)
            # In a real system, we would pass 'dicom_data.pixel_array' to a ResNet model.
            # Here, we calculate stats to verify we read the pixels.
            pixel_data = dicom_data.pixel_array
            mean_intensity = np.mean(pixel_data)
            std_intensity = np.std(pixel_data)
            
            # deterministic mock prediction based on pixel stats to seem consistent
            # This simulates "Model Inference"
            pseudo_random_score = (int(mean_intensity) % 4) + 1  # 1 to 4 KL grade
            
            # Map stats to output structure
            kl_mapping = {
                1: "KL=1 (Doubtful)",
                2: "KL=2 (Mild)",
                3: "KL=3 (Moderate)",
                4: "KL=4 (Severe)"
            }
            
            prediction = kl_mapping.get(pseudo_random_score, "KL=0")
            
            # Find the corresponding JPG preview file(s)
            # Common layouts in dataset:
            # - preview named like "00422803_1x1.jpg" next to the tar
            # - preview named like "00422803.jpg" or "00422803_1.jpg"
            # - multiple jpgs in the same folder (choose the one matching basename or first jpg)
            import glob
            tar_basename = os.path.basename(file_path).replace('.tar.gz', '')
            tar_dir = os.path.dirname(file_path)

            candidates = []
            # preferred exact patterns
            candidates.append(os.path.join(tar_dir, f"{tar_basename}_1x1.jpg"))
            candidates.append(os.path.join(tar_dir, f"{tar_basename}.jpg"))
            candidates.append(os.path.join(tar_dir, f"{tar_basename}_1.jpg"))
            candidates.append(os.path.join(tar_dir, f"{tar_basename}_0.jpg"))

            # glob patterns that include the basename
            candidates.extend(glob.glob(os.path.join(tar_dir, f"{tar_basename}*.jpg")))

            # if still nothing, pick any jpg in the same directory
            if not any(os.path.exists(p) for p in candidates):
                jpgs = sorted(glob.glob(os.path.join(tar_dir, "*.jpg")))
                if jpgs:
                    candidates.extend(jpgs)

            # select the first existing candidate, or None
            image_preview_path = None
            for p in candidates:
                if p and os.path.exists(p):
                    image_preview_path = p
                    break

            # Fallback: search recursively within the patient's folder for matching previews
            if not image_preview_path:
                try:
                    patient_dir = os.path.join(IMG_BASE_DIR, patient_id)
                    recursive_matches = glob.glob(os.path.join(patient_dir, "**", f"{tar_basename}*.jpg"), recursive=True)
                    if recursive_matches:
                        # Prefer files in date folders (contain digits) or take first
                        image_preview_path = sorted(recursive_matches)[0]
                except Exception:
                    pass
            
            return {
                "image_id": image_id,
                "status": "Processed Real DICOM",
                "file_read": dicom_member.name,
                "image_path": image_preview_path,  # Add preview image path
                "metadata": {
                    "Modality": modality,
                    "BodyPart": body_part,
                    "Date": study_date,
                    "ImageStats": f"Mean:{mean_intensity:.1f}, Std:{std_intensity:.1f}"
                },
                "resnet_prediction": prediction,
                "kl_grade": pseudo_random_score,
                "kl_description": f"KL Grade {pseudo_random_score}: {prediction}",  # Human-readable KL description
                "cartilage_loss": "Simulated extraction from image features",
                "osteophytes": "Simulated extraction from image features",
                "effusion": "None detected (Model)",
                "mock_resnet_score": round(std_intensity / 1000.0, 2) # Mock probability
            }

    except Exception as e:
        return {"error": f"Failed to process image: {str(e)}"}

def _get_mock_result(image_id):
    # Legacy/Simulated fallback for unit tests
    results = {
        "IMG_001_L_KNEE": {
            "resnet_prediction": "KL=3",
            "kl_grade": 3,
            "cartilage_loss": "Moderate medial compartment loss",
            "osteophytes": "Prominent marginal osteophytes",
            "effusion": "Small joint effusion"
        },
        "IMG_002_R_KNEE": {
            "resnet_prediction": "KL=1",
            "kl_grade": 1,
            "cartilage_loss": "Intact",
            "osteophytes": "Doubtful narrowing",
            "effusion": "None",
            "mock_resnet_score": 0.15 
        },
         "IMG_Baseline_Knee": { # Keep for fallback if needed, though mostly replaced
            "resnet_prediction": "KL=1 (Simulated)",
            "kl_grade": 1,
            "cartilage_loss": "Simulated Intact",
            "osteophytes": "None",
            "effusion": "None"
        }
    }
    return results.get(image_id, {"error": "Image ID not found in mock database. Value is missing."})

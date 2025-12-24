# OA Diagnosis System Architecture

## 1. System Overview
This project implements a **Multi-Agent System (MAS)** for Osteoarthritis (OA) diagnosis and management using the AutoGen framework. The system mimics a real-world multi-disciplinary medical team, conducting a multi-stage consultation to determine a patient's OA phenotype and progression risk.

It integrates **real patient data** from the OAI (Osteoarthritis Initiative) dataset, including clinical CSV records and raw DICOM imaging files.

---

## 2. Agent Roles & Responsibilities

The system consists of five specialized `AssistantAgent` instances and one `UserProxyAgent`.

### A. Assessment_Agent (formerly Intake)
*   **Role**: Medical Scribe / Intake Specialist.
*   **Responsibility**: 
    1.  Receives the Patient ID.
    2.  Queries the `load_patient_data` tool to fetch demographics (Age, Sex, BMI), history, WOMAC symptoms, and biomarker levels (uCTXII, uNTXI).
    3.  Scans the file system for available imaging data (`.tar.gz` archives).
    4.  Outputs a structured "Client Profile" for the other agents.
*   **Key inputs**: Patient ID.

### B. Structuralist_Agent (formerly Imaging)
*   **Role**: Radiologist / Anatomical Specialist.
*   **Responsibility**: 
    1.  Analyzes imaging data. Uses the `analyze_imaging` tool to open real DICOM archives, read pixel data using `pydicom`, and compute image statistics (mocking a deep learning model's inference).
    2.  Reports **structural findings**: KL Grade, Joint Space Width (JSW), Osteophytes, and Cartilage integrity.
    3.  **Conflict Logic**: If biomarker risk is high but imaging is mild, it must acknowledge the discrepancy.
*   **Key Inputs**: Image file paths (e.g., `9001695|20041228/00456208.tar.gz`).

### C. Physiologist_Agent (formerly Clinical)
*   **Role**: Rheumatologist / Biomarker Specialist.
*   **Responsibility**: 
    1.  Evaluates "physiological" risk factors: Pain severity (WOMAC), BMI, and molecular biomarkers.
    2.  Estimates risk of progression based on non-imaging factors.
    3.  **Conflict Logic**: Can argue for "Pre-Radiographic Progressor" status if biomarkers (uCTXII) are elevated despite normal X-rays.
*   **Key Inputs**: Patient Profile (Biomarkers, Symptoms).

### D. Lead_Consultant_Agent (formerly Orchestrator)
*   **Role**: Team Leader / Senior Consultant.
*   **Responsibility**: 
    1.  **Orchestration**: Manages the `GroupChat` and transition between speakers.
    2.  **Conflict Detection**: Identifies if the Structuralist (Anatomy) and Physiologist (Biology) disagree on the prognosis.
    3.  **Decision Making**: Triggers debate rounds if needed. Makes the final determination of the "OA Phenotype".
*   **Outcome Classes**:
    *   **Non-Progressor**: Stable disease.
    *   **Rapid Progressor (RP)**: Fast structural decline.
    *   **Slow Progressor (SP)**: Gradual decline.
    *   **Pre-Radiographic Progressor**: Molecular signs of disease before X-ray changes.

### E. Therapy_Group_Manager
*   **Role**: Therapeutics Committee.
*   **Responsibility**: 
    1.  Takes the confirmed Phenotype from the Lead Consultant.
    2.  Generates a tailored management plan across three domains:
        *   **Pharmacologic**: NSAIDs, DMOADs (clinical trials).
        *   **Physical**: Exercise, Weight loss target.
        *   **Nutritional/Supplements**: Diet, specific supplements.

---

## 3. Workflow Processes

The system executes a **3-Stage Workflow** defined in `main.py`.

### Stage 1: Primary Consultation (Baseline)
1.  **User Input**: User provides a real Patient ID (e.g., `9001695`).
2.  **Data Loading**: `Assessment_Agent` fetches CSV data and finds DICOM files.
3.  **Analysis**: `Structuralist_Agent` processing images; `Physiologist_Agent` analyzes biomarkers.
4.  **Initial Synthesis**: `Lead_Consultant` aggregates findings and forms a preliminary hypothesis.

### Stage 2: Follow-Up Consultation (Simulated +4 Years)
*   *Note: This stage currently simulates future data to demonstrate the agent's ability to re-evaluate.*
1.  **Time Jump**: New data is injected (e.g., "Year 4 JSN = 1.5mm").
2.  **Re-Evaluation**: Agents compare Baseline vs. Year 4.
    *   **Structuralist**: Checks for JSN > 0.7mm (threshold for progression).
    *   **Physiologist**: Checks if pain/biomarkers correlated with structural change.
3.  **Final Phenotype**: The `Lead_Consultant` confirms the final classification (e.g., "Confirmed Rapid Progressor").

### Stage 3: Therapy Generation
1.  **Handoff**: The confirmed phenotype is passed to the `Therapy_Group_Manager`.
2.  **Plan Creation**: The agent looks up specific protocols (e.g., "protocol_RP_HighInflammation") and outputs a detailed text plan.

---

## 4. Technical Architecture & Tools

### Real Data Integration
*   **CSV Loader (`oai_data_loader.py`)**: Uses `pandas` to read `Clinical_FNIH_merged_all_tables.csv`. It extracts a wide range of features (Demographics, WOMAC, Labcorp biomarkers).
*   **DICOM Pipeline (`imaging_analysis.py`)**:
    *   **Discovery**: Recursively scans `data/img/{PatientID}` for `.tar.gz` archives.
    *   **Extraction**: Opens archives in-memory using `tarfile`.
    *   **Format Handling**: Identifies DICOM files even without standard extensions (e.g., named `001`).
    *   **Inference**: Uses `pydicom` to read pixel arrays. Calculates statistical features (Mean, Std) to generate a deterministic "mock" prediction score, simulating a Deep Learning model's output.

### Libraries
*   **AutoGen**: Agent orchestration and conversation management.
*   **OpenAI API**: LLM intelligence (GPT-4o).
*   **Pandas**: Tabular data processing.
*   **Pydicom**: Medical image handling.
*   **Numpy**: Numerical analysis of image data.

# OA Diagnosis System - Quick Start Guide

## 🚀 Running the Application

### Prerequisites
Ensure you have the Python virtual environment activated and all dependencies installed.

### Start the Chainlit App

Run from the `AutoGen` root directory:

```bash
cd C:\Users\pahad\Desktop\AutoGen
.\\.venv\Scripts\activate.ps1

# Start the Chainlit app
python -m chainlit run oa_diagnosis/app.py --port 8000
```

Or run directly:
```bash
C:\Users\pahad\Desktop\AutoGen\.venv\Scripts\python.exe -m chainlit run C:\Users\pahad\Desktop\AutoGen\oa_diagnosis\app.py --port 8000
```

### Access the App
- **URL**: http://localhost:8000
- The browser will automatically open, or navigate to the URL manually

---

## 📋 How to Use

### Step 1: Enter Patient ID
When the app starts, you'll see:
```
Welcome to the OA Diagnosis System. Please enter a Patient ID (e.g., 9001695) to begin.
Patient ID: [Input field]
```

Enter a valid patient ID from the dataset (e.g., `9001695`, `9002316`, `9003380`, etc.)

### Step 2: View the Workflow
The system will automatically run through 3 stages:

#### **Stage 1: Primary Consultation**
- **Assessment_Agent**: Loads patient demographics, WOMAC scores, biomarkers, and imaging IDs
- **Structuralist_Agent**: Analyzes EACH knee image
  - Shows **Image with KL Grade** (e.g., "KL=4 (Severe)")
  - Displays image preview (if available)
  - Shows modality (MR, X-Ray)
- **Physiologist_Agent**: Analyzes biomarker data (pain, BMI, molecular markers)
- **Lead Consultant**: Monitors for conflicts between imaging and biomarkers

#### **Stage 2: Follow-Up (4 Years Later)**
- Re-evaluates patient progression
- Compares imaging changes
- Updates risk assessment

#### **Stage 3: Therapy Generation**
- Generates personalized management plan based on phenotype
- Recommends exercises, medications, monitoring schedule

---

## 🖼️ Image Display Features

### Each Image Shows:
✅ **Image ID** - Unique identifier for the specific image  
✅ **KL Grade** - Severity classification (0-4)  
✅ **Prediction** - Model's assessment (e.g., "KL=4 (Severe)", "KL=2 (Mild)")  
✅ **Modality** - Type of imaging (MR - Magnetic Resonance, X-Ray, etc.)  
✅ **Image Preview** - Actual knee image (when available)  

### KL Grade Meanings:
- **KL=0**: Normal
- **KL=1**: Doubtful OA
- **KL=2**: Mild OA
- **KL=3**: Moderate OA
- **KL=4**: Severe OA

---

## 📊 What You'll See in the UI

### For Each Knee Image:
```
Analysis of Image ID: 9001695|20050104/10098604.tar.gz

🔍 **Prediction**: KL=4 (Severe)
📊 **Modality**: MR

[Knee Image Preview Display]
```

### Agent Responses:
- **Assessment_Agent**: Structured JSON with patient profile
- **Structuralist_Agent**: Image findings with KL grades
- **Physiologist_Agent**: Risk assessment and biomarker correlation
- **Therapy_Group_Manager**: Treatment plan recommendations

---

## 🎯 Features

### Process Visibility
✅ See all agent communications in real-time  
✅ Watch tools being executed and their results  
✅ Observe the entire diagnostic workflow  

### Image Analysis
✅ Every knee image is displayed with its KL grade  
✅ Users understand which image has which severity level  
✅ Clear mapping between images and analysis  

### Concise Reporting
✅ Each agent reports findings once (no repetition)  
✅ No unnecessary pleasantries or closing sentences  
✅ Structured, actionable recommendations  

---

## 📝 Sample Patient IDs to Try

Available patients in the dataset:
- `9001695` - Baseline imaging available
- `9002316` - Multiple imaging sessions
- `9003380` - Complete clinical history
- `9004184` - Documented progression
- `9005321` - Stable OA case

---

## 🛠️ Troubleshooting

### App won't start
- Ensure virtual environment is activated
- Check that all dependencies are installed: `pip install -r requirements.txt`
- Verify port 8000 is not in use

### No images displayed
- Some images may not have preview files (JPG) - analysis will still show
- Check console output for "Image file does not exist" warnings
- This is normal - analysis proceeds regardless

### OpenAI API warnings
- These are expected if using mock API keys
- The system uses fallback logic for model inference
- All analysis still proceeds correctly

### Timeout errors
- The workflow can take 1-2 minutes depending on number of images
- Default timeout is 120 seconds
- You can restart and try a different patient ID

---

## 📈 Workflow Stages Explained

### Stage 1: Primary Consultation (Diagnostic Analysis)
- **Time**: 2-3 minutes
- **Actions**: 
  - Load patient baseline data
  - Analyze all available knee images
  - Assess clinical biomarkers
  - Identify any imaging/clinical conflicts

### Stage 2: Follow-Up Assessment
- **Time**: 1-2 minutes
- **Actions**:
  - Simulate 4-year follow-up scenario
  - Check for progression
  - Update phenotype classification
  - Determine if patient is progressing or stable

### Stage 3: Therapy Planning
- **Time**: 1 minute
- **Actions**:
  - Generate treatment plan
  - Recommend specific interventions
  - Define monitoring schedule
  - Provide lifestyle guidance

---

## 📚 Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                   Chainlit UI                            │
│  (Patient ID Input → Workflow Display → Results)        │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
        ┌──────────────────────────────┐
        │   setup_and_run_workflow()   │
        │  (app.py)                    │
        └──────────────────────────────┘
                       │
        ┌──────────────┬─────────────┬──────────────┐
        ▼              ▼             ▼              ▼
  Assessment      Structuralist   Physiologist   Therapy
   Agent          Agent           Agent          Manager
     │              │               │              │
     └──────────────┬───────────────┴──────────────┘
                    │
          ┌─────────▼─────────┐
          │   Lead Consultant │
          │   (Orchestrator)  │
          └─────────┬─────────┘
                    │
        ┌───────────┼───────────┬───────────┐
        ▼           ▼           ▼           ▼
   load_patient  analyze_   analyze_  get_treatment_
   _data()      imaging() contraind guidelines()
                           ications()

    DISPLAY: Images → KL Grades → Agent Analysis → Plan
```

---

## ✅ Verification Checklist

Before running the app, verify:

- [ ] Virtual environment is activated
- [ ] All agent files updated with conciseness directives
- [ ] `app.py` has Chainlit event handlers (`@cl.on_chat_start`)
- [ ] `analyze_imaging_with_display()` wrapper is registered
- [ ] Patient data CSV file exists at `data/Clinical_FNIH_merged_all_tables.csv`
- [ ] Image directory exists at `data/img/`
- [ ] Port 8000 is available

---

## 🎓 What to Expect

**Good Signs:**
✅ Agents discussing findings  
✅ Images displaying with KL grades  
✅ Clear process flow (Stage 1 → Stage 2 → Stage 3)  
✅ Final phenotype classification  
✅ Treatment recommendations  

**Normal Warnings:**
⚠️ OpenAI API warnings (expected with mock keys)  
⚠️ Some images may skip ("Not a knee image")  
⚠️ Image preview files may not exist  

All of these are normal and don't affect the diagnosis process.

---

## 📞 Need Help?

Check the debug output in the terminal:
- Look for `DEBUG:` lines showing what's being executed
- Check for specific error messages
- Verify image paths and patient data are accessible

---

**Ready to go! Run the app and enter a patient ID to see the full workflow with images and analysis.** 🚀

# Multi-Agent OA Diagnosis Framework

This project implements a multi-agent system for Osteoarthritis (OA) diagnosis using [Microsoft AutoGen](https://microsoft.github.io/autogen/).

## Structure

- **Core Layer**: `main.py` handles the orchestration and lifecycle.
- **AgentChat Layer**: `agents/` contains specific agent definitions.
- **Extensions Layer**: `tools/` contains data loaders and analysis tools (mocked for this prototype).

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set your OpenAI API Key:
   ```bash
   # Windows PowerShell
   $env:OPENAI_API_KEY="sk-..."
   ```

3. Run the diagnosis system:
   ```bash
   python -m oa_diagnosis.main
   ```

4. Or run the **Chainlit UI**:
   ```bash
   python -m chainlit run oa_diagnosis/app.py
   ```

## Workflow

1. **Intake Agent** loads patient P001 data.
2. **Imaging Agent** analyzes the mocked MRI/X-ray data.
3. **Clinical Agent** reviews meds and guidelines.
4. **Case Retrieval Agent** finds similar historical cases.
5. **Orchestrator** synthesizes a final report.

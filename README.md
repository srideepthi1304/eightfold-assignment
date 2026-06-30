```markdown
# Multi-Source Candidate Data Ingestion Engine

A dependency-free Python pipeline that ingests candidate data from structured ATS records and unstructured recruiter notes, normalizes and merges the information into a canonical profile, and produces configurable output through a projection layer.

---

## 🛠️ Processing Pipeline

```text
ATS JSON --------\
                  \
                   --> Normalize --> Merge --> Canonical Profile
                  /                                   |
Recruiter Notes--/                                    v
                                             Configurable Projection
                                                      |
                                                      v
                                              Final JSON Output

```

---

## 💻 Running the Project

### 1. Execute the Ingestion Pipeline

To run the pipeline engine end-to-end and emit the finalized, schema-validated JSON payload directly to the console terminal, run:

```cmd
python engine.py --ats ats_input.json --notes notes_input.txt --config config.json

```

### 2. Run the Automated Test Suite

To execute the complete unit test suite and verify system error handling and path resolution rules, run:

```cmd
python -m unittest test_engine.py

```

---

## 📁 Project Structure

* `engine.py`: The core ingestion engine housing data normalizers, provenance merging, and path projection logic.
* `config.json`: The layout schema matrix regulating target fields, type primitive rules, and fallback defaults.
* `test_engine.py`: Automated testing suite validating operational safety guardrails and profile data transformations.
* `ats_input.json`: Sample structured input representing an Applicant Tracking System data dump.
* `notes_input.txt`: Sample unstructured text input containing raw recruiter interview notes.

---

## 📤 Expected Output Preview

```json
{
  "candidate_id": "cand_0cba00ca",
  "full_name": "Jane Doe",
  "headline": "Software Engineer",
  "years_experience": 4,
  "primary_email": "jane.doe@example.com",
  "phone": "+15550192834",
  "home_city": "San Francisco",
  "home_region": "California",
  "home_country": "US",
  "skills": [
    {
      "name": "Python",
      "confidence": 0.98,
      "sources": [
        "ats_json",
        "recruiter_notes"
      ]
    }
  ]
}

```

---

## 🎯 Core Engineering Highlights

* **Dynamic Configuration Layer:** Output schema mapping is completely driven by `config.json` without modifying Python source files.
* **Data Provenance & Trust Scoring:** Tracks origin history metadata for every merged attribute, applying a corroboration calculation for overlapping fields.
* **Defensive Guardrails:** Features an active identity validation mismatch block and an empty structural list primitive shield to block out-of-bounds runtime faults.
* **Zero External Dependencies:** Built entirely with standard library models (`json`, `re`, `argparse`, `hashlib`, `unittest`).

```

```

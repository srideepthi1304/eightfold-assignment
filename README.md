# Multi-Source Candidate Data Ingestion Engine

A dependency-free Python pipeline that ingests candidate data from structured ATS records and unstructured recruiter notes, merges them into a canonical profile, and produces configurable JSON output through a projection layer.

---

## 🏗️ Processing Pipeline

```text
ATS JSON --------\
                  \
                   --> Normalize --> Merge --> Canonical Profile
                  /                                 |
Recruiter Notes--/                                 |
                                                   |
                                                   v
                                      Configurable Projection
                                                   |
                                                   v
                                          Schema Validation
                                                   |
                                                   v
                                              Final JSON
```

---

## ✨ Features

- **Multi-Source Data Ingestion**
  - Merges structured ATS JSON with unstructured recruiter notes into a single canonical profile.

- **Data Normalization**
  - Normalizes phone numbers to E.164 format.
  - Standardizes skill names using synonym mapping.
  - Normalizes country information and cleans text values.

- **Conflict Resolution**
  - Uses ATS data as the primary source while incorporating additional information from recruiter notes.
  - Prevents accidental profile merging through identity verification.

- **Confidence Scoring**
  - Assigns confidence scores based on source reliability.
  - ATS Source: **0.95**
  - Recruiter Notes: **0.75**
  - Automatically increases confidence when multiple sources corroborate the same information.

- **Provenance Tracking**
  - Records the source, extraction method, and confidence for every merged field.

- **Dynamic Path Resolver**
  - Supports configurable runtime field mapping without modifying Python code.
  - Examples:
    - `emails[0]`
    - `phones[0]`
    - `location.city`
    - `location.region`
    - `location.country`
    - `skills.name`

- **Configurable Projection**
  - Output schema is completely driven by `config.json`.
  - Supports field renaming, nested object traversal, list indexing, and projection of complex objects.

- **Schema Validation**
  - Validates required fields.
  - Verifies E.164 phone formatting.
  - Supports configurable handling of missing fields.

- **Deterministic Candidate IDs**
  - Generates stable candidate identifiers using an MD5 hash of the primary email address.

- **Unit Testing**
  - Includes automated unit tests covering normalization, path resolution, projection, and profile transformation.

---

## 📁 Project Structure

```text
engine.py          Main transformation engine
config.json        Projection configuration
ats_input.json     Sample ATS input
notes_input.txt    Sample recruiter notes
test_engine.py     Unit test suite
README.md          Project documentation
```

---

## 🚀 Running the Project

### Execute the pipeline

```bash
python engine.py --ats ats_input.json --notes notes_input.txt --config config.json
```

### Run the test suite

```bash
python -m unittest test_engine.py
```

---

## 📤 Example Output

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

## 🔮 Future Improvements

For a production-scale deployment, the following enhancements could be added:

1. **Advanced Identity Resolution**
   - Replace substring matching with multi-identifier matching using email, phone number, and fuzzy string matching algorithms such as Jaro-Winkler or Levenshtein Distance.

2. **External Configuration**
   - Move lookup tables such as `CITY_DATABASE` and `SYNONYM_LOOKUP` into databases or centralized configuration services.

3. **Schema Versioning**
   - Support multiple output schemas for different downstream applications without changing the transformation engine.

4. **Additional Data Connectors**
   - Add ingestion modules for LinkedIn exports, GitHub profiles, resume PDF parsing, and additional ATS platforms.

5. **Observability**
   - Add structured logging, audit trails, metrics, and monitoring for production deployments.

---

## 🧪 Technologies Used

- Python 3
- JSON
- Regular Expressions (`re`)
- argparse
- hashlib
- unittest

No external dependencies are required.

---

## 📌 Design Highlights

- Separation between canonical data and projected output
- Configuration-driven field mapping
- Dynamic nested path resolution
- Source-aware confidence scoring
- Provenance tracking for traceability
- Deterministic candidate ID generation
- Modular architecture for future extensibility

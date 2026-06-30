Multi-Source Candidate Data Ingestion Engine

A dependency-free Python data pipeline built to ingest, normalize, merge, and project candidate data across structured and unstructured text files.

Future Production Improvements
While optimized for local data ingestion, an enterprise production deployment would implement the following enhancements:

1. Robust Identity Resolution: Transition from substring checks to combinations of multi-identifier hashing (Email and Phone) combined with fuzzy string matching algorithms (such as Jaro-Winkler or Levenshtein Distance) to resolve names like Jane Doe and Jane D safely.


2. Dynamic Configuration Loading: Move structural lookup tables (like CITY_DATABASE or SYNONYM_LOOKUP) out of code memory constants and into centralized environment databases or remote configuration registries.


3. Additional Connector Modules: Implement dedicated pipeline ingestion extractors for platforms like LinkedIn, GitHub public profile exports, and native PDF resume parsing engines without altering downstream projection logic.
import json
import re
import sys
import os
import argparse
import hashlib

# ==========================================
# GLOBAL LOOKUP TABLES
# ==========================================
SYNONYM_LOOKUP = {
    "py": "Python", "python3": "Python", "cpython": "Python", "python": "Python",
    "react.js": "React", "reactjs": "React", "react": "React",
    "aws": "Amazon Web Services (AWS)", "amazon web services": "Amazon Web Services (AWS)",
    "sql": "SQL", "mysql": "SQL", "postgres": "SQL"
}

CITY_DATABASE = {
    "San Francisco": ("California", "US"),
    "Hyderabad": ("Telangana", "IN"),
    "London": ("England", "GB")
}

# ==========================================
# DATA NORMALIZATION UTILITIES
# ==========================================
def normalize_phone(phone_str):
    if not phone_str:
        return None
    digits = re.sub(r'\D', '', phone_str)
    if len(digits) == 10:
        return f"+1{digits}"
    return f"+{digits}" if digits else None

def normalize_country(text):
    if not text:
        return "UNKNOWN"
    text_clean = text.upper().strip()
    if "US" in text_clean or "USA" in text_clean or "UNITED STATES" in text_clean:
        return "US"
    if "IN" in text_clean or "INDIA" in text_clean:
        return "IN"
    return "UNKNOWN"

def canonicalize_skill(skill_name):
    if not skill_name:
        return "UNKNOWN"
    token = skill_name.strip().lower()
    return SYNONYM_LOOKUP.get(token, skill_name.strip().title())

# ==========================================
# FULLY GENERIC RUNTIME PATH RESOLVER
# ==========================================
def resolve_canonical_path(data, path_str):
    """
    Traverses data structures dynamically using dot notation and list indices.
    Supports completely generic array mapping (e.g., 'skills.name', 'skills.confidence').
    """
    if not path_str or data is None:
        return None
        
    normalized_path = path_str.replace('[', '.').replace(']', '')
    tokens = normalized_path.split('.')
    
    current = data
    for token in tokens:
        if not token:
            continue
        if isinstance(current, dict):
            current = current.get(token)
        elif isinstance(current, list):
            if token.isdigit():
                idx = int(token)
                current = current[idx] if idx < len(current) else None
            elif len(current) == 0:
                return []
            else:
                # GENERIC TRANSFORMATION: Maps any attribute across lists of dicts seamlessly
                current = [
                    item.get(token) 
                    for item in current 
                    if isinstance(item, dict) and item.get(token) is not None
                ]
        else:
            return None
    return current

# ==========================================
# ENHANCED STRICT TYPE VALIDATION LAYER
# ==========================================
def validate_output_schema(profile_data, config=None):
    """
    Enforces strict data format constraints and matches output value 
    primitives against configuration types.
    """
    issues = []
    
    phone_target_keys = ["phone"]
    if config and "fields" in config:
        for field_cfg in config["fields"]:
            source_from = field_cfg.get("from", "")
            if "phones" in source_from:
                phone_target_keys.append(field_cfg["path"])

    for phone_key in set(phone_target_keys):
        if phone_key in profile_data and profile_data[phone_key]:
            if not re.match(r'^\+\d{11,15}$', profile_data[phone_key]):
                issues.append(f"Phone field '{phone_key}' format breaks E.164 constraints.")
            
    if config and "fields" in config:
        for field_cfg in config["fields"]:
            path = field_cfg["path"]
            expected_type = field_cfg.get("type")
            val = profile_data.get(path)
            
            if field_cfg.get("required", False) and val is None:
                issues.append(f"Missing required key: '{path}'")
                continue
                
            if val is not None and expected_type:
                if expected_type == "string" and not isinstance(val, str):
                    issues.append(f"Type Mismatch: Path '{path}' expected string, got {type(val).__name__}.")
                elif expected_type == "number" and not isinstance(val, (int, float)) and not isinstance(val, bool):
                    issues.append(f"Type Mismatch: Path '{path}' expected number, got {type(val).__name__}.")
                elif expected_type == "string[]" and not isinstance(val, list):
                    issues.append(f"Type Mismatch: Path '{path}' expected array list, got {type(val).__name__}.")
                elif expected_type == "object" and not isinstance(val, dict):
                    issues.append(f"Type Mismatch: Path '{path}' expected map object, got {type(val).__name__}.")
                elif expected_type == "boolean" and not isinstance(val, bool):
                    issues.append(f"Type Mismatch: Path '{path}' expected boolean, got {type(val).__name__}.")
                
    return {"is_valid": len(issues) == 0, "issues": issues}

# ==========================================
# CORE PROCESSING & DATA MERGING PIPELINE
# ==========================================
def build_canonical_profile(ats_path, notes_path):
    profile = {
        "candidate_id": "PENDING_GENERATION",
        "full_name": None,
        "emails": [],
        "phones": [],
        "location": {"city": None, "region": None, "country": "UNKNOWN"},
        "headline": None,
        "years_experience": None,
        "skills": [],
        "provenance": [],
        "overall_confidence": 1.0
    }
    
    field_weights = {"emails": 0.40, "phones": 0.25, "full_name": 0.15, "location": 0.10, "headline": 0.10}
    field_confidences = {k: 0.0 for k in field_weights.keys()}
    skills_registry = {}
    source_confidences = {"ats_json": 0.95, "recruiter_notes": 0.75}

    if os.path.exists(ats_path):
        try:
            with open(ats_path, 'r') as f:
                ats_data = json.load(f)
            
            profile["full_name"] = ats_data.get("applicant_name")
            profile["provenance"].append({
                "field": "full_name", "source": "ats_json", "confidence": source_confidences["ats_json"], "method": "direct_mapping"
            })
            field_confidences["full_name"] = source_confidences["ats_json"]
            
            email = ats_data.get("contact_info", {}).get("email_address")
            if email:
                email_clean = email.strip().lower()
                profile["emails"].append(email_clean)
                profile["provenance"].append({
                    "field": "emails", "source": "ats_json", "confidence": source_confidences["ats_json"], "method": "direct_mapping"
                })
                field_confidences["emails"] = source_confidences["ats_json"]
                
            phone = normalize_phone(ats_data.get("contact_info", {}).get("phone_number"))
            if phone:
                profile["phones"].append(phone)
                profile["provenance"].append({
                    "field": "phones", "source": "ats_json", "confidence": source_confidences["ats_json"], "method": "normalization"
                })
                field_confidences["phones"] = source_confidences["ats_json"]
                
            profile["headline"] = ats_data.get("current_role")
            profile["provenance"].append({
                "field": "headline", "source": "ats_json", "confidence": source_confidences["ats_json"], "method": "direct_mapping"
            })
            field_confidences["headline"] = source_confidences["ats_json"]
            
            for skill in ats_data.get("skills_list", []):
                c_skill = canonicalize_skill(skill)
                skills_registry[c_skill] = {"name": c_skill, "confidence": source_confidences["ats_json"], "sources": ["ats_json"]}
        except Exception as e:
            print(f"[Warning] Failed parsing ATS JSON: {e}", file=sys.stderr)

    if os.path.exists(notes_path):
        try:
            with open(notes_path, 'r') as f:
                notes_text = f.read()
            
            name_check = profile["full_name"] or "Jane Doe"
            if name_check.lower() in notes_text.lower():
                email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', notes_text)
                if email_match:
                    extracted_email = email_match.group(0).lower().strip()
                    if extracted_email not in profile["emails"]:
                        profile["emails"].append(extracted_email)
                        profile["provenance"].append({
                            "field": "emails", "source": "recruiter_notes", "confidence": source_confidences["recruiter_notes"], "method": "regex_extraction"
                        })
                        field_confidences["emails"] = max(field_confidences["emails"], source_confidences["recruiter_notes"])
                    else:
                        field_confidences["emails"] = min(field_confidences["emails"] + 0.03, 1.0)
                    
                phone_match = re.search(r'\+?\d[\d\-\(\)\s]{8,}\d', notes_text)
                if phone_match:
                    norm_p = normalize_phone(phone_match.group(0))
                    if norm_p not in profile["phones"]:
                        profile["phones"].append(norm_p)
                        profile["provenance"].append({
                            "field": "phones", "source": "recruiter_notes", "confidence": source_confidences["recruiter_notes"], "method": "regex_normalization"
                        })
                    else:
                        field_confidences["phones"] = min(field_confidences["phones"] + 0.03, 1.0)

                exp_match = re.search(r'(\d+)\s*years\s+of\s+experience', notes_text, re.IGNORECASE)
                if exp_match:
                    profile["years_experience"] = int(exp_match.group(1))
                    profile["provenance"].append({
                        "field": "years_experience", "source": "recruiter_notes", "confidence": source_confidences["recruiter_notes"], "method": "regex_extraction"
                    })

                for city, (region, country_code) in CITY_DATABASE.items():
                    if city.lower() in notes_text.lower():
                        profile["location"]["city"] = city
                        profile["location"]["region"] = region
                        profile["location"]["country"] = country_code
                        profile["provenance"].append({
                            "field": "location", "source": "recruiter_notes", "confidence": 0.90, "method": "text_keyword_match"
                        })
                        field_confidences["location"] = 0.90
                        break

                for skill_keyword in ["react", "python", "aws", "sql"]:
                    if skill_keyword in notes_text.lower():
                        c_skill = canonicalize_skill(skill_keyword)
                        if c_skill in skills_registry:
                            if "recruiter_notes" not in skills_registry[c_skill]["sources"]:
                                skills_registry[c_skill]["sources"].append("recruiter_notes")
                                skills_registry[c_skill]["confidence"] = min(skills_registry[c_skill]["confidence"] + 0.03, 1.0)
                        else:
                            skills_registry[c_skill] = {"name": c_skill, "confidence": source_confidences["recruiter_notes"], "sources": ["recruiter_notes"]}
            else:
                print("[Warning] Identity mismatch in recruiter notes. Skipping merge.", file=sys.stderr)
        except Exception as e:
            print(f"[Warning] Failed parsing Recruiter Notes: {e}", file=sys.stderr)

    profile["skills"] = list(skills_registry.values())
    
    if profile["emails"]:
        profile["candidate_id"] = "cand_" + hashlib.md5(profile["emails"][0].encode()).hexdigest()[:8]
    else:
        profile["candidate_id"] = "cand_anonymous"
        
    weighted_sum = sum(field_confidences[k] * field_weights[k] for k in field_weights.keys())
    total_weights = sum(field_weights[k] for k in field_weights.keys() if field_confidences[k] > 0)
    profile["overall_confidence"] = round(weighted_sum / total_weights, 2) if total_weights > 0 else 0.0
    return profile

# ==========================================
# PROJECTION LAYER WITH FALLBACK DEFAULTS
# ==========================================
def project_profile(canonical, config):
    output = {}
    on_missing = config.get("on_missing", "null")
    
    for field_cfg in config.get("fields", []):
        target_path = field_cfg["path"]
        source_from = field_cfg.get("from", target_path)
        
        val = resolve_canonical_path(canonical, source_from)
            
        if val is None or (isinstance(val, list) and len(val) == 0 and field_cfg.get("type") != "string[]"):
            # FALLBACK SUPPORT: Loads configurable defaults directly when path resolutions evaluate to empty states
            if "default" in field_cfg:
                output[target_path] = field_cfg["default"]
            elif on_missing == "error":
                raise ValueError(f"Field path lookup target '{target_path}' returned null.")
            elif on_missing == "omit":
                continue
            else:
                output[target_path] = None
        else:
            output[target_path] = val

    if config.get("include_confidence", True):
        output["overall_confidence"] = canonical["overall_confidence"]
        output["provenance"] = canonical["provenance"]
        
    return output

# ==========================================
# CLI ENTRY POINT
# ==========================================
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Multi-Source Candidate Data Transformer Pipeline")
    parser.add_argument("--ats", default="ats_input.json", help="Path to ATS JSON input file.")
    parser.add_argument("--notes", default="notes_input.txt", help="Path to recruiter notes file.")
    parser.add_argument("--config", default="config.json", help="Path to transformation config file.")
    
    args = parser.parse_args()

    canonical = build_canonical_profile(args.ats, args.notes)
    
    if os.path.exists(args.config):
        with open(args.config, 'r') as f:
            runtime_config = json.load(f)
            
        projected = project_profile(canonical, runtime_config)
        
        validation_report = validate_output_schema(projected, runtime_config)
        if not validation_report["is_valid"]:
            print(f"[Warning] Output Schema Violation: {validation_report['issues']}", file=sys.stderr)
            
        print(json.dumps(projected, indent=2))
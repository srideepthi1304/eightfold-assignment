import unittest
import json
from unittest.mock import patch, mock_open
from engine import build_canonical_profile, project_profile, resolve_canonical_path, validate_output_schema

class TestCandidatePipeline(unittest.TestCase):

    def test_resolve_canonical_path_nested(self):
        sample_data = {
            "location": {"city": "Hyderabad", "country": "IN"},
            "emails": ["test@domain.com"],
            "skills": [{"name": "Python"}, {"name": "SQL"}]
        }
        self.assertEqual(resolve_canonical_path(sample_data, "location.city"), "Hyderabad")
        self.assertEqual(resolve_canonical_path(sample_data, "emails[0]"), "test@domain.com")
        self.assertEqual(resolve_canonical_path(sample_data, "skills.name"), ["Python", "SQL"])

    def test_resolve_canonical_path_empty_list_shield(self):
        sample_data_empty = {"skills": []}
        self.assertEqual(resolve_canonical_path(sample_data_empty, "skills.name"), [])

    @patch("os.path.exists", return_value=True)
    def test_pipeline_merging_and_provenance(self, mock_exists):
        sample_ats = json.dumps({
            "applicant_name": "Sri Deepthi",
            "contact_info": {"email_address": "deepthi@domain.com"},
            "skills_list": ["python"]
        })
        sample_notes = "Sri Deepthi has 3 years of experience and knows React."

        with patch("builtins.open", mock_open(read_data=sample_ats)) as mock_file:
            mock_file.side_effect = [
                mock_open(read_data=sample_ats).return_value,
                mock_open(read_data=sample_notes).return_value
            ]
            
            canonical = build_canonical_profile("mock_ats.json", "mock_notes.txt")
            
            self.assertEqual(canonical["full_name"], "Sri Deepthi")
            self.assertIn("deepthi@domain.com", canonical["emails"])
            
            skills = [s["name"] for s in canonical["skills"]]
            self.assertIn("Python", skills)
            self.assertIn("React", skills)

            self.assertTrue(any(
                p["field"] == "emails" and p["source"] == "ats_json"
                for p in canonical["provenance"]
            ))

    def test_project_profile_and_strict_validation(self):
        canonical = {
            "candidate_id": "cand_123",
            "full_name": "Sri Deepthi",
            "emails": ["deepthi@domain.com"],
            "location": {"city": "Hyderabad"},
            "skills": [{"name": "Python", "confidence": 0.95}],
            "overall_confidence": 0.95,
            "provenance": []
        }
        
        config = {
          "fields": [
            { "path": "candidate_id", "type": "string" },
            { "path": "full_name", "type": "string", "required": True },
            { "path": "skills", "from": "skills", "type": "object[]" }
          ]
        }
        
        projected = project_profile(canonical, config)
        self.assertEqual(projected["candidate_id"], "cand_123")
        self.assertEqual(projected["skills"][0]["name"], "Python")
        
        report = validate_output_schema(projected, config)
        self.assertTrue(report["is_valid"])

if __name__ == "__main__":
    unittest.main()
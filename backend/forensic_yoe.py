from app.resume_jd.pipelines.phase_04_matcher import Phase4Matcher
matcher = Phase4Matcher()

texts = [
  ("5+ years Python", True),
  ("2 years Python", True),
  ("Python 3.11", False),
  ("5TB/day pipeline", False),
  ("2024 release", False),
  ("Python version 2", False),
  ("3 years and 6 months experience", True),
]

for t, expect_match in texts:
    result = matcher._extract_yoe(t)
    ok = (result is not None) == expect_match
    status = "OK" if ok else "FAIL"
    print(f"[{status}] {repr(t)} -> yoe={result} (expected_match={expect_match})")

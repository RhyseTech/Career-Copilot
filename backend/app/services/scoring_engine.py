from typing import Dict, List

class ScoringEngine:
    def __init__(self):
        pass

    def calculate_resume_score(self, parsed_data: Dict, extracted_skills: List[str], experience_data: Dict) -> Dict:
        """
        Calculates the Resume-Only ATS Compatibility Score.
        Weights: Structure 15%, Skills 20%, Experience 20%, Content Quality 20%, Keyword 10%, Impact 15%.
        """
        sections = parsed_data.get("sections", {})
        raw_text = parsed_data.get("raw_text", "")
        
        # 1. Structure Score (15%)
        # Check if essential sections exist
        essential_sections = ["summary", "experience", "education", "skills"]
        found_sections = [s for s in essential_sections if sections.get(s, "").strip()]
        structure_score = (len(found_sections) / len(essential_sections)) * 100

        # 2. Skills Quality (20%)
        # Assuming >= 10 skills is good
        skills_score = min((len(extracted_skills) / 10) * 100, 100)

        # 3. Experience Quality (20%)
        # Assuming >= 2 years is basic threshold for a good score, capping at 10 years for normal scale
        exp_years = experience_data.get("total_years", 0)
        exp_score = min((exp_years / 10) * 100, 100)
        if exp_years == 0 and sections.get("experience"):
            exp_score = 50 # Partial credit if they have the section but parser failed

        # 4. Content Quality (20%)
        # Basic heuristic: words count
        word_count = len(raw_text.split())
        content_score = 100 if 300 <= word_count <= 800 else max(100 - abs(word_count - 550)*0.2, 0)

        # 5. Keyword Coverage (10%)
        # Basic heuristic for MVP: relies heavily on skills extracted
        keyword_score = skills_score

        # Check for numbers/metrics in experience section (ignoring dates/years)
        exp_text = sections.get("experience", "")
        import re
        # Detect percentages (e.g., 50%, 99.9%), Currency (e.g., $10k, $500,000), Multipliers (e.g., 5x, 10X), and large numbers with '+' (e.g., 1000+)
        metric_pattern = r'\d+(?:\.\d+)?\s*%|[\$€£₹]\s*\d+(?:,\d{3})*(?:\.\d+)?(?:k|K|m|M|b|B)?|\d+(?:\.\d+)?\s*[xX]\b|\b\d{2,}(?:,\d{3})*\s*\+'
        metrics_matches = re.findall(metric_pattern, exp_text)
        metrics_count = len(metrics_matches)
        impact_score = min((metrics_count / 3) * 100, 100) # 3+ metrics is 100%

        # Calculate weighted overall score
        overall_score = (
            structure_score * 0.15 +
            skills_score * 0.20 +
            exp_score * 0.20 +
            content_score * 0.20 +
            keyword_score * 0.10 +
            impact_score * 0.15
        )

        # Detailed Checks Generation for Premium UI
        detailed_checks = {
            "Sections": [],
            "Content": [],
            "Experience": []
        }

        # Structure Check
        missing_sections = [s for s in essential_sections if not sections.get(s, "").strip()]
        if len(missing_sections) == 0:
            detailed_checks["Sections"].append({"name": "ATS Essentials", "status": "pass", "score": 100, "message": "All essential sections found (Summary, Experience, Education, Skills)."})
        else:
            detailed_checks["Sections"].append({"name": "ATS Essentials", "status": "warn" if len(missing_sections) <= 2 else "fail", "score": structure_score, "message": f"Missing essential sections: {', '.join(missing_sections)}."})

        # Skills Check
        if skills_score == 100:
            detailed_checks["Content"].append({"name": "Skills Coverage", "status": "pass", "score": 100, "message": f"Excellent! Found {len(extracted_skills)} skills."})
        else:
            detailed_checks["Content"].append({"name": "Skills Coverage", "status": "warn", "score": skills_score, "message": f"Found only {len(extracted_skills)} skills. We recommend 10+ for optimal ATS matching."})

        # Experience Depth Check
        if exp_score >= 80:
            detailed_checks["Experience"].append({"name": "Experience Depth", "status": "pass", "score": exp_score, "message": f"Solid experience depth ({exp_years} years)."})
        else:
            detailed_checks["Experience"].append({"name": "Experience Depth", "status": "fail" if exp_score < 40 else "warn", "score": exp_score, "message": f"Detected {exp_years} years of experience. ATS systems often look for clearer duration formatting."})

        # Word Count Check
        if content_score == 100:
            detailed_checks["Content"].append({"name": "Length & Word Count", "status": "pass", "score": 100, "message": f"Resume length is optimal ({word_count} words)."})
        else:
            detailed_checks["Content"].append({"name": "Length & Word Count", "status": "warn", "score": content_score, "message": f"Resume has {word_count} words. Aim for the 300-800 word sweet spot."})

        # Impact Metrics Check
        if impact_score == 100:
            detailed_checks["Experience"].append({"name": "Quantifying Impact", "status": "pass", "score": 100, "message": f"Great job quantifying achievements (found {metrics_count} metrics)!"})
        else:
            detailed_checks["Experience"].append({"name": "Quantifying Impact", "status": "fail", "score": impact_score, "message": f"Found only {metrics_count} quantifiable metrics (e.g., %, $, multipliers). Aim for at least 3 to prove impact."})

        breakdown_list = [
            {"label": "Structure", "score": round(structure_score, 0)},
            {"label": "Skills Coverage", "score": round(skills_score, 0)},
            {"label": "Experience", "score": round(exp_score, 0)},
            {"label": "Content Quality", "score": round(content_score, 0)},
            {"label": "Keyword Match", "score": round(keyword_score, 0)},
            {"label": "Impact Metrics", "score": round(impact_score, 0)},
        ]

        lagging_fields = [item["label"] for item in breakdown_list if item["score"] < 75]

        eligibility = []
        if overall_score >= 80:
            eligibility = ["Tier-1 IT", "Product Comps"]
        elif overall_score >= 60:
            eligibility = ["Tier-2 IT", "Startups"]
        else:
            eligibility = ["Mass Recruiters"]

        return {
            "total_score": round(overall_score, 0),
            "breakdown": breakdown_list,
            "lagging_fields": lagging_fields,
            "eligibility": eligibility,
            "detailed_checks": detailed_checks
        }

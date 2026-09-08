import re
from typing import Dict

class Sectionizer:
    """
    Deterministically splits JD text into distinct logical sections 
    (e.g., 'Responsibilities', 'Requirements', 'Benefits').
    """
    def __init__(self):
        # Heuristic keywords for detecting section boundaries
        self.section_headers = {
            "Job Summary": [r"about the role", r"job summary", r"role overview"],
            "Responsibilities": [r"responsibilities", r"what you'll do", r"your impact", r"key aspects include"],
            "Required Qualifications": [r"requirements", r"minimum qualifications", r"required qualifications", r"must have", r"what you need", r"required skills"],
            "Preferred Qualifications": [r"preferred qualifications", r"nice to have", r"bonus points", r"preferred skills", r"desirable"],
            "Benefits": [r"benefits", r"perks", r"what we offer"]
        }

    def extract_sections(self, raw_text: str) -> Dict[str, str]:
        """
        Splits text by identifying headers and associating subsequent lines.
        """
        lines = [line.strip() for line in raw_text.split('\n') if line.strip()]
        sections = {"Uncategorized": ""}
        current_section = "Uncategorized"
        
        for line in lines:
            line_lower = line.lower()
            found_header = False
            
            # Check if line looks like a header (short length + matching keywords)
            if len(line) < 50:
                for section_name, keywords in self.section_headers.items():
                    if any(re.search(rf"\b{kw}\b", line_lower) for kw in keywords):
                        current_section = section_name
                        if section_name not in sections:
                            sections[section_name] = ""
                        found_header = True
                        break
            
            if not found_header:
                sections[current_section] += line + "\n"
                
        # Clean up
        return {k: v.strip() for k, v in sections.items() if v.strip()}

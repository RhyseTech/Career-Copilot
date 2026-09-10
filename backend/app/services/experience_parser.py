import re
from datetime import datetime
import warnings

class ExperienceParser:
    def __init__(self):
        warnings.warn("ExperienceParser is deprecated and causes severe capability loss. Use structured_data instead.", DeprecationWarning, stacklevel=2)
        # Basic regex to catch date ranges like "Jan 2020 - Present" or "2018 - 2021"
        self.date_pattern = re.compile(
            r'((?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?\s+)?\d{4})\s*(?:-|to|–)\s*((?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?\s+)?\d{4}|Present|Current)', 
            re.IGNORECASE
        )

    def parse_experience(self, text: str) -> dict:
        """
        Parses experience section to find total years of experience.
        This is a basic heuristic approach for MVP.
        """
        matches = self.date_pattern.findall(text)
        total_years = 0.0
        
        for start_str, end_str in matches:
            try:
                # Naive year extraction for MVP
                start_year = int(re.search(r'\d{4}', start_str).group())
                
                if end_str.lower() in ['present', 'current']:
                    end_year = datetime.now().year
                else:
                    end_year = int(re.search(r'\d{4}', end_str).group())
                
                years = end_year - start_year
                if years > 0 and years < 40: # Sanity check
                    total_years += years
            except Exception:
                continue
                
        return {
            "total_years": total_years,
            "raw_matches": matches
        }

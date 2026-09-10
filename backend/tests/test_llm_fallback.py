import sys
import os
import json
import pytest
from unittest.mock import patch, MagicMock

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from app.services.llm_optimizer import LLMOptimizer

def mock_gemini_success():
    mock = MagicMock()
    mock.status_code = 200
    mock.json.return_value = {
        "candidates": [
            {
                "finishReason": "STOP",
                "content": {
                    "parts": [{"text": json.dumps({"cv": {"sections": {"experience": [{"company": "A", "position": "B"}], "projects": [{"name": "A"}], "certifications": [{"name": "A"}]}}})}]
                }
            }
        ]
    }
    return mock

def mock_gemini_503():
    mock = MagicMock()
    mock.status_code = 503
    mock.raise_for_status.side_effect = requests.exceptions.HTTPError("503")
    return mock

def mock_gemini_429():
    mock = MagicMock()
    mock.status_code = 429
    mock.raise_for_status.side_effect = requests.exceptions.HTTPError("429")
    return mock

def mock_groq_length_error():
    mock = MagicMock()
    mock.status_code = 200
    mock.json.return_value = {
        "choices": [
            {
                "finish_reason": "length",
                "message": {"content": "{}"}
            }
        ]
    }
    return mock

def mock_groq_success():
    mock = MagicMock()
    mock.status_code = 200
    mock.json.return_value = {
        "choices": [
            {
                "finish_reason": "stop",
                "message": {"content": json.dumps({"cv": {"sections": {"experience": [{"company": "A", "position": "B"}], "projects": [{"name": "A"}], "certifications": [{"name": "A"}]}}})}
            }
        ]
    }
    return mock

import requests

class TestLLMFallback:
    def setup_method(self):
        self.opt = LLMOptimizer()
        self.opt.provider = "gemini"
        self.opt.gemini_key = "test_g"
        self.opt.groq_key = "test_q"
        
        from app.services.llm_optimizer import _CACHE
        _CACHE.clear()

    @patch("app.services.llm_optimizer.requests.post")
    @patch("time.sleep")
    def test_gemini_503_retry(self, mock_sleep, mock_post):
        # 2 failures then success
        mock_post.side_effect = [mock_gemini_503(), mock_gemini_503(), mock_gemini_success()]
        
        raw_text = "Experience Projects Certifications"
        result = self.opt.generate_rendercv_json(raw_text)
        
        assert mock_post.call_count == 3
        assert result is not None

    @patch("app.services.llm_optimizer.requests.post")
    @patch("time.sleep")
    def test_gemini_429_retry(self, mock_sleep, mock_post):
        mock_post.side_effect = [mock_gemini_429(), mock_gemini_success()]
        
        raw_text = "Experience Projects Certifications"
        result = self.opt.generate_rendercv_json(raw_text)
        
        assert mock_post.call_count == 2
        assert result is not None

    @patch("app.services.llm_optimizer.requests.post")
    def test_gemini_success_no_fallback(self, mock_post):
        mock_post.return_value = mock_gemini_success()
        
        raw_text = "Experience Projects Certifications"
        result = self.opt.generate_rendercv_json(raw_text)
        
        assert mock_post.call_count == 1
        assert result is not None

    @patch("app.services.llm_optimizer.requests.post")
    def test_groq_length_reject(self, mock_post):
        self.opt.provider = "groq"
        self.opt.gemini_key = None
        mock_post.return_value = mock_groq_length_error()
        
        raw_text = "Experience"
        with pytest.raises(Exception, match="Phase 1 LLM Extraction Failure.*Groq generation incomplete: finish_reason=length"):
            self.opt.generate_rendercv_json(raw_text)

    def test_materially_incomplete_reject(self):
        raw_text = "Here is my Experience and Projects and Certifications"
        bad_json = {
            "cv": {"sections": {
                "experience": [],
                "projects": [{"name": "A"}],
                "certifications": [{"name": "A"}]
            }}
        }
        with pytest.raises(Exception, match="Material Validation Error: Source contains experience but none was extracted"):
            self.opt._validate_rendercv_completeness(raw_text, bad_json)

    def test_valid_complete_accept(self):
        raw_text = "Here is my Experience and Projects and Certifications"
        good_json = {
            "cv": {"sections": {
                "experience": [{"company": "A", "position": "B"}],
                "projects": [{"name": "A"}],
                "certifications": [{"name": "A"}]
            }}
        }
        self.opt._validate_rendercv_completeness(raw_text, good_json) # Should not raise

    def test_source_certifications_omitted_reject(self):
        raw_text = "Certifications: 1. AWS 2. GCP"
        bad_json = {
            "cv": {"sections": {
                "certifications": [],
                "experience": [{"company": "A", "position": "B"}]
            }}
        }
        with pytest.raises(Exception, match="Material Validation Error: Source contains certifications but none were extracted"):
            self.opt._validate_rendercv_completeness(raw_text, bad_json)

    def test_source_projects_omitted_reject(self):
        raw_text = "Projects: Syntethic Data Generator"
        bad_json = {
            "cv": {"sections": {
                "projects": [],
                "experience": [{"company": "A", "position": "B"}]
            }}
        }
        with pytest.raises(Exception, match="Material Validation Error: Source contains projects but none were extracted"):
            self.opt._validate_rendercv_completeness(raw_text, bad_json)

if __name__ == "__main__":
    pytest.main(["-v", __file__])

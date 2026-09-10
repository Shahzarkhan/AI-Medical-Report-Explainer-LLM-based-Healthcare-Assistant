import os
import json
import re
import streamlit as st
from dotenv import load_dotenv
import google.generativeai as genai

from app.services.rag_service import retrieve_context, format_context

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

if API_KEY:
    genai.configure(api_key=API_KEY)

# Lightweight stable model for development/testing. It is designed for
# high-throughput, cost-sensitive workloads.
MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")
model = genai.GenerativeModel(MODEL_NAME) if API_KEY else None


def _error_result(message: str) -> dict:
    return {
        "health_score": 0,
        "risk_level": "Unknown",
        "abnormal_tests": 0,
        "normal_tests": 0,
        "overall_summary": message,
        "health_tips": [],
        "abnormal_values": [],
    }


def _clean_json(text: str) -> dict:
    text = text.strip().replace("```json", "").replace("```", "").strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            return json.loads(match.group())
        raise ValueError("Gemini returned invalid JSON.")


@st.cache_data(show_spinner=False)
def explain_medical_report(report_text):
    """Explain a report using local RAG context + Gemini LLM."""
    if not API_KEY or model is None:
        return _error_result("Gemini API key is missing. Add GEMINI_API_KEY to your .env file.")

    # Retrieval is local, so it does not consume a Gemini request.
    rag_results = retrieve_context(report_text, top_k=5)
    rag_context = format_context(rag_results)

    prompt = f"""
You are an experienced medical report analyzer.

You are part of a Retrieval-Augmented Generation (RAG) system.
The LOCAL MEDICAL KNOWLEDGE below was retrieved because it is relevant to the
uploaded report. Use it as supporting educational context, but do not invent
facts that are not supported by the report or the retrieved context.

IMPORTANT MEDICAL SAFETY RULES:
- Do not diagnose a disease from a single laboratory result.
- Do not claim certainty when the report is ambiguous.
- Use the laboratory reference range shown in the report when available.
- If a result may require urgent attention, say so clearly and recommend prompt
  professional medical evaluation.
- This output is educational and is not a medical diagnosis or a substitute for
  a clinician.

LOCAL MEDICAL KNOWLEDGE (RAG):
{rag_context}

Return ONLY valid JSON.
Do NOT write markdown.
Do NOT write ```json.
Do NOT write explanations outside JSON.

Use this format exactly:

{{
    "health_score": 0,
    "risk_level": "",
    "abnormal_tests": 0,
    "normal_tests": 0,
    "overall_summary": "2-3 short sentences (maximum 60 words)",
    "health_tips": ["", "", "", "", ""],
    "abnormal_values": [
        {{
            "test_name": "",
            "patient_value": "",
            "normal_range": "",
            "risk": "",
            "explanation": "",
            "possible_reason": "",
            "food": "",
            "lifestyle": "",
            "doctor_consultation": ""
        }}
    ]
}}

Rules:
- Overall Health Summary: only 2-3 short sentences, maximum 60 words.
- Highlight only the most important findings there.
- Return exactly 5 personalized health tips.
- Tips must be easy to understand, actionable, and based on the report.
- For every abnormal test, assign exactly one risk level: High, Moderate, or Low.
- Do not fabricate a test value or reference range.

MEDICAL REPORT:
{report_text}
"""

    try:
        response = model.generate_content(prompt)
        result = _clean_json(response.text)
        # Keep RAG provenance outside the LLM's JSON schema.
        result["_rag_sources"] = [
            {"source": item["source"], "score": item["score"]}
            for item in rag_results
        ]
        return result

    except Exception as e:
        message = str(e)
        if "429" in message or "RESOURCE_EXHAUSTED" in message or "quota" in message.lower():
            return _error_result(
                "Gemini API quota is currently exhausted. The app's RAG retrieval still works locally; "
                "wait for the quota reset or use a project with available Gemini quota."
            )
        return _error_result(f"AI analysis failed: {message}")


@st.cache_data(show_spinner=False)
def compare_medical_reports(report1_text, report2_text):
    if not API_KEY or model is None:
        return {
            "report1": {"health_score": 0, "risk_level": "Unknown", "normal_tests": 0, "abnormal_tests": 0},
            "report2": {"health_score": 0, "risk_level": "Unknown", "normal_tests": 0, "abnormal_tests": 0},
            "comparison": [],
        }

    prompt = f"""
You are an expert medical report analyzer.
Compare these two medical reports.
Do not diagnose. Use only information present in the reports.
Return ONLY valid JSON.

Format:
{{
    "report1": {{
        "health_score": 0,
        "risk_level": "",
        "normal_tests": 0,
        "abnormal_tests": 0
    }},
    "report2": {{
        "health_score": 0,
        "risk_level": "",
        "normal_tests": 0,
        "abnormal_tests": 0
    }},
    "comparison": [
        {{
            "test_name": "",
            "report1_value": "",
            "report2_value": "",
            "better_report": "",
            "remark": ""
        }}
    ]
}}

Medical Report 1:
{report1_text}

Medical Report 2:
{report2_text}
"""

    try:
        response = model.generate_content(prompt)
        return _clean_json(response.text)
    except Exception:
        return {
            "report1": {"health_score": 0, "risk_level": "Unknown", "normal_tests": 0, "abnormal_tests": 0},
            "report2": {"health_score": 0, "risk_level": "Unknown", "normal_tests": 0, "abnormal_tests": 0},
            "comparison": [],
        }

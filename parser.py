import re
import fitz

def extract_dashboard_data(ai_response):

    score = 0
    risk = "Unknown"
    abnormal = 0
    normal = 0

    score_match = re.search(r"Health Score.*?(\d+)", ai_response, re.IGNORECASE)
    if score_match:
        score = int(score_match.group(1))

    risk_match = re.search(
        r"Risk Level.*?(Low|Medium|High)",
        ai_response,
        re.IGNORECASE
    )
    if risk_match:
        risk = risk_match.group(1).capitalize()

    abnormal_match = re.search(
        r"Abnormal Tests.*?(\d+)",
        ai_response,
        re.IGNORECASE
    )
    if abnormal_match:
        abnormal = int(abnormal_match.group(1))

    normal_match = re.search(
        r"Normal Tests.*?(\d+)",
        ai_response,
        re.IGNORECASE
    )
    if normal_match:
        normal = int(normal_match.group(1))

    return score, risk, abnormal, normal

def extract_text_from_pdf(uploaded_file):
    pdf = fitz.open(stream=uploaded_file.read(), filetype="pdf")

    text = ""
    for page in pdf:
        text += page.get_text()

    pdf.close()
    return text
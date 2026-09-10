from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

def create_pdf(summary, filename="medical_report_summary.pdf"):

    doc = SimpleDocTemplate(filename)

    styles = getSampleStyleSheet()

    story = []

    story.append(
        Paragraph("<b>AI Medical Report Summary</b>", styles["Heading1"])
    )

    for line in summary.split("\n"):

        if line.strip() != "":

            story.append(
                Paragraph(line, styles["BodyText"])
            )

    doc.build(story)

    return filename
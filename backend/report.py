from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

def create_report(path, patient, prediction, top_probs, risk, symptoms, notes):
    doc = SimpleDocTemplate(str(path), pagesize=A4)
    styles = getSampleStyleSheet()
    story = [
        Paragraph("HealthGuard AI — Health Screening Report", styles["Title"]),
        Paragraph("Educational screening output; not a medical diagnosis.", styles["Normal"]),
        Spacer(1,12),
        Paragraph("Patient / Session", styles["Heading2"]),
    ]
    data = [[str(k), str(v)] for k,v in patient.items()]
    t = Table(data, colWidths=[180, 300])
    t.setStyle(TableStyle([("GRID",(0,0),(-1,-1),.5,colors.grey),("BACKGROUND",(0,0),(0,-1),colors.whitesmoke)]))
    story += [t, Spacer(1,12), Paragraph("Screening result", styles["Heading2"]),
              Paragraph(f"Predicted pattern: {prediction}", styles["Normal"]),
              Paragraph(f"Risk level: {risk}", styles["Normal"]),
              Paragraph("Top model probabilities:", styles["Normal"])]
    for c,p in top_probs:
        story.append(Paragraph(f"• {c}: {p:.1%}", styles["Normal"]))
    story += [Spacer(1,10), Paragraph("Reported symptoms", styles["Heading2"]),
              Paragraph(", ".join(symptoms) if symptoms else "None reported", styles["Normal"]),
              Spacer(1,10), Paragraph("General next steps", styles["Heading2"]),
              Paragraph(notes, styles["Normal"]),
              Spacer(1,16),
              Paragraph("If symptoms are severe, rapidly worsening, or include emergency warning signs, seek urgent medical care. This tool should not be used to make treatment decisions.", styles["Normal"])]
    doc.build(story)

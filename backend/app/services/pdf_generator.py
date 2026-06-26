from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from typing import Dict, Any

def generate_pdf_report(resume_name: str, analysis: Dict[str, Any]) -> bytes:
    """
    Generates a professional PDF report containing the resume analysis results.
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=45,
        leftMargin=45,
        topMargin=45,
        bottomMargin=45
    )
    story = []
    
    # Setup styles
    styles = getSampleStyleSheet()
    
    primary_color = colors.HexColor('#0f172a')  # Slate 900
    secondary_color = colors.HexColor('#4f46e5')  # Indigo 600
    text_color = colors.HexColor('#334155')  # Slate 700
    border_color = colors.HexColor('#e2e8f0')  # Slate 200

    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=22,
        leading=26,
        textColor=primary_color,
        spaceAfter=6
    )
    
    subtitle_style = ParagraphStyle(
        'DocSub',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#64748b'),
        spaceAfter=15
    )

    section_style = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=18,
        textColor=secondary_color,
        spaceBefore=12,
        spaceAfter=6,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'BodyTextCustom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=text_color,
        spaceAfter=8
    )

    bullet_style = ParagraphStyle(
        'BulletCustom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=text_color,
        leftIndent=15,
        firstLineIndent=-10,
        spaceAfter=4
    )

    # Document Header
    story.append(Paragraph("AI Resume Analysis Report", title_style))
    story.append(Paragraph(f"Analyzed Resume: {resume_name}", subtitle_style))
    story.append(Spacer(1, 10))

    # Score Card Grid (ATS Score & Job Match Score)
    ats_val = analysis.get("ats_score", 0)
    match_val = analysis.get("match_percentage", 0)
    
    score_data = [
        [
            Paragraph(f"<b>ATS Compatibility Score</b><br/><font size=30 color='#4f46e5'><b>{ats_val}/100</b></font>", body_style),
            Paragraph(f"<b>Job Description Match</b><br/><font size=30 color='#10b981'><b>{match_val}%</b></font>", body_style)
        ]
    ]
    
    score_table = Table(score_data, colWidths=[250, 250])
    score_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8fafc')),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOX', (0, 0), (-1, -1), 1, border_color),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, border_color),
        ('TOPPADDING', (0, 0), (-1, -1), 15),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 15),
    ]))
    story.append(score_table)
    story.append(Spacer(1, 15))

    # Executive Summaries
    story.append(Paragraph("Executive Summary", section_style))
    exp_summary = analysis.get("experience_summary", "No experience summary available.")
    edu_summary = analysis.get("education_summary", "No education summary available.")
    story.append(Paragraph(f"<b>Experience:</b> {exp_summary}", body_style))
    story.append(Paragraph(f"<b>Education:</b> {edu_summary}", body_style))
    story.append(Spacer(1, 10))

    # Skills Analysis
    story.append(Paragraph("Skills Map", section_style))
    detected_skills = ", ".join(analysis.get("skills_detected", [])) or "None detected"
    missing_skills = ", ".join(analysis.get("missing_skills", [])) or "None missing"
    
    skills_data = [
        [Paragraph("<b>Detected Skills</b>", body_style), Paragraph(detected_skills, body_style)],
        [Paragraph("<b>Missing Skills (Recommended)</b>", body_style), Paragraph(missing_skills, body_style)]
    ]
    
    skills_table = Table(skills_data, colWidths=[120, 380])
    skills_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOX', (0, 0), (-1, -1), 0.5, border_color),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, border_color),
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f1f5f9')),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(skills_table)
    story.append(Spacer(1, 15))

    # Strengths and Weaknesses
    story.append(Paragraph("Key Insights & Recommendations", section_style))
    
    story.append(Paragraph("<b>Strengths:</b>", body_style))
    for strength in analysis.get("strengths", ["Clear structure"]):
        story.append(Paragraph(f"• {strength}", bullet_style))
        
    story.append(Spacer(1, 5))
    story.append(Paragraph("<b>Weaknesses & Gap Analysis:</b>", body_style))
    for weakness in analysis.get("weaknesses", ["Lacks metrics"]):
        story.append(Paragraph(f"• {weakness}", bullet_style))

    story.append(Spacer(1, 10))

    # Actionable Improvement Checklist
    story.append(Paragraph("Actionable Improvement Plan", section_style))
    for suggestion in analysis.get("improvement_suggestions", ["Quantify achievements."]):
        story.append(Paragraph(f"<b>[ ]</b> {suggestion}", bullet_style))
        
    story.append(Spacer(1, 10))

    # Recruiter Tips
    story.append(Paragraph("Recruiter Insider Tips", section_style))
    for tip in analysis.get("recruiter_tips", []):
        story.append(Paragraph(f"💡 {tip}", bullet_style))

    # Build the document
    doc.build(story)
    return buffer.getvalue()

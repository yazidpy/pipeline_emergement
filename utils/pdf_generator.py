import os
from datetime import date
from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image

def generate_daily_planning_pdf(df_planning, report_date, logo_path=None):
    """
    Génère un PDF du planning journalier.
    df_planning: DataFrame avec colonnes [heure_debut, heure_fin, cours_nom, salle, ens_nom]
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=18)
    elements = []
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor("#1e3a5f"),
        alignment=1,
        spaceAfter=20
    )

    # 1. Logo & Entête
    if logo_path and os.path.exists(logo_path):
        img = Image(logo_path, width=80, height=80)
        img.hAlign = 'CENTER'
        elements.append(img)
        elements.append(Spacer(1, 10))

    elements.append(Paragraph(f"Planning du Jour : {report_date}", title_style))
    elements.append(Spacer(1, 20))

    # 2. Données du Tableau
    data = [["Horaire", "Formation / Niveau", "Cours", "Salle", "Enseignant"]]
    
    if df_planning.empty:
        data.append(["-", "Aucun cours prévu", "-", "-", "-"])
    else:
        for _, row in df_planning.iterrows():
            time_range = f"{str(row['heure_debut'])[:5]} - {str(row['heure_fin'])[:5]}"
            form_niv = f"{row.get('formation_nom', 'N/A')}\n({row.get('niveau', 'N/A')})"
            full_ens = f"{row.get('ens_prenom', '')} {row.get('ens_nom', '')}".strip()
            
            data.append([
                time_range,
                form_niv,
                row['cours_nom'],
                row['salle'] if 'salle' in row and row['salle'] else "N/A",
                full_ens if full_ens else "N/A"
            ])

    # 3. Style du Tableau
    # Largeur A4 utile environ 535 points
    table = Table(data, colWidths=[80, 140, 130, 60, 125])
    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1e3a5f")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#d1d5db")),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
    ])
    table.setStyle(style)
    elements.append(table)
    
    # Pied de page
    elements.append(Spacer(1, 50))
    footer_style = ParagraphStyle('Footer', parent=styles['Normal'], fontSize=8, textColor=colors.grey, alignment=1)
    elements.append(Paragraph(f"Généré le {date.today()} par SmartAcademy System", footer_style))

    doc.build(elements)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes

def generate_student_report_pdf(student_data, attendance_df, metrics, logo_path=None):
    """
    Génère un Certificat d'Assiduité formel.
    metrics: dict {'nb_presences', 'nb_absences', 'taux', 'total_heures', 'date_debut', 'date_fin'}
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=50, leftMargin=50, topMargin=50, bottomMargin=50)
    elements = []
    
    styles = getSampleStyleSheet()
    
    # Styles personnalisés
    title_style = ParagraphStyle('CertTitle', parent=styles['Heading1'], fontSize=22, textColor=colors.HexColor("#1e3a5f"), alignment=1, spaceAfter=30)
    normal_style = ParagraphStyle('CertNormal', parent=styles['Normal'], fontSize=11, leading=14, spaceAfter=10)
    header_style = ParagraphStyle('CertHeader', parent=styles['Normal'], fontSize=10, leading=12)
    metric_label_style = ParagraphStyle('MetricLabel', parent=styles['Normal'], fontSize=10, textColor=colors.grey)
    metric_value_style = ParagraphStyle('MetricValue', parent=styles['Normal'], fontSize=12, fontName='Helvetica-Bold')

    # 1. Logo & Organisme
    if logo_path and os.path.exists(logo_path):
        img = Image(logo_path, width=70, height=70)
        img.hAlign = 'CENTER'
        elements.append(img)
        elements.append(Spacer(1, 10))

    elements.append(Paragraph("CERTIFICAT D’ASSIDUITÉ", title_style))
    elements.append(Spacer(1, 10))

    # 2. Infos Organisme
    org_html = """
    <b>Organisme de formation :</b><br/>
    Nom : SmartAcademy Institute<br/>
    Adresse : 123 Rue de l'Innovation, 75001 Paris<br/>
    Téléphone : +33 1 23 45 67 89<br/>
    E-mail : contact@smartacademy.edu
    """
    elements.append(Paragraph(org_html, header_style))
    elements.append(Spacer(1, 20))

    # 3. Corps du certificat
    corps_html = f"""
    <b>CERTIFIE QUE :</b><br/><br/>
    L'apprenant <b>{student_data['prenom']} {student_data['nom'].upper()}</b>, 
    inscrit sous le numéro <b>{student_data['numero_et']}</b>, a participé activement à la formation 
    intitulée : <b>{student_data['formation_nom']}</b> ({student_data['niveau']}).<br/><br/>
    Durée de la formation : du <b>{metrics['date_debut']}</b> au <b>{metrics['date_fin']}</b>.<br/>
    Nombre total d'heures de formation suivies : <b>{metrics['total_heures']} heures</b>.
    """
    elements.append(Paragraph(corps_html, normal_style))
    elements.append(Spacer(1, 20))

    # 4. Indicateurs Clés (Tableau horizontal)
    ind_data = [
        [Paragraph("Présences", metric_label_style), Paragraph("Absences", metric_label_style), Paragraph("Taux d'Assiduité", metric_label_style)],
        [Paragraph(f"{metrics['nb_presences']}", metric_value_style), Paragraph(f"{metrics['nb_absences']}", metric_value_style), Paragraph(f"{metrics['taux']}%", metric_value_style)]
    ]
    ind_table = Table(ind_data, colWidths=[150, 150, 150])
    ind_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 5),
    ]))
    elements.append(ind_table)
    elements.append(Spacer(1, 30))

    # 5. Texte de conclusion
    conclusion = "L'apprenant a assisté aux sessions de formation conformément au calendrier établi. L'assiduité de l'apprenant et son engagement actif ont été remarquables."
    elements.append(Paragraph(conclusion, normal_style))
    elements.append(Spacer(1, 30))

    # 6. Signature
    elements.append(Paragraph(f"Fait à Paris, le <b>{date.today().strftime('%d/%m/%Y')}</b>", normal_style))
    elements.append(Spacer(1, 40))
    
    sig_data = [["", "[Cachet et Signature de l'Organisme]"]]
    sig_table = Table(sig_data, colWidths=[300, 200])
    sig_table.setStyle(TableStyle([('ALIGN', (1, 0), (1, 0), 'CENTER'), ('FONTNAME', (1, 0), (1, 0), 'Helvetica-Oblique')]))
    elements.append(sig_table)

    doc.build(elements)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes

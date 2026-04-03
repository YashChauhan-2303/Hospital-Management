import os
import io
from django.conf import settings
from django.core.files.base import ContentFile
from django.utils import timezone
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT


def generate_billing_pdf(billing):
    """
    Generate a professional A4 invoice PDF using ReportLab.
    Saves the PDF to the Billing instance's pdf_file field.
    """
    buffer = io.BytesIO()
    appointment = billing.appointment
    patient = appointment.patient
    doctor = appointment.doctor

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
    )

    styles = getSampleStyleSheet()
    navy = colors.HexColor('#0f172a')
    blue = colors.HexColor('#3b82f6')
    light_gray = colors.HexColor('#f8fafc')
    mid_gray = colors.HexColor('#64748b')

    title_style = ParagraphStyle(
        'Title', parent=styles['Heading1'],
        fontSize=24, textColor=navy, alignment=TA_LEFT,
        spaceAfter=4, fontName='Helvetica-Bold',
    )
    subtitle_style = ParagraphStyle(
        'Subtitle', parent=styles['Normal'],
        fontSize=11, textColor=blue, alignment=TA_LEFT,
        spaceAfter=2, fontName='Helvetica',
    )
    label_style = ParagraphStyle(
        'Label', parent=styles['Normal'],
        fontSize=9, textColor=mid_gray, fontName='Helvetica',
    )
    value_style = ParagraphStyle(
        'Value', parent=styles['Normal'],
        fontSize=10, textColor=navy, fontName='Helvetica-Bold',
    )
    body_style = ParagraphStyle(
        'Body', parent=styles['Normal'],
        fontSize=10, textColor=navy, fontName='Helvetica',
    )

    elements = []

    # ── Header ───────────────────────────────────────────────────────────────
    elements.append(Paragraph('MediCare HMS', title_style))
    elements.append(Paragraph('Professional Healthcare Management', subtitle_style))
    elements.append(HRFlowable(width='100%', thickness=2, color=blue))
    elements.append(Spacer(1, 0.4 * cm))

    # Invoice meta
    invoice_data = [
        [
            Paragraph('<b>INVOICE</b>', ParagraphStyle('inv', fontSize=18, textColor=navy, fontName='Helvetica-Bold')),
            Paragraph(f'Invoice #: <b>INV-{billing.pk:05d}</b><br/>Date: <b>{billing.issued_at.strftime("%d %B %Y")}</b><br/>Status: <b>{"PAID" if billing.is_paid else "UNPAID"}</b>',
                      ParagraphStyle('invmeta', fontSize=10, textColor=navy, fontName='Helvetica', alignment=TA_RIGHT)),
        ]
    ]
    invoice_table = Table(invoice_data, colWidths=['50%', '50%'])
    invoice_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, 0), 'LEFT'),
        ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    elements.append(invoice_table)
    elements.append(Spacer(1, 0.6 * cm))

    # ── Patient & Doctor Info ─────────────────────────────────────────────────
    info_data = [
        [
            Paragraph('<b>BILLED TO</b>', label_style),
            Paragraph('<b>CONSULTING DOCTOR</b>', label_style),
        ],
        [
            Paragraph(f'<b>{patient.get_full_name()}</b><br/>{patient.email}<br/>{patient.phone or "—"}', value_style),
            Paragraph(f'<b>Dr. {doctor.get_full_name()}</b><br/>{getattr(doctor, "doctor_profile", None) and doctor.doctor_profile.specialization or "Physician"}<br/>{doctor.email}', value_style),
        ],
    ]
    info_table = Table(info_data, colWidths=['50%', '50%'])
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), light_gray),
        ('TEXTCOLOR', (0, 0), (-1, 0), mid_gray),
        ('FONTSIZE', (0, 0), (-1, 0), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 12),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 0.6 * cm))

    # ── Service Table ──────────────────────────────────────────────────────────
    service_header = [
        Paragraph('<b>SERVICE</b>', label_style),
        Paragraph('<b>DATE</b>', label_style),
        Paragraph('<b>TYPE</b>', label_style),
        Paragraph('<b>AMOUNT</b>', label_style),
    ]
    service_row = [
        Paragraph(f'Medical Consultation<br/><font color="#64748b" size="8">Dr. {doctor.get_full_name()}</font>', body_style),
        Paragraph(appointment.appointment_date.strftime('%d %b %Y'), body_style),
        Paragraph(appointment.get_appointment_type_display(), body_style),
        Paragraph(f'₹{billing.amount:,.2f}', ParagraphStyle('amt', fontSize=10, textColor=navy, fontName='Helvetica-Bold', alignment=TA_RIGHT)),
    ]
    service_data = [service_header, service_row]
    service_table = Table(service_data, colWidths=['40%', '20%', '20%', '20%'])
    service_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), light_gray),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8fafc')]),
        ('TEXTCOLOR', (0, 0), (-1, 0), mid_gray),
        ('FONTSIZE', (0, 0), (-1, 0), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('LEFTPADDING', (0, 0), (-1, -1), 12),
        ('ALIGN', (3, 0), (3, -1), 'RIGHT'),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
    ]))
    elements.append(service_table)
    elements.append(Spacer(1, 0.4 * cm))

    # ── Total ──────────────────────────────────────────────────────────────────
    total_data = [
        ['', '', Paragraph('TOTAL', label_style), Paragraph(f'<b>₹{billing.amount:,.2f}</b>', ParagraphStyle('total', fontSize=14, textColor=blue, fontName='Helvetica-Bold', alignment=TA_RIGHT))],
    ]
    total_table = Table(total_data, colWidths=['40%', '20%', '20%', '20%'])
    total_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), light_gray),
        ('TOPPADDING', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('LEFTPADDING', (0, 0), (-1, -1), 12),
        ('ALIGN', (3, 0), (3, -1), 'RIGHT'),
        ('BOX', (0, 0), (-1, -1), 1, blue),
    ]))
    elements.append(total_table)
    elements.append(Spacer(1, 1 * cm))

    # ── Footer ────────────────────────────────────────────────────────────────
    elements.append(HRFlowable(width='100%', thickness=0.5, color=colors.HexColor('#e2e8f0')))
    elements.append(Spacer(1, 0.3 * cm))
    elements.append(Paragraph(
        'Thank you for choosing MediCare HMS. For queries, contact support@medicare-hms.com',
        ParagraphStyle('footer', fontSize=8, textColor=mid_gray, alignment=TA_CENTER, fontName='Helvetica'),
    ))

    doc.build(elements)

    # Save to billing instance
    filename = f'bill_INV{billing.pk:05d}_{patient.username}.pdf'
    billing.pdf_file.save(filename, ContentFile(buffer.getvalue()), save=False)
    buffer.close()

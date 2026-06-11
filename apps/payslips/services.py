import os
from django.conf import settings
from django.core.mail import EmailMessage
from django.utils import timezone
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

from .models import Payslip

def generate_pdf_payslip(payslip):
    """Generates a high-quality PDF payslip for the employee and saves it to media."""
    payroll = payslip.payroll
    employee = payroll.employee
    user = employee.user
    period = payroll.period

    # Create folder if it doesn't exist
    pdf_dir = os.path.join(settings.MEDIA_ROOT, 'payslips')
    os.makedirs(pdf_dir, exist_ok=True)
    
    pdf_filename = f"{payslip.payslip_code}.pdf"
    pdf_path = os.path.join(pdf_dir, pdf_filename)
    
    # ReportLab doc setup
    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )
    
    styles = getSampleStyleSheet()
    
    # Custom Styles
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=18,
        textColor=colors.HexColor('#0F172A'), # Slate 900
        spaceAfter=6
    )
    
    subtitle_style = ParagraphStyle(
        'SubtitleStyle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        textColor=colors.HexColor('#4F46E5'), # Indigo 600
        spaceAfter=15
    )
    
    body_bold = ParagraphStyle(
        'BodyBold',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        textColor=colors.HexColor('#1E293B')
    )
    
    body_normal = ParagraphStyle(
        'BodyNormal',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        textColor=colors.HexColor('#334155')
    )

    story = []
    
    # Title
    story.append(Paragraph("VEESRI ENTERPRISE", title_style))
    story.append(Paragraph(f"PAYSLIP FOR PERIOD: {period.name.upper()}", subtitle_style))
    
    # Employee Details Table (2 columns)
    emp_details = [
        [
            Paragraph("<b>Employee Code:</b>", body_normal), Paragraph(employee.employee_code, body_bold),
            Paragraph("<b>Bank Account:</b>", body_normal), Paragraph(employee.bank_account_number or "-", body_bold)
        ],
        [
            Paragraph("<b>Employee Name:</b>", body_normal), Paragraph(user.get_full_name(), body_bold),
            Paragraph("<b>Bank Name / IFSC:</b>", body_normal), Paragraph(employee.bank_ifsc_code or "-", body_bold)
        ],
        [
            Paragraph("<b>Department:</b>", body_normal), Paragraph(employee.department.name if employee.department else "-", body_bold),
            Paragraph("<b>PF Account:</b>", body_normal), Paragraph(employee.pf_account_number or "-", body_bold)
        ],
        [
            Paragraph("<b>Designation:</b>", body_normal), Paragraph(employee.designation.title if employee.designation else "-", body_bold),
            Paragraph("<b>PAN Number:</b>", body_normal), Paragraph(employee.pan_number or "-", body_bold)
        ]
    ]
    
    det_table = Table(emp_details, colWidths=[110, 160, 110, 160])
    det_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8FAFC')),
        ('PADDING', (0,0), (-1,-1), 6),
        ('LINEBELOW', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    
    story.append(det_table)
    story.append(Spacer(1, 20))
    
    # Earnings vs Deductions Table
    basic = float(payroll.basic_salary)
    hra = float(payroll.hra)
    da = float(payroll.da)
    travel = float(payroll.travel_allowance)
    medical = float(payroll.medical_allowance)
    bonus = float(payroll.bonus)
    ot = float(payroll.overtime_pay)
    
    pf = float(payroll.pf_deduction)
    esi = float(payroll.esi_deduction)
    pt = float(payroll.professional_tax)
    tds = float(payroll.income_tax)
    leave_ded = float(payroll.leave_deductions)
    late = float(payroll.late_penalties)
    
    gross_earnings = basic + hra + da + travel + medical + ot + bonus
    gross_deductions = pf + esi + pt + tds + leave_ded + late
    net_salary = gross_earnings - gross_deductions
    
    breakdown_data = [
        [Paragraph("<b>EARNINGS</b>", body_bold), Paragraph("<b>AMOUNT</b>", body_bold), 
         Paragraph("<b>DEDUCTIONS</b>", body_bold), Paragraph("<b>AMOUNT</b>", body_bold)],
        
        [Paragraph("Basic Salary", body_normal), Paragraph(f"${basic:.2f}", body_normal),
         Paragraph("Provident Fund (PF)", body_normal), Paragraph(f"${pf:.2f}", body_normal)],
        
        [Paragraph("House Rent Allowance (HRA)", body_normal), Paragraph(f"${hra:.2f}", body_normal),
         Paragraph("Employee State Ins (ESI)", body_normal), Paragraph(f"${esi:.2f}", body_normal)],
        
        [Paragraph("Dearness Allowance (DA)", body_normal), Paragraph(f"${da:.2f}", body_normal),
         Paragraph("Professional Tax (PT)", body_normal), Paragraph(f"${pt:.2f}", body_normal)],
        
        [Paragraph("Travel Allowance", body_normal), Paragraph(f"${travel:.2f}", body_normal),
         Paragraph("TDS / Income Tax", body_normal), Paragraph(f"${tds:.2f}", body_normal)],
        
        [Paragraph("Medical Allowance", body_normal), Paragraph(f"${medical:.2f}", body_normal),
         Paragraph("Leave Deductions", body_normal), Paragraph(f"${leave_ded:.2f}", body_normal)],
        
        [Paragraph("Overtime Pay", body_normal), Paragraph(f"${ot:.2f}", body_normal),
         Paragraph("Late Penalty Deduction", body_normal), Paragraph(f"${late:.2f}", body_normal)],
        
        [Paragraph("Bonus & Adjustments", body_normal), Paragraph(f"${bonus:.2f}", body_normal),
         Paragraph("", body_normal), Paragraph("", body_normal)],
        
        [Paragraph("<b>Gross Earnings</b>", body_bold), Paragraph(f"<b>${gross_earnings:.2f}</b>", body_bold),
         Paragraph("<b>Gross Deductions</b>", body_bold), Paragraph(f"<b>${gross_deductions:.2f}</b>", body_bold)],
    ]
    
    breakdown_table = Table(breakdown_data, colWidths=[180, 90, 180, 90])
    breakdown_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (1,0), colors.HexColor('#EEF2F6')),
        ('BACKGROUND', (2,0), (3,0), colors.HexColor('#FEE2E2')),
        ('PADDING', (0,0), (-1,-1), 6),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('ALIGN', (1,1), (1,-1), 'RIGHT'),
        ('ALIGN', (3,1), (3,-1), 'RIGHT'),
        ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor('#F1F5F9')),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    
    story.append(breakdown_table)
    story.append(Spacer(1, 15))
    
    # Net Salary Summary Table
    summary_data = [
        [Paragraph("<b>NET PAYABLE SALARY:</b>", body_bold), Paragraph(f"<b>${net_salary:.2f}</b>", title_style)]
    ]
    summary_table = Table(summary_data, colWidths=[200, 340])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#EEF2F6')),
        ('PADDING', (0,0), (-1,-1), 10),
        ('ALIGN', (1,0), (1,0), 'RIGHT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOX', (0,0), (-1,-1), 1.5, colors.HexColor('#4F46E5')),
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 30))
    
    # Signatures Table
    sig_data = [
        [Paragraph("_____________________________<br/><b>Employee Signature</b>", body_normal),
         Paragraph("_____________________________<br/><b>Authorized Seal & Signature</b>", body_normal)]
    ]
    sig_table = Table(sig_data, colWidths=[270, 270])
    sig_table.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 20),
    ]))
    story.append(sig_table)

    # Build PDF
    doc.build(story)
    
    # Save the relative file path to the model
    payslip.pdf_file.name = f"payslips/{pdf_filename}"
    payslip.save()
    return pdf_path

def dispatch_payslip_email(payslip):
    """Sends the generated payslip PDF to the employee's email address."""
    payroll = payslip.payroll
    employee = payroll.employee
    user = employee.user
    
    if not user.email:
        print(f"Skipping email dispatch for {user.username} - no email configured.")
        return False
        
    subject = f"Payslip for {payroll.period.name} - Veesri Enterprise"
    
    html_message = f"""
    <html>
      <body style="font-family: Arial, sans-serif; color: #334155; line-height: 1.6;">
        <h2 style="color: #4f46e5;">Hello {user.get_full_name()},</h2>
        <p>Your payslip for <strong>{payroll.period.name}</strong> is now ready and available for download.</p>
        <table style="border-collapse: collapse; width: 100%; max-width: 400px; margin: 15px 0;">
          <tr style="background-color: #f8fafc; border-bottom: 1px solid #e2e8f0;">
            <th style="padding: 8px; text-align: left;">Employee Code</th>
            <td style="padding: 8px;">{employee.employee_code}</td>
          </tr>
          <tr style="border-bottom: 1px solid #e2e8f0;">
            <th style="padding: 8px; text-align: left;">Net Salary</th>
            <td style="padding: 8px; font-weight: bold; color: #0f172a;">${payroll.net_salary:.2f}</td>
          </tr>
        </table>
        <p>Please find the attached PDF copy of your payslip for your records.</p>
        <p>Best Regards,<br/><strong>HR Operations Team</strong><br/>Veesri Enterprise</p>
      </body>
    </html>
    """
    
    email = EmailMessage(
        subject,
        html_message,
        settings.DEFAULT_FROM_EMAIL or 'hr@veesri.com',
        [user.email]
    )
    email.content_subtype = "html"
    
    # Attach PDF
    pdf_path = os.path.join(settings.MEDIA_ROOT, payslip.pdf_file.name)
    if os.path.exists(pdf_path):
        email.attach_file(pdf_path)
        
    try:
        email.send()
        payslip.is_email_sent = True
        payslip.sent_at = timezone.now()
        payslip.save()
        return True
    except Exception as e:
        print(f"Failed to send email to {user.email}:", e)
        return False

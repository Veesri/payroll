import time
import threading
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os
from datetime import datetime

def send_email_job(app):
    with app.app_context():
        from models import db, EmailQueue, EmailLog, EmailSettings
        
        # Give db time to initialize on fresh start
        time.sleep(5)
        
        while True:
            try:
                # Check for pending emails
                pending_emails = EmailQueue.query.filter_by(status='pending').all()
                if pending_emails:
                    settings = EmailSettings.query.first()
                    
                    # Fallback to ENV variables
                    smtp_host = settings.smtp_host if (settings and settings.smtp_host) else os.environ.get('MAIL_SERVER')
                    smtp_port = settings.smtp_port if (settings and settings.smtp_port) else int(os.environ.get('MAIL_PORT', 587))
                    use_tls = settings.use_tls if settings else (os.environ.get('MAIL_USE_TLS', 'True').lower() in ['true', '1', 'on'])
                    use_ssl = settings.use_ssl if settings else False
                    smtp_username = settings.smtp_username if (settings and settings.smtp_username) else os.environ.get('MAIL_USERNAME')
                    smtp_password = settings.smtp_password if (settings and settings.smtp_password) else os.environ.get('MAIL_PASSWORD')
                    sender_name = settings.sender_name if (settings and settings.sender_name) else "HR Department"
                    sender_email = settings.sender_email if (settings and settings.sender_email) else os.environ.get('MAIL_DEFAULT_SENDER')
                    reply_to = settings.reply_to if settings else None
                    provider_type = settings.provider_type if settings else 'env_fallback'
                    
                    if not smtp_host:
                        print("Email Settings not configured in UI or .env missing MAIL_SERVER. Marking failed.")
                        for email_job in pending_emails:
                            email_job.status = 'failed'
                            log = EmailLog(
                                email_queue_id=email_job.id,
                                recipient=email_job.recipient,
                                subject=email_job.subject,
                                status='failed',
                                error_message="SMTP configuration is missing."
                            )
                            db.session.add(log)
                        db.session.commit()
                        time.sleep(10)
                        continue

                    server = None
                    try:
                        # Setup SMTP connection per batch
                        if use_ssl:
                            server = smtplib.SMTP_SSL(smtp_host, smtp_port)
                        else:
                            server = smtplib.SMTP(smtp_host, smtp_port)
                            if use_tls:
                                server.starttls()
                                
                        if smtp_username and smtp_password:
                            server.login(smtp_username, smtp_password)
                            
                        for email_job in pending_emails:
                            try:
                                msg = MIMEMultipart()
                                msg['From'] = f"{sender_name} <{sender_email}>"
                                msg['To'] = email_job.recipient
                                msg['Subject'] = email_job.subject
                                if reply_to:
                                    msg['Reply-To'] = reply_to
                                
                                msg.attach(MIMEText(email_job.body, 'html'))

                                # Attachments
                                if email_job.attachment_path:
                                    paths = email_job.attachment_path.split(',')
                                    for p in paths:
                                        p = p.strip()
                                        if os.path.exists(p):
                                            with open(p, "rb") as attachment:
                                                part = MIMEBase('application', 'octet-stream')
                                                part.set_payload(attachment.read())
                                            encoders.encode_base64(part)
                                            part.add_header('Content-Disposition', f"attachment; filename= {os.path.basename(p)}")
                                            msg.attach(part)
                                
                                server.send_message(msg)
                                email_job.status = 'sent'
                                
                                # Log success
                                log = EmailLog(
                                    email_queue_id=email_job.id,
                                    recipient=email_job.recipient,
                                    subject=email_job.subject,
                                    status='sent',
                                    provider=provider_type
                                )
                                db.session.add(log)
                                
                            except Exception as e:
                                email_job.status = 'failed'
                                email_job.retry_count += 1
                                log = EmailLog(
                                    email_queue_id=email_job.id,
                                    recipient=email_job.recipient,
                                    subject=email_job.subject,
                                    status='failed',
                                    error_message=str(e),
                                    provider=provider_type
                                )
                                db.session.add(log)
                                
                            db.session.commit()
                            
                    except Exception as conn_e:
                        print(f"SMTP Connection Error: {conn_e}")
                        # Mark all as failed if connection fails
                        for email_job in pending_emails:
                            email_job.status = 'failed'
                            email_job.retry_count += 1
                            log = EmailLog(
                                email_queue_id=email_job.id,
                                recipient=email_job.recipient,
                                subject=email_job.subject,
                                status='failed',
                                error_message=str(conn_e),
                                provider=provider_type
                            )
                            db.session.add(log)
                        db.session.commit()
                        
                    finally:
                        if server:
                            try:
                                server.quit()
                            except:
                                pass
            except Exception as e:
                print(f"Email Worker Loop Error: {e}")
            
            # Poll every 10 seconds
            time.sleep(10)

def start_email_worker(app):
    worker_thread = threading.Thread(target=send_email_job, args=(app,), daemon=True)
    worker_thread.start()
    return worker_thread

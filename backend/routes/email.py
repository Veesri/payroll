from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from models import db, EmailSettings, EmailTemplate, EmailQueue, EmailLog, Employee
from routes.employee import role_required
from datetime import datetime, timedelta

email_bp = Blueprint('email', __name__)

@email_bp.route('/settings', methods=['GET'])
@jwt_required()
@role_required(['hr_admin', 'super_admin'])
def get_settings():
    settings = EmailSettings.query.first()
    if not settings:
        settings = EmailSettings()
        db.session.add(settings)
        db.session.commit()
    
    return jsonify({
        'id': settings.id,
        'provider_type': settings.provider_type,
        'smtp_host': settings.smtp_host,
        'smtp_port': settings.smtp_port,
        'smtp_username': settings.smtp_username,
        'smtp_password': settings.smtp_password, # Optional to hide this in prod
        'use_tls': settings.use_tls,
        'use_ssl': settings.use_ssl,
        'sender_name': settings.sender_name,
        'sender_email': settings.sender_email,
        'reply_to': settings.reply_to,
        'status': settings.status
    }), 200

@email_bp.route('/settings', methods=['PUT'])
@jwt_required()
@role_required(['hr_admin', 'super_admin'])
def update_settings():
    data = request.get_json()
    settings = EmailSettings.query.first()
    if not settings:
        settings = EmailSettings()
        db.session.add(settings)
        
    settings.provider_type = data.get('provider_type', settings.provider_type)
    settings.smtp_host = data.get('smtp_host', settings.smtp_host)
    settings.smtp_port = data.get('smtp_port', settings.smtp_port)
    settings.smtp_username = data.get('smtp_username', settings.smtp_username)
    settings.smtp_password = data.get('smtp_password', settings.smtp_password)
    settings.use_tls = data.get('use_tls', settings.use_tls)
    settings.use_ssl = data.get('use_ssl', settings.use_ssl)
    settings.sender_name = data.get('sender_name', settings.sender_name)
    settings.sender_email = data.get('sender_email', settings.sender_email)
    settings.reply_to = data.get('reply_to', settings.reply_to)
    
    db.session.commit()
    return jsonify(message="Email settings updated successfully"), 200

@email_bp.route('/test', methods=['POST'])
@jwt_required()
@role_required(['hr_admin', 'super_admin'])
def test_email():
    data = request.get_json()
    recipient = data.get('email')
    if not recipient:
        return jsonify(message="Recipient email required"), 400
        
    # Push test to queue
    q = EmailQueue(
        recipient=recipient,
        subject="Test Email from Enterprise HRMS",
        body="<h3>Success!</h3><p>Your SMTP settings are configured correctly.</p>"
    )
    db.session.add(q)
    db.session.commit()
    
    return jsonify(message="Test email queued. Please check logs to verify delivery."), 200

@email_bp.route('/templates', methods=['GET', 'POST'])
@jwt_required()
@role_required(['hr_admin', 'super_admin'])
def manage_templates():
    if request.method == 'GET':
        templates = EmailTemplate.query.all()
        return jsonify([{
            'id': t.id,
            'name': t.name,
            'subject': t.subject,
            'body': t.body,
            'updated_at': t.updated_at.strftime('%Y-%m-%d %H:%M')
        } for t in templates]), 200
        
    if request.method == 'POST':
        data = request.get_json()
        if not data.get('name') or not data.get('subject'):
            return jsonify(message="Name and Subject required"), 400
            
        t = EmailTemplate(
            name=data['name'],
            subject=data['subject'],
            body=data.get('body', '')
        )
        db.session.add(t)
        db.session.commit()
        return jsonify(message="Template created successfully"), 201

@email_bp.route('/templates/<int:id>', methods=['PUT', 'DELETE'])
@jwt_required()
@role_required(['hr_admin', 'super_admin'])
def update_template(id):
    t = EmailTemplate.query.get_or_404(id)
    if request.method == 'PUT':
        data = request.get_json()
        t.name = data.get('name', t.name)
        t.subject = data.get('subject', t.subject)
        t.body = data.get('body', t.body)
        db.session.commit()
        return jsonify(message="Template updated successfully"), 200
        
    if request.method == 'DELETE':
        db.session.delete(t)
        db.session.commit()
        return jsonify(message="Template deleted"), 200

@email_bp.route('/compose', methods=['POST'])
@jwt_required()
@role_required(['hr_admin', 'super_admin'])
def compose_email():
    data = request.get_json()
    audience = data.get('audience', 'specific') # all, department, specific
    dept_id = data.get('department_id')
    emp_ids = data.get('employee_ids', [])
    subject = data.get('subject')
    body = data.get('body')
    
    if not subject or not body:
        return jsonify(message="Subject and body required"), 400
        
    query = Employee.query.filter_by(status='active')
    
    if audience == 'all':
        pass
    elif audience == 'department':
        query = query.filter_by(department_id=dept_id)
    else:
        query = query.filter(Employee.id.in_(emp_ids))
        
    employees = query.all()
    queued_count = 0
    
    for emp in employees:
        if emp.email:
            # simple var replacement
            personalized_body = body.replace('{{employee_name}}', emp.first_name).replace('{{employee_id}}', str(emp.id))
            q = EmailQueue(
                recipient=emp.email,
                subject=subject,
                body=personalized_body
            )
            db.session.add(q)
            queued_count += 1
            
    db.session.commit()
    return jsonify(message=f"Queued {queued_count} emails successfully"), 201

@email_bp.route('/queue', methods=['GET'])
@jwt_required()
@role_required(['hr_admin', 'super_admin'])
def get_queue():
    status_filter = request.args.get('status')
    query = EmailQueue.query
    if status_filter:
        query = query.filter_by(status=status_filter)
        
    queue = query.order_by(EmailQueue.created_at.desc()).limit(100).all()
    return jsonify([{
        'id': q.id,
        'recipient': q.recipient,
        'subject': q.subject,
        'status': q.status,
        'retry_count': q.retry_count,
        'created_at': q.created_at.strftime('%Y-%m-%d %H:%M')
    } for q in queue]), 200

@email_bp.route('/logs', methods=['GET'])
@jwt_required()
@role_required(['hr_admin', 'super_admin'])
def get_logs():
    logs = EmailLog.query.order_by(EmailLog.sent_at.desc()).limit(100).all()
    return jsonify([{
        'id': l.id,
        'recipient': l.recipient,
        'subject': l.subject,
        'status': l.status,
        'provider': l.provider,
        'sent_at': l.sent_at.strftime('%Y-%m-%d %H:%M'),
        'error_message': l.error_message
    } for l in logs]), 200

@email_bp.route('/dashboard', methods=['GET'])
@jwt_required()
@role_required(['hr_admin', 'super_admin'])
def get_dashboard_stats():
    total = EmailLog.query.count()
    delivered = EmailLog.query.filter_by(status='sent').count()
    failed = EmailLog.query.filter_by(status='failed').count()
    pending = EmailQueue.query.filter_by(status='pending').count()
    
    return jsonify({
        'total': total,
        'delivered': delivered,
        'failed': failed,
        'pending': pending
    }), 200

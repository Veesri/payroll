import os
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from config import Config
from models import db
from datetime import timedelta

def create_app(config_class=Config):
    app = Flask(__name__, static_folder='uploads', static_url_path='/uploads')
    app.config.from_object(config_class)
    
    # Configure JWT expiration
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=12)

    CORS(app)
    db.init_app(app)
    Migrate(app, db)
    jwt = JWTManager(app)

    # Mail Configuration (Supports environment variables or falls back to dummy)
    app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', 587))
    app.config['MAIL_USE_TLS'] = os.environ.get('MAIL_USE_TLS', 'True').lower() in ['true', 'on', '1']
    app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME', 'dummy@example.com')
    app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD', 'dummy_password')
    app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER', 'dummy@example.com')
    app.config['MAIL_SUPPRESS_SEND'] = os.environ.get('MAIL_SUPPRESS_SEND', 'True').lower() in ['true', 'on', '1']

    
    from flask_mail import Mail
    mail = Mail(app)
    app.mail = mail

    # Register blueprints (routes)
    from routes.auth import auth_bp
    from routes.department import department_bp
    from routes.employee import employee_bp
    from routes.attendance import attendance_bp
    from routes.leaves import leave_bp
    from routes.salary import salary_bp
    from routes.payroll import payroll_bp
    from routes.payslip import payslip_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(department_bp, url_prefix='/api/departments')
    app.register_blueprint(employee_bp, url_prefix='/api/employees')
    app.register_blueprint(attendance_bp, url_prefix='/api/attendance')
    app.register_blueprint(leave_bp, url_prefix='/api/leaves')
    app.register_blueprint(salary_bp, url_prefix='/api/salary')
    app.register_blueprint(payroll_bp, url_prefix='/api/payroll')
    app.register_blueprint(payslip_bp, url_prefix='/api/payslips')

    @app.route('/health', methods=['GET'])
    def health_check():
        return {'status': 'healthy', 'message': 'HRMS API is running'}, 200

    return app

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5000)

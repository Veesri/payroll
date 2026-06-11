from app import create_app
from models import db, User, Employee, Department
from werkzeug.security import generate_password_hash

app = create_app()

def seed():
    with app.app_context():
        # Ensure all tables are created in the database
        db.create_all()

        if User.query.filter_by(username='superadmin').first():
            print("Database already seeded.")
            return

        print("Seeding database...")
        # Create Super Admin
        super_admin = User(
            username='superadmin',
            password_hash=generate_password_hash('password123'),
            role='super_admin',
            is_approved=True
        )

        # Create HR Admin
        hr_admin = User(
            username='hradmin',
            password_hash=generate_password_hash('password123'),
            role='hr_admin',
            is_approved=True
        )

        # Create an Employee User
        emp_user = User(
            username='employee1',
            password_hash=generate_password_hash('password123'),
            role='employee',
            is_approved=True
        )

        db.session.add_all([super_admin, hr_admin, emp_user])
        db.session.commit()

        # Create Department
        it_dept = Department(name='IT Department', description='Information Technology')
        db.session.add(it_dept)
        db.session.commit()

        # Create Employee profile
        emp_profile = Employee(
            user_id=emp_user.id,
            department_id=it_dept.id,
            first_name='John',
            last_name='Doe',
            email='john.doe@example.com',
            phone='1234567890',
            designation='Software Engineer'
        )
        db.session.add(emp_profile)
        db.session.commit()

        print("Seed completed successfully.")

if __name__ == '__main__':
    seed()

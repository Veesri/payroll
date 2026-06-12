from app import create_app
from models import db, LeaveType

app = create_app()

def seed_leave_types():
    with app.app_context():
        if not LeaveType.query.first():
            types = [
                LeaveType(name="Casual Leave", days_allowed=12),
                LeaveType(name="Sick Leave", days_allowed=15),
                LeaveType(name="Earned Leave", days_allowed=24),
                LeaveType(name="Loss of Pay", days_allowed=30)
            ]
            db.session.add_all(types)
            db.session.commit()
            print("Successfully seeded leave types!")
        else:
            print("Leave types already exist.")

if __name__ == "__main__":
    seed_leave_types()

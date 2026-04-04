from app import app
from models import db, User
from werkzeug.security import generate_password_hash

def create_manager():
    with app.app_context():
        # Check if manager already exists
        manager = User.query.filter_by(phone='9999999999').first()
        if not manager:
            manager = User(
                phone='9999999999',
                name='Fleet Administrator',
                role='FLEET_MANAGER',
                password_hash=generate_password_hash('admin123')
            )
            db.session.add(manager)
            db.session.commit()
            print("Manager account created: 9999999999 / admin123")
        else:
            print("Manager account already exists: 9999999999 / admin123")

if __name__ == "__main__":
    create_manager()

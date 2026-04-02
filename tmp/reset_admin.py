from backend.auth import hash_password
from backend.database import SessionLocal
from backend.models import Admin

def reset():
    db = SessionLocal()
    admin = db.query(Admin).filter(Admin.username == 'admin').first()
    if admin:
        admin.password_hash = hash_password('admin123')
        print("Admin password reset to 'admin123'")
    else:
        admin = Admin(username='admin', password_hash=hash_password('admin123'))
        db.add(admin)
        print("Admin created with username 'admin' and password 'admin123'")
    db.commit()
    db.close()

if __name__ == "__main__":
    reset()

"""
Run with: poetry run python seed.py
"""
from app.config.database import SessionLocal, engine, Base
from app.models.models import User, Task
from app.utils.password import hash_password

Base.metadata.create_all(bind=engine)

db = SessionLocal()

try:
    # Admin user
    if not db.query(User).filter(User.email == "admin@example.com").first():
        admin = User(
            name="Admin User",
            email="admin@example.com",
            password=hash_password("Admin@123"),
            role="ADMIN",
        )
        db.add(admin)
        db.flush()

    # Regular user
    if not db.query(User).filter(User.email == "user@example.com").first():
        user = User(
            name="Regular User",
            email="user@example.com",
            password=hash_password("User@123"),
            role="USER",
        )
        db.add(user)
        db.flush()

        db.add_all([
            Task(title="Set up project",   status="DONE",        priority="HIGH",   userId=user.id,
                 description="Initialize the FastAPI project"),
            Task(title="Write API docs",   status="IN_PROGRESS", priority="MEDIUM", userId=user.id,
                 description="Document all endpoints with Swagger"),
            Task(title="Add unit tests",   status="TODO",        priority="LOW",    userId=user.id,
                 description="Cover auth and task routers"),
        ])

    db.commit()
    print("✅ Seed complete")
    print("   Admin  → admin@example.com / Admin@123")
    print("   User   → user@example.com  / User@123")

except Exception as e:
    db.rollback()
    print(f"❌ Seed failed: {e}")
finally:
    db.close()

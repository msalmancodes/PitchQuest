from pitchquest_api.database import engine
from pitchquest_api.models import Base

def create_tables():
    """Create all database tables"""
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created successfully!")
        print("Tables created:")
        print("  - sessions")
        print("  - messages") 
        print("  - evaluations")
    except Exception as e:
        print(f"❌ Failed to create tables: {e}")

if __name__ == "__main__":
    create_tables()
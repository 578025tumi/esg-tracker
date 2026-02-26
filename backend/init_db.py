from database import engine, Base
# Import your models here so Base knows about them
from models import ESGJob 

def create_tables():
    print("Connecting to Supabase and creating tables...")
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ Tables created successfully in Supabase!")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    create_tables()
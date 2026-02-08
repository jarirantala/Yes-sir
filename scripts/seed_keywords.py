
import sys
import os

# Add backend directory to sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), '../backend'))

import database

def seed():
    print("Seeding keywords...")
    try:
        # Seed 'home' -> '1600 Amphitheatre Parkway, Mountain View, CA'
        home = database.save_keyword('home', '1600 Amphitheatre Parkway, Mountain View, CA')
        print(f"Seeded home: {home}")
        
        # Seed 'office' -> '111 8th Ave, New York, NY'
        office = database.save_keyword('office', '111 8th Ave, New York, NY')
        print(f"Seeded office: {office}")
        
        print("Seeding complete.")
        
        # Verify
        print("\nVerifying...")
        keywords = database.get_all_keywords()
        print(f"Keywords in DB: {keywords}")
        
    except Exception as e:
        print(f"Error seeding: {e}")

if __name__ == "__main__":
    seed()

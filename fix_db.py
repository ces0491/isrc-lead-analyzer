#!/usr/bin/env python3
"""
Database fix script for PostgreSQL JSON index issue
Run this script to fix the database without manual SQL commands
"""

import psycopg2
import os

# Your database connection string
DATABASE_URL = "postgresql://isrc_analyzer_user:NIzOKKFFQcoP0jFiOdyFif3yeZT00nBv@dpg-d1qddpjipnbc738ua6fg-a/isrc_analyzer"

def fix_database():
    """Fix the PostgreSQL JSON index issue"""
    
    # SQL commands to fix the issue
    fix_commands = [
        "DROP INDEX IF EXISTS ix_processing_performance;",
        "CREATE INDEX IF NOT EXISTS ix_processing_logs_time ON processing_logs (processing_time_seconds);",
        "CREATE INDEX IF NOT EXISTS ix_processing_logs_sources_gin ON processing_logs USING GIN (data_sources_used);",
        "CREATE INDEX IF NOT EXISTS ix_processing_logs_performance_partial ON processing_logs (processing_time_seconds) WHERE data_sources_used IS NOT NULL;",
    ]
    
    verification_command = "SELECT indexname FROM pg_indexes WHERE tablename = 'processing_logs' ORDER BY indexname;"
    
    try:
        # Connect to database
        print("🔌 Connecting to PostgreSQL database...")
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        # Execute fix commands
        print("🔧 Executing database fixes...")
        for i, command in enumerate(fix_commands, 1):
            print(f"   {i}. {command}")
            cursor.execute(command)
        
        # Commit changes
        conn.commit()
        print("✅ Database fixes applied successfully!")
        
        # Verify the fix
        print("\n🔍 Verifying indexes...")
        cursor.execute(verification_command)
        indexes = cursor.fetchall()
        
        print("Current processing_logs indexes:")
        for index in indexes:
            print(f"   - {index[0]}")
        
        # Close connection
        cursor.close()
        conn.close()
        
        print("\n🎉 Database fix completed successfully!")
        print("Your Prism Analytics Engine should now start without errors.")
        
    except Exception as e:
        print(f"❌ Database fix failed: {e}")
        print("\nTry one of the other connection methods or check your connection details.")
        return False
    
    return True

if __name__ == "__main__":
    fix_database()

# Save this as fix_database.py and run with:
# python fix_database.py
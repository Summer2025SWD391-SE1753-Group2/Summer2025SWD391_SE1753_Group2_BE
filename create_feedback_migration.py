#!/usr/bin/env python3
"""
Migration script to create feedback tables and seed default data
"""

import uuid
from datetime import datetime, timezone
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.core.settings import settings

def create_feedback_tables():
    """Create feedback tables"""
    engine = create_engine(settings.DATABASE_URL)
    
    # Create feedback_type table
    create_feedback_type_table = """
    CREATE TABLE IF NOT EXISTS feedback_type (
        feedback_type_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        name VARCHAR(100) UNIQUE NOT NULL,
        display_name VARCHAR(200) NOT NULL,
        description TEXT,
        icon VARCHAR(100),
        color VARCHAR(7),
        is_default BOOLEAN DEFAULT FALSE,
        status VARCHAR(20) DEFAULT 'active',
        sort_order VARCHAR(10) DEFAULT '0',
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        created_by UUID REFERENCES account(account_id),
        updated_by UUID REFERENCES account(account_id)
    );
    """
    
    # Create feedback table
    create_feedback_table = """
    CREATE TABLE IF NOT EXISTS feedback (
        feedback_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        title VARCHAR(300) NOT NULL,
        description TEXT NOT NULL,
        feedback_type_id UUID NOT NULL REFERENCES feedback_type(feedback_type_id),
        priority VARCHAR(20) DEFAULT 'medium',
        status VARCHAR(20) DEFAULT 'pending',
        screenshot_url TEXT,
        browser_info VARCHAR(200),
        device_info VARCHAR(200),
        resolution_note TEXT,
        resolved_at TIMESTAMP WITH TIME ZONE,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        created_by UUID NOT NULL REFERENCES account(account_id),
        updated_by UUID REFERENCES account(account_id),
        resolved_by UUID REFERENCES account(account_id)
    );
    """
    
    # Create indexes
    create_indexes = """
    CREATE INDEX IF NOT EXISTS idx_feedback_type_name ON feedback_type(name);
    CREATE INDEX IF NOT EXISTS idx_feedback_created_by ON feedback(created_by);
    CREATE INDEX IF NOT EXISTS idx_feedback_status ON feedback(status);
    CREATE INDEX IF NOT EXISTS idx_feedback_type_id ON feedback(feedback_type_id);
    CREATE INDEX IF NOT EXISTS idx_feedback_created_at ON feedback(created_at);
    """
    
    with engine.connect() as conn:
        print("Creating feedback_type table...")
        conn.execute(text(create_feedback_type_table))
        
        print("Creating feedback table...")
        conn.execute(text(create_feedback_table))
        
        print("Creating indexes...")
        conn.execute(text(create_indexes))
        
        conn.commit()
        print("✅ Tables created successfully!")

def seed_default_feedback_types():
    """Seed default feedback types"""
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    default_types = [
        {
            "name": "bug_report",
            "display_name": "Bug Report",
            "description": "Report a bug or technical issue",
            "icon": "bug",
            "color": "#dc3545",
            "is_default": True,
            "sort_order": "1"
        },
        {
            "name": "feature_request",
            "display_name": "Feature Request",
            "description": "Request a new feature or improvement",
            "icon": "lightbulb",
            "color": "#28a745",
            "is_default": True,
            "sort_order": "2"
        },
        {
            "name": "content_report",
            "display_name": "Content Report",
            "description": "Report inappropriate content",
            "icon": "flag",
            "color": "#ffc107",
            "is_default": True,
            "sort_order": "3"
        },
        {
            "name": "user_report",
            "display_name": "User Report",
            "description": "Report user misconduct or violation",
            "icon": "user-times",
            "color": "#fd7e14",
            "is_default": True,
            "sort_order": "4"
        },
        {
            "name": "general_feedback",
            "display_name": "General Feedback",
            "description": "General feedback or suggestions",
            "icon": "comment",
            "color": "#6f42c1",
            "is_default": True,
            "sort_order": "5"
        },
        {
            "name": "other",
            "display_name": "Other",
            "description": "Other types of feedback",
            "icon": "ellipsis-h",
            "color": "#6c757d",
            "is_default": True,
            "sort_order": "6"
        }
    ]
    
    with SessionLocal() as db:
        for feedback_type_data in default_types:
            # Check if type already exists
            existing = db.execute(
                text("SELECT 1 FROM feedback_type WHERE name = :name"),
                {"name": feedback_type_data["name"]}
            ).first()
            
            if not existing:
                insert_query = """
                INSERT INTO feedback_type (
                    name, display_name, description, icon, color, 
                    is_default, status, sort_order, created_at, updated_at
                ) VALUES (
                    :name, :display_name, :description, :icon, :color,
                    :is_default, :status, :sort_order, :created_at, :updated_at
                )
                """
                
                db.execute(text(insert_query), {
                    **feedback_type_data,
                    "status": "active",
                    "created_at": datetime.now(timezone.utc),
                    "updated_at": datetime.now(timezone.utc)
                })
                print(f"✅ Created feedback type: {feedback_type_data['display_name']}")
            else:
                print(f"⏭️  Feedback type already exists: {feedback_type_data['display_name']}")
        
        db.commit()
        print("✅ Default feedback types seeded successfully!")

def main():
    print("🚀 Starting Feedback Migration...")
    print("=" * 50)
    
    try:
        # Create tables
        create_feedback_tables()
        
        # Seed default data
        seed_default_feedback_types()
        
        print("\n🎉 Migration completed successfully!")
        print("=" * 50)
        print("📋 What was created:")
        print("   - feedback_type table")
        print("   - feedback table")
        print("   - Default feedback types (6 types)")
        print("   - Indexes for performance")
        
    except Exception as e:
        print(f"❌ Migration failed: {str(e)}")
        raise

if __name__ == "__main__":
    main() 
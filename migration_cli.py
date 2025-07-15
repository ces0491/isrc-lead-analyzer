# migration_cli.py
"""
Command-line interface for database migrations
Simple commands to manage Prism Analytics Engine database schema
"""

import sys
import argparse
import subprocess
from pathlib import Path

def run_command(cmd, description):
    """Run a command with nice output"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=True)
        if result.stdout:
            print(f"   {result.stdout.strip()}")
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        if e.stdout:
            print(f"   Output: {e.stdout}")
        if e.stderr:
            print(f"   Error: {e.stderr}")
        return False

def install_alembic():
    """Install Alembic if not present"""
    try:
        import alembic
        print(f"✅ Alembic is already installed (version {alembic.__version__})")
        return True
    except ImportError:
        print("📦 Installing Alembic...")
        return run_command(f"{sys.executable} -m pip install alembic", "Alembic installation")

def init_migrations():
    """Initialize migrations for the first time"""
    print("🎵 Initializing migrations for Prism Analytics Engine...")
    
    if not install_alembic():
        return False
    
    # Run the setup script
    return run_command(f"{sys.executable} setup_migrations.py", "Migration setup")

def create_migration(message):
    """Create a new migration"""
    if not message:
        message = input("Enter migration description: ")
    
    return run_command(
        f"alembic revision --autogenerate -m \"{message}\"", 
        f"Creating migration: {message}"
    )

def upgrade_database():
    """Upgrade database to latest migration"""
    return run_command("alembic upgrade head", "Database upgrade")

def downgrade_database(revision="base"):
    """Downgrade database to specific revision"""
    warning = input(f"⚠️  WARNING: This will downgrade to '{revision}' and may cause data loss. Continue? (y/N): ")
    if warning.lower() != 'y':
        print("Cancelled.")
        return True
    
    return run_command(f"alembic downgrade {revision}", f"Database downgrade to {revision}")

def migration_status():
    """Show current migration status"""
    print("📊 Migration Status:")
    run_command("alembic current", "Current revision")
    run_command("alembic heads", "Latest available revision")
    run_command("alembic history", "Migration history")

def quick_fix():
    """Quick fix for the spotify_id issue"""
    return run_command(f"{sys.executable} migrate.py", "Quick fix for spotify_id column")

def main():
    parser = argparse.ArgumentParser(description="Prism Analytics Engine - Database Migration CLI")
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Init command
    subparsers.add_parser('init', help='Initialize migrations (first time setup)')
    
    # Create migration command
    create_parser = subparsers.add_parser('create', help='Create a new migration')
    create_parser.add_argument('-m', '--message', help='Migration description')
    
    # Upgrade command
    subparsers.add_parser('upgrade', help='Upgrade database to latest migration')
    
    # Downgrade command
    downgrade_parser = subparsers.add_parser('downgrade', help='Downgrade database')
    downgrade_parser.add_argument('revision', nargs='?', default='base', help='Target revision (default: base)')
    
    # Status command
    subparsers.add_parser('status', help='Show migration status')
    
    # Quick fix command
    subparsers.add_parser('quickfix', help='Quick fix for spotify_id column issue')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Check if we're in the right directory
    if not Path("config/database.py").exists():
        print("❌ Error: Please run this script from the project root directory")
        return 1
    
    success = True
    
    if args.command == 'init':
        success = init_migrations()
    elif args.command == 'create':
        success = create_migration(args.message)
    elif args.command == 'upgrade':
        success = upgrade_database()
    elif args.command == 'downgrade':
        success = downgrade_database(args.revision)
    elif args.command == 'status':
        migration_status()
    elif args.command == 'quickfix':
        success = quick_fix()
    
    if success:
        print("\n🎉 Operation completed successfully!")
        if args.command in ['init', 'upgrade', 'quickfix']:
            print("   You can now restart your Prism Analytics Engine application.")
    else:
        print("\n❌ Operation failed. Please check the errors above.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
# Prism Analytics Engine - Alembic Fix Script
# Run this in PowerShell to fix all Alembic issues

Write-Host "🔧 Fixing Prism Analytics Engine Alembic Setup..." -ForegroundColor Cyan

# Step 1: Install required packages
Write-Host "`n📦 Installing required packages..." -ForegroundColor Yellow
pip install psycopg2-binary==2.9.7

# Step 2: Set environment variable for testing (PowerShell syntax)
Write-Host "`n🔗 Setting up database connection..." -ForegroundColor Yellow
$env:DATABASE_URL = "sqlite:///test_migration.db"
Write-Host "Database URL set to: $env:DATABASE_URL"

# Step 3: Update requirements.txt
Write-Host "`n📝 Updating requirements.txt..." -ForegroundColor Yellow
if (!(Get-Content requirements.txt -ErrorAction SilentlyContinue | Select-String "psycopg2-binary")) {
    Add-Content requirements.txt "psycopg2-binary==2.9.7"
}

# Step 4: Backup existing files
Write-Host "`n💾 Backing up existing config files..." -ForegroundColor Yellow
if (Test-Path "alembic.ini") {
    Copy-Item "alembic.ini" "alembic.ini.backup"
}
if (Test-Path "alembic/env.py") {
    Copy-Item "alembic/env.py" "alembic/env.py.backup"
}

# Step 5: Create the fixed alembic.ini
Write-Host "`n⚙️ Creating fixed alembic.ini..." -ForegroundColor Yellow
@"
# A generic, single database configuration.

[alembic]
# path to migration scripts
script_location = alembic

# template used to generate migration file names; The default value is %%(rev)s_%%(slug)s
# Uncomment the line below if you want the files to be prepended with date and time
# file_template = %%(year)d_%%(month).2d_%%(day).2d_%%(hour).2d%%(minute).2d-%%(rev)s_%%(slug)s

# sys.path path, will be prepended to sys.path if present.
# defaults to the current working directory.
prepend_sys_path = .

# timezone to use when rendering the date within the migration file
# as well as the filename.
# If specified, requires the python-dateutil library that can be
# installed by adding `alembic[tz]` to the pip requirements
# string value is passed to dateutil.tz.gettz()
# leave blank for localtime
# timezone =

# max length of characters to apply to the
# "slug" field
# truncate_slug_length = 40

# set to 'true' to run the environment during
# the 'revision' command, regardless of autogenerate
# revision_environment = false

# set to 'true' to allow .pyc and .pyo files without
# a source .py file to be detected as revisions in the
# versions/ directory
# sourceless = false

# version number format
version_num_format = %d

# version path separator; as mentioned above, this is the character used to split
# version_num_format into a tuple
# version_path_separator = :

# set to 'true' to search source files recursively
# in each "version_locations" directory
# recursive_version_locations = false

# the output encoding used when revision files
# are written from script.py.mako
# output_encoding = utf-8

# Database URL - will be replaced by environment variable in env.py
sqlalchemy.url = driver://user:pass@localhost/dbname

[post_write_hooks]
# post_write_hooks defines scripts or Python functions that are run
# on newly generated revision scripts.  See the documentation for further
# detail and examples

# format using "black" - use the console_scripts runner, against the "black" entrypoint
# hooks = black
# black.type = console_scripts
# black.entrypoint = black
# black.options = -l 79 REVISION_SCRIPT_FILENAME

# Logging configuration
[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console
qualname =

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S
"@ | Out-File -FilePath "alembic.ini" -Encoding UTF8

# Step 6: Test the setup
Write-Host "`n🧪 Testing Alembic setup..." -ForegroundColor Yellow

try {
    # Test alembic current
    Write-Host "Testing alembic current..."
    alembic current
    
    # Generate migration
    Write-Host "Generating migration..."
    alembic revision --autogenerate -m "Fix PostgreSQL JSON index issue for Prism Analytics"
    
    # Run migration
    Write-Host "Running migration..."
    alembic upgrade head
    
    Write-Host "`n✅ Alembic setup successful!" -ForegroundColor Green
    Write-Host "Migration files created in: alembic/versions/" -ForegroundColor Green
    
} catch {
    Write-Host "`n❌ Error occurred: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "Check the error details above and try the manual steps below." -ForegroundColor Yellow
}

# Step 7: Production deployment info
Write-Host "`n🚀 Next Steps for Production Deployment:" -ForegroundColor Cyan
Write-Host "1. Commit changes: git add . && git commit -m 'Fix Alembic setup for Prism Analytics'"
Write-Host "2. Push to trigger deploy: git push origin main"
Write-Host "3. Monitor Render logs at: https://dashboard.render.com"
Write-Host "4. Check app health: https://isrc-analyzer-api.onrender.com/api/health"

Write-Host "`n🎉 Prism Analytics Engine database migration setup complete!" -ForegroundColor Magenta
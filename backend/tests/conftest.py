import os

# Set environment variables for tests before any other imports
os.environ["JWT_SECRET_KEY"] = "test-secret-key"
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"

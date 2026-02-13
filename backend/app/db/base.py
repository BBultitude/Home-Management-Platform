"""
Import all models here for Alembic to detect them
This file is imported by Alembic's env.py for auto-generating migrations
"""

from app.db.database import Base

# Import all models so Alembic can detect them for auto-generating migrations
from app.models.user import User
from app.models.trusted_device import TrustedDevice
from app.models.audit_log import AuditLog
from app.models.file import File

# Future models will be imported here as they're created
# from app.models.tax_wfh_entry import TaxWFHEntry
# from app.models.tax_travel_entry import TaxTravelEntry
# ... etc

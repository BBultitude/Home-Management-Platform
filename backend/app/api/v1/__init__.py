"""API version 1 routes"""

from fastapi import APIRouter

from app.api.v1 import auth, mfa, audit, files, tax_wfh, tax_travel, financial, assets, projects, knowledge, meals, dashboard, admin

# Create main API router
api_router = APIRouter()

# Include sub-routers
api_router.include_router(auth.router)
api_router.include_router(mfa.router)
api_router.include_router(audit.router)
api_router.include_router(files.router)
api_router.include_router(tax_wfh.router)
api_router.include_router(tax_travel.router)
api_router.include_router(financial.router)
api_router.include_router(assets.router)
api_router.include_router(projects.router)
api_router.include_router(knowledge.router)
api_router.include_router(meals.router)
api_router.include_router(dashboard.router)
api_router.include_router(admin.router)

# Future routers will be added here:
# api_router.include_router(users.router)
# api_router.include_router(documents.router)
# etc.

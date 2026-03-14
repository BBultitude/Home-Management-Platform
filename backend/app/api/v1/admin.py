"""
Admin API endpoints
User management, system statistics, and administrative oversight
"""

import io
import os
import shutil
import subprocess
import tempfile
import zipfile
from datetime import datetime, timezone
from typing import Optional
from urllib.parse import urlparse
from uuid import UUID
from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.api.dependencies import get_db, require_admin
from app.core.config import settings
from app.models.user import User, UserRole
from app.services.admin_service import AdminService
from app.services.audit_service import AuditService
from app.models.audit_log import AuditModule, AuditAction, AuditLog, EventType, Severity
from app.schemas.admin import (
    UserUpdateRequest,
    UserRoleUpdateRequest,
    UserActiveUpdateRequest,
    UserDetailResponse,
    UserListResponse,
    MFAResetResponse,
    SystemStatsResponse,
    UserStatisticsResponse
)
from app.schemas.audit import AuditLogResponse, AuditLogListResponse


router = APIRouter(prefix="/admin", tags=["admin"])


# ===== User Management Endpoints =====

@router.get("/users", response_model=UserListResponse)
async def list_users(
    search: Optional[str] = Query(None, description="Search by username, email, or name"),
    role: Optional[str] = Query(None, description="Filter by role: admin, editor, reader"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    List all users with optional filtering (admin only)

    Supports search and filtering by role and active status.
    """
    role_filter = UserRole(role) if role else None

    users = AdminService.list_users(
        db=db,
        search=search,
        role=role_filter,
        is_active=is_active,
        limit=limit,
        offset=offset
    )

    total = AdminService.get_user_count(
        db=db,
        search=search,
        role=role_filter,
        is_active=is_active
    )

    return UserListResponse(
        users=[
            UserDetailResponse(
                id=str(u.id),
                username=u.username,
                email=u.email,
                full_name=u.full_name,
                role=u.role.value,
                is_active=u.is_active,
                mfa_enabled=u.mfa_enabled,
                created_at=u.created_at.isoformat(),
                updated_at=u.updated_at.isoformat(),
                last_login=u.last_login.isoformat() if u.last_login else None
            )
            for u in users
        ],
        total=total,
        limit=limit,
        offset=offset
    )


@router.get("/users/{user_id}", response_model=UserDetailResponse)
async def get_user(
    user_id: UUID,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get user details by ID (admin only)"""
    user = AdminService.get_user_by_id(db, user_id)

    return UserDetailResponse(
        id=str(user.id),
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        role=user.role.value,
        is_active=user.is_active,
        mfa_enabled=user.mfa_enabled,
        created_at=user.created_at.isoformat(),
        updated_at=user.updated_at.isoformat(),
        last_login=user.last_login.isoformat() if user.last_login else None
    )


@router.put("/users/{user_id}", response_model=UserDetailResponse)
async def update_user(
    user_id: UUID,
    user_data: UserUpdateRequest,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Update user details (admin only)

    Can update username, email, and full name.
    Cannot update role (use dedicated endpoint).
    """
    user = AdminService.update_user(
        db=db,
        user_id=user_id,
        admin_user=current_user,
        username=user_data.username,
        email=user_data.email,
        full_name=user_data.full_name
    )

    return UserDetailResponse(
        id=str(user.id),
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        role=user.role.value,
        is_active=user.is_active,
        mfa_enabled=user.mfa_enabled,
        created_at=user.created_at.isoformat(),
        updated_at=user.updated_at.isoformat(),
        last_login=user.last_login.isoformat() if user.last_login else None
    )


@router.put("/users/{user_id}/role", response_model=UserDetailResponse)
async def update_user_role(
    user_id: UUID,
    role_data: UserRoleUpdateRequest,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Update user role (admin only)

    Prevents:
    - Changing own role
    - Removing last admin
    """
    user = AdminService.update_user_role(
        db=db,
        user_id=user_id,
        admin_user=current_user,
        new_role=UserRole(role_data.role)
    )

    return UserDetailResponse(
        id=str(user.id),
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        role=user.role.value,
        is_active=user.is_active,
        mfa_enabled=user.mfa_enabled,
        created_at=user.created_at.isoformat(),
        updated_at=user.updated_at.isoformat(),
        last_login=user.last_login.isoformat() if user.last_login else None
    )


@router.put("/users/{user_id}/active", response_model=UserDetailResponse)
async def toggle_user_active(
    user_id: UUID,
    active_data: UserActiveUpdateRequest,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Activate or deactivate user (admin only)

    Prevents:
    - Deactivating self
    - Deactivating last admin
    """
    user = AdminService.toggle_user_active(
        db=db,
        user_id=user_id,
        admin_user=current_user,
        is_active=active_data.is_active
    )

    return UserDetailResponse(
        id=str(user.id),
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        role=user.role.value,
        is_active=user.is_active,
        mfa_enabled=user.mfa_enabled,
        created_at=user.created_at.isoformat(),
        updated_at=user.updated_at.isoformat(),
        last_login=user.last_login.isoformat() if user.last_login else None
    )


@router.delete("/users/{user_id}")
async def delete_user(
    user_id: UUID,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Delete user (admin only)

    Prevents:
    - Deleting self
    - Deleting last admin

    WARNING: This permanently deletes the user.
    """
    AdminService.delete_user(db, user_id, current_user)

    return {"message": "User deleted successfully", "user_id": str(user_id)}


@router.post("/users/{user_id}/reset-mfa", response_model=MFAResetResponse)
async def reset_user_mfa(
    user_id: UUID,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Reset user's MFA setup (admin only)

    Generates new MFA secret and QR code.
    User must re-scan and re-enable MFA.
    """
    result = AdminService.reset_user_mfa(db, user_id, current_user)

    return MFAResetResponse(**result)


# ===== System Statistics Endpoints =====

@router.get("/stats", response_model=SystemStatsResponse)
async def get_system_stats(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Get system-wide statistics (admin only)

    Returns user counts, security stats, and activity metrics.
    """
    stats = AdminService.get_system_stats(db)

    return SystemStatsResponse(**stats)


@router.get("/users/{user_id}/stats", response_model=UserStatisticsResponse)
async def get_user_statistics(
    user_id: UUID,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Get statistics for a specific user (admin only)

    Returns activity counts and account information.
    """
    stats = AdminService.get_user_statistics(db, user_id)

    return UserStatisticsResponse(**stats)


# ===== Enhanced Audit Log Endpoints =====

@router.get("/audit/users/{user_id}", response_model=AuditLogListResponse)
async def get_user_audit_logs(
    user_id: UUID,
    module: Optional[str] = Query(None, description="Filter by module"),
    action: Optional[str] = Query(None, description="Filter by action"),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Get audit logs for a specific user (admin only)

    Returns all audit log entries for the specified user.
    """
    query = db.query(AuditLog).filter(AuditLog.user_id == user_id)

    if module:
        query = query.filter(AuditLog.module == AuditModule(module))

    if action:
        query = query.filter(AuditLog.action == AuditAction(action))

    total = query.count()
    logs = query.order_by(AuditLog.created_at.desc()).limit(limit).offset(offset).all()

    return AuditLogListResponse(
        logs=[AuditLogResponse.model_validate(log) for log in logs],
        total=total,
        limit=limit,
        offset=offset
    )


@router.get("/audit/modules/{module}", response_model=AuditLogListResponse)
async def get_module_audit_logs(
    module: str,
    action: Optional[str] = Query(None, description="Filter by action"),
    user_id: Optional[str] = Query(None, description="Filter by user"),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Get audit logs for a specific module (admin only)

    Returns all audit log entries for the specified module.
    """
    query = db.query(AuditLog).filter(AuditLog.module == AuditModule(module))

    if action:
        query = query.filter(AuditLog.action == AuditAction(action))

    if user_id:
        query = query.filter(AuditLog.user_id == UUID(user_id))

    total = query.count()
    logs = query.order_by(AuditLog.created_at.desc()).limit(limit).offset(offset).all()

    return AuditLogListResponse(
        logs=[AuditLogResponse.model_validate(log) for log in logs],
        total=total,
        limit=limit,
        offset=offset
    )


@router.get("/audit/actions/{action}", response_model=AuditLogListResponse)
async def get_action_audit_logs(
    action: str,
    module: Optional[str] = Query(None, description="Filter by module"),
    user_id: Optional[str] = Query(None, description="Filter by user"),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Get audit logs for a specific action (admin only)

    Returns all audit log entries for the specified action type.
    """
    query = db.query(AuditLog).filter(AuditLog.action == AuditAction(action))

    if module:
        query = query.filter(AuditLog.module == AuditModule(module))

    if user_id:
        query = query.filter(AuditLog.user_id == UUID(user_id))

    total = query.count()
    logs = query.order_by(AuditLog.created_at.desc()).limit(limit).offset(offset).all()

    return AuditLogListResponse(
        logs=[AuditLogResponse.model_validate(log) for log in logs],
        total=total,
        limit=limit,
        offset=offset
    )


# ===== Backup Endpoint =====

@router.get("/backup/download")
async def download_backup(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Download a full backup as a ZIP archive (admin only).

    The archive contains:
    - backup_YYYYMMDD_HHMMSS.sql — pg_dump of the database
    - files/ — all uploaded user files
    """
    # Parse DB connection details from the URL with password
    raw_url = settings.database_url_with_password
    # Strip the driver prefix so urlparse can handle it
    parsed = urlparse(raw_url.replace("postgresql+psycopg://", "postgresql://"))
    db_host = parsed.hostname or "db"
    db_port = str(parsed.port or 5432)
    db_user = parsed.username or "homeuser"
    db_pass = parsed.password or ""
    db_name = (parsed.path or "/homedb").lstrip("/")

    # Run pg_dump
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    sql_filename = f"backup_{timestamp}.sql"

    env = os.environ.copy()
    env["PGPASSWORD"] = db_pass

    try:
        result = subprocess.run(
            [
                "pg_dump",
                "-h", db_host,
                "-p", db_port,
                "-U", db_user,
                "--no-password",
                db_name,
            ],
            capture_output=True,
            env=env,
            timeout=120,
        )
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="pg_dump not found on server")
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=500, detail="pg_dump timed out")

    if result.returncode != 0:
        raise HTTPException(
            status_code=500,
            detail=f"pg_dump failed: {result.stderr.decode(errors='replace')[:500]}"
        )

    sql_data = result.stdout

    # Build ZIP in memory
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr(sql_filename, sql_data)

        upload_dir = settings.UPLOAD_DIR
        if upload_dir.exists():
            for file_path in upload_dir.rglob("*"):
                if file_path.is_file():
                    arcname = "files/" + str(file_path.relative_to(upload_dir))
                    zf.write(file_path, arcname)

    zip_buffer.seek(0)

    # Log the backup event
    AuditService.log_event(
        db=db,
        event_type=EventType.BACKUP_DOWNLOAD,
        user_id=current_user.id,
        username=current_user.username,
        resource_type="backup",
        severity=Severity.WARNING,
        details={"filename": f"backup_{timestamp}.zip"},
    )
    db.commit()

    zip_filename = f"backup_{timestamp}.zip"
    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={"Content-Disposition": f'attachment; filename="{zip_filename}"'},
    )


@router.post("/backup/restore")
async def restore_backup(
    file: UploadFile = File(...),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """
    Restore database and files from a backup ZIP (admin only).

    Accepts the ZIP produced by /backup/download. Replays the SQL dump
    via psql and overwrites the uploads directory with any files/ found
    inside the archive. This is a destructive operation.
    """
    if not file.filename or not file.filename.lower().endswith(".zip"):
        raise HTTPException(status_code=400, detail="Uploaded file must be a ZIP archive (.zip)")

    with tempfile.TemporaryDirectory() as tmpdir:
        zip_path = os.path.join(tmpdir, "restore.zip")
        content = await file.read()
        with open(zip_path, "wb") as f:
            f.write(content)

        # Validate and extract ZIP
        try:
            with zipfile.ZipFile(zip_path, "r") as zf:
                names = zf.namelist()
                sql_files = [n for n in names if n.startswith("backup_") and n.endswith(".sql")]
                if not sql_files:
                    raise HTTPException(
                        status_code=400,
                        detail="ZIP does not contain a valid backup SQL file (expected backup_*.sql)"
                    )
                zf.extractall(tmpdir)
        except zipfile.BadZipFile:
            raise HTTPException(status_code=400, detail="Uploaded file is not a valid ZIP archive")

        sql_file_path = os.path.join(tmpdir, sql_files[0])

        # Parse DB connection details
        raw_url = settings.database_url_with_password
        parsed = urlparse(raw_url.replace("postgresql+psycopg://", "postgresql://"))
        db_host = parsed.hostname or "db"
        db_port = str(parsed.port or 5432)
        db_user = parsed.username or "homeuser"
        db_pass = parsed.password or ""
        db_name = (parsed.path or "/homedb").lstrip("/")

        env = os.environ.copy()
        env["PGPASSWORD"] = db_pass

        try:
            result = subprocess.run(
                [
                    "psql",
                    "-h", db_host,
                    "-p", db_port,
                    "-U", db_user,
                    "-d", db_name,
                    "-f", sql_file_path,
                ],
                capture_output=True,
                env=env,
                timeout=300,
            )
        except FileNotFoundError:
            raise HTTPException(status_code=500, detail="psql not found on server")
        except subprocess.TimeoutExpired:
            raise HTTPException(status_code=500, detail="Database restore timed out after 300s")

        if result.returncode != 0:
            raise HTTPException(
                status_code=500,
                detail=f"psql failed: {result.stderr.decode(errors='replace')[:500]}"
            )

        # Restore uploaded files if present in the archive
        files_restored = False
        files_dir = os.path.join(tmpdir, "files")
        if os.path.isdir(files_dir):
            upload_dir = settings.UPLOAD_DIR
            upload_dir.mkdir(parents=True, exist_ok=True)
            shutil.copytree(files_dir, str(upload_dir), dirs_exist_ok=True)
            files_restored = True

    # Log the restore event (outside the tempdir context — temp files are gone)
    AuditService.log_event(
        db=db,
        event_type=EventType.BACKUP_RESTORE,
        user_id=current_user.id,
        username=current_user.username,
        resource_type="backup",
        severity=Severity.WARNING,
        details={"sql_file": sql_files[0], "files_restored": files_restored},
    )
    db.commit()

    return {"message": "Restore completed", "tables_restored": True, "files_restored": files_restored}

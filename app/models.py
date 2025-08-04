from sqlmodel import SQLModel, Field, Relationship, JSON, Column
from datetime import datetime
from typing import Optional, List, Dict, Any
from decimal import Decimal


# Persistent models (stored in database)
class User(SQLModel, table=True):
    """Employee/User model for storing employee information"""

    __tablename__ = "users"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    employee_id: str = Field(unique=True, max_length=50, description="Unique employee identifier")
    name: str = Field(max_length=100, description="Employee full name")
    email: str = Field(unique=True, max_length=255, regex=r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
    department: str = Field(max_length=100, description="Employee department")
    is_active: bool = Field(default=True, description="Whether employee is active")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationship to attendance records
    attendance_records: List["AttendanceRecord"] = Relationship(back_populates="user")


class AttendanceRecord(SQLModel, table=True):
    """Attendance record model for storing employee check-ins"""

    __tablename__ = "attendance_records"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", description="Reference to the employee")

    # Photo data - stored as base64 or file path
    photo_data: str = Field(description="Photo taken from device camera (base64 encoded or file path)")
    photo_mime_type: str = Field(max_length=50, default="image/jpeg", description="MIME type of the photo")

    # Location data
    latitude: Decimal = Field(max_digits=10, decimal_places=8, description="GPS latitude coordinate")
    longitude: Decimal = Field(max_digits=11, decimal_places=8, description="GPS longitude coordinate")
    location_accuracy: Optional[Decimal] = Field(
        default=None, max_digits=10, decimal_places=2, description="GPS accuracy in meters"
    )
    address: Optional[str] = Field(default=None, max_length=500, description="Resolved address from coordinates")

    # GPS validation fields
    is_mock_location: bool = Field(default=False, description="Whether mock/fake GPS was detected")
    gps_validation_data: Optional[Dict[str, Any]] = Field(
        default=None, sa_column=Column(JSON), description="Additional GPS validation metadata"
    )

    # Employee input
    description: str = Field(max_length=500, description="Employee description of attendance")

    # Timestamps
    submitted_at: datetime = Field(default_factory=datetime.utcnow, description="When the attendance was submitted")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Status and validation
    status: str = Field(default="pending", max_length=20, description="Record status: pending, approved, rejected")
    is_valid: bool = Field(default=True, description="Whether the attendance record is considered valid")
    rejection_reason: Optional[str] = Field(
        default=None, max_length=500, description="Reason for rejection if applicable"
    )

    # Relationship back to user
    user: User = Relationship(back_populates="attendance_records")


class LocationValidation(SQLModel, table=True):
    """Model for storing location validation rules and trusted zones"""

    __tablename__ = "location_validations"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=100, description="Name of the location/zone")

    # Geofence definition
    center_latitude: Decimal = Field(max_digits=10, decimal_places=8, description="Center point latitude")
    center_longitude: Decimal = Field(max_digits=11, decimal_places=8, description="Center point longitude")
    radius_meters: Decimal = Field(max_digits=10, decimal_places=2, description="Allowed radius in meters")

    # Validation settings
    is_active: bool = Field(default=True, description="Whether this validation zone is active")
    allow_mock_location: bool = Field(default=False, description="Whether to allow mock GPS in this zone")
    strict_validation: bool = Field(default=True, description="Whether to apply strict GPS validation")

    # Metadata
    description: Optional[str] = Field(default=None, max_length=500, description="Description of the location")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


# Non-persistent schemas (for validation, forms, API requests/responses)
class UserCreate(SQLModel, table=False):
    """Schema for creating a new user/employee"""

    employee_id: str = Field(max_length=50)
    name: str = Field(max_length=100)
    email: str = Field(max_length=255)
    department: str = Field(max_length=100)


class UserUpdate(SQLModel, table=False):
    """Schema for updating user information"""

    name: Optional[str] = Field(default=None, max_length=100)
    email: Optional[str] = Field(default=None, max_length=255)
    department: Optional[str] = Field(default=None, max_length=100)
    is_active: Optional[bool] = Field(default=None)


class AttendanceSubmission(SQLModel, table=False):
    """Schema for submitting attendance record"""

    user_id: int
    photo_data: str = Field(description="Base64 encoded photo data")
    photo_mime_type: str = Field(default="image/jpeg", max_length=50)
    latitude: Decimal = Field(max_digits=10, decimal_places=8)
    longitude: Decimal = Field(max_digits=11, decimal_places=8)
    location_accuracy: Optional[Decimal] = Field(default=None, max_digits=10, decimal_places=2)
    address: Optional[str] = Field(default=None, max_length=500)
    description: str = Field(max_length=500)
    gps_validation_data: Optional[Dict[str, Any]] = Field(default=None)


class AttendanceUpdate(SQLModel, table=False):
    """Schema for updating attendance record status"""

    status: Optional[str] = Field(default=None, max_length=20)
    is_valid: Optional[bool] = Field(default=None)
    rejection_reason: Optional[str] = Field(default=None, max_length=500)


class LocationValidationCreate(SQLModel, table=False):
    """Schema for creating location validation rules"""

    name: str = Field(max_length=100)
    center_latitude: Decimal = Field(max_digits=10, decimal_places=8)
    center_longitude: Decimal = Field(max_digits=11, decimal_places=8)
    radius_meters: Decimal = Field(max_digits=10, decimal_places=2)
    allow_mock_location: bool = Field(default=False)
    strict_validation: bool = Field(default=True)
    description: Optional[str] = Field(default=None, max_length=500)


class LocationValidationUpdate(SQLModel, table=False):
    """Schema for updating location validation rules"""

    name: Optional[str] = Field(default=None, max_length=100)
    center_latitude: Optional[Decimal] = Field(default=None, max_digits=10, decimal_places=8)
    center_longitude: Optional[Decimal] = Field(default=None, max_digits=11, decimal_places=8)
    radius_meters: Optional[Decimal] = Field(default=None, max_digits=10, decimal_places=2)
    is_active: Optional[bool] = Field(default=None)
    allow_mock_location: Optional[bool] = Field(default=None)
    strict_validation: Optional[bool] = Field(default=None)
    description: Optional[str] = Field(default=None, max_length=500)


# Response schemas for API
class AttendanceRecordResponse(SQLModel, table=False):
    """Response schema for attendance record with user information"""

    id: int
    user_id: int
    user_name: str
    user_employee_id: str
    latitude: Decimal
    longitude: Decimal
    address: Optional[str]
    description: str
    is_mock_location: bool
    status: str
    is_valid: bool
    submitted_at: datetime
    rejection_reason: Optional[str]

    @classmethod
    def from_attendance_record(cls, record: AttendanceRecord) -> "AttendanceRecordResponse":
        """Create response from attendance record with user data"""
        if record.id is None:
            raise ValueError("Attendance record ID cannot be None")

        return cls(
            id=record.id,
            user_id=record.user_id,
            user_name=record.user.name,
            user_employee_id=record.user.employee_id,
            latitude=record.latitude,
            longitude=record.longitude,
            address=record.address,
            description=record.description,
            is_mock_location=record.is_mock_location,
            status=record.status,
            is_valid=record.is_valid,
            submitted_at=record.submitted_at,
            rejection_reason=record.rejection_reason,
        )

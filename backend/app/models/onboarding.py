from __future__ import annotations

import enum
import uuid
from datetime import datetime
from typing import Any, Optional

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    Uuid,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Plan(str, enum.Enum):
    starter = "starter"
    pro = "pro"
    agency = "agency"


class FirmUserRole(str, enum.Enum):
    owner = "owner"
    admin = "admin"
    staff = "staff"


class Country(str, enum.Enum):
    India = "India"
    UAE = "UAE"
    UK = "UK"
    US = "US"
    Singapore = "Singapore"
    Australia = "Australia"
    Other = "Other"


class EntityType(str, enum.Enum):
    individual = "individual"
    sole_proprietor = "sole_proprietor"
    sole_trader = "sole_trader"
    partnership = "partnership"
    llp = "llp"
    private_limited = "private_limited"
    public_limited = "public_limited"
    trust = "trust"
    llc = "llc"
    s_corp = "s_corp"
    c_corp = "c_corp"
    other = "other"


class ClientStatus(str, enum.Enum):
    invited = "invited"
    signature_pending = "signature_pending"
    in_progress = "in_progress"
    documents_pending = "documents_pending"
    under_review = "under_review"
    completed = "completed"
    active = "active"


class ChecklistItemStatus(str, enum.Enum):
    pending = "pending"
    uploaded = "uploaded"
    verified = "verified"
    rejected = "rejected"
    waived = "waived"


class DocumentReviewStatus(str, enum.Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"


class MessageChannel(str, enum.Enum):
    whatsapp = "whatsapp"
    sms = "sms"


class MessageDeliveryStatus(str, enum.Enum):
    sent = "sent"
    delivered = "delivered"
    failed = "failed"


def _enum_values(cls: type[enum.Enum]) -> list[str]:
    return [e.value for e in cls]


class Firm(Base):
    __tablename__ = "firms"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(128), unique=True, nullable=False, index=True)
    country: Mapped[str] = mapped_column(String(64), default="India")
    logo_url: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True)
    primary_color: Mapped[str] = mapped_column(String(16), default="#2563EB")
    whatsapp_number: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    plan: Mapped[Plan] = mapped_column(Enum(Plan, values_callable=_enum_values), default=Plan.starter)
    plan_client_limit: Mapped[int] = mapped_column(Integer, default=10)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    users: Mapped[list["FirmUser"]] = relationship(back_populates="firm", cascade="all, delete-orphan")
    clients: Mapped[list["Client"]] = relationship(back_populates="firm", cascade="all, delete-orphan")


class FirmUser(Base):
    __tablename__ = "firm_users"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    firm_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("firms.id"), nullable=False)
    supabase_user_id: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[FirmUserRole] = mapped_column(
        Enum(FirmUserRole, values_callable=_enum_values), default=FirmUserRole.staff
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    firm: Mapped["Firm"] = relationship(back_populates="users")
    assigned_clients: Mapped[list["Client"]] = relationship(
        back_populates="assignee", foreign_keys="Client.assigned_to"
    )


class Client(Base):
    __tablename__ = "clients"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    firm_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("firms.id"), nullable=False, index=True)
    client_name: Mapped[str] = mapped_column(String(255), nullable=False)
    business_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[str] = mapped_column(String(32), nullable=False)
    country: Mapped[Country] = mapped_column(Enum(Country, values_callable=_enum_values), nullable=False)
    entity_type: Mapped[EntityType] = mapped_column(Enum(EntityType, values_callable=_enum_values), nullable=False)
    services: Mapped[list[Any]] = mapped_column(JSON, default=list)
    industry: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    financial_year_end: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    status: Mapped[ClientStatus] = mapped_column(
        Enum(ClientStatus, values_callable=_enum_values), default=ClientStatus.invited
    )
    completion_pct: Mapped[int] = mapped_column(Integer, default=0)
    onboarding_link: Mapped[str] = mapped_column(String(512), unique=True, nullable=False)
    onboarding_token: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), default=uuid.uuid4, unique=True)
    assigned_to: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid(as_uuid=True), ForeignKey("firm_users.id"), nullable=True)
    engagement_letter_sent: Mapped[bool] = mapped_column(Boolean, default=False)
    engagement_letter_signed: Mapped[bool] = mapped_column(Boolean, default=False)
    signature_envelope_id: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    last_activity_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    firm: Mapped["Firm"] = relationship(back_populates="clients")
    assignee: Mapped[Optional["FirmUser"]] = relationship(
        back_populates="assigned_clients", foreign_keys=[assigned_to]
    )
    checklist_items: Mapped[list["ChecklistItem"]] = relationship(
        back_populates="client", cascade="all, delete-orphan", order_by="ChecklistItem.display_order"
    )
    documents: Mapped[list["Document"]] = relationship(back_populates="client", cascade="all, delete-orphan")


class ChecklistItem(Base):
    __tablename__ = "checklist_items"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    client_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("clients.id", ondelete="CASCADE"))
    category: Mapped[str] = mapped_column(String(128), nullable=False)
    item_name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="")
    is_required: Mapped[bool] = mapped_column(Boolean, default=True)
    status: Mapped[ChecklistItemStatus] = mapped_column(
        Enum(ChecklistItemStatus, values_callable=_enum_values), default=ChecklistItemStatus.pending
    )
    document_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid(as_uuid=True), nullable=True
    )
    waived_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    waived_by: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid(as_uuid=True), ForeignKey("firm_users.id"), nullable=True)
    display_order: Mapped[int] = mapped_column(Integer, default=0)

    client: Mapped["Client"] = relationship(back_populates="checklist_items")
    linked_document: Mapped[Optional["Document"]] = relationship(
        back_populates="checklist_item_ref",
        foreign_keys="Document.checklist_item_id",
        primaryjoin="ChecklistItem.id==Document.checklist_item_id",
        uselist=False,
    )


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    client_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("clients.id"), nullable=False)
    firm_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("firms.id"), nullable=False)
    checklist_item_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("checklist_items.id"), nullable=True
    )
    filename: Mapped[str] = mapped_column(String(512), nullable=False)
    original_filename: Mapped[str] = mapped_column(String(512), nullable=False)
    storage_path: Mapped[str] = mapped_column(String(1024), nullable=False)
    storage_bucket: Mapped[str] = mapped_column(String(128), default="cpaos-documents")
    file_size: Mapped[int] = mapped_column(Integer, default=0)
    mime_type: Mapped[str] = mapped_column(String(128), nullable=False)
    uploaded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    uploaded_by: Mapped[str] = mapped_column(String(64), nullable=False)
    ai_document_type: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    ai_confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    ai_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    ai_issues: Mapped[list[Any]] = mapped_column(JSON, default=list)
    reviewed_by: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid(as_uuid=True), ForeignKey("firm_users.id"), nullable=True)
    reviewed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    review_status: Mapped[DocumentReviewStatus] = mapped_column(
        Enum(DocumentReviewStatus, values_callable=_enum_values), default=DocumentReviewStatus.pending
    )
    rejection_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    client: Mapped["Client"] = relationship(back_populates="documents")
    checklist_item_ref: Mapped[Optional["ChecklistItem"]] = relationship(
        back_populates="linked_document",
        foreign_keys=[checklist_item_id],
    )


class WhatsAppLog(Base):
    __tablename__ = "whatsapp_logs"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    client_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("clients.id"), nullable=False)
    firm_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("firms.id"), nullable=False)
    channel: Mapped[MessageChannel] = mapped_column(
        Enum(MessageChannel, values_callable=_enum_values), default=MessageChannel.whatsapp
    )
    message_type: Mapped[str] = mapped_column(String(64), nullable=False)
    phone_number: Mapped[str] = mapped_column(String(32), nullable=False)
    message_content: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[MessageDeliveryStatus] = mapped_column(
        Enum(MessageDeliveryStatus, values_callable=_enum_values), default=MessageDeliveryStatus.sent
    )
    sent_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)


class OnboardingActivity(Base):
    __tablename__ = "onboarding_activity"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    client_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("clients.id"), nullable=False)
    firm_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("firms.id"), nullable=False)
    action: Mapped[str] = mapped_column(String(128), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    performed_by: Mapped[str] = mapped_column(String(128), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

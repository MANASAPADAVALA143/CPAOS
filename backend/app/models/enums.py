from __future__ import annotations

import enum


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

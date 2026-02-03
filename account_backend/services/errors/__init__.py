from .base import BaseServiceError
from .account import (
    AccountNotFoundError,
    AccountRegisterError,
    AccountLoginError,
    AccountPasswordError,
    AccountNotLinkTenantError,
    CurrentPasswordIncorrectError,
    LinkAccountIntegrateError,
    TenantNotFoundError,
    AccountAlreadyInTenantError,
    AccountAlreadyExist,
    InvalidActionError,
    CannotOperateSelfError,
    NoPermissionError,
    MemberNotInTenantError,
    RoleAlreadyAssignedError
)

__all__ = [
    "BaseServiceError",
    "AccountNotFoundError",
    "AccountRegisterError",
    "AccountLoginError",
    "AccountPasswordError",
    "AccountNotLinkTenantError",
    "CurrentPasswordIncorrectError",
    "LinkAccountIntegrateError",
    "TenantNotFoundError",
    "AccountAlreadyInTenantError",
    "AccountAlreadyExist",
    "InvalidActionError",
    "CannotOperateSelfError",
    "NoPermissionError",
    "MemberNotInTenantError",
    "RoleAlreadyAssignedError"
]

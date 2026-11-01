from typing import Any, Protocol
from uuid import UUID

from src.entities.dto.exhibitions import Exhibition, ExhibitionInput, Submission


class ExhibitionRepository(Protocol):
    async def leaderboard(self, exhibition_id: UUID, limit: int, cursor: int) -> dict[str, Any]: ...
    async def pending_counts(self) -> dict[str, Any]: ...
    async def is_administrator(self, user_id: UUID) -> bool: ...
    async def delete(self, exhibition_id: UUID) -> None: ...
    async def withdraw(
        self, exhibition_id: UUID, submission_id: UUID, actor: UUID, reason: str | None
    ) -> None: ...
    async def review_withdrawal(
        self,
        exhibition_id: UUID,
        submission_id: UUID,
        actor: UUID,
        status: str,
        reason: str | None,
    ) -> None: ...
    async def eligible(
        self,
        user_id: UUID,
        limit: int,
        cursor: int,
        work_id: UUID | None = None,
        exhibition_id: UUID | None = None,
    ) -> list[Exhibition]: ...
    async def allowed(self, user_id: UUID, permission: str) -> bool: ...
    async def list_exhibitions(
        self, limit: int, cursor: int, period: str = "all"
    ) -> list[Exhibition]: ...
    async def get(self, exhibition_id: UUID) -> Exhibition: ...
    async def save(
        self, user_id: UUID, data: ExhibitionInput, exhibition_id: UUID | None
    ) -> Exhibition: ...
    async def submit(
        self, exhibition_id: UUID, user_id: UUID, work_id: UUID
    ) -> None: ...
    async def submissions(
        self,
        exhibition_id: UUID,
        viewer: UUID | None,
        scope: str,
        limit: int,
        cursor: int,
        status: str | None = None,
    ) -> list[Submission]: ...
    async def review(
        self,
        exhibition_id: UUID,
        submission_id: UUID,
        actor: UUID,
        status: str,
        reason: str | None,
    ) -> None: ...
    async def block(
        self, exhibition_id: UUID, user_id: UUID, actor: UUID, reason: str | None
    ) -> None: ...
    async def blocks(
        self, exhibition_id: UUID, limit: int, cursor: int
    ) -> list[dict[str, str]]: ...
    async def banner(self, exhibition_id: UUID, path: str | None) -> str | None: ...

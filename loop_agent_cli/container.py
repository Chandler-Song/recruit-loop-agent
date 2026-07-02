"""
DI Container — builds and owns all Repository / Service instances.

Usage::

    async with Container(db_url) as c:
        positions = await c.position_repo.get_all()
"""

from __future__ import annotations

import sys
import os
from pathlib import Path
from typing import Optional, Any

# ---------------------------------------------------------------------------
# Ensure the project root (parent of *this* package's parent) is on sys.path
# so that ``import app.…`` works even when the CLI is installed via pip
# without the project root being the cwd.
# ---------------------------------------------------------------------------
_PROJECT_ROOT = str(Path(__file__).resolve().parent.parent)
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession  # noqa: E402
from sqlalchemy.orm import sessionmaker  # noqa: E402

from app.core.config import settings  # noqa: E402
from app.database.base import Base  # noqa: E402

# Repositories  # noqa: E402
from app.repositories.position import PositionRepository  # noqa: E402
from app.repositories.candidate import CandidateRepository  # noqa: E402
from app.repositories.pipeline import PipelineRepository  # noqa: E402
from app.repositories.outreach_log import OutreachLogRepository  # noqa: E402
from app.repositories.agent_run import AgentRunRepository  # noqa: E402
from app.repositories.node_log import NodeLogRepository  # noqa: E402
from app.repositories.scheduler_job import SchedulerJobRepository  # noqa: E402

# Services  # noqa: E402
from app.services.candidate import CandidateService  # noqa: E402
from app.services.search import SearchService  # noqa: E402
from app.services.score import ScoreService  # noqa: E402
from app.services.pipeline import PipelineService  # noqa: E402
from app.services.email import EmailService  # noqa: E402
from app.services.position import PositionService  # noqa: E402
from app.services.dashboard import DashboardService  # noqa: E402
from app.services.runner import RunnerService  # noqa: E402
from app.services.scheduler import SchedulerService  # noqa: E402


class Container:
    """Async context-manager that provides repositories and services."""

    def __init__(self, db_url: Optional[str] = None) -> None:
        self._db_url: str = db_url or settings.database_url
        self._engine: Any = None
        self._session_factory: Any = None
        self._db: Optional[AsyncSession] = None

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    async def __aenter__(self) -> "Container":
        self._engine = create_async_engine(
            self._db_url,
            echo=False,
            pool_pre_ping=True,
            pool_recycle=300,
        )
        self._session_factory = sessionmaker(
            self._engine, class_=AsyncSession, expire_on_commit=False,
        )
        # Ensure tables exist
        async with self._engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        self._db = self._session_factory()
        return self

    async def __aexit__(
        self,
        exc_type: Optional[type],
        exc_val: Optional[BaseException],
        exc_tb: Any,
    ) -> None:
        if self._db is not None:
            await self._db.close()
        if self._engine is not None:
            await self._engine.dispose()

    # ------------------------------------------------------------------
    # Repositories (7)
    # ------------------------------------------------------------------

    @property
    def position_repo(self) -> PositionRepository:
        assert self._db is not None
        return PositionRepository(self._db)

    @property
    def candidate_repo(self) -> CandidateRepository:
        assert self._db is not None
        return CandidateRepository(self._db)

    @property
    def pipeline_repo(self) -> PipelineRepository:
        assert self._db is not None
        return PipelineRepository(self._db)

    @property
    def outreach_log_repo(self) -> OutreachLogRepository:
        assert self._db is not None
        return OutreachLogRepository(self._db)

    @property
    def agent_run_repo(self) -> AgentRunRepository:
        assert self._db is not None
        return AgentRunRepository(self._db)

    @property
    def node_log_repo(self) -> NodeLogRepository:
        assert self._db is not None
        return NodeLogRepository(self._db)

    @property
    def scheduler_job_repo(self) -> SchedulerJobRepository:
        assert self._db is not None
        return SchedulerJobRepository(self._db)

    # ------------------------------------------------------------------
    # Services (7 + 2 composite)
    # ------------------------------------------------------------------

    @property
    def candidate_service(self) -> CandidateService:
        return CandidateService(self.candidate_repo)

    @property
    def search_service(self) -> SearchService:
        return SearchService(self.candidate_service)

    @property
    def score_service(self) -> ScoreService:
        return ScoreService()

    @property
    def pipeline_service(self) -> PipelineService:
        return PipelineService(self.pipeline_repo)

    @property
    def email_service(self) -> EmailService:
        return EmailService(self.outreach_log_repo)

    @property
    def position_service(self) -> PositionService:
        return PositionService(self.position_repo)

    @property
    def dashboard_service(self) -> DashboardService:
        return DashboardService(
            position_repo=self.position_repo,
            agent_run_repo=self.agent_run_repo,
            pipeline_repo=self.pipeline_repo,
            candidate_repo=self.candidate_repo,
            node_log_repo=self.node_log_repo,
        )

    @property
    def runner(self) -> RunnerService:
        return RunnerService(
            search_service=self.search_service,
            score_service=self.score_service,
            pipeline_service=self.pipeline_service,
            email_service=self.email_service,
            candidate_repo=self.candidate_repo,
            position_repo=self.position_repo,
            pipeline_repo=self.pipeline_repo,
            outreach_log_repo=self.outreach_log_repo,
            agent_run_repo=self.agent_run_repo,
            node_log_repo=self.node_log_repo,
        )

    @property
    def scheduler(self) -> SchedulerService:
        return SchedulerService(
            position_repo=self.position_repo,
            job_repo=self.scheduler_job_repo,
            runner_service=self.runner,
        )

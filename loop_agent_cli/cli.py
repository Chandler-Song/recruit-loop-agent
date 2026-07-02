"""
loop-agent-cli — Typer CLI entry point.

15 commands + 3 helper functions, built on Typer + Rich.
"""

from __future__ import annotations

import asyncio
import json
import os
import sys
import uuid
from typing import Optional, Any, List

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box

from loop_agent_cli import __version__
from loop_agent_cli.container import Container

console = Console()

# ---------------------------------------------------------------------------
# Typer app
# ---------------------------------------------------------------------------

app = typer.Typer(
    name="loop-agent",
    help="Recruiting Loop Agent — CLI frontend",
    no_args_is_help=True,
    add_completion=False,
)

run_app = typer.Typer(help="执行招聘循环")
position_app = typer.Typer(help="职位管理")
candidate_app = typer.Typer(help="候选人管理")
pipeline_app = typer.Typer(help="招聘管道管理")
schedule_app = typer.Typer(help="调度管理")

app.add_typer(run_app, name="run")
app.add_typer(position_app, name="position")
app.add_typer(candidate_app, name="candidate")
app.add_typer(pipeline_app, name="pipeline")
app.add_typer(schedule_app, name="schedule")


# ===================================================================
# Helper functions (3)
# ===================================================================


def _run(coro: Any) -> Any:
    """在事件循环中运行异步协程。"""
    return asyncio.run(coro)


def _parse_json_or_file(value: Optional[str]) -> Optional[list]:
    """
    解析输入为 list[str]。
    优先级: JSON 解析 → 文件读取 → 逗号分割。
    """
    if value is None:
        return None

    # 1. Try JSON
    try:
        parsed = json.loads(value)
        if isinstance(parsed, list):
            return parsed
    except (json.JSONDecodeError, TypeError):
        pass

    # 2. Try file
    if os.path.isfile(value):
        with open(value, "r", encoding="utf-8") as f:
            content = f.read().strip()
        # Try JSON inside file
        try:
            parsed = json.loads(content)
            if isinstance(parsed, list):
                return parsed
        except (json.JSONDecodeError, TypeError):
            pass
        # Line-by-line
        lines = [line.strip() for line in content.splitlines() if line.strip()]
        if lines:
            return lines

    # 3. Comma-separated
    return [item.strip() for item in value.split(",") if item.strip()]


def _print_result(result: dict) -> None:
    """打印 run_recruiting_loop 的结果到 Rich Panel。"""
    status = result.get("status", "unknown")
    duration = result.get("duration_ms", 0)

    if status == "failed":
        error_msg = result.get("error", "Unknown error")
        console.print(
            Panel(
                f"[red]Error:[/] {error_msg}\nDuration: {duration} ms",
                title="Recruiting Loop — Failed",
                border_style="red",
            )
        )
        return

    # completed
    res = result.get("results", {})
    lines = [
        f"Candidates found: {res.get('candidates_found', 0)}",
        f"Candidates added: {res.get('candidates_added', 0)}",
        f"Emails sent:      {res.get('emails_sent', 0)}",
        f"Duration:         {duration} ms",
        f"Continue loop:    {res.get('continue_loop', 'N/A')}",
    ]
    errors = res.get("errors", [])
    body = "\n".join(lines)
    if errors:
        body += "\n\n[red]Errors:[/]"
        for err in errors:
            body += f"\n  • {err}"

    console.print(
        Panel(body, title="Recruiting Loop — Completed", border_style="green")
    )


def _validate_uuid(value: str) -> Optional[uuid.UUID]:
    """校验 UUID 格式，返回 UUID 对象或 None。"""
    try:
        return uuid.UUID(value)
    except (ValueError, AttributeError):
        return None


# ===================================================================
# run commands
# ===================================================================


@run_app.command("position")
def run_position(
    position_id: str = typer.Argument(..., help="Position UUID"),
    db_url: Optional[str] = typer.Option(None, "--db", help="数据库 URL"),
) -> None:
    """对已有职位执行一次招聘循环。"""
    pid = _validate_uuid(position_id)
    if pid is None:
        console.print(f"[red]无效的 UUID: {position_id}[/]")
        raise typer.Exit(1)

    async def _do() -> None:
        async with Container(db_url) as c:
            # 校验职位存在
            pos = await c.position_repo.get_by_id(pid)
            if not pos:
                console.print(f"[red]职位不存在: {position_id}[/]")
                return
            console.print(f"[dim]正在对职位 '{pos.title}' 执行招聘循环…[/]")
            result = await c.runner.run_recruiting_loop(pid)
            _print_result(result)

    _run(_do())


@run_app.command("create-and-run")
def run_create_and_run(
    title: str = typer.Option(..., "--title", "-t", help="职位名称"),
    company: str = typer.Option(..., "--company", "-c", help="公司名称"),
    desc: Optional[str] = typer.Option(None, "--desc", "-d", help="职位描述"),
    location: Optional[str] = typer.Option(None, "--location", "-l", help="工作地点"),
    skills: Optional[str] = typer.Option(None, "--skills", "-s", help="技能要求 (JSON/文件/逗号分隔)"),
    keywords: Optional[str] = typer.Option(None, "--keywords", "-k", help="搜索关键词"),
    interval: int = typer.Option(60, "--interval", "-i", help="循环间隔(分钟)"),
    db_url: Optional[str] = typer.Option(None, "--db", help="数据库 URL"),
) -> None:
    """创建新职位并立即执行招聘循环。"""
    required_skills = _parse_json_or_file(skills)
    search_keywords = _parse_json_or_file(keywords)

    async def _do() -> None:
        async with Container(db_url) as c:
            # 延迟导入 PositionCreate
            from app.schemas.position import PositionCreate

            position_data = PositionCreate(
                title=title,
                company=company,
                description=desc,
                location=location,
                required_skills=required_skills,
                search_keywords=search_keywords,
                loop_interval=interval,
            )
            position = await c.position_repo.create(position_data)
            console.print(
                f"[green]✓ 职位已创建:[/] {position.title}  "
                f"[dim](ID: {position.id})[/]"
            )
            console.print(f"[dim]正在执行招聘循环…[/]")
            result = await c.runner.run_recruiting_loop(
                uuid.UUID(position.id) if isinstance(position.id, str) else position.id
            )
            _print_result(result)

    _run(_do())


# ===================================================================
# position commands
# ===================================================================


@position_app.command("list")
def position_list(
    db_url: Optional[str] = typer.Option(None, "--db", help="数据库 URL"),
) -> None:
    """列出所有职位。"""

    async def _do() -> None:
        async with Container(db_url) as c:
            positions = await c.position_repo.get_all()
            if not positions:
                console.print("[dim]没有找到任何职位[/]")
                return

            table = Table(title="Positions", box=box.ROUNDED)
            table.add_column("ID", style="dim", max_width=36)
            table.add_column("Title", style="cyan")
            table.add_column("Company", style="green")
            table.add_column("Status")
            table.add_column("Skills")
            table.add_column("Loop", justify="center")

            for pos in positions:
                # Status colour
                status_map = {"active": "green", "paused": "yellow", "closed": "red"}
                status_style = status_map.get(pos.status, "white")

                # Skills — try to parse from JSON string
                skills_display = ""
                if pos.required_skills:
                    if isinstance(pos.required_skills, str):
                        try:
                            skills_list = json.loads(pos.required_skills)
                        except (json.JSONDecodeError, TypeError):
                            skills_list = [pos.required_skills]
                    elif isinstance(pos.required_skills, list):
                        skills_list = pos.required_skills
                    else:
                        skills_list = []
                    skills_display = ", ".join(str(s) for s in skills_list)
                    if len(skills_display) > 40:
                        skills_display = skills_display[:37] + "…"

                # Loop
                loop_display = (
                    f"{pos.loop_interval}m"
                    if pos.loop_enabled
                    else "off"
                )

                table.add_row(
                    str(pos.id),
                    pos.title or "",
                    pos.company or "",
                    f"[{status_style}]{pos.status}[/]",
                    skills_display,
                    loop_display,
                )

            console.print(table)

    _run(_do())


@position_app.command("create")
def position_create(
    title: str = typer.Option(..., "--title", "-t", help="职位名称"),
    company: str = typer.Option(..., "--company", "-c", help="公司名称"),
    desc: Optional[str] = typer.Option(None, "--desc", "-d", help="职位描述"),
    location: Optional[str] = typer.Option(None, "--location", "-l", help="工作地点"),
    skills: Optional[str] = typer.Option(None, "--skills", "-s", help="技能要求"),
    keywords: Optional[str] = typer.Option(None, "--keywords", "-k", help="搜索关键词"),
    interval: int = typer.Option(60, "--interval", "-i", help="循环间隔(分钟)"),
    db_url: Optional[str] = typer.Option(None, "--db", help="数据库 URL"),
) -> None:
    """创建新职位。"""
    required_skills = _parse_json_or_file(skills)
    search_keywords = _parse_json_or_file(keywords)

    async def _do() -> None:
        async with Container(db_url) as c:
            from app.schemas.position import PositionCreate

            position_data = PositionCreate(
                title=title,
                company=company,
                description=desc,
                location=location,
                required_skills=required_skills,
                search_keywords=search_keywords,
                loop_interval=interval,
            )
            position = await c.position_repo.create(position_data)
            console.print(
                f"[green]✓ 职位已创建:[/] {position.title}\n"
                f"  [dim]ID: {position.id}[/]"
            )

    _run(_do())


@position_app.command("show")
def position_show(
    position_id: str = typer.Argument(..., help="Position UUID"),
    db_url: Optional[str] = typer.Option(None, "--db", help="数据库 URL"),
) -> None:
    """查看职位详情。"""
    pid = _validate_uuid(position_id)
    if pid is None:
        console.print(f"[red]无效的 UUID: {position_id}[/]")
        raise typer.Exit(1)

    async def _do() -> None:
        async with Container(db_url) as c:
            pos = await c.position_repo.get_by_id(pid)
            if not pos:
                console.print(f"[red]职位不存在: {position_id}[/]")
                return

            # Parse skills
            skills_display = "—"
            if pos.required_skills:
                if isinstance(pos.required_skills, str):
                    try:
                        skills_display = ", ".join(json.loads(pos.required_skills))
                    except (json.JSONDecodeError, TypeError):
                        skills_display = pos.required_skills
                elif isinstance(pos.required_skills, list):
                    skills_display = ", ".join(pos.required_skills)

            keywords_display = "—"
            if pos.search_keywords:
                if isinstance(pos.search_keywords, str):
                    try:
                        keywords_display = ", ".join(json.loads(pos.search_keywords))
                    except (json.JSONDecodeError, TypeError):
                        keywords_display = pos.search_keywords
                elif isinstance(pos.search_keywords, list):
                    keywords_display = ", ".join(pos.search_keywords)

            loop_info = (
                f"enabled, every {pos.loop_interval}m"
                if pos.loop_enabled
                else "disabled"
            )

            body = "\n".join([
                f"  ID:          {pos.id}",
                f"  Status:      {pos.status}",
                f"  Location:    {pos.location or '—'}",
                f"  Description: {pos.description or '—'}",
                f"  Skills:      {skills_display}",
                f"  Keywords:    {keywords_display}",
                f"  Loop:        {loop_info}",
                f"  Created:     {pos.created_at}",
            ])
            console.print(Panel(body, title=f"{pos.title} @ {pos.company}"))

    _run(_do())


@position_app.command("close")
def position_close(
    position_id: str = typer.Argument(..., help="Position UUID"),
    db_url: Optional[str] = typer.Option(None, "--db", help="数据库 URL"),
) -> None:
    """关闭职位。"""
    pid = _validate_uuid(position_id)
    if pid is None:
        console.print(f"[red]无效的 UUID: {position_id}[/]")
        raise typer.Exit(1)

    async def _do() -> None:
        async with Container(db_url) as c:
            pos = await c.position_service.close_position(pid)
            if not pos:
                console.print(f"[red]职位不存在: {position_id}[/]")
                return
            console.print(f"[green]✓ 职位已关闭:[/] {pos.title} ({pos.id})")

    _run(_do())


# ===================================================================
# candidate commands
# ===================================================================


@candidate_app.command("list")
def candidate_list(
    limit: int = typer.Option(20, "--limit", "-n", help="显示数量"),
    db_url: Optional[str] = typer.Option(None, "--db", help="数据库 URL"),
) -> None:
    """列出候选人。"""

    async def _do() -> None:
        async with Container(db_url) as c:
            candidates = await c.candidate_repo.get_all()
            candidates = candidates[:limit]
            if not candidates:
                console.print("[dim]没有找到任何候选人[/]")
                return

            table = Table(title="Candidates", box=box.ROUNDED)
            table.add_column("ID", style="dim", max_width=36)
            table.add_column("Name", style="cyan")
            table.add_column("GitHub", style="green")
            table.add_column("Company")
            table.add_column("Followers", justify="right")
            table.add_column("Repos", justify="right")
            table.add_column("Source")

            for cand in candidates:
                table.add_row(
                    str(cand.id),
                    cand.name or "—",
                    cand.github_login or "—",
                    cand.company or "—",
                    str(cand.followers or 0),
                    str(cand.public_repos or 0),
                    cand.source or "—",
                )

            console.print(table)

    _run(_do())


@candidate_app.command("show")
def candidate_show(
    candidate_id: str = typer.Argument(..., help="Candidate UUID"),
    db_url: Optional[str] = typer.Option(None, "--db", help="数据库 URL"),
) -> None:
    """查看候选人详情。"""
    cid = _validate_uuid(candidate_id)
    if cid is None:
        console.print(f"[red]无效的 UUID: {candidate_id}[/]")
        raise typer.Exit(1)

    async def _do() -> None:
        async with Container(db_url) as c:
            cand = await c.candidate_repo.get_by_id(cid)
            if not cand:
                console.print(f"[red]候选人不存在: {candidate_id}[/]")
                return

            # Parse skills
            skills_display = "—"
            if cand.skills:
                if isinstance(cand.skills, str):
                    try:
                        skills_display = ", ".join(json.loads(cand.skills))
                    except (json.JSONDecodeError, TypeError):
                        skills_display = cand.skills
                elif isinstance(cand.skills, list):
                    skills_display = ", ".join(cand.skills)

            bio = cand.bio or "—"
            if len(bio) > 80:
                bio = bio[:77] + "…"

            body = "\n".join([
                f"  ID:           {cand.id}",
                f"  GitHub:       {cand.github_login or '—'}",
                f"  Email:        {cand.email or '—'}",
                f"  Company:      {cand.company or '—'}",
                f"  Title:        {cand.title or '—'}",
                f"  Location:     {cand.location or '—'}",
                f"  Bio:          {bio}",
                f"  Skills:       {skills_display}",
                f"  Followers:    {cand.followers or 0}",
                f"  Public Repos: {cand.public_repos or 0}",
                f"  Source:       {cand.source or '—'}",
                f"  Appearances:  {cand.appearance_count or 1}",
            ])
            console.print(Panel(body, title=cand.name or cand.github_login or "Candidate"))

    _run(_do())


# ===================================================================
# pipeline commands
# ===================================================================

_STATUS_COLORS = {
    "discovered": "dim",
    "contacted": "yellow",
    "replied": "green",
    "interview": "cyan",
    "offer": "bold green",
    "rejected": "red",
}

_VALID_STATUSES = list(_STATUS_COLORS.keys())


@pipeline_app.command("list")
def pipeline_list(
    position: Optional[str] = typer.Option(None, "--position", "-p", help="按职位过滤"),
    status: Optional[str] = typer.Option(None, "--status", "-s", help="按状态过滤"),
    db_url: Optional[str] = typer.Option(None, "--db", help="数据库 URL"),
) -> None:
    """列出招聘管道。"""

    async def _do() -> None:
        async with Container(db_url) as c:
            pipelines: list = []

            if position:
                pid = _validate_uuid(position)
                if pid is None:
                    console.print(f"[red]无效的 UUID: {position}[/]")
                    raise typer.Exit(1)
                pipelines = await c.pipeline_repo.get_by_position(pid)
            elif status:
                pipelines = await c.pipeline_repo.get_by_status(None, status)  # type: ignore[arg-type]
            else:
                pipelines = await c.pipeline_repo.get_all()

            if not pipelines:
                console.print("[dim]没有找到任何管道记录[/]")
                return

            table = Table(title="Pipelines", box=box.ROUNDED)
            table.add_column("ID", style="dim", max_width=36)
            table.add_column("Position", max_width=36)
            table.add_column("Candidate", max_width=36)
            table.add_column("Status")
            table.add_column("Score", justify="right")
            table.add_column("Notes")

            for pl in pipelines:
                color = _STATUS_COLORS.get(pl.status, "white")
                table.add_row(
                    str(pl.id),
                    str(pl.position_id),
                    str(pl.candidate_id),
                    f"[{color}]{pl.status}[/]",
                    f"{pl.score:.1f}" if pl.score is not None else "—",
                    (pl.notes or "—")[:40],
                )

            console.print(table)

    _run(_do())


@pipeline_app.command("update-status")
def pipeline_update_status(
    pipeline_id: str = typer.Argument(..., help="Pipeline UUID"),
    status: str = typer.Argument(..., help="新状态"),
    db_url: Optional[str] = typer.Option(None, "--db", help="数据库 URL"),
) -> None:
    """更新管道状态。"""
    pid = _validate_uuid(pipeline_id)
    if pid is None:
        console.print(f"[red]无效的 UUID: {pipeline_id}[/]")
        raise typer.Exit(1)

    if status not in _VALID_STATUSES:
        console.print(
            f"[red]无效状态: {status}[/]\n"
            f"合法值: {', '.join(_VALID_STATUSES)}"
        )
        raise typer.Exit(1)

    async def _do() -> None:
        async with Container(db_url) as c:
            pl = await c.pipeline_service.update_pipeline_status(pid, status)
            if not pl:
                console.print(f"[red]管道不存在: {pipeline_id}[/]")
                return
            console.print(
                f"[green]✓ 管道状态已更新:[/] {pl.id} → [{_STATUS_COLORS.get(status, 'white')}]{status}[/]"
            )

    _run(_do())


# ===================================================================
# schedule commands
# ===================================================================


@schedule_app.command("start")
def schedule_start(
    db_url: Optional[str] = typer.Option(None, "--db", help="数据库 URL"),
) -> None:
    """启动后台调度器 (Ctrl+C 退出)。"""

    async def _scheduler_loop() -> None:
        async with Container(db_url) as c:
            await c.scheduler.start()
            console.print("[green]调度器已启动[/] — 按 Ctrl+C 停止")
            try:
                while True:
                    await asyncio.sleep(1)
            except KeyboardInterrupt:
                await c.scheduler.stop()
                console.print("\n[yellow]调度器已停止[/]")

    _run(_scheduler_loop())


@schedule_app.command("list")
def schedule_list(
    db_url: Optional[str] = typer.Option(None, "--db", help="数据库 URL"),
) -> None:
    """列出调度任务。"""

    async def _do() -> None:
        async with Container(db_url) as c:
            jobs = await c.scheduler_job_repo.get_all()
            if not jobs:
                console.print("[dim]没有找到任何调度任务[/]")
                return

            table = Table(title="Scheduler Jobs", box=box.ROUNDED)
            table.add_column("ID", style="dim", max_width=36)
            table.add_column("Position ID", max_width=36)
            table.add_column("Enabled")
            table.add_column("Interval", justify="right")
            table.add_column("Total Runs", justify="right")
            table.add_column("Status")
            table.add_column("Next Run")

            for job in jobs:
                table.add_row(
                    str(job.id),
                    str(job.position_id),
                    "✓" if job.enabled else "✗",
                    f"{job.interval_minutes}m",
                    str(job.total_runs or 0),
                    job.status or "—",
                    str(job.next_run or "—"),
                )

            console.print(table)

    _run(_do())


# ===================================================================
# dashboard
# ===================================================================


@app.command("dashboard")
def dashboard(
    db_url: Optional[str] = typer.Option(None, "--db", help="数据库 URL"),
) -> None:
    """查看仪表盘摘要。"""

    async def _do() -> None:
        async with Container(db_url) as c:
            summary = await c.dashboard_service.get_dashboard_summary()
            body = "\n".join([
                f"  Running Positions: {summary.get('running_positions', 0)}",
                f"  Today Loops:       {summary.get('today_loops', 0)}",
                f"  Today Candidates:   {summary.get('today_candidates', 0)}",
                f"  Today Emails:      {summary.get('today_emails', 0)}",
                f"  Today Replies:     {summary.get('today_replies', 0)}",
                f"  Today Errors:      {summary.get('today_errors', 0)}",
            ])
            console.print(Panel(body, title="Dashboard"))

    _run(_do())


# ===================================================================
# graph
# ===================================================================


@app.command("graph")
def graph() -> None:
    """显示 LangGraph 图结构 (ASCII)。"""
    diagram = """\
┌─────────┐    ┌─────────┐    ┌─────────┐
│  Search  │───▶│  Score   │───▶│ Pipeline │
└─────────┘    └─────────┘    └─────────┘
                                     │
┌─────────┐    ┌──────────┐    ┌──────▼───┐
│Evaluate  │◀───│ Outreach │◀───│  Dedup   │
└─────────┘    └──────────┘    └──────────┘
     │
     ▼
 [loop / stop]\
"""
    console.print(Panel(diagram, title="LangGraph — Recruiting Loop"))


# ===================================================================
# version
# ===================================================================


@app.command("version")
def version() -> None:
    """显示版本信息。"""
    console.print(f"loop-agent-cli v{__version__}")
    console.print("[dim]Based on recruit-loop-agent core engine[/]")


# ===================================================================
# Entry point
# ===================================================================

if __name__ == "__main__":
    app()

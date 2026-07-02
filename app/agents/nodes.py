"""
LangGraph node functions for the recruiting agent pipeline.

Nodes that benefit from LLM intelligence (score, outreach, evaluate) call
the async :class:`~app.core.llm_client.LLMClient` and fall back to
rule-based defaults when the LLM is unavailable.
"""

from __future__ import annotations

import json
import logging
from typing import Any, Dict, List, Optional

from app.agents.state import RecruitingState
from app.core.llm_client import LLMClient, LLMError, get_llm_client

logger = logging.getLogger("recruiting_agent.nodes")


# ===================================================================
# Helpers
# ===================================================================


def _safe_get(d: Any, key: str, default: Any = None) -> Any:
    """Get value from dict or object attribute."""
    if isinstance(d, dict):
        return d.get(key, default)
    return getattr(d, key, default)


def _build_candidate_summary(candidate: Dict[str, Any]) -> str:
    """Build a short text summary of a candidate for LLM prompts."""
    name = _safe_get(candidate, "name", "Unknown")
    skills = _safe_get(candidate, "skills", []) or []
    if isinstance(skills, str):
        try:
            skills = json.loads(skills)
        except (json.JSONDecodeError, TypeError):
            skills = [skills]
    bio = _safe_get(candidate, "bio", "") or ""
    company = _safe_get(candidate, "company", "") or ""
    title = _safe_get(candidate, "title", "") or ""
    source = _safe_get(candidate, "source", "") or ""
    return (
        f"Name: {name}\n"
        f"Title: {title}\n"
        f"Company: {company}\n"
        f"Skills: {', '.join(skills) if skills else 'N/A'}\n"
        f"Bio: {bio}\n"
        f"Source: {source}"
    )


def _build_position_summary(position: Any) -> str:
    """Build a short text summary of a position for LLM prompts."""
    title = _safe_get(position, "title", "Unknown")
    company = _safe_get(position, "company", "") or ""
    description = _safe_get(position, "description", "") or ""
    required_skills = _safe_get(position, "required_skills", []) or []
    if isinstance(required_skills, str):
        try:
            required_skills = json.loads(required_skills)
        except (json.JSONDecodeError, TypeError):
            required_skills = [required_skills]
    location = _safe_get(position, "location", "") or ""
    salary_min = _safe_get(position, "salary_min", "") or ""
    salary_max = _safe_get(position, "salary_max", "") or ""
    salary_range = ""
    if salary_min and salary_max:
        salary_range = f"{salary_min} - {salary_max}"
    return (
        f"Title: {title}\n"
        f"Company: {company}\n"
        f"Location: {location}\n"
        f"Salary: {salary_range}\n"
        f"Required Skills: {', '.join(required_skills) if required_skills else 'N/A'}\n"
        f"Description: {description[:500]}"
    )


# ===================================================================
# search_node  (unchanged — rule-based)
# ===================================================================


async def search_node(state: RecruitingState) -> Dict[str, Any]:
    """
    Search node: Perform candidate search based on position requirements.
    """
    try:
        position = state["position"]
        keywords = [position.title] + (position.required_skills or []) + (position.search_keywords or [])

        search_results = {
            "keywords": keywords,
            "candidates": state.get("candidates", []),
            "found_count": len(state.get("candidates", [])),
        }

        metrics = state.get("metrics", {})
        metrics["search_count"] = metrics.get("search_count", 0) + 1

        return {
            **state,
            "keywords": keywords,
            "candidates": state.get("candidates", []),
            "metrics": metrics,
        }
    except Exception as e:
        errors = state.get("errors", [])
        errors.append(f"Search node error: {str(e)}")
        return {**state, "errors": errors}


# ===================================================================
# dedup_node  (unchanged — rule-based)
# ===================================================================


async def dedup_node(state: RecruitingState) -> Dict[str, Any]:
    """
    Deduplication node: Remove duplicate candidates.
    """
    try:
        candidates = state.get("candidates", [])
        seen_ids: set = set()
        unique_candidates: List[Dict[str, Any]] = []

        for candidate in candidates:
            source_id = candidate.get("source_id") or (
                candidate.get("id") if hasattr(candidate, "id") else None
            )
            if source_id not in seen_ids:
                seen_ids.add(source_id)
                unique_candidates.append(candidate)

        dedup_result = {
            "original_count": len(candidates),
            "unique_count": len(unique_candidates),
            "duplicates_removed": len(candidates) - len(unique_candidates),
        }

        metrics = state.get("metrics", {})
        metrics["candidates_deduped"] = len(unique_candidates)

        return {
            **state,
            "dedup_result": [unique_candidates],
            "candidates": unique_candidates,
            "metrics": metrics,
        }
    except Exception as e:
        errors = state.get("errors", [])
        errors.append(f"Dedup node error: {str(e)}")
        return {**state, "errors": errors}


# ===================================================================
# score_node  (LLM-powered with rule-based fallback)
# ===================================================================

_SCORE_SYSTEM_PROMPT = """\
You are an expert technical recruiter. Given a job position and a candidate profile,
produce a match score from 0 to 100 and a brief reason.

Respond in this exact JSON format (no extra text):
{
  "score": <int 0-100>,
  "reason": "<one-sentence explanation>"
}
"""


def _fallback_score(candidate: Dict[str, Any], position: Any) -> Dict[str, Any]:
    """Rule-based fallback: simple skill-overlap scoring."""
    required = _safe_get(position, "required_skills", []) or []
    if isinstance(required, str):
        try:
            required = json.loads(required)
        except (json.JSONDecodeError, TypeError):
            required = [required]
    required_lower = {s.strip().lower() for s in required if s}

    candidate_skills = _safe_get(candidate, "skills", []) or []
    if isinstance(candidate_skills, str):
        try:
            candidate_skills = json.loads(candidate_skills)
        except (json.JSONDecodeError, TypeError):
            candidate_skills = [candidate_skills]
    candidate_lower = {s.strip().lower() for s in candidate_skills if s}

    if not required_lower:
        return {"score": 50, "reason": "No required skills specified; default score."}

    overlap = required_lower & candidate_lower
    ratio = len(overlap) / len(required_lower)
    score = int(ratio * 100)
    reason = f"Skill overlap: {len(overlap)}/{len(required_lower)} ({', '.join(overlap) or 'none'})"
    return {"score": max(score, 10), "reason": reason}


async def score_node(state: RecruitingState) -> Dict[str, Any]:
    """
    Scoring node: Score candidates using LLM based on position requirements.
    Falls back to rule-based skill-overlap scoring if LLM is unavailable.
    """
    try:
        candidates = state.get("candidates", [])
        position = state["position"]
        position_summary = _build_position_summary(position)

        scored_candidates: List[Dict[str, Any]] = []
        score_details: List[Dict[str, Any]] = []

        # Try to get LLM client; if not configured, use fallback for all
        try:
            llm = get_llm_client()
            llm_available = bool(llm.api_base_url and llm.api_key)
        except Exception:
            llm = None
            llm_available = False

        for candidate in candidates:
            result: Dict[str, Any]

            if llm_available and llm is not None:
                try:
                    candidate_summary = _build_candidate_summary(candidate)
                    user_prompt = (
                        f"Position:\n{position_summary}\n\n"
                        f"Candidate:\n{candidate_summary}\n\n"
                        f"Score this candidate's match for the position."
                    )
                    parsed = await llm.chat_json(
                        user_prompt,
                        system_prompt=_SCORE_SYSTEM_PROMPT,
                    )
                    if parsed and isinstance(parsed, dict) and "score" in parsed:
                        result = {
                            "score": max(0, min(100, int(parsed["score"]))),
                            "reason": parsed.get("reason", "LLM score"),
                        }
                    else:
                        raise ValueError("LLM returned invalid score format")
                except (LLMError, Exception) as exc:
                    logger.warning("LLM scoring failed for candidate, using fallback: %s", exc)
                    result = _fallback_score(candidate, position)
            else:
                result = _fallback_score(candidate, position)

            scored_candidates.append({**candidate, "score": float(result["score"])})
            score_details.append({
                "candidate_id": _safe_get(candidate, "id", "unknown"),
                "score": result["score"],
                "reason": result["reason"],
            })

        metrics = state.get("metrics", {})
        metrics["candidates_scored"] = len(scored_candidates)

        return {
            **state,
            "candidates": scored_candidates,
            "score_details": score_details,
            "metrics": metrics,
        }
    except Exception as e:
        errors = state.get("errors", [])
        errors.append(f"Score node error: {str(e)}")
        return {**state, "errors": errors}


# ===================================================================
# pipeline_node  (unchanged — rule-based)
# ===================================================================


async def pipeline_node(state: RecruitingState) -> Dict[str, Any]:
    """
    Pipeline node: Update pipeline with scored candidates.
    """
    try:
        candidates = state.get("candidates", [])
        position = state["position"]

        pipeline_updates: List[Dict[str, Any]] = []
        for candidate in candidates:
            pipeline_update = {
                "candidate_id": _safe_get(candidate, "id", "unknown"),
                "position_id": position.id,
                "status": "discovered",
                "score": _safe_get(candidate, "score", 0),
            }
            pipeline_updates.append(pipeline_update)

        metrics = state.get("metrics", {})
        metrics["pipeline_updates"] = len(pipeline_updates)

        return {
            **state,
            "pipeline_updates": pipeline_updates,
            "metrics": metrics,
        }
    except Exception as e:
        errors = state.get("errors", [])
        errors.append(f"Pipeline node error: {str(e)}")
        return {**state, "errors": errors}


# ===================================================================
# outreach_node  (LLM-powered with template fallback)
# ===================================================================

_OUTREACH_SYSTEM_PROMPT = """\
You are a professional recruiting email writer. Generate a personalized \
recruitment outreach email for a candidate based on their background and \
the job position.

Respond in this exact JSON format (no extra text):
{
  "subject": "<email subject line>",
  "body": "<email body text>"
}

Guidelines:
- Keep the tone professional but warm
- Reference specific skills or experience from the candidate's profile
- Mention the position title and company
- Include a clear call-to-action
- Keep the body under 200 words
"""


def _fallback_outreach(candidate: Dict[str, Any], position: Any) -> Dict[str, str]:
    """Template-based fallback email."""
    name = _safe_get(candidate, "name", "Candidate")
    title = _safe_get(position, "title", "the position")
    company = _safe_get(position, "company", "our company")
    return {
        "subject": f"Exciting Opportunity: {title} at {company}",
        "body": (
            f"Hi {name},\n\n"
            f"I came across your profile and was impressed by your background. "
            f"We have an exciting opportunity for a {title} role at {company} "
            f"that I think would be a great fit for your skills.\n\n"
            f"Would you be open to a quick chat to learn more?\n\n"
            f"Best regards,\n"
            f"Recruiting Team"
        ),
    }


async def outreach_node(state: RecruitingState) -> Dict[str, Any]:
    """
    Outreach node: Generate personalized recruitment emails using LLM.
    Falls back to a fixed template if LLM is unavailable.
    """
    try:
        candidates = state.get("candidates", [])
        position = state["position"]
        position_summary = _build_position_summary(position)

        # Determine LLM availability
        try:
            llm = get_llm_client()
            llm_available = bool(llm.api_base_url and llm.api_key)
        except Exception:
            llm = None
            llm_available = False

        outreach_emails: List[Dict[str, Any]] = []
        metrics = state.get("metrics", {})
        emails_sent = 0

        for candidate in candidates[:10]:  # Limit outreach batch size
            email_result: Dict[str, str]

            if llm_available and llm is not None:
                try:
                    candidate_summary = _build_candidate_summary(candidate)
                    user_prompt = (
                        f"Position:\n{position_summary}\n\n"
                        f"Candidate:\n{candidate_summary}\n\n"
                        f"Write a personalized recruitment outreach email."
                    )
                    parsed = await llm.chat_json(
                        user_prompt,
                        system_prompt=_OUTREACH_SYSTEM_PROMPT,
                    )
                    if parsed and isinstance(parsed, dict) and "subject" in parsed:
                        email_result = {
                            "subject": str(parsed["subject"]),
                            "body": str(parsed.get("body", "")),
                        }
                    else:
                        raise ValueError("LLM returned invalid email format")
                except (LLMError, Exception) as exc:
                    logger.warning("LLM outreach failed for candidate, using fallback: %s", exc)
                    email_result = _fallback_outreach(candidate, position)
            else:
                email_result = _fallback_outreach(candidate, position)

            outreach_emails.append({
                "candidate_id": _safe_get(candidate, "id", "unknown"),
                "candidate_name": _safe_get(candidate, "name", "Unknown"),
                "subject": email_result["subject"],
                "body": email_result["body"],
                "status": "generated",
                "type": "email",
            })
            emails_sent += 1

        metrics["outreach_attempts"] = emails_sent
        metrics["emails_sent"] = emails_sent

        return {
            **state,
            "outreach_emails": outreach_emails,
            "metrics": metrics,
        }
    except Exception as e:
        errors = state.get("errors", [])
        errors.append(f"Outreach node error: {str(e)}")
        return {**state, "errors": errors}


# ===================================================================
# evaluate_node  (LLM-powered with rule-based fallback)
# ===================================================================

_EVALUATE_SYSTEM_PROMPT = """\
You are a recruiting strategy analyst. Based on the current recruiting loop \
results, decide whether the agent should continue searching for more candidates \
or stop.

Respond in this exact JSON format (no extra text):
{
  "continue_loop": <true or false>,
  "reason": "<one-sentence explanation>"
}

Consider:
- How many qualified candidates have been found (score >= 60)?
- Is the pipeline healthy?
- Has enough outreach been done?
- Is the position likely still active?
"""


def _fallback_evaluate(state: RecruitingState) -> Dict[str, Any]:
    """Rule-based fallback: continue if position is active and few candidates found."""
    position = state.get("position")
    metrics = state.get("metrics", {})
    candidates = state.get("candidates", [])

    if position is None:
        return {"continue_loop": False, "reason": "No position in state."}

    is_active = _safe_get(position, "status", "") == "active"
    scored_above_threshold = sum(
        1 for c in candidates if _safe_get(c, "score", 0) >= 60
    )
    emails_sent = metrics.get("emails_sent", 0)

    # Stop if: position closed, or found enough good candidates with outreach done
    if not is_active:
        return {"continue_loop": False, "reason": "Position is not active."}
    if scored_above_threshold >= 5 and emails_sent >= 3:
        return {
            "continue_loop": False,
            "reason": f"Found {scored_above_threshold} qualified candidates and sent {emails_sent} emails.",
        }
    return {
        "continue_loop": True,
        "reason": f"Only {scored_above_threshold} qualified candidates so far; continuing search.",
    }


async def evaluate_node(state: RecruitingState) -> Dict[str, Any]:
    """
    Evaluation node: Use LLM to decide whether to continue the recruiting loop.
    Falls back to rule-based logic if LLM is unavailable.
    """
    try:
        metrics = state.get("metrics", {})
        candidates = state.get("candidates", [])
        position = state.get("position")

        # Determine LLM availability
        try:
            llm = get_llm_client()
            llm_available = bool(llm.api_base_url and llm.api_key)
        except Exception:
            llm = None
            llm_available = False

        result: Dict[str, Any]

        if llm_available and llm is not None:
            try:
                position_summary = _build_position_summary(position)
                score_details = state.get("score_details", [])
                outreach_emails = state.get("outreach_emails", [])

                user_prompt = (
                    f"Position:\n{position_summary}\n\n"
                    f"Current Loop Results:\n"
                    f"- Total candidates found: {len(candidates)}\n"
                    f"- Candidates scored: {metrics.get('candidates_scored', 0)}\n"
                    f"- Outreach emails sent: {metrics.get('emails_sent', 0)}\n"
                    f"- Pipeline updates: {metrics.get('pipeline_updates', 0)}\n\n"
                    f"Score Details:\n{json.dumps(score_details[:10], indent=2, default=str)}\n\n"
                    f"Should the recruiting agent continue searching for more candidates "
                    f"or stop the loop?"
                )
                parsed = await llm.chat_json(
                    user_prompt,
                    system_prompt=_EVALUATE_SYSTEM_PROMPT,
                )
                if parsed and isinstance(parsed, dict) and "continue_loop" in parsed:
                    result = {
                        "continue_loop": bool(parsed["continue_loop"]),
                        "reason": parsed.get("reason", "LLM evaluation"),
                    }
                else:
                    raise ValueError("LLM returned invalid evaluation format")
            except (LLMError, Exception) as exc:
                logger.warning("LLM evaluation failed, using fallback: %s", exc)
                result = _fallback_evaluate(state)
        else:
            result = _fallback_evaluate(state)

        metrics["evaluation_completed"] = True
        logger.info(
            "Evaluate result: continue=%s reason=%s",
            result["continue_loop"],
            result.get("reason", ""),
        )

        return {
            **state,
            "continue_loop": result["continue_loop"],
            "metrics": metrics,
        }
    except Exception as e:
        errors = state.get("errors", [])
        errors.append(f"Evaluate node error: {str(e)}")
        return {**state, "errors": errors, "continue_loop": False}

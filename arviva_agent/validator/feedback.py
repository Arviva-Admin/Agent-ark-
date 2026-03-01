"""Feedback- och repair-policy för autonom loop."""

from __future__ import annotations

from dataclasses import dataclass

from arviva_agent.validator.verifier import VerificationResult


@dataclass
class FeedbackDecision:
    action: str  # continue | retry | replan | stop
    reason: str


class FeedbackPolicy:
    def decide(self, verification: VerificationResult, retries: int, max_retries: int = 1) -> FeedbackDecision:
        if verification.ok:
            return FeedbackDecision(action="continue", reason=verification.message)
        if retries < max_retries:
            return FeedbackDecision(action="retry", reason="Verifiering misslyckades, försök igen")
        return FeedbackDecision(action="replan", reason="Verifiering misslyckades efter retries")

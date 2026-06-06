"""
Model Assignments — domain-to-model routing with current Claude model IDs.

Maps work domains to appropriate models based on capabilities, cost,
and tier preferences.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, List, Dict


class ModelTier(str, Enum):
    """Model cost/capability tier."""
    FREE = "free"
    OPENROUTER = "openrouter"
    LOCAL = "local"
    PAID = "paid"


class Domain(str, Enum):
    """Work domain categories."""
    CODE = "code"
    ANALYSIS = "analysis"
    CREATIVE = "creative"
    QA = "qa"
    RESEARCH = "research"
    PLANNING = "planning"
    COMMUNICATION = "communication"
    GENERAL = "general"


@dataclass
class ModelSpec:
    """Specification for a model."""
    model_id: str
    tier: ModelTier
    context_window: int
    cost_per_1k_input: float   # USD per 1k input tokens
    cost_per_1k_output: float  # USD per 1k output tokens
    capabilities: List[str] = field(default_factory=list)


# Current model catalogue
MODELS: Dict[str, ModelSpec] = {
    "claude-opus-4-6": ModelSpec(
        model_id="claude-opus-4-6",
        tier=ModelTier.PAID,
        context_window=200_000,
        cost_per_1k_input=15.0 / 1000,   # $15 / 1M → $0.015 / 1k
        cost_per_1k_output=75.0 / 1000,  # $75 / 1M → $0.075 / 1k
        capabilities=["code", "analysis", "reasoning", "creative"],
    ),
    "claude-sonnet-4-6": ModelSpec(
        model_id="claude-sonnet-4-6",
        tier=ModelTier.PAID,
        context_window=200_000,
        cost_per_1k_input=3.0 / 1000,    # $3 / 1M
        cost_per_1k_output=15.0 / 1000,  # $15 / 1M
        capabilities=["code", "analysis", "communication"],
    ),
    "claude-haiku-4-5": ModelSpec(
        model_id="claude-haiku-4-5",
        tier=ModelTier.PAID,
        context_window=200_000,
        cost_per_1k_input=0.25 / 1000,   # $0.25 / 1M
        cost_per_1k_output=1.25 / 1000,  # $1.25 / 1M
        capabilities=["quick", "qa", "routing"],
    ),
    "inflection-3-pi": ModelSpec(
        model_id="inflection-3-pi",
        tier=ModelTier.LOCAL,
        context_window=8_000,
        cost_per_1k_input=0.0,
        cost_per_1k_output=0.0,
        capabilities=["communication", "general"],
    ),
}

# Domain → preferred model_id
DOMAIN_ASSIGNMENTS: Dict[Domain, str] = {
    Domain.CODE: "claude-sonnet-4-6",
    Domain.ANALYSIS: "claude-sonnet-4-6",
    Domain.CREATIVE: "claude-sonnet-4-6",
    Domain.QA: "claude-haiku-4-5",
    Domain.RESEARCH: "claude-opus-4-6",
    Domain.PLANNING: "claude-opus-4-6",
    Domain.COMMUNICATION: "claude-haiku-4-5",
    Domain.GENERAL: "claude-sonnet-4-6",
}


class ModelRouter:
    """Routes work domains to appropriate models."""

    def get_model(
        self,
        domain: Domain,
        tier_preference: ModelTier = ModelTier.PAID,
    ) -> ModelSpec:
        """
        Return the best ModelSpec for the given domain and tier preference.

        Falls back to claude-sonnet-4-6 if the preferred model does not match
        the requested tier.
        """
        preferred_id = DOMAIN_ASSIGNMENTS.get(domain, "claude-sonnet-4-6")
        preferred_spec = MODELS[preferred_id]

        # If tier matches, return it directly
        if preferred_spec.tier == tier_preference:
            return preferred_spec

        # Otherwise find the best model in the requested tier that covers domain
        domain_value = domain.value
        candidates = [
            spec for spec in MODELS.values()
            if spec.tier == tier_preference and domain_value in spec.capabilities
        ]
        if candidates:
            # Return cheapest candidate
            return min(candidates, key=lambda s: s.cost_per_1k_input)

        # Last resort: return the assigned model regardless of tier
        return preferred_spec

    def estimate_cost(
        self,
        model_id: str,
        input_tokens: int,
        output_tokens: int,
    ) -> float:
        """
        Estimate USD cost for a model invocation.

        Returns 0.0 if model_id is not found.
        """
        spec = MODELS.get(model_id)
        if spec is None:
            return 0.0
        return (
            spec.cost_per_1k_input * input_tokens / 1000
            + spec.cost_per_1k_output * output_tokens / 1000
        )

    def list_models(self, tier: Optional[ModelTier] = None) -> List[ModelSpec]:
        """Return all models, optionally filtered by tier."""
        if tier is None:
            return list(MODELS.values())
        return [spec for spec in MODELS.values() if spec.tier == tier]


# Alias kept for backward compatibility
ModelAssignments = ModelRouter

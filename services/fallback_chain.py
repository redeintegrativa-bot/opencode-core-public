"""
Fallback Chain Manager

Manages agent failover chains as defined in error-recovery.md.
When a primary agent fails, automatically routes to fallback agents.
"""

import logging
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field

logger = logging.getLogger("fallback_chain")


@dataclass
class RecoveryAttempt:
    """Record of a recovery attempt."""
    timestamp: float
    primary_agent: str
    fallback_agent: str
    error: str
    success: bool


# Fallback chains from error-recovery.md
# Format: primary_agent -> [fallback1, fallback2, ...]
FALLBACK_CHAINS: Dict[str, List[str]] = {
    # Core Agents
    "orchestrator": ["engineer"],
    "architect": ["engineer"],
    "engineer": [],
    "researcher": ["engineer"],
    "security": ["engineer"],
    "database": ["engineer"],
    "automation": ["engineer"],
    "ai_specialist": ["engineer"],
    "browser": ["engineer"],

    # L1 Expert Agents (mapped to AIOS agent types)
    "gui_super_expert": ["engineer"],
    "database_expert": ["engineer"],
    "security_unified_expert": ["engineer"],
    "mql_expert": ["engineer"],
    "trading_strategy_expert": ["engineer"],
    "tester_expert": ["engineer"],
    "architect_expert": ["engineer"],
    "integration_expert": ["engineer"],
    "devops_expert": ["engineer"],
    "languages_expert": ["engineer"],
    "ai_integration_expert": ["engineer"],
    "claude_systems_expert": ["engineer"],
    "mobile_expert": ["engineer"],
    "n8n_expert": ["engineer"],
    "social_identity_expert": ["engineer"],
    "reverse_engineering_expert": ["engineer"],
    "offensive_security_expert": ["security"],
    "notification_expert": ["engineer"],
    "browser_automation_expert": ["browser"],
    "mcp_integration_expert": ["engineer"],
    "payment_integration_expert": ["engineer"],
    "mql_decompilation_expert": ["engineer"],
}

# Universal fallback - if no chain defined, use this
UNIVERSAL_FALLBACK = "engineer"


class FallbackChain:
    """
    Manages failover chains for agents.

    When a primary agent fails:
    1. Look up fallback chain
    2. Try fallback agents in order
    3. If all fail, return failure with full history
    """

    def __init__(self, agents: Dict[str, Any] = None):
        """
        Args:
            agents: Dict of agent_name -> agent_instance
                    If None, chains are tracked but no execution happens.
        """
        self._agents = agents or {}
        self._recovery_history: List[RecoveryAttempt] = []
        self._max_fallback_attempts = 3
        logger.info("FallbackChain initialized")

    def set_agents(self, agents: Dict[str, Any]):
        """Set or update the agent instances."""
        self._agents = agents

    def get_chain(self, agent_name: str) -> List[str]:
        """Get the fallback chain for an agent."""
        chain = FALLBACK_CHAINS.get(agent_name, [])
        # Always add universal fallback if not already in chain
        if UNIVERSAL_FALLBACK not in chain and UNIVERSAL_FALLBACK != agent_name:
            chain = chain + [UNIVERSAL_FALLBACK]
        return chain

    def execute_with_fallback(
        self,
        task: Dict[str, Any],
        primary_agent_name: str,
    ) -> Dict[str, Any]:
        """
        Execute a task with automatic fallback.

        Args:
            task: Task dictionary to execute
            primary_agent_name: Name of the primary agent to try first

        Returns:
            Dict with keys: success, agent, result, attempts, errors
        """
        attempts = []
        errors = []
        chain = self.get_chain(primary_agent_name)

        # Try primary agent first
        primary_agent = self._agents.get(primary_agent_name)
        if primary_agent is None:
            errors.append(f"Primary agent '{primary_agent_name}' not found")
        else:
            result = self._try_agent(primary_agent, task, primary_agent_name)
            attempts.append(result)
            if result["success"]:
                return {
                    "success": True,
                    "agent": primary_agent_name,
                    "result": result["result"],
                    "attempts": attempts,
                    "errors": errors,
                }
            errors.append(
                f"Primary agent '{primary_agent_name}' failed: {result['error']}"
            )

        # Try fallback agents
        for fallback_name in chain:
            fallback_agent = self._agents.get(fallback_name)
            if fallback_agent is None:
                errors.append(f"Fallback agent '{fallback_name}' not found, skipping")
                continue

            logger.info(
                f"Failing over from '{primary_agent_name}' to '{fallback_name}'"
            )

            result = self._try_agent(fallback_agent, task, fallback_name)
            attempts.append(result)

            if result["success"]:
                self._record_recovery(
                    primary_agent_name, fallback_name, "", True
                )
                return {
                    "success": True,
                    "agent": fallback_name,
                    "result": result["result"],
                    "attempts": attempts,
                    "errors": errors,
                }

            errors.append(
                f"Fallback agent '{fallback_name}' failed: {result['error']}"
            )
            self._record_recovery(
                primary_agent_name, fallback_name, result["error"], False
            )

        # All agents failed
        logger.error(
            f"All agents failed for task. Primary: {primary_agent_name}, "
            f"Chain: {chain}"
        )
        return {
            "success": False,
            "agent": None,
            "result": None,
            "attempts": attempts,
            "errors": errors,
        }

    def _try_agent(
        self, agent: Any, task: Dict, agent_name: str
    ) -> Dict[str, Any]:
        """Try to execute a task with a specific agent."""
        try:
            from ..base_agent import AgentStatus

            # Skip if agent is busy or offline
            if agent.status in (AgentStatus.BUSY, AgentStatus.OFFLINE):
                return {
                    "success": False,
                    "agent": agent_name,
                    "result": None,
                    "error": f"Agent '{agent_name}' is {agent.status.value}",
                }

            # Check circuit breaker
            if not agent._circuit_breaker.can_execute():
                return {
                    "success": False,
                    "agent": agent_name,
                    "result": None,
                    "error": f"Circuit breaker open for '{agent_name}'",
                }

            result = agent._execute_with_retry(task)
            return {
                "success": result.success,
                "agent": agent_name,
                "result": result,
                "error": None if result.success else str(result.errors),
            }

        except Exception as e:
            return {
                "success": False,
                "agent": agent_name,
                "result": None,
                "error": str(e),
            }

    def _record_recovery(
        self,
        primary: str,
        fallback: str,
        error: str,
        success: bool,
    ):
        """Record a recovery attempt."""
        attempt = RecoveryAttempt(
            timestamp=time.time(),
            primary_agent=primary,
            fallback_agent=fallback,
            error=error,
            success=success,
        )
        self._recovery_history.append(attempt)
        logger.info(
            f"Recovery recorded: {primary} -> {fallback}, "
            f"success={success}"
        )

    def get_recovery_history(self) -> List[Dict]:
        """Get history of all recovery attempts."""
        return [
            {
                "timestamp": a.timestamp,
                "primary": a.primary_agent,
                "fallback": a.fallback_agent,
                "error": a.error,
                "success": a.success,
            }
            for a in self._recovery_history
        ]

    def get_stats(self) -> Dict[str, Any]:
        """Get fallback chain statistics."""
        total = len(self._recovery_history)
        successful = sum(1 for a in self._recovery_history if a.success)
        return {
            "total_attempts": total,
            "successful_recoveries": successful,
            "failed_recoveries": total - successful,
            "success_rate": successful / total if total > 0 else 0,
        }

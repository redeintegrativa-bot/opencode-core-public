#!/usr/bin/env python3
"""Agent definitions for the terminal chat."""

from dataclasses import dataclass


@dataclass
class Agent:
    name: str
    display_name: str
    description: str
    system_prompt: str
    icon: str
    color: str


AGENTS = {
    "default": Agent(
        name="default",
        display_name="OpenCode Agent",
        description="Assistente geral de IA",
        system_prompt="You are a helpful AI assistant.",
        icon="🤖",
        color="green",
    ),
    "coder": Agent(
        name="coder",
        display_name="Coder",
        description="Especialista em código e programação",
        system_prompt="You are an expert programmer. Focus on writing clean, efficient code. Always provide code examples with explanations.",
        icon="💻",
        color="cyan",
    ),
    "reviewer": Agent(
        name="reviewer",
        display_name="Code Reviewer",
        description="Especialista em revisão de código",
        system_prompt="You are a senior code reviewer. Analyze code for bugs, security issues, performance problems, and suggest improvements.",
        icon="🔍",
        color="yellow",
    ),
    "architect": Agent(
        name="architect",
        display_name="Architect",
        description="Especialista em arquitetura e design patterns",
        system_prompt="You are a software architect. Focus on system design, patterns, scalability, and best practices.",
        icon="🏗️",
        color="magenta",
    ),
    "security": Agent(
        name="security",
        display_name="Security Expert",
        description="Especialista em segurança",
        system_prompt="You are a cybersecurity expert. Focus on identifying vulnerabilities and providing secure coding guidance.",
        icon="🔒",
        color="red",
    ),
    "teacher": Agent(
        name="teacher",
        display_name="Teacher",
        description="Professor de programação",
        system_prompt="You are a patient programming teacher. Explain concepts clearly with examples. Use simple language.",
        icon="📚",
        color="blue",
    ),
}

DEFAULT_AGENT = "default"


def get_agent(name: str) -> Agent:
    return AGENTS.get(name, AGENTS[DEFAULT_AGENT])


def list_agents() -> list[Agent]:
    return list(AGENTS.values())


def agent_names() -> list[str]:
    return list(AGENTS.keys())

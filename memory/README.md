# Memory System

Extracted from AIOS (AI Operating System) core memory system.

## Overview

This module provides persistent memory storage for agents with support for:
- Different memory types (episodic, semantic, procedural)
- Keyword-based search with relevance scoring
- Memory consolidation for similar memories
- Memory sharing between agents
- Disk persistence with JSON storage

## Features

- **Memory Types**: Episodic, semantic, and procedural memory classification
- **Search**: Keyword-based relevance scoring with importance and recency weighting
- **Consolidation**: Automatically merges similar memories above a configurable threshold
- **Sharing**: Copy memories between agents with source tracking
- **Persistence**: Automatic JSON file storage in `memory/agents/` directory

## Usage

```python
from memory import MemorySystem, MemoryType

# Initialize
system = MemorySystem("/path/to/project")

# Add memory
memory = system.add_memory(
    agent_name="engineer",
    memory_type=MemoryType.SEMANTIC,
    content={"text": "Important finding"},
    keywords=["finding", "analysis"],
    importance=0.8
)

# Search memories
results = system.search_memories("finding analysis", agent_name="engineer")

# Consolidate similar memories
system.consolidate_memories("engineer", threshold=0.7)
```

## CLI Usage

```bash
python memory.py --root /path/to/project add agent_name semantic "text content"
python memory.py --root /path/to/project list agent_name
python memory.py --root /path/to/project search "query"
python memory.py --root /path/to/project stats
python memory.py --root /path/to/project consolidate agent_name
python memory.py --root /path/to/project share memory_id target_agent
```

## Storage

Memories are stored as JSON files:
- `memory/agents/{agent_name}.json` - Per-agent memory storage
- `memory/shared/index.json` - Shared memory index

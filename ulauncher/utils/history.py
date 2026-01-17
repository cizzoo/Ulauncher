from __future__ import annotations

import json
import logging
import os
import time

from ulauncher import paths

logger = logging.getLogger(__name__)

# Max number of commands to keep in history
# TODO: it would be nice to make this configurable via settings
MAX_HISTORY_ITEMS = 1000


class CommandHistory:
    def __init__(self) -> None:
        self.filepath = paths.HISTORY
        self.items = []  # [{'query': str, 'timestamp': float}]
        self.index = 0
        self.stash = None
        self.load()

    def load(self) -> None:
        """
        Load history from disk. Handles both new JSON format and legacy plain text.
        """
        try:
            if os.path.exists(self.filepath):
                with open(self.filepath, encoding="utf-8") as f:
                    content = f.read()

                if not content.strip():
                    self.items = []
                    self.reset_index()
                    return

                data = json.loads(content)
                if isinstance(data, list):
                    self.items = data

        except (OSError, json.JSONDecodeError) as e:
            logger.warning("Failed to load history: %s", e)
            self.items = []

        self.reset_index()

    def save(self) -> None:
        """Save the current list of items to the JSON file."""
        try:
            os.makedirs(os.path.dirname(self.filepath), exist_ok=True)
            with open(self.filepath, "w", encoding="utf-8") as f:
                json.dump(self.items, f, indent=0)
        except OSError as e:
            logger.warning("Failed to save history: %s", e)

    def add(self, query: str) -> None:
        """
        Add a command to history.
        - Updates timestamp if command already exists.
        - Enforces MAX_HISTORY_ITEMS limit (removes oldest).
        """
        query = query.strip()
        if not query:
            return

        current_time = time.time()

        # Remove existing entry for this query (to update its timestamp/position to "newest")
        self.items = [item for item in self.items if item["query"] != query]

        self.items.append({"query": query, "timestamp": current_time})

        # Enforce Limit: Remove oldest items (index 0) if over limit
        if len(self.items) > MAX_HISTORY_ITEMS:
            excess = len(self.items) - MAX_HISTORY_ITEMS
            self.items = self.items[excess:]

        self.save()
        self.reset_index()

    def prev(self, current_query: str = "") -> str | None:
        """Move back in time."""
        # Stash current input if we are starting navigation from the bottom
        if self.index == len(self.items):
            self.stash = current_query

        if self.index > 0:
            self.index -= 1
            return self.items[self.index]["query"]
        return None

    def next(self) -> str | None:
        """Move forward in time."""
        if self.index < len(self.items):
            self.index += 1
            if self.index == len(self.items):
                # We are back at the present, restore the stashed input
                return self.stash if self.stash is not None else ""
            return self.items[self.index]["query"]
        return None

    def reset_index(self) -> None:
        """Reset the navigation pointer to the end."""
        self.index = len(self.items)
        self.stash = None

    def current_match(self, text: str) -> bool:
        """Check if the current text matches the history item at the current index"""
        if 0 <= self.index < len(self.items):
            return self.items[self.index] == text
        return False

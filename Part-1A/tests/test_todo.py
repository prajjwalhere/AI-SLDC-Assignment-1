"""Deterministic tests for Smart Todo CLI — derived from specification acceptance criteria."""

import json
import os
import tempfile

import pytest

# Add src to path
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from todo_cli import TaskManager


@pytest.fixture
def manager(tmp_path):
    """Create a TaskManager with a temporary data file."""
    data_file = str(tmp_path / "test_todos.json")
    return TaskManager(data_file=data_file)


# --- CRUD: Create ---

class TestAddTask:
    def test_add_basic_task(self, manager):
        task = manager.add("Buy groceries")
        assert task["title"] == "Buy groceries"
        assert task["status"] == "pending"
        assert task["priority"] == "medium"
        assert task["tags"] == []
        assert task["id"] == 1

    def test_add_task_with_priority(self, manager):
        task = manager.add("Fix bug", priority="high")
        assert task["priority"] == "high"

    def test_add_task_with_tags(self, manager):
        task = manager.add("Deploy app", tags=["work", "urgent"])
        assert task["tags"] == ["work", "urgent"]

    def test_add_task_increments_id(self, manager):
        t1 = manager.add("Task 1")
        t2 = manager.add("Task 2")
        assert t2["id"] == t1["id"] + 1

    def test_add_task_empty_title_raises(self, manager):
        with pytest.raises(ValueError, match="title cannot be empty"):
            manager.add("")

    def test_add_task_whitespace_title_raises(self, manager):
        with pytest.raises(ValueError, match="title cannot be empty"):
            manager.add("   ")

    def test_add_task_invalid_priority_raises(self, manager):
        with pytest.raises(ValueError, match="Invalid priority"):
            manager.add("Task", priority="critical")

    def test_add_task_strips_whitespace_from_title(self, manager):
        task = manager.add("  Buy milk  ")
        assert task["title"] == "Buy milk"

    def test_add_task_empty_tag_raises(self, manager):
        with pytest.raises(ValueError, match="Tags cannot be empty"):
            manager.add("Task", tags=["valid", ""])

    def test_add_task_has_timestamps(self, manager):
        task = manager.add("Task")
        assert "created_at" in task
        assert "updated_at" in task


# --- CRUD: Read ---

class TestGetTask:
    def test_get_existing_task(self, manager):
        created = manager.add("Test task")
        fetched = manager.get(created["id"])
        assert fetched is not None
        assert fetched["title"] == "Test task"

    def test_get_nonexistent_task_returns_none(self, manager):
        assert manager.get(999) is None


# --- CRUD: Update ---

class TestUpdateTask:
    def test_update_title(self, manager):
        task = manager.add("Old title")
        updated = manager.update(task["id"], title="New title")
        assert updated["title"] == "New title"

    def test_update_priority(self, manager):
        task = manager.add("Task")
        updated = manager.update(task["id"], priority="high")
        assert updated["priority"] == "high"

    def test_update_tags(self, manager):
        task = manager.add("Task")
        updated = manager.update(task["id"], tags=["new-tag"])
        assert updated["tags"] == ["new-tag"]

    def test_update_nonexistent_raises(self, manager):
        with pytest.raises(ValueError, match="not found"):
            manager.update(999, title="X")

    def test_update_invalid_field_raises(self, manager):
        task = manager.add("Task")
        with pytest.raises(ValueError, match="Cannot update field"):
            manager.update(task["id"], status="done")

    def test_update_empty_title_raises(self, manager):
        task = manager.add("Task")
        with pytest.raises(ValueError, match="title cannot be empty"):
            manager.update(task["id"], title="")

    def test_update_refreshes_updated_at(self, manager):
        task = manager.add("Task")
        original_updated = task["updated_at"]
        import time
        time.sleep(0.01)
        updated = manager.update(task["id"], title="Changed")
        assert updated["updated_at"] >= original_updated


# --- CRUD: Delete ---

class TestDeleteTask:
    def test_delete_existing_task(self, manager):
        task = manager.add("To delete")
        assert manager.delete(task["id"]) is True
        assert manager.get(task["id"]) is None

    def test_delete_nonexistent_raises(self, manager):
        with pytest.raises(ValueError, match="not found"):
            manager.delete(999)

    def test_delete_does_not_affect_other_tasks(self, manager):
        t1 = manager.add("Keep this")
        t2 = manager.add("Delete this")
        manager.delete(t2["id"])
        assert manager.get(t1["id"]) is not None
        assert len(manager.list_tasks()) == 1


# --- Status Transitions ---

class TestStatusTransitions:
    def test_pending_to_in_progress(self, manager):
        task = manager.add("Task")
        updated = manager.transition(task["id"], "in_progress")
        assert updated["status"] == "in_progress"

    def test_in_progress_to_done(self, manager):
        task = manager.add("Task")
        manager.transition(task["id"], "in_progress")
        updated = manager.transition(task["id"], "done")
        assert updated["status"] == "done"

    def test_pending_to_done_blocked(self, manager):
        task = manager.add("Task")
        with pytest.raises(ValueError, match="Invalid transition"):
            manager.transition(task["id"], "done")

    def test_done_to_in_progress_blocked(self, manager):
        task = manager.add("Task")
        manager.transition(task["id"], "in_progress")
        manager.transition(task["id"], "done")
        with pytest.raises(ValueError, match="Invalid transition"):
            manager.transition(task["id"], "in_progress")

    def test_done_is_terminal(self, manager):
        task = manager.add("Task")
        manager.transition(task["id"], "in_progress")
        manager.transition(task["id"], "done")
        with pytest.raises(ValueError, match="terminal state"):
            manager.transition(task["id"], "done")

    def test_transition_nonexistent_raises(self, manager):
        with pytest.raises(ValueError, match="not found"):
            manager.transition(999, "in_progress")


# --- Filtering & Sorting ---

class TestListAndFilter:
    def test_list_all_tasks(self, manager):
        manager.add("Task 1")
        manager.add("Task 2")
        assert len(manager.list_tasks()) == 2

    def test_filter_by_tag(self, manager):
        manager.add("Work task", tags=["work"])
        manager.add("Personal task", tags=["personal"])
        manager.add("Both", tags=["work", "personal"])
        result = manager.list_tasks(tag="work")
        assert len(result) == 2
        assert all("work" in t["tags"] for t in result)

    def test_filter_by_status(self, manager):
        t1 = manager.add("Pending task")
        t2 = manager.add("Started task")
        manager.transition(t2["id"], "in_progress")
        result = manager.list_tasks(status="in_progress")
        assert len(result) == 1
        assert result[0]["id"] == t2["id"]

    def test_sort_by_priority(self, manager):
        manager.add("Low task", priority="low")
        manager.add("High task", priority="high")
        manager.add("Medium task", priority="medium")
        result = manager.list_tasks(sort_by_priority=True)
        priorities = [t["priority"] for t in result]
        assert priorities == ["high", "medium", "low"]

    def test_filter_invalid_status_raises(self, manager):
        with pytest.raises(ValueError, match="Invalid status filter"):
            manager.list_tasks(status="cancelled")

    def test_combined_filter_and_sort(self, manager):
        manager.add("Low work", priority="low", tags=["work"])
        manager.add("High work", priority="high", tags=["work"])
        manager.add("High personal", priority="high", tags=["personal"])
        result = manager.list_tasks(tag="work", sort_by_priority=True)
        assert len(result) == 2
        assert result[0]["priority"] == "high"


# --- JSON Persistence ---

class TestPersistence:
    def test_data_persists_across_instances(self, tmp_path):
        data_file = str(tmp_path / "persist_test.json")
        m1 = TaskManager(data_file=data_file)
        m1.add("Persistent task")

        m2 = TaskManager(data_file=data_file)
        assert len(m2.list_tasks()) == 1
        assert m2.list_tasks()[0]["title"] == "Persistent task"

    def test_json_file_is_valid_after_operations(self, tmp_path):
        data_file = str(tmp_path / "valid_json.json")
        m = TaskManager(data_file=data_file)
        m.add("Task 1")
        m.add("Task 2")
        m.delete(1)

        with open(data_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        assert isinstance(data, list)
        assert len(data) == 1

    def test_empty_file_starts_fresh(self, tmp_path):
        data_file = str(tmp_path / "empty.json")
        m = TaskManager(data_file=data_file)
        assert m.list_tasks() == []


# --- ID Immutability ---

class TestIdImmutability:
    def test_id_stable_after_update(self, manager):
        task = manager.add("Task")
        original_id = task["id"]
        updated = manager.update(task["id"], title="New Title")
        assert updated["id"] == original_id

    def test_id_stable_after_transition(self, manager):
        task = manager.add("Task")
        original_id = task["id"]
        transitioned = manager.transition(task["id"], "in_progress")
        assert transitioned["id"] == original_id

    def test_ids_unique_after_deletion(self, manager):
        t1 = manager.add("Task 1")
        t2 = manager.add("Task 2")
        manager.delete(t1["id"])
        t3 = manager.add("Task 3")
        assert t3["id"] != t1["id"]
        assert t3["id"] != t2["id"]

"""Smart Todo & Task CLI — CRUD, tag filtering, JSON persistence, priority sorting, status transitions."""

import json
import argparse
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional


DATA_FILE = "todos.json"

VALID_PRIORITIES = ("high", "medium", "low")
VALID_STATUSES = ("pending", "in_progress", "done")
VALID_TRANSITIONS = {
    "pending": ["in_progress"],
    "in_progress": ["done"],
    "done": [],
}


class TaskManager:
    """Manages tasks with CRUD operations, filtering, and JSON persistence."""

    def __init__(self, data_file: str = DATA_FILE):
        self.data_file = Path(data_file)
        self.tasks: list[dict] = []
        self._load()

    def _load(self) -> None:
        if self.data_file.exists():
            with open(self.data_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                if not isinstance(data, list):
                    raise ValueError("Corrupted data file: root must be a JSON array")
                self.tasks = data

    def _save(self) -> None:
        self.data_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.data_file, "w", encoding="utf-8") as f:
            json.dump(self.tasks, f, indent=2, ensure_ascii=False)

    def _next_id(self) -> int:
        if not self.tasks:
            return 1
        return max(t["id"] for t in self.tasks) + 1

    def add(
        self,
        title: str,
        priority: str = "medium",
        tags: Optional[list[str]] = None,
    ) -> dict:
        if not title or not title.strip():
            raise ValueError("Task title cannot be empty")
        if priority not in VALID_PRIORITIES:
            raise ValueError(f"Invalid priority '{priority}'. Must be one of: {', '.join(VALID_PRIORITIES)}")
        if tags is not None:
            for tag in tags:
                if not tag or not tag.strip():
                    raise ValueError("Tags cannot be empty strings")

        now = datetime.now().isoformat()
        task = {
            "id": self._next_id(),
            "title": title.strip(),
            "priority": priority,
            "status": "pending",
            "tags": [t.strip() for t in (tags or [])],
            "created_at": now,
            "updated_at": now,
        }
        self.tasks.append(task)
        self._save()
        return task

    def get(self, task_id: int) -> Optional[dict]:
        for task in self.tasks:
            if task["id"] == task_id:
                return task
        return None

    def update(self, task_id: int, **kwargs: object) -> dict:
        task = self.get(task_id)
        if task is None:
            raise ValueError(f"Task {task_id} not found")

        allowed_fields = {"title", "priority", "tags"}
        for key, value in kwargs.items():
            if key not in allowed_fields:
                raise ValueError(f"Cannot update field: {key}")
            if key == "title" and (not value or not str(value).strip()):
                raise ValueError("Task title cannot be empty")
            if key == "priority" and value not in VALID_PRIORITIES:
                raise ValueError(f"Invalid priority '{value}'. Must be one of: {', '.join(VALID_PRIORITIES)}")
            task[key] = value

        task["updated_at"] = datetime.now().isoformat()
        self._save()
        return task

    def transition(self, task_id: int, new_status: str) -> dict:
        task = self.get(task_id)
        if task is None:
            raise ValueError(f"Task {task_id} not found")

        current = task["status"]
        allowed = VALID_TRANSITIONS.get(current, [])
        if new_status not in allowed:
            raise ValueError(
                f"Invalid transition: {current} -> {new_status}. "
                f"Allowed from '{current}': {allowed if allowed else 'none (terminal state)'}"
            )

        task["status"] = new_status
        task["updated_at"] = datetime.now().isoformat()
        self._save()
        return task

    def delete(self, task_id: int) -> bool:
        task = self.get(task_id)
        if task is None:
            raise ValueError(f"Task {task_id} not found")
        self.tasks = [t for t in self.tasks if t["id"] != task_id]
        self._save()
        return True

    def list_tasks(
        self,
        tag: Optional[str] = None,
        status: Optional[str] = None,
        sort_by_priority: bool = False,
    ) -> list[dict]:
        result = self.tasks[:]

        if tag:
            result = [t for t in result if tag in t.get("tags", [])]

        if status:
            if status not in VALID_STATUSES:
                raise ValueError(f"Invalid status filter '{status}'. Must be one of: {', '.join(VALID_STATUSES)}")
            result = [t for t in result if t["status"] == status]

        if sort_by_priority:
            priority_order = {"high": 0, "medium": 1, "low": 2}
            result.sort(key=lambda t: priority_order.get(t["priority"], 1))

        return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Smart Todo & Task CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    add_p = subparsers.add_parser("add", help="Add a new task")
    add_p.add_argument("title", help="Task title")
    add_p.add_argument("-p", "--priority", choices=VALID_PRIORITIES, default="medium")
    add_p.add_argument("-t", "--tags", nargs="*", default=[])

    list_p = subparsers.add_parser("list", help="List tasks")
    list_p.add_argument("--tag", help="Filter by tag")
    list_p.add_argument("--status", choices=VALID_STATUSES)
    list_p.add_argument("--sort-priority", action="store_true")

    get_p = subparsers.add_parser("get", help="Get a specific task")
    get_p.add_argument("id", type=int)

    upd_p = subparsers.add_parser("update", help="Update a task")
    upd_p.add_argument("id", type=int)
    upd_p.add_argument("--title")
    upd_p.add_argument("--priority", choices=VALID_PRIORITIES)
    upd_p.add_argument("--tags", nargs="*")

    tr_p = subparsers.add_parser("transition", help="Change task status")
    tr_p.add_argument("id", type=int)
    tr_p.add_argument("status", choices=["in_progress", "done"])

    del_p = subparsers.add_parser("delete", help="Delete a task")
    del_p.add_argument("id", type=int)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    manager = TaskManager()

    try:
        if args.command == "add":
            task = manager.add(args.title, args.priority, args.tags)
            print(json.dumps(task, indent=2))
        elif args.command == "list":
            tasks = manager.list_tasks(
                tag=args.tag,
                status=args.status,
                sort_by_priority=args.sort_priority,
            )
            print(json.dumps(tasks, indent=2))
        elif args.command == "get":
            task = manager.get(args.id)
            if task:
                print(json.dumps(task, indent=2))
            else:
                print(f"Task {args.id} not found", file=sys.stderr)
                sys.exit(1)
        elif args.command == "update":
            kwargs = {}
            if args.title:
                kwargs["title"] = args.title
            if args.priority:
                kwargs["priority"] = args.priority
            if args.tags is not None:
                kwargs["tags"] = args.tags
            task = manager.update(args.id, **kwargs)
            print(json.dumps(task, indent=2))
        elif args.command == "transition":
            task = manager.transition(args.id, args.status)
            print(json.dumps(task, indent=2))
        elif args.command == "delete":
            manager.delete(args.id)
            print(f"Task {args.id} deleted")
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

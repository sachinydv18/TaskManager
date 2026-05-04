import json
import os
from datetime import datetime
import uuid

FILE_NAME = "tasks.json"


# -------------------------------
# Task Class
# -------------------------------
class Task:
    def __init__(self, id, title, priority, due_date, tags, completed=False):
        self.id = id
        self.title = title
        self.priority = priority
        self.due_date = due_date
        
        # Ensure tags is always a list of strings
        if isinstance(tags, list):
            self.tags = [str(t).strip() for t in tags if str(t).strip()]
        else:
            self.tags = []
            
        # Ensure completed is always a boolean
        self.completed = bool(completed)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "priority": self.priority,
            "due_date": self.due_date,
            "tags": self.tags,
            "completed": self.completed
        }


# -------------------------------
# Task Manager Class
# -------------------------------
class TaskManager:
    def __init__(self):
        self.tasks = []
        self.load_tasks()

    # -------- LOAD --------
    def load_tasks(self):
        if not os.path.exists(FILE_NAME):
            return

        try:
            with open(FILE_NAME, "r") as file:
                data = json.load(file)

                if isinstance(data, list):
                    self.tasks = []
                    for task_data in data:
                        # Safe loading with defaults to prevent crashes on malformed/corrupted JSON
                        task = Task(
                            id=task_data.get("id", str(uuid.uuid4())),
                            title=task_data.get("title", "Untitled"),
                            priority=task_data.get("priority", "Medium"),
                            due_date=task_data.get("due_date", ""),
                            tags=task_data.get("tags", []),
                            completed=task_data.get("completed", False)
                        )
                        self.tasks.append(task)
                else:
                    print("⚠ Invalid JSON structure. Resetting tasks.")
                    self.tasks = []
        except json.JSONDecodeError:
            print("⚠ Corrupted JSON file. Resetting tasks.")
            self.tasks = []
        except Exception as e:
            print(f"⚠ Error loading file: {e}")
            self.tasks = []

    # -------- SAVE --------
    def save_tasks(self):
        with open(FILE_NAME, "w") as file:
            json.dump([task.to_dict() for task in self.tasks], file, indent=4)

    # -------- ADD --------
    def add_task(self):
        title = input("Enter title: ").strip()
        if not title:
            print("❌ Title cannot be empty!")
            return

        priority = input("Enter priority (Low/Medium/High): ").strip().capitalize()
        if priority not in ["Low", "Medium", "High"]:
            print("❌ Invalid priority! Please use Low, Medium, or High.")
            return

        due_date = input("Enter due date (YYYY-MM-DD): ").strip()
        try:
            datetime.strptime(due_date, "%Y-%m-%d")
        except ValueError:
            print("❌ Invalid date format! Please use YYYY-MM-DD.")
            return

        tags_input = input("Enter tags (comma separated, or leave blank): ").strip()
        tags = [t.strip() for t in tags_input.split(",") if t.strip()] if tags_input else []

        task = Task(
            id=str(uuid.uuid4()),
            title=title,
            priority=priority,
            due_date=due_date,
            tags=tags
        )
        self.tasks.append(task)
        self.save_tasks()
        print("✅ Task added successfully!")

    # -------- VIEW --------
    def view_tasks(self):
        print("\n===== TASK LIST =====")
        if not self.tasks:
            print("⚠ No tasks available.\n")
            return

        for i, task in enumerate(self.tasks, start=1):
            status = "✅ Completed" if task.completed else "⬜ Pending"
            tags_str = ", ".join(task.tags) if task.tags else "None"
            
            print(f"Task #{i}")
            print(f"  ID        : {task.id}")
            print(f"  Title     : {task.title}")
            print(f"  Priority  : {task.priority}")
            print(f"  Due Date  : {task.due_date}")
            print(f"  Tags      : {tags_str}")
            print(f"  Status    : {status}")
            print("---------------------------")

    # -------- DELETE --------
    def delete_task(self):
        task_id = input("Enter task ID to delete: ").strip()
        for i, task in enumerate(self.tasks):
            if task.id == task_id:
                self.tasks.pop(i)
                self.save_tasks()
                print("🗑 Task deleted successfully!")
                return
        print("❌ Task not found!")

    # -------- COMPLETE --------
    def mark_complete(self):
        task_id = input("Enter task ID to mark complete: ").strip()
        for task in self.tasks:
            if task.id == task_id:
                if task.completed:
                    print("ℹ Task is already completed.")
                else:
                    task.completed = True
                    self.save_tasks()
                    print("✔ Task marked complete!")
                return
        print("❌ Task not found!")

    # -------- SEARCH --------
    def search_tasks(self):
        keyword = input("Enter keyword to search: ").strip().lower()
        if not keyword:
            print("❌ Keyword cannot be empty!")
            return

        results = [
            t for t in self.tasks
            if keyword in t.title.lower() or keyword in " ".join(t.tags).lower()
        ]

        if not results:
            print("🔍 No matching tasks found.")
            return

        print(f"\n🔍 Found {len(results)} matching task(s):")
        for i, task in enumerate(results, start=1):
            print(f"  {i}. {task.title} (ID: {task.id}) - Priority: {task.priority}")

    # -------- FILTER --------
    def filter_tasks(self):
        print("\nFilter Options:")
        print("1. By Priority")
        print("2. By Tag")
        choice = input("Choose option (1/2): ").strip()

        if choice == "1":
            priority = input("Enter priority (Low/Medium/High): ").strip().capitalize()
            results = [t for t in self.tasks if t.priority == priority]
        elif choice == "2":
            tag = input("Enter tag: ").strip().lower()
            results = [t for t in self.tasks if tag in [tg.lower() for tg in t.tags]]
        else:
            print("❌ Invalid choice!")
            return

        if not results:
            print("🔍 No tasks match your filter.")
            return

        print(f"\n📋 Found {len(results)} task(s):")
        for task in results:
            print(f"  • {task.title} (ID: {task.id}) - {task.priority} - Due: {task.due_date}")


# -------------------------------
# CLI Interface
# -------------------------------
class CLI:
    def __init__(self):
        self.manager = TaskManager()

    def run(self):
        while True:
            print("\n==== TASK MANAGER ====")
            print("1. Add Task")
            print("2. View Tasks")
            print("3. Delete Task")
            print("4. Mark Complete")
            print("5. Search Tasks")
            print("6. Filter Tasks")
            print("7. Exit")

            choice = input("\nEnter choice: ").strip()

            if choice == "1":
                self.manager.add_task()
            elif choice == "2":
                self.manager.view_tasks()
            elif choice == "3":
                self.manager.delete_task()
            elif choice == "4":
                self.manager.mark_complete()
            elif choice == "5":
                self.manager.search_tasks()
            elif choice == "6":
                self.manager.filter_tasks()
            elif choice == "7":
                print("👋 Goodbye!")
                break
            else:
                print("❌ Invalid choice! Please enter a number between 1 and 7.")

            # Pause to let the user read output before clearing/continuing
            input("\nPress Enter to continue...")


# -------------------------------
# MAIN
# -------------------------------
if __name__ == "__main__":
    CLI().run()
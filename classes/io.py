import csv
import json


from classes.item import Item

class IO_CSV:
    def _read_csv(path, fieldnames) -> tuple[bool, list[Item]]:
        """Read CSV file and return success/error boolean and the list of `Item`s."""
        # Read the CSV file
        try:
            with open(path, "r", newline='') as f:
                reader = csv.DictReader(f, fieldnames=fieldnames)
                reader.__next__()  # Skip header
                lst = [Item(**row) for row in reader]
            return True, lst
        
        except (FileNotFoundError, PermissionError, OSError) as e:
            print(f"Error reading {path}: {e}")
            return False, []
    
    def _write_csv(path, fieldnames, data: list[Item]) -> tuple[bool, None]:
        try:
            with open(path, "w", newline='') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows([item.model_dump() for item in data])
        except PermissionError:
            print(f"Permission to write is required for {path}.")
            return False, None
        except IsADirectoryError:
            print(f"Not a file: {path}.")
            return False, None
        except OSError as e:
            print(f"OS Error occurred: {e}")
            return False, None
        else:
            print(f"Successfully exported data to {path}")
            return True, None

class IO_JSON:
    def _read_json(path) -> tuple[bool, list[Item]]:
        """Read JSON file. Accept either a list of item dicts or an object with 'items' key."""
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, dict) and "items" in data:
                raw = data["items"]
            elif isinstance(data, list):
                raw = data
            else:
                print(f"Unexpected JSON structure in {path}. Expected list or {{'items': [...]}}.")
                return False, []
            lst = [Item(**row) for row in raw]
            return True, lst
        except (FileNotFoundError, PermissionError, OSError, json.JSONDecodeError) as e:
            print(f"Error reading {path}: {e}")
            return False, []

    def _write_json(path, data: list[Item]) -> tuple[bool, None]:
        try:
            payload = [item.model_dump() for item in data]
            with open(path, "w", encoding="utf-8") as f:
                json.dump(payload, f, ensure_ascii=False, indent=2)
        except PermissionError:
            print(f"Permission to write is required for {path}.")
            return False, None
        except IsADirectoryError:
            print(f"Not a file: {path}.")
            return False, None
        except OSError as e:
            print(f"OS Error occurred: {e}")
            return False, None
        else:
            print(f"Successfully exported data to {path}")
            return True, None

class IO_SQL:
    pass

import re
from pathlib import Path
from typing import List, Dict, Any, Optional

class PreseedParser:
    """
    A parser for Debian Preseed configuration and template files.
    Extracted data is suitable for building dynamic UI components like dropdowns.
    """

    # Matches: d-i owner/question type value (handles commented out template lines too)
    DI_PATTERN = re.compile(r"^(?:#\s*)?d-i\s+([\w\-/._]+)\s+(\w+)\s*(.*)$")
    CHOICES_PATTERN = re.compile(r"^(?:#\s*)?Possible choices:\s*(.*)$")
    DESCRIPTION_START = "### Description:"

    def __init__(self):
        self.results = []

    def _clean_comment(self, line: str) -> str:
        """Removes leading # and whitespace."""
        return line.lstrip("#").strip()

    def parse(self, file_path: str) -> List[Dict[str, Any]]:
        """Parses a preseed or template file into a list of structured dictionaries."""
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        parsed_items = []
        current_item: Dict[str, Any] = self._reset_buffer()
        
        with open(path, 'r', encoding='utf-8') as f:
            for line in f:
                clean_line = line.strip()
                
                # 1. Detect Description Start
                if clean_line.startswith(self.DESCRIPTION_START):
                    # If we found a new description but have a pending key, save it first
                    if current_item["key"]:
                        parsed_items.append(current_item)
                        current_item = self._reset_buffer()
                    
                    desc_text = clean_line.replace(self.DESCRIPTION_START, "").strip()
                    current_item["description"] = [desc_text] if desc_text else []
                    continue

                # 2. Detect Choices
                choice_match = self.CHOICES_PATTERN.match(clean_line)
                if choice_match:
                    raw_choices = choice_match.group(1).strip()
                    # Split by comma if it's not a variable like ${CHOICES}
                    if raw_choices and not raw_choices.startswith("${"):
                        current_item["choices"] = [c.strip() for c in raw_choices.split(",")]
                    else:
                        current_item["choices"] = raw_choices
                    continue

                # 3. Detect d-i key/type/value
                di_match = self.DI_PATTERN.match(clean_line)
                if di_match:
                    current_item["key"] = di_match.group(1)
                    current_item["type"] = di_match.group(2)
                    current_item["value"] = di_match.group(3).strip()
                    continue

                # 4. Accumulate generic comments as part of description
                if clean_line.startswith("#") and current_item["description"] is not None:
                    # Stop accumulating if we hit another header or empty line logic
                    content = self._clean_comment(clean_line)
                    if content and not content.startswith("---") and "###" not in line:
                        current_item["description"].append(content)

            # Append the final item if it exists
            if current_item["key"]:
                parsed_items.append(current_item)

        return self._post_process(parsed_items)

    def _reset_buffer(self) -> Dict[str, Any]:
        return {
            "key": None,
            "type": None,
            "value": None,
            "description": None,
            "choices": []
        }

    def _post_process(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Cleans up lists into strings and prepares final objects."""
        for item in items:
            if isinstance(item["description"], list):
                item["description"] = " ".join(item["description"]).strip()
            
            # Logic for boolean types
            if item["type"] == "boolean":
                item["choices"] = ["true", "false"]
        return items

if __name__ == "__main__":
    # Example Usage
    parser = PreseedParser()
    try:
        # Test with the full template file
        data = parser.parse("../../seedfiles/bookworm/amd64-main-full.txt")
        
        print(f"Parsed {len(data)} items.")
        # Show a sample item that would be a dropdown (select type)
        dropdowns = [i for i in data if i["type"] == "select"]
        if dropdowns:
            sample = dropdowns[0]
            print(f"\nExample Dropdown Item:")
            print(f"Key: {sample['key']}\nLabel: {sample['description']}\nChoices: {sample['choices']}")
    except Exception as e:
        print(f"Error: {e}")
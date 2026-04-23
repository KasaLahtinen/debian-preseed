
import sys
import re
from pathlib import Path
from typing import List, Dict, Any, Optional
import json # Import for JSON output

class PreseedParser:
    """
    A parser for Debian Preseed configuration and template files.
    Extracted data is suitable for building dynamic UI components like dropdowns.
    """

    # Matches: d-i owner/question type value (handles commented out template lines too)
#    DI_PATTERN = re.compile(r"^(?:#\s*)?d-i\s+([\w\-/._]+)\s+(\w+)\s*(.*)$")
    DI_PATTERN = re.compile(r"^d-i\s+([\w\-/._]+)\s+(\w+)\s*(.*)$")
    CHOICES_PATTERN = re.compile(r"^(?:#\s*)?Possible choices:\s*(.*)$")
    DESCRIPTION_START = "### Description:"

    def __init__(self):
        self.results = []
        self.current_group = "General"

    def _clean_comment(self, line: str) -> str:
        """Removes leading # and whitespace."""
        return line.lstrip("# ").strip()

    def parse(self, file_path: str) -> List[Dict[str, Any]]:
        """Parses a preseed or template file into a list of structured dictionaries."""
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        parsed_items = []
        self.current_group = "General"
        current_item: Dict[str, Any] = self._reset_buffer()
        
        with open(path, 'r', encoding='utf-8') as f:
            for line in f:
                clean_line = line.strip()

                # Ignore empty lines or lines that are just a divider of #
                if not clean_line or re.match(r"^#+$", clean_line):
                    continue

                # Detect Udeb or Category headers (e.g. #### anna.udeb or ### Localization)
                # We check these before Description to avoid misidentifying the description start
                if (clean_line.startswith("####") or clean_line.startswith("###")) and not clean_line.startswith(self.DESCRIPTION_START):
                    header_text = clean_line.lstrip("# ").strip()
                    if header_text:
                        self.current_group = header_text
                    continue
                
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
            "choices": [],
            "group": self.current_group
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

    def to_json_schema(self, parsed_data: List[Dict[str, Any]], title: str = "Debian Preseed Configuration", description: str = "Schema for Debian Preseed configuration options") -> Dict[str, Any]:
        """
        Converts parsed preseed data into a JSON Schema.
        """
        schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "title": title,
            "description": description,
            "type": "object",
            "properties": {},
            "additionalProperties": False # By default, disallow properties not defined in the schema
        }

        for item in parsed_data:
            key = item["key"]
            if not key:
                continue

            prop_schema: Dict[str, Any] = {
                "description": item["description"] if item["description"] else f"Configuration for {key}",
                "group": item.get("group", "General") # Custom metadata for UI grouping
            }
            if item.get("group"):
                prop_schema["description"] = f"[{item['group']}] " + prop_schema["description"]

            # Map preseed types to JSON schema types and add constraints
            if item["type"] == "string":
                prop_schema["type"] = "string"
                # Add format for password fields based on value placeholder
                if item["value"] == "<password>":
                    prop_schema["format"] = "password"
            elif item["type"] == "boolean":
                prop_schema["type"] = "boolean"
                # Convert string choices to actual boolean literals for JSON schema enum
                if item["choices"] == ["true", "false"]:
                    prop_schema["enum"] = [True, False]
            elif item["type"] == "select":
                prop_schema["type"] = "string" # Select choices are usually strings
                if item["choices"] and not isinstance(item["choices"], str) and item["choices"] != ["<choice>"]:
                    prop_schema["enum"] = item["choices"]
                elif isinstance(item["choices"], str) and item["choices"].startswith("${"):
                    prop_schema["description"] += f" (Dynamic choices: {item['choices']})"
            elif item["type"] == "multiselect":
                prop_schema["type"] = "array"
                prop_schema["uniqueItems"] = True
                if item["choices"] and not isinstance(item["choices"], str) and item["choices"] != ["<choice(s)>"]:
                    prop_schema["items"] = {"type": "string", "enum": item["choices"]}
                elif isinstance(item["choices"], str) and item["choices"].startswith("${"):
                    prop_schema["description"] += f" (Dynamic choices: {item['choices']})"
                    prop_schema["items"] = {"type": "string"} # Indicate array of strings, but enum is dynamic
                else:
                    prop_schema["items"] = {"type": "string"} # Default to array of strings
            elif item["type"] in ["text", "note", "password"]: # Treat text and note as strings for schema purposes
                prop_schema["type"] = "string"
                if item["type"] == "password":
                    prop_schema["format"] = "password"
            else:
                # Default to string for unknown or generic types
                prop_schema["type"] = "string"
            
            # Add default value if present and not a placeholder
            if item["value"] and item["value"] not in ["<string>", "<choice>", "<choice(s)>", "<password>"]:
                if prop_schema["type"] == "boolean":
                    prop_schema["default"] = (item["value"].lower() == "true")
                elif prop_schema["type"] == "array":
                    # For multiselect, default value might be a comma-separated string
                    # or a single value. This needs careful handling.
                    if item["value"]:
                        default_values = [v.strip() for v in item["value"].split(',')]
                        prop_schema["default"] = default_values
                else:
                    prop_schema["default"] = item["value"]

            schema["properties"][key] = prop_schema
        
        return schema

def main():
    import argparse
    import sys

    parser = argparse.ArgumentParser(description="Parse Debian Preseed and template files.")
    parser.add_argument("input", help="Path to the preseed or template file")
    parser.add_argument("--schema", action="store_true", help="Output as JSON Schema instead of raw data")
    
    args = parser.parse_args()
    
    preseed_parser = PreseedParser()
    try:
        data = preseed_parser.parse(args.input)
        
        if args.schema:
            output = preseed_parser.to_json_schema(data, title=Path(args.input).name)
        else:
            output = data
            
        print(json.dumps(output, indent=2))
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    # If running directly, default to the test logic provided earlier
    if len(sys.argv) > 1:
        main()
    else:
        # Default test run
        p = PreseedParser()
        try:
            data = p.parse("../../seedfiles/example-preseed.txt")
            print(f"Parsed {len(data)} items from example-preseed.txt")
            # Show one item as a sample
            if data:
                print("\nSample Item (JSON):")
                print(json.dumps(data[0], indent=2))
        except Exception as e:
            print(f"Error: {e}")
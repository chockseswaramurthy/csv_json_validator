import csv
import json
import sys
from typing import Tuple
import ast

def preprocess_json_string(json_str: str) -> str:
    """
    Preprocess a string that looks like a Python list/array but uses single quotes
    """
    try:
        # Remove any surrounding single quotes if they exist
        json_str = json_str.strip()
        if json_str.startswith("'") and json_str.endswith("'"):
            json_str = json_str[1:-1]

        # Try to evaluate as Python literal
        python_obj = ast.literal_eval(json_str)
        return json.dumps(python_obj)
    except (ValueError, SyntaxError) as e:
        raise ValueError(f"Failed to process string: {str(e)}")

def is_valid_json(json_str: str) -> Tuple[bool, str]:
    """
    Check if a string is valid JSON.
    Returns a tuple of (is_valid, error_message)
    """
    if not json_str:
        return False, "Empty string"

    try:
        processed_str = preprocess_json_string(json_str)
        json.loads(processed_str)
        return True, ""
    except ValueError as e:
        return False, f"Preprocessing error: {str(e)}"
    except json.JSONDecodeError as e:
        return False, f"JSON decode error: {str(e)}"

def validate_csv_json_field(csv_file: str, field_name: str) -> None:
    """
    Validate JSON in a specific field of a CSV file
    """
    good_rows = 0
    bad_rows = 0
    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            # Use custom dialect to handle single-quote delimited CSV
            csv.register_dialect('custom',
                                 delimiter=',',
                                 quotechar="'",
                                 doublequote=True,
                                 skipinitialspace=True)

            reader = csv.DictReader(f, dialect='custom')

            if field_name not in reader.fieldnames:
                print(f"Error: Field '{field_name}' not found in CSV. Available fields: {', '.join(reader.fieldnames)}")
                return

            for line_num, row in enumerate(reader, start=2):
                json_str = row[field_name]

                is_valid, error = is_valid_json(json_str)

                if not is_valid:
                    bad_rows += 1
                    print(f"Line {line_num}: Invalid JSON")
                    print(f"Content: {json_str}")
                    print(f"Error: {error}")
                    print("-" * 50)
                else:
                    good_rows += 1

        print(f"Validation complete. {good_rows} valid rows, {bad_rows} invalid rows")
    except FileNotFoundError:
        print(f"Error: File '{csv_file}' not found")
    except Exception as e:
        print(f"Error processing file: {str(e)}")

def main():
    if len(sys.argv) != 3:
        print("Usage: python script.py <csv_file> <field_name>")
        sys.exit(1)

    csv_file = sys.argv[1]
    field_name = sys.argv[2]

    validate_csv_json_field(csv_file, field_name)

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
CSV to HTML Table Converter

This script converts data from CSV to HTML table format.
It reads CSV data, processes it, and replaces a table with class 'summary-table' in an HTML file.
"""

import csv
import argparse
import sys
from pathlib import Path
from typing import List, Dict


def read_csv_data(csv_file: str) -> List[Dict[str, str]]:
    """Read CSV file and return list of dictionaries."""
    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            data = list(reader)
        return data
    except FileNotFoundError:
        print(f"Error: CSV file '{csv_file}' not found.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error reading CSV file: {e}", file=sys.stderr)
        sys.exit(1)


def process_data(data: List[Dict[str, str]], rub_rate: float) -> List[Dict[str, str]]:
    """Process CSV data, extract required columns, and sort by model_permaslug."""
    processed = []

    for row in data:
        # Extract required fields
        model = row.get('model_permaslug', '')
        cost_total = row.get('cost_total', '0')
        generation_time_ms = row.get('generation_time_ms', '0')

        # Skip empty rows
        if not model:
            continue

        # Convert cost to float
        try:
            cost_usd = float(cost_total) if cost_total else 0.0
        except ValueError:
            cost_usd = 0.0

        # Convert generation time from ms to seconds
        try:
            time_sec = float(generation_time_ms) / 1000.0 if generation_time_ms else 0.0
        except ValueError:
            time_sec = 0.0

        # Calculate RUB price
        cost_rub = cost_usd * rub_rate

        processed.append({
            'model': model,
            'cost_usd': cost_usd,
            'cost_rub': cost_rub,
            'time_sec': time_sec
        })

    # Sort by model_permaslug alphabetically
    processed.sort(key=lambda x: x['model'])

    return processed


def generate_html_table(data: List[Dict[str, str]]) -> str:
    """Generate HTML table from processed data."""
    html_lines = ['<table class="summary-table">']
    html_lines.append('                <thead>')
    html_lines.append('                    <tr>')
    html_lines.append('                        <th>Модель</th>')
    html_lines.append('                        <th>Цена, USD</th>')
    html_lines.append('                        <th>Цена, рубли РФ</th>')
    html_lines.append('                        <th>Время генерации, сек</th>')
    html_lines.append('                        <th>Субъективная оценка</th>')
    html_lines.append('                    </tr>')
    html_lines.append('                </thead>')
    html_lines.append('                <tbody>')

    for row in data:
        html_lines.append('                    <tr>')
        html_lines.append(f'                        <td>{row["model"]}</td>')
        html_lines.append(f'                        <td>${row["cost_usd"]:.6f}</td>')
        html_lines.append(f'                        <td>{row["cost_rub"]:.2f}₽</td>')
        html_lines.append(f'                        <td>{row["time_sec"]:.2f}</td>')
        html_lines.append('                        <td></td>')
        html_lines.append('                    </tr>')

    html_lines.append('                </tbody>')
    html_lines.append('            </table>')

    return '\n'.join(html_lines)


def replace_table_in_html(html_file: str, new_table: str) -> None:
    """Replace the .summary-table in HTML file with new table."""
    try:
        with open(html_file, 'r', encoding='utf-8') as f:
            html_content = f.read()
    except FileNotFoundError:
        print(f"Error: HTML file '{html_file}' not found.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error reading HTML file: {e}", file=sys.stderr)
        sys.exit(1)

    # Find the table with class="summary-table" and replace it
    # We need to find the opening <table class="summary-table"> and closing </table>
    import re

    # Pattern to match the entire summary-table from <table to </table>
    pattern = r'<table\s+class="summary-table"[^>]*>.*?</table>'

    # Check if pattern exists
    if not re.search(pattern, html_content, re.DOTALL | re.IGNORECASE):
        print(f"Error: No table with class 'summary-table' found in '{html_file}'.", file=sys.stderr)
        sys.exit(1)

    # Replace the table
    new_html_content = re.sub(pattern, new_table, html_content, flags=re.DOTALL | re.IGNORECASE)

    # Write back to file
    try:
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(new_html_content)
        print(f"Successfully updated table in '{html_file}'")
    except Exception as e:
        print(f"Error writing HTML file: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    """Main function to parse arguments and run the conversion."""
    parser = argparse.ArgumentParser(
        description='Convert CSV data to HTML table and replace in HTML file'
    )
    parser.add_argument(
        'csv_file',
        help='Path to CSV file'
    )
    parser.add_argument(
        '--rub-rate',
        type=float,
        default=76.0,
        help='RUB to USD exchange rate (default: 76.0)'
    )
    parser.add_argument(
        'html_output',
        help='Path to HTML file where table should be replaced'
    )

    args = parser.parse_args()

    # Read CSV data
    csv_data = read_csv_data(args.csv_file)

    # Process data
    processed_data = process_data(csv_data, args.rub_rate)

    # Generate HTML table
    html_table = generate_html_table(processed_data)

    # Replace table in HTML file
    replace_table_in_html(args.html_output, html_table)


if __name__ == '__main__':
    main()

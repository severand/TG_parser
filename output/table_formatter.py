"""ASCII table formatter for console output.

Creates beautiful ASCII tables for displaying data in terminal.
"""

from typing import List, Dict, Any, Optional


class TableFormatter:
    """Formats data into ASCII tables."""

    def __init__(self, width: int = 80):
        """Initialize TableFormatter.

        Args:
            width: Terminal width for table layout
        """
        self.width = width

    def create_table(
        self,
        headers: List[str],
        rows: List[List[str]],
        borders: bool = True
    ) -> str:
        """Create ASCII table from headers and rows.

        Args:
            headers: Column headers
            rows: Table rows (list of lists)
            borders: Whether to include borders

        Returns:
            Formatted table string
        """
        if not headers or not rows:
            return ""

        # Calculate column widths
        col_widths = []
        for col_idx, header in enumerate(headers):
            max_width = len(str(header))
            for row in rows:
                if col_idx < len(row):
                    max_width = max(max_width, len(str(row[col_idx])))
            col_widths.append(max_width + 2)  # Add padding

        # Build table
        lines = []

        if borders:
            # Top border
            lines.append(self._create_border(col_widths))

        # Header
        header_row = self._create_row(headers, col_widths)
        lines.append(header_row)

        if borders:
            # Header separator
            lines.append(self._create_border(col_widths, char='='))

        # Rows
        for row in rows:
            row_str = self._create_row(row, col_widths)
            lines.append(row_str)

        if borders:
            # Bottom border
            lines.append(self._create_border(col_widths))

        return "\n".join(lines)

    def _create_border(self, widths: List[int], char: str = '-') -> str:
        """Create table border line.

        Args:
            widths: Column widths
            char: Border character

        Returns:
            Border line
        """
        parts = []
        for width in widths:
            parts.append(char * width)
        return "+" + "+".join(parts) + "+"

    def _create_row(self, items: List[Any], widths: List[int]) -> str:
        """Create table row.

        Args:
            items: Row items
            widths: Column widths

        Returns:
            Formatted row
        """
        parts = []
        for idx, item in enumerate(items):
            if idx < len(widths):
                width = widths[idx]
                text = str(item)
                # Pad to width
                padded = text.ljust(width)
                parts.append(padded)

        return "|" + "|".join(parts) + "|"

    def create_key_value_table(self, data: Dict[str, Any]) -> str:
        """Create key-value table.

        Args:
            data: Dictionary to display

        Returns:
            Formatted table
        """
        rows = []
        for key, value in data.items():
            formatted_key = str(key).replace('_', ' ').title()
            if isinstance(value, float):
                formatted_value = f"{value:.2f}"
            else:
                formatted_value = str(value)
            rows.append([formatted_key, formatted_value])

        return self.create_table(
            headers=["Metric", "Value"],
            rows=rows
        )

    def create_comparison_table(
        self,
        headers: List[str],
        data: Dict[str, List[Any]]
    ) -> str:
        """Create comparison table.

        Args:
            headers: Column headers
            data: Dictionary where keys are row names, values are column values

        Returns:
            Formatted table
        """
        rows = []
        for row_name, values in data.items():
            row = [row_name] + [str(v) for v in values]
            rows.append(row)

        all_headers = ["Name"] + headers
        return self.create_table(all_headers, rows)

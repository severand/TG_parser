"""Console output formatter for displaying results in terminal.

Features:
- Pretty printing of results with colors
- Progress bar display
- Table formatting for statistics
- Structured output (summary, details, tables)
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import sys

from utils.logger import Logger
from data.models import Message, SearchResult, ParsingStatistics
from output.table_formatter import TableFormatter


logger = Logger.get_instance()

# ANSI color codes
class Colors:
    """ANSI color codes for terminal output."""
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    ITALIC = '\033[3m'
    UNDERLINE = '\033[4m'

    # Colors
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    GRAY = '\033[90m'

    # Bright colors
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'


class ConsoleOutput:
    """Handles console output formatting and display."""

    def __init__(self, use_colors: bool = True, width: int = 80):
        """Initialize ConsoleOutput.

        Args:
            use_colors: Whether to use ANSI colors
            width: Terminal width for formatting
        """
        self.use_colors = use_colors
        self.width = width
        self.table_formatter = TableFormatter(width=width)

    def _colorize(self, text: str, color: str) -> str:
        """Apply color to text if colors enabled.

        Args:
            text: Text to colorize
            color: Color code

        Returns:
            Colored text or plain text
        """
        if not self.use_colors:
            return text
        return f"{color}{text}{Colors.RESET}"

    def _print(self, text: str = "", end: str = "\n"):
        """Print to stdout.

        Args:
            text: Text to print
            end: Line ending
        """
        print(text, end=end)

    def print_header(self, title: str):
        """Print colored header.

        Args:
            title: Header title
        """
        self._print()
        self._print(self._colorize(f"{'='*self.width}", Colors.CYAN))
        self._print(
            self._colorize(
                f" {title.center(self.width-2)} ",
                Colors.BOLD + Colors.CYAN
            )
        )
        self._print(self._colorize(f"{'='*self.width}", Colors.CYAN))
        self._print()

    def print_subheader(self, title: str):
        """Print subheader.

        Args:
            title: Subheader title
        """
        self._print(self._colorize(f"\n>>> {title}", Colors.BOLD + Colors.BLUE))
        self._print(self._colorize(f"-" * (len(title) + 4), Colors.BLUE))

    def print_success(self, message: str):
        """Print success message.

        Args:
            message: Success message
        """
        self._print(self._colorize(f"✓ {message}", Colors.GREEN))

    def print_error(self, message: str):
        """Print error message.

        Args:
            message: Error message
        """
        self._print(self._colorize(f"✗ {message}", Colors.RED))

    def print_warning(self, message: str):
        """Print warning message.

        Args:
            message: Warning message
        """
        self._print(self._colorize(f"⚠ {message}", Colors.YELLOW))

    def print_info(self, message: str):
        """Print info message.

        Args:
            message: Info message
        """
        self._print(self._colorize(f"ℹ {message}", Colors.CYAN))

    def print_message(self, message: Message, show_full: bool = False):
        """Print single message.

        Args:
            message: Message to print
            show_full: Show full message or summary
        """
        # Header
        header = f"[Message #{message.id}] "
        if message.author:
            header += f"by {message.author} "
        if message.timestamp:
            header += f"at {message.timestamp.strftime('%Y-%m-%d %H:%M')}"

        self._print(self._colorize(header, Colors.BOLD))

        # Content
        text = message.text[:200] if not show_full else message.text
        if len(message.text) > 200 and not show_full:
            text += "..."
        self._print(text)

        # Stats
        stats_line = f"👁 {message.views} views"
        if message.reactions > 0:
            stats_line += f" | 👍 {message.reactions} reactions"
        if message.mentions:
            stats_line += f" | @mentions: {', '.join(message.mentions[:3])}"
        if message.hashtags:
            stats_line += f" | #tags: {', '.join(message.hashtags[:3])}"

        self._print(self._colorize(stats_line, Colors.DIM + Colors.GRAY))
        self._print()

    def print_search_result(
        self,
        result: SearchResult,
        index: Optional[int] = None,
        show_context: bool = True
    ):
        """Print single search result.

        Args:
            result: Search result to print
            index: Result number
            show_context: Whether to show context snippet
        """
        # Header
        header = f"[Result {index or ''}] "
        if result.author:
            header += f"by {result.author} "
        if result.timestamp:
            header += f"at {result.timestamp.strftime('%Y-%m-%d %H:%M')}"

        self._print(self._colorize(header, Colors.BOLD + Colors.GREEN))

        # Relevance score
        score = result.relevance_score
        if score >= 80:
            score_color = Colors.BRIGHT_GREEN
        elif score >= 60:
            score_color = Colors.YELLOW
        else:
            score_color = Colors.GRAY
        self._print(self._colorize(f"Relevance: {score:.1f}%", score_color))

        # Keywords highlighted
        keywords_str = ", ".join(result.matched_keywords)
        self._print(self._colorize(f"Matched: {keywords_str}", Colors.MAGENTA))

        # Context
        if show_context and result.context:
            self._print(f"Context: {result.context}")

        # Text snippet
        snippet = result.text_snippet[:150]
        if len(result.text_snippet) > 150:
            snippet += "..."
        self._print(f"Text: {snippet}")

        # Engagement
        engagement = f"👁 {result.views} views"
        if result.reactions > 0:
            engagement += f" | 👍 {result.reactions} reactions"
        self._print(self._colorize(engagement, Colors.GRAY))
        self._print()

    def print_results(self, results: List[SearchResult], show_top: int = 20):
        """Print multiple search results.

        Args:
            results: List of search results
            show_top: Number of top results to show
        """
        if not results:
            self.print_warning("No results found")
            return

        self.print_subheader(f"Search Results ({len(results)} found)")

        for idx, result in enumerate(results[:show_top], 1):
            self.print_search_result(result, idx)

        if len(results) > show_top:
            self._print(
                self._colorize(
                    f"\n... and {len(results) - show_top} more results",
                    Colors.GRAY
                )
            )

    def print_statistics(self, stats: Dict[str, Any]):
        """Print statistics in formatted table.

        Args:
            stats: Statistics dictionary
        """
        self.print_subheader("Statistics")

        rows = []
        for key, value in stats.items():
            # Format key
            formatted_key = key.replace('_', ' ').title()

            # Format value
            if isinstance(value, float):
                formatted_value = f"{value:.2f}"
            else:
                formatted_value = str(value)

            rows.append([formatted_key, formatted_value])

        table = self.table_formatter.create_table(
            headers=["Metric", "Value"],
            rows=rows
        )
        self._print(table)

    def print_progress(self, current: int, total: int, prefix: str = ""):
        """Print progress bar.

        Args:
            current: Current progress
            total: Total items
            prefix: Progress prefix text
        """
        if total == 0:
            return

        percent = current / total
        filled = int(self.width * percent)
        bar = '█' * filled + '░' * (self.width - filled)

        percent_str = f"{percent*100:.1f}%"
        progress_str = f"{prefix} [{bar}] {current}/{total} ({percent_str})"

        # Overwrite line
        sys.stdout.write('\r' + progress_str[:self.width])
        sys.stdout.flush()

        if current >= total:
            self._print()  # New line when complete

    def print_summary(
        self,
        total_messages: int,
        total_results: int,
        duration_seconds: float,
        success: bool = True
    ):
        """Print execution summary.

        Args:
            total_messages: Total messages parsed
            total_results: Total search results
            duration_seconds: Execution time
            success: Whether operation was successful
        """
        self.print_subheader("Summary")

        if success:
            self.print_success(
                f"Parsed {total_messages} messages in {duration_seconds:.2f}s"
            )
            self.print_success(f"Found {total_results} matching results")
        else:
            self.print_error("Operation failed")

        if duration_seconds > 0:
            rate = total_messages / duration_seconds
            self._print(f"Processing rate: {rate:.1f} messages/sec")

    def print_separator(self):
        """Print visual separator."""
        self._print(self._colorize("-" * self.width, Colors.GRAY))
        self._print()

    def clear_screen(self):
        """Clear terminal screen."""
        if sys.platform == 'win32':
            import os
            os.system('cls')
        else:
            import os
            os.system('clear')

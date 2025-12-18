#!/usr/bin/env python3
"""Main entry point for Telegram Parser.

Usage:
    python main.py --channels "@channel1" "@channel2" --keywords "keyword1" "keyword2"
    python main.py --channels "@channel" --keywords "test" --output-format json --output-file results.json
"""

import click
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from core.parser import Parser
from output.console_output import ConsoleOutput
from output.json_exporter import JSONExporter
from output.csv_exporter import CSVExporter
from stats.reporter import Reporter
from utils.logger import Logger
from utils.validators import validate_keywords
from utils.exceptions import ParserException, ValidationException


logger = Logger.get_instance()


@click.group()
@click.version_option(version='1.0.0')
def cli():
    """Telegram Parser - Extract and search messages from Telegram channels."""
    pass


@cli.command()
@click.option(
    '--channels',
    multiple=True,
    required=True,
    help='Channel URLs or usernames to parse (can specify multiple times)'
)
@click.option(
    '--keywords',
    multiple=True,
    required=True,
    help='Keywords to search for (can specify multiple times)'
)
@click.option(
    '--output-format',
    type=click.Choice(['console', 'json', 'csv', 'all']),
    default='console',
    help='Output format for results'
)
@click.option(
    '--output-file',
    type=str,
    default=None,
    help='Output file name (auto-generated if not specified)'
)
@click.option(
    '--output-dir',
    type=click.Path(),
    default='results',
    help='Output directory for files'
)
@click.option(
    '--max-workers',
    type=int,
    default=4,
    help='Maximum concurrent threads'
)
@click.option(
    '--max-messages',
    type=int,
    default=None,
    help='Maximum messages per channel'
)
@click.option(
    '--date-from',
    type=str,
    default=None,
    help='Start date for filtering (YYYY-MM-DD)'
)
@click.option(
    '--date-to',
    type=str,
    default=None,
    help='End date for filtering (YYYY-MM-DD)'
)
@click.option(
    '--min-views',
    type=int,
    default=None,
    help='Minimum views to include'
)
@click.option(
    '--with-urls',
    is_flag=True,
    help='Only include messages with URLs'
)
@click.option(
    '--report',
    is_flag=True,
    help='Generate summary report'
)
def search(
    channels: tuple,
    keywords: tuple,
    output_format: str,
    output_file: Optional[str],
    output_dir: str,
    max_workers: int,
    max_messages: Optional[int],
    date_from: Optional[str],
    date_to: Optional[str],
    min_views: Optional[int],
    with_urls: bool,
    report: bool,
):
    """Parse channels and search for keywords."""

    try:
        # Initialize
        console = ConsoleOutput(use_colors=True)
        console.print_header("Telegram Parser - Search Operation")

        # Validate input
        if not channels:
            console.print_error("No channels specified")
            return

        if not keywords:
            console.print_error("No keywords specified")
            return

        logger.info(f"Starting search: {len(channels)} channels, {len(keywords)} keywords")

        # Parse dates if provided
        date_from_dt = None
        date_to_dt = None
        if date_from:
            try:
                date_from_dt = datetime.strptime(date_from, '%Y-%m-%d')
            except ValueError:
                console.print_error(f"Invalid date format: {date_from}")
                return

        if date_to:
            try:
                date_to_dt = datetime.strptime(date_to, '%Y-%m-%d')
            except ValueError:
                console.print_error(f"Invalid date format: {date_to}")
                return

        # Initialize parser
        parser = Parser(max_workers=max_workers)

        # Build search filters
        filters = {}
        if date_from_dt:
            filters['date_from'] = date_from_dt
        if date_to_dt:
            filters['date_to'] = date_to_dt
        if min_views:
            filters['min_views'] = min_views
        if with_urls:
            filters['has_url'] = True

        # Parse and search
        console.print_info(f"Parsing {len(channels)} channels...")
        result = parser.parse_and_search(
            channels=list(channels),
            keywords=list(keywords),
            max_messages=max_messages,
            **filters
        )

        if not result['success']:
            console.print_error(f"Search failed: {result['error']}")
            return

        # Display results
        messages = result['messages']
        search_results = result['search_results']
        stats = result['statistics']

        console.print_success(f"Successfully parsed {len(messages)} messages")
        console.print_success(f"Found {len(search_results)} matching results")

        # Show results based on format
        if output_format in ['console', 'all']:
            console.print_separator()
            if search_results:
                console.print_results(search_results, show_top=10)
            else:
                console.print_warning("No matching results found")

            console.print_separator()
            console.print_statistics(stats)
            console.print_summary(
                total_messages=len(messages),
                total_results=len(search_results),
                duration_seconds=stats.get('duration_seconds', 0),
                success=True
            )

        # Export to files if requested
        if output_format in ['json', 'all']:
            json_exporter = JSONExporter(output_dir=output_dir)
            json_file = json_exporter.export_search_results(
                search_results,
                filename=output_file
            )
            console.print_success(f"JSON export: {json_file}")

        if output_format in ['csv', 'all']:
            csv_exporter = CSVExporter(output_dir=output_dir)
            csv_file = csv_exporter.export_search_results(
                search_results,
                filename=output_file.replace('.json', '.csv') if output_file else None
            )
            console.print_success(f"CSV export: {csv_file}")

        # Generate report if requested
        if report:
            reporter = Reporter(parser.stats_collector)
            report_file = Path(output_dir) / f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            reporter.export_report_to_file(str(report_file))
            console.print_success(f"Report saved: {report_file}")

        logger.info("Search operation completed successfully")

    except ValidationException as e:
        console.print_error(f"Validation error: {e}")
        logger.error(f"Validation error: {e}")
    except ParserException as e:
        console.print_error(f"Parser error: {e}")
        logger.error(f"Parser error: {e}")
    except Exception as e:
        console.print_error(f"Unexpected error: {e}")
        logger.error(f"Unexpected error: {e}")


@cli.command()
@click.option(
    '--channels',
    multiple=True,
    required=True,
    help='Channel URLs or usernames to parse'
)
@click.option(
    '--output-dir',
    type=click.Path(),
    default='results',
    help='Output directory'
)
@click.option(
    '--max-workers',
    type=int,
    default=4,
    help='Maximum concurrent threads'
)
def parse(
    channels: tuple,
    output_dir: str,
    max_workers: int,
):
    """Parse channels without searching."""

    try:
        console = ConsoleOutput(use_colors=True)
        console.print_header("Telegram Parser - Parse Operation")

        if not channels:
            console.print_error("No channels specified")
            return

        parser = Parser(max_workers=max_workers)
        messages = parser.parse_channels(list(channels), show_progress=True)

        # Export
        json_exporter = JSONExporter(output_dir=output_dir)
        json_file = json_exporter.export_messages(messages)
        console.print_success(f"Exported {len(messages)} messages to {json_file}")

        # Statistics
        stats = parser.get_statistics()
        console.print_statistics(stats)

    except Exception as e:
        console.print_error(f"Error: {e}")
        logger.error(f"Error: {e}")


@cli.command()
def version():
    """Show version information."""
    click.echo("Telegram Parser v1.0.0")
    click.echo("")
    click.echo("A powerful tool for parsing and searching Telegram channel messages.")
    click.echo("")
    click.echo("Features:")
    click.echo("  - Multi-threaded channel parsing")
    click.echo("  - Advanced keyword search with relevance scoring")
    click.echo("  - Filter by date, views, hashtags, mentions")
    click.echo("  - Export to JSON and CSV")
    click.echo("  - Comprehensive statistics and reporting")
    click.echo("")
    click.echo("Usage: python main.py --help")


if __name__ == '__main__':
    cli()

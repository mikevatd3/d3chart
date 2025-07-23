import click
import pandas as pd
import sys
from pathlib import Path
from .charts import BarChart, Histogram, LineChart, DoughnutChart, HexbinChart


@click.group()
@click.version_option()
def cli():
    """D3-style chart maker CLI tool for generating SVG charts from CSV data."""
    pass


@cli.command()
@click.argument('filename', required=False)
@click.option('--output', '-o', help='Output SVG filename')
@click.option('--width', default=800, help='Chart width in pixels')
@click.option('--height', default=600, help='Chart height in pixels')
def bar(filename, output, width, height):
    """Create a basic bar chart (requires: id, category, value columns)."""
    data = _read_csv_data(filename)
    chart = BarChart(data, width, height)
    svg_content = chart.generate()
    _write_output(svg_content, output, filename, 'bar')


@cli.command()
@click.argument('filename', required=False)
@click.option('--output', '-o', help='Output SVG filename')
@click.option('--width', default=800, help='Chart width in pixels')
@click.option('--height', default=600, help='Chart height in pixels')
@click.option('--bins', default=20, help='Number of histogram bins')
def histogram(filename, output, width, height, bins):
    """Create a histogram (requires: id, value columns)."""
    data = _read_csv_data(filename)
    chart = Histogram(data, width, height, bins)
    svg_content = chart.generate()
    _write_output(svg_content, output, filename, 'histogram')


@cli.command()
@click.argument('filename', required=False)
@click.option('--output', '-o', help='Output SVG filename')
@click.option('--width', default=800, help='Chart width in pixels')
@click.option('--height', default=600, help='Chart height in pixels')
def line(filename, output, width, height):
    """Create a line chart (requires: id, time, value columns)."""
    data = _read_csv_data(filename)
    chart = LineChart(data, width, height)
    svg_content = chart.generate()
    _write_output(svg_content, output, filename, 'line')


@cli.command()
@click.argument('filename', required=False)
@click.option('--output', '-o', help='Output SVG filename')
@click.option('--width', default=800, help='Chart width in pixels')
@click.option('--height', default=600, help='Chart height in pixels')
def doughnut(filename, output, width, height):
    """Create a doughnut chart (requires: id, category, value columns)."""
    data = _read_csv_data(filename)
    chart = DoughnutChart(data, width, height)
    svg_content = chart.generate()
    _write_output(svg_content, output, filename, 'doughnut')


@cli.command()
@click.argument('filename', required=False)
@click.option('--output', '-o', help='Output SVG filename')
@click.option('--width', default=800, help='Chart width in pixels')
@click.option('--height', default=600, help='Chart height in pixels')
def hexbin(filename, output, width, height):
    """Create a hexbin chart (requires: id, independent, dependent columns)."""
    data = _read_csv_data(filename)
    chart = HexbinChart(data, width, height)
    svg_content = chart.generate()
    _write_output(svg_content, output, filename, 'hexbin')


def _read_csv_data(filename):
    """Read CSV data from file or stdin."""
    if filename:
        return pd.read_csv(filename)
    else:
        return pd.read_csv(sys.stdin)


def _write_output(svg_content, output_filename, input_filename, chart_type):
    """Write SVG content to file or stdout."""
    if output_filename:
        with open(output_filename, 'w') as f:
            f.write(svg_content)
    elif input_filename:
        # Generate output filename based on input
        input_path = Path(input_filename)
        output_path = input_path.with_suffix(f'.{chart_type}.svg')
        with open(output_path, 'w') as f:
            f.write(svg_content)
    else:
        # Print to stdout
        print(svg_content)


if __name__ == "__main__":
    cli()

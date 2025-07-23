# StandardCharts

D3-style chart maker CLI tool for generating SVG charts from CSV data.

## Installation

```bash
pip install .
```

## Usage

After installation, use the `d3chart` command to generate charts:

```bash
d3chart [CHART_TYPE] [CSV_FILE] [OPTIONS]
```

### Chart Types

#### Bar Chart
Creates a basic bar chart from categorical data.

**Required CSV columns:** `id`, `category`, `value`

```bash
d3chart bar data.csv --output chart.svg --width 800 --height 600
```

#### Histogram
Creates a histogram from numerical data.

**Required CSV columns:** `id`, `value`

```bash
d3chart histogram data.csv --bins 20 --output hist.svg
```

#### Line Chart
Creates a line chart for time series data.

**Required CSV columns:** `id`, `time`, `value`

```bash
d3chart line timeseries.csv --output line.svg
```

#### Doughnut Chart
Creates a doughnut (ring) chart for categorical data.

**Required CSV columns:** `id`, `category`, `value`

```bash
d3chart doughnut data.csv --output doughnut.svg
```

#### Hexbin Chart
Creates a hexagonal binning chart for scatter plot data.

**Required CSV columns:** `id`, `independent`, `dependent`

```bash
d3chart hexbin scatter.csv --output hexbin.svg
```

### Options

- `--output`, `-o`: Output SVG filename (optional)
- `--width`: Chart width in pixels (default: 800)
- `--height`: Chart height in pixels (default: 600)
- `--bins`: Number of histogram bins (histogram only, default: 20)

### Input/Output Behavior

- **With filename and --output**: Reads from file, writes to specified output
- **With filename only**: Reads from file, writes to `[filename].[charttype].svg`
- **No filename**: Reads from stdin, writes to stdout (for piping)

### Examples

```bash
# Generate bar chart from file
d3chart bar sales.csv --output sales_chart.svg

# Generate histogram with custom bins
d3chart histogram values.csv --bins 30

# Pipe data through
cat data.csv | d3chart line --output result.svg

# Generate with custom dimensions
d3chart doughnut categories.csv --width 600 --height 400
```

### CSV Format Requirements

Each chart type expects specific column names in your CSV file:

- **Bar/Doughnut**: `id`, `category`, `value`
- **Histogram**: `id`, `value`
- **Line**: `id`, `time`, `value`
- **Hexbin**: `id`, `independent`, `dependent`

### Color Schemes

The tool uses predefined color palettes:
- Categorical colors from `categorical.csv`
- Color ramps from `ramps.csv`
- Standard histogram color: `rgb(101,150,207)`

All charts output clean SVG with IBM Plex Sans font styling.
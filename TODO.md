# D3 `standardchart` chart maker

This will be a cli tool that is an extreme subset of matplotlib charts. It will 
take csvs as input either from stdin or from a filename and produce svg files of
charts.

Try to keep the standard colors in a singular editable place.


## Charts supported

- [ ] Basic bar chart (input data must have 3 columns -- id, category, value)
- [ ] Histogram (input data must have 2 columns -- id, value)
- [ ] Line chart (input data must have 3 columns -- id, time, value)
- [ ] Doughnut chart (input data must have 3 columns -- id, category, value)
- [ ] Hexbin instead of scatter (input data must have 3 columns -- id, independent, dependent)

The chart type should sub-commands, i.e `d3chart bar [options] <filename>`.


## Color standards

The color standards are available in two files:

- ramps.csv (for use on hexbin)
- categorical.csv (for use on basic bar, doughnut, line)

- Use `rgb(101,150,207)` as the standard color for histogram


## Fonts

- 'IBM Plex Sans' for everything


## Technical

- Use `uv` for all dependency management.


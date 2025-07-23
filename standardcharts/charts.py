import pandas as pd
import math
from typing import List, Tuple, Dict


class ColorPalette:
    """Manages color standards for charts."""
    
    def __init__(self):
        self.categorical_colors = self._load_categorical_colors()
        self.ramp_colors = self._load_ramp_colors()
        self.histogram_color = "rgb(101,150,207)"
    
    def _load_categorical_colors(self) -> List[str]:
        """Load categorical colors from embedded data."""
        colors_data = [
            "211, 89, 28",    # red
            "236, 186, 102",  # yellow
            "135, 175, 63",   # green
            "88, 191, 172",   # teal
            "101, 150, 207",  # blue
            "202, 127, 204"   # purple
        ]
        return [f"rgb({color})" for color in colors_data]
    
    def _load_ramp_colors(self) -> Dict[str, List[str]]:
        """Load color ramps from embedded data."""
        ramps_data = {
            "Green-to-Blue": ["33, 89, 44", "135, 175, 63", "118, 163, 138", "101, 150, 207", "32, 105, 138"],
            "Blues": ["9, 58, 81", "32, 105, 138", "101, 150, 207", "182, 204, 230", "217, 233, 252"],
            "Greens": ["24, 60, 32", "33, 89, 44", "135, 175, 63", "196, 215, 163", "229, 243, 205"]
        }
        ramps = {}
        for name, colors in ramps_data.items():
            ramps[name] = [f"rgb({color})" for color in colors]
        return ramps
    
    def get_categorical_color(self, index: int) -> str:
        """Get categorical color by index (cycles through available colors)."""
        return self.categorical_colors[index % len(self.categorical_colors)]
    
    def get_ramp_colors(self, ramp_name: str = "Blues") -> List[str]:
        """Get color ramp for continuous data."""
        return self.ramp_colors.get(ramp_name, self.ramp_colors["Blues"])


class BaseChart:
    """Base class for all chart types."""
    
    def __init__(self, data: pd.DataFrame, width: int, height: int):
        self.data = data
        self.width = width
        self.height = height
        self.colors = ColorPalette()
        self.margin = {"top": 20, "right": 20, "bottom": 40, "left": 60}
        self.chart_width = width - self.margin["left"] - self.margin["right"]
        self.chart_height = height - self.margin["top"] - self.margin["bottom"]
    
    def _create_svg_header(self) -> str:
        """Create SVG header with styles."""
        return f'''<?xml version="1.0" encoding="UTF-8"?>
<svg width="{self.width}" height="{self.height}" xmlns="http://www.w3.org/2000/svg">
<style>
    text {{
        font-family: 'IBM Plex Sans', sans-serif;
        font-size: 12px;
        fill: #333;
    }}
    .axis-line {{
        stroke: #333;
        stroke-width: 1;
    }}
    .tick-line {{
        stroke: #666;
        stroke-width: 0.5;
    }}
</style>
<g transform="translate({self.margin["left"]}, {self.margin["top"]})">'''
    
    def _create_svg_footer(self) -> str:
        """Create SVG footer."""
        return '</g></svg>'
    
    def generate(self) -> str:
        """Generate SVG content - to be implemented by subclasses."""
        raise NotImplementedError


class BarChart(BaseChart):
    """Basic bar chart implementation."""
    
    def __init__(self, data: pd.DataFrame, width: int, height: int):
        super().__init__(data, width, height)
        self._validate_data()
    
    def _validate_data(self):
        """Validate that data has the required number of columns."""
        if len(self.data.columns) < 2:
            raise ValueError(f"BarChart requires at least 2 columns, got {len(self.data.columns)}")
        
        # Assign column names based on position: category, then value columns
        num_cols = len(self.data.columns)
        value_col_names = [f'value_{i}' for i in range(num_cols - 1)]
        self.data.columns = ['category'] + value_col_names
        self.value_columns = value_col_names
    
    def generate(self) -> str:
        """Generate stacked bar chart SVG."""
        # Reserve space for legend
        legend_width = 120
        original_chart_width = self.chart_width
        self.chart_width = original_chart_width - legend_width
        
        svg_parts = [self._create_svg_header()]
        
        # Group data by category and sum all value columns
        grouped = self.data.groupby('category')[self.value_columns].sum().reset_index()
        
        # Calculate total heights for each category
        grouped['total'] = grouped[self.value_columns].sum(axis=1)
        max_total = grouped['total'].max()
        categories = grouped['category'].tolist()
        
        # X scale (categories)
        bar_width = self.chart_width / len(categories)
        
        # Y scale (values)
        y_scale = self.chart_height / max_total if max_total > 0 else 1
        
        # Draw stacked bars
        for i, (_, row) in enumerate(grouped.iterrows()):
            x = i * bar_width
            current_y = self.chart_height
            
            # Draw each stack segment
            for j, value_col in enumerate(self.value_columns):
                segment_height = row[value_col] * y_scale
                if segment_height > 0:
                    current_y -= segment_height
                    color = self.colors.get_categorical_color(j)
                    
                    svg_parts.append(f'<rect x="{x + bar_width*0.1}" y="{current_y}" width="{bar_width*0.8}" height="{segment_height}" fill="{color}"/>')
            
            # Add category label
            svg_parts.append(f'<text x="{x + bar_width/2}" y="{self.chart_height + 20}" text-anchor="middle">{row["category"]}</text>')
        
        # Draw axes
        svg_parts.append(f'<line x1="0" y1="{self.chart_height}" x2="{self.chart_width}" y2="{self.chart_height}" class="axis-line"/>')
        svg_parts.append(f'<line x1="0" y1="0" x2="0" y2="{self.chart_height}" class="axis-line"/>')
        
        # Add Y-axis labels
        for i in range(5):
            y_val = (max_total / 4) * i
            y_pos = self.chart_height - (y_val * y_scale) if max_total > 0 else self.chart_height
            svg_parts.append(f'<text x="-10" y="{y_pos + 4}" text-anchor="end">{y_val:.0f}</text>')
            if i > 0:
                svg_parts.append(f'<line x1="0" y1="{y_pos}" x2="{self.chart_width}" y2="{y_pos}" class="tick-line"/>')
        
        # Add legend
        legend_x = self.chart_width + 20
        legend_y = 20
        
        for j, value_col in enumerate(self.value_columns):
            color = self.colors.get_categorical_color(j)
            rect_y = legend_y + j * 20
            
            # Legend color box
            svg_parts.append(f'<rect x="{legend_x}" y="{rect_y}" width="12" height="12" fill="{color}"/>')
            
            # Legend text
            svg_parts.append(f'<text x="{legend_x + 18}" y="{rect_y + 9}" text-anchor="start">{value_col}</text>')
        
        # Restore original chart width
        self.chart_width = original_chart_width
        
        svg_parts.append(self._create_svg_footer())
        return '\n'.join(svg_parts)


class Histogram(BaseChart):
    """Histogram implementation."""
    
    def __init__(self, data: pd.DataFrame, width: int, height: int, bins: int):
        super().__init__(data, width, height)
        self.bins = bins
        self._validate_data()
    
    def _validate_data(self):
        """Validate that data has the required number of columns."""
        if len(self.data.columns) < 2:
            raise ValueError(f"Histogram requires at least 2 columns, got {len(self.data.columns)}")
        
        # Assign column names based on position
        self.data.columns = ['id', 'value'] + list(self.data.columns[2:])
    
    def generate(self) -> str:
        """Generate histogram SVG."""
        svg_parts = [self._create_svg_header()]
        
        # Create histogram bins
        values = self.data['value']
        hist, bin_edges = pd.cut(values, bins=self.bins, retbins=True)
        counts = hist.value_counts().sort_index()
        
        # Calculate scales
        max_count = counts.max()
        bin_width = self.chart_width / self.bins
        y_scale = self.chart_height / max_count
        
        # Draw bars
        for i, (interval, count) in enumerate(counts.items()):
            x = i * bin_width
            bar_height = count * y_scale
            y = self.chart_height - bar_height
            
            svg_parts.append(f'<rect x="{x}" y="{y}" width="{bin_width-1}" height="{bar_height}" fill="{self.colors.histogram_color}"/>')
        
        # Draw axes
        svg_parts.append(f'<line x1="0" y1="{self.chart_height}" x2="{self.chart_width}" y2="{self.chart_height}" class="axis-line"/>')
        svg_parts.append(f'<line x1="0" y1="0" x2="0" y2="{self.chart_height}" class="axis-line"/>')
        
        # Add axis labels
        for i in range(0, self.bins + 1, max(1, self.bins // 5)):
            x_pos = i * bin_width
            if i < len(bin_edges):
                label = f"{bin_edges[i]:.1f}"
                svg_parts.append(f'<text x="{x_pos}" y="{self.chart_height + 20}" text-anchor="middle">{label}</text>')
        
        for i in range(5):
            y_val = (max_count / 4) * i
            y_pos = self.chart_height - (y_val * y_scale)
            svg_parts.append(f'<text x="-10" y="{y_pos + 4}" text-anchor="end">{int(y_val)}</text>')
            if i > 0:
                svg_parts.append(f'<line x1="0" y1="{y_pos}" x2="{self.chart_width}" y2="{y_pos}" class="tick-line"/>')
        
        svg_parts.append(self._create_svg_footer())
        return '\n'.join(svg_parts)


class LineChart(BaseChart):
    """Line chart implementation."""
    
    def __init__(self, data: pd.DataFrame, width: int, height: int):
        super().__init__(data, width, height)
        self._validate_data()
    
    def _validate_data(self):
        """Validate that data has the required number of columns."""
        if len(self.data.columns) < 3:
            raise ValueError(f"LineChart requires at least 3 columns, got {len(self.data.columns)}")
        
        # Assign column names based on position
        self.data.columns = ['id', 'time', 'value'] + list(self.data.columns[3:])
    
    def generate(self) -> str:
        """Generate line chart SVG."""
        svg_parts = [self._create_svg_header()]
        
        # Group by id to create separate lines
        groups = self.data.groupby('id')
        
        # Calculate scales
        all_times = pd.to_datetime(self.data['time']).sort_values()
        time_range = (all_times.max() - all_times.min()).total_seconds()
        min_time = all_times.min()
        
        min_value = self.data['value'].min()
        max_value = self.data['value'].max()
        value_range = max_value - min_value
        
        # Draw lines for each group
        for i, (group_id, group_data) in enumerate(groups):
            color = self.colors.get_categorical_color(i)
            group_data = group_data.sort_values('time')
            
            points = []
            for _, row in group_data.iterrows():
                time_val = pd.to_datetime(row['time'])
                x = ((time_val - min_time).total_seconds() / time_range) * self.chart_width
                y = self.chart_height - ((row['value'] - min_value) / value_range) * self.chart_height
                points.append(f"{x},{y}")
            
            if len(points) > 1:
                path = f'<polyline points="{" ".join(points)}" fill="none" stroke="{color}" stroke-width="2"/>'
                svg_parts.append(path)
        
        # Draw axes
        svg_parts.append(f'<line x1="0" y1="{self.chart_height}" x2="{self.chart_width}" y2="{self.chart_height}" class="axis-line"/>')
        svg_parts.append(f'<line x1="0" y1="0" x2="0" y2="{self.chart_height}" class="axis-line"/>')
        
        # Add axis labels
        for i in range(5):
            y_val = min_value + (value_range / 4) * i
            y_pos = self.chart_height - ((y_val - min_value) / value_range) * self.chart_height
            svg_parts.append(f'<text x="-10" y="{y_pos + 4}" text-anchor="end">{y_val:.1f}</text>')
            if i > 0 and i < 4:
                svg_parts.append(f'<line x1="0" y1="{y_pos}" x2="{self.chart_width}" y2="{y_pos}" class="tick-line"/>')
        
        svg_parts.append(self._create_svg_footer())
        return '\n'.join(svg_parts)


class DoughnutChart(BaseChart):
    """Doughnut chart implementation."""
    
    def __init__(self, data: pd.DataFrame, width: int, height: int):
        super().__init__(data, width, height)
        self._validate_data()
    
    def _validate_data(self):
        """Validate that data has the required number of columns."""
        if len(self.data.columns) < 2:
            raise ValueError(f"DoughnutChart requires at least 2 columns, got {len(self.data.columns)}")
        
        # Assign column names based on position
        self.data.columns = ['category', 'value'] + list(self.data.columns[2:])
    
    def generate(self) -> str:
        """Generate doughnut chart SVG."""
        svg_parts = [self._create_svg_header()]
        
        # Group data by category and sum values
        grouped = self.data.groupby('category')['value'].sum().reset_index()
        total = grouped['value'].sum()
        
        # Chart dimensions
        radius = min(self.chart_width, self.chart_height) / 2 * 0.8
        inner_radius = radius * 0.5
        center_x = self.chart_width / 2
        center_y = self.chart_height / 2
        
        # Draw arcs
        current_angle = 0
        for i, (_, row) in enumerate(grouped.iterrows()):
            angle = (row['value'] / total) * 2 * math.pi
            color = self.colors.get_categorical_color(i)
            
            # Calculate arc path
            start_x = center_x + radius * math.cos(current_angle)
            start_y = center_y + radius * math.sin(current_angle)
            end_x = center_x + radius * math.cos(current_angle + angle)
            end_y = center_y + radius * math.sin(current_angle + angle)
            
            inner_start_x = center_x + inner_radius * math.cos(current_angle)
            inner_start_y = center_y + inner_radius * math.sin(current_angle)
            inner_end_x = center_x + inner_radius * math.cos(current_angle + angle)
            inner_end_y = center_y + inner_radius * math.sin(current_angle + angle)
            
            large_arc = 1 if angle > math.pi else 0
            
            path = f'''<path d="M {start_x} {start_y} 
                      A {radius} {radius} 0 {large_arc} 1 {end_x} {end_y}
                      L {inner_end_x} {inner_end_y}
                      A {inner_radius} {inner_radius} 0 {large_arc} 0 {inner_start_x} {inner_start_y} Z"
                      fill="{color}"/>'''
            svg_parts.append(path)
            
            # Add label
            label_angle = current_angle + angle / 2
            label_radius = radius + 20
            label_x = center_x + label_radius * math.cos(label_angle)
            label_y = center_y + label_radius * math.sin(label_angle)
            svg_parts.append(f'<text x="{label_x}" y="{label_y}" text-anchor="middle">{row["category"]}</text>')
            
            current_angle += angle
        
        svg_parts.append(self._create_svg_footer())
        return '\n'.join(svg_parts)


class HexbinChart(BaseChart):
    """Hexbin chart implementation."""
    
    def __init__(self, data: pd.DataFrame, width: int, height: int):
        super().__init__(data, width, height)
        self._validate_data()
    
    def _validate_data(self):
        """Validate that data has the required number of columns."""
        if len(self.data.columns) < 3:
            raise ValueError(f"HexbinChart requires at least 3 columns, got {len(self.data.columns)}")
        
        # Assign column names based on position
        self.data.columns = ['id', 'independent', 'dependent'] + list(self.data.columns[3:])
    
    def generate(self) -> str:
        """Generate hexbin chart SVG."""
        svg_parts = [self._create_svg_header()]
        
        # Calculate scales
        x_min, x_max = self.data['independent'].min(), self.data['independent'].max()
        y_min, y_max = self.data['dependent'].min(), self.data['dependent'].max()
        
        x_range = x_max - x_min
        y_range = y_max - y_min
        
        # Create hexagonal bins
        hex_size = 20
        hex_cols = int(self.chart_width / (hex_size * 1.5)) + 1
        hex_rows = int(self.chart_height / (hex_size * math.sqrt(3))) + 1
        
        # Count points in each hexagon
        hex_counts = {}
        for _, row in self.data.iterrows():
            x_norm = (row['independent'] - x_min) / x_range
            y_norm = (row['dependent'] - y_min) / y_range
            
            col = int(x_norm * hex_cols)
            row_idx = int(y_norm * hex_rows)
            
            key = (col, row_idx)
            hex_counts[key] = hex_counts.get(key, 0) + 1
        
        if not hex_counts:
            svg_parts.append(self._create_svg_footer())
            return '\n'.join(svg_parts)
        
        max_count = max(hex_counts.values())
        colors = self.colors.get_ramp_colors("Blues")
        
        # Draw hexagons
        for (col, row), count in hex_counts.items():
            x = col * hex_size * 1.5
            y = row * hex_size * math.sqrt(3)
            if col % 2 == 1:
                y += hex_size * math.sqrt(3) / 2
            
            # Color based on count
            color_idx = min(int((count / max_count) * (len(colors) - 1)), len(colors) - 1)
            color = colors[color_idx]
            
            # Create hexagon path
            points = []
            for i in range(6):
                angle = i * math.pi / 3
                px = x + hex_size * math.cos(angle)
                py = y + hex_size * math.sin(angle)
                points.append(f"{px},{py}")
            
            svg_parts.append(f'<polygon points="{" ".join(points)}" fill="{color}" stroke="white" stroke-width="0.5"/>')
        
        # Draw axes
        svg_parts.append(f'<line x1="0" y1="{self.chart_height}" x2="{self.chart_width}" y2="{self.chart_height}" class="axis-line"/>')
        svg_parts.append(f'<line x1="0" y1="0" x2="0" y2="{self.chart_height}" class="axis-line"/>')
        
        # Add axis labels
        for i in range(5):
            x_val = x_min + (x_range / 4) * i
            x_pos = (i / 4) * self.chart_width
            svg_parts.append(f'<text x="{x_pos}" y="{self.chart_height + 20}" text-anchor="middle">{x_val:.1f}</text>')
            
            y_val = y_min + (y_range / 4) * i
            y_pos = self.chart_height - (i / 4) * self.chart_height
            svg_parts.append(f'<text x="-10" y="{y_pos + 4}" text-anchor="end">{y_val:.1f}</text>')
        
        svg_parts.append(self._create_svg_footer())
        return '\n'.join(svg_parts)
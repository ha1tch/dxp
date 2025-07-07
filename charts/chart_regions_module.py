"""
Module for drawing highlighted regions on the chart to group related systems
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch
from distributed_systems_data import *

# Define regions based on system clusters
# Using exact coordinates from the plot area
REGIONS = [
    {
        'name': 'Fire & Forget',
        'color': 'lightblue',
        'alpha': 0.2,
        'bounds': {
            'x_min': 127.729412,    # Plot area left edge
            'x_max': 360,           # Extend to include Fire & Forget pattern
            'y_min': 600,           # Just above "Any (25%)" line
            'y_max': 815.121176     # Plot area bottom edge
        },
        'label_offset': {'x': 0, 'y': 30}  # Place label inside region
    },
    {
        'name': 'Practical Consensus',
        'color': 'lightgreen',
        'alpha': 0.2,
        'bounds': {
            'x_min': 440,           # Around EPaxos area
            'x_max': 760,           # Include consensus protocols
            'y_min': 280,           # Above strong quorum
            'y_max': 540            # Below Fire & Forget systems
        },
        'label_offset': {'x': 0, 'y': 30}  # Place label inside region
    },
    {
        'name': 'Full ACID',
        'color': 'lightcoral',
        'alpha': 0.2,
        'bounds': {
            'x_min': 840,           # Start around Full ACID point
            'x_max': 853.2,         # Plot area right edge
            'y_min': 28.658824,     # Plot area top edge
            'y_max': 300            # Down to include ACID systems
        },
        'label_offset': {'x': -50, 'y': 30}  # Offset left for narrow region
    }
]

def draw_region(ax, region):
    """
    Draw a single highlighted region on the chart.
    
    Args:
        ax: Matplotlib axis object
        region: Dictionary containing region properties
    """
    bounds = region['bounds']
    
    # Calculate rectangle properties
    x = bounds['x_min']
    y = bounds['y_min']
    width = bounds['x_max'] - bounds['x_min']
    height = bounds['y_max'] - bounds['y_min']
    
    # Create rounded rectangle with tighter corners
    rect = FancyBboxPatch(
        (x, y), width, height,
        boxstyle="round,pad=0.01",
        facecolor=region['color'],
        edgecolor='none',
        alpha=region['alpha'],
        zorder=1  # Draw behind grid lines and data points
    )
    
    ax.add_patch(rect)
    
    # Add region label (positioned inside the region at the top)
    label_x = (bounds['x_min'] + bounds['x_max']) / 2 + region['label_offset']['x']
    label_y = bounds['y_min'] + region['label_offset']['y']
    
    # Determine label color based on region color
    label_colors = {
        'lightblue': 'darkblue',
        'lightgreen': 'darkgreen',
        'lightcoral': 'darkred'
    }
    label_color = label_colors.get(region['color'], 'black')
    
    ax.text(label_x, label_y, region['name'],
            fontsize=14, fontweight='bold', fontfamily='sans-serif',
            color=label_color, ha='center', va='top',
            zorder=2)

def add_region_annotations(ax):
    """
    Add optional annotations about regions (unusual patterns, opportunities, etc.)
    
    Args:
        ax: Matplotlib axis object
    """
    annotations = [
        {
            'text': ['High coordination,', 'Low agreement', '(Unusual)'],
            'x': 320,
            'y': 300,
            'color': 'darkgray',
            'style': 'italic'
        },
        {
            'text': ['Low coordination,', 'High agreement', '(Innovation)'],
            'x': 190,
            'y': 270,
            'color': 'darkgray',
            'style': 'italic'
        },
        {
            'text': ['Empty space:', 'Opportunity?'],
            'x': 730,
            'y': 660,
            'color': 'darkgray',
            'style': 'italic'
        }
    ]
    
    for annotation in annotations:
        y_offset = 0
        for line in annotation['text']:
            ax.text(annotation['x'], annotation['y'] + y_offset, line,
                    fontsize=10, fontfamily='sans-serif',
                    color=annotation['color'], fontstyle=annotation['style'],
                    ha='left', va='top', zorder=2)
            y_offset += 15  # Line spacing

def setup_regions(ax, include_annotations=True):
    """
    Main function to set up all highlighted regions.
    Should be called BEFORE plotting data points but AFTER setting up axes.
    
    Args:
        ax: Matplotlib axis object
        include_annotations: Whether to include region annotations (default: True)
    """
    # Draw all regions
    for region in REGIONS:
        draw_region(ax, region)
    
    # Add annotations if requested
    if include_annotations:
        add_region_annotations(ax)
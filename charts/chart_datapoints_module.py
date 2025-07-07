"""
Module for plotting data points on the chart
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import RegularPolygon
import numpy as np
from distributed_systems_data import *

def get_marker_properties(category):
    """
    Get marker style and size for a given category.
    
    Args:
        category: Category name from CATEGORIES
    
    Returns:
        dict: Marker properties for matplotlib
    """
    cat_info = CATEGORIES.get(category, {})
    
    # Base properties
    props = {
        'color': cat_info.get('color', '#000000'),
        'edgecolor': 'white',
        'linewidth': 0.5,
        'zorder': 10  # Ensure data points are drawn above grid lines
    }
    
    # Set marker style and size based on category
    if cat_info.get('marker') == 'triangle':
        props['marker'] = '^'
        props['markersize'] = 10
    elif cat_info.get('marker') == 'star':
        props['marker'] = '*'
        props['markersize'] = 12
    elif cat_info.get('marker') == 'square':
        props['marker'] = 's'
        props['markersize'] = 10
    else:  # circle (default)
        props['marker'] = 'o'
        props['markersize'] = 10
    
    return props

def plot_data_point(ax, x, y, category):
    """
    Plot a single data point.
    
    Args:
        ax: Matplotlib axis object
        x: X coordinate
        y: Y coordinate
        category: Category of the data point
    """
    props = get_marker_properties(category)
    
    # Plot the marker
    ax.plot(x, y, 
            marker=props['marker'],
            markersize=props['markersize'],
            markerfacecolor=props['color'],
            markeredgecolor=props['edgecolor'],
            markeredgewidth=props['linewidth'],
            zorder=props['zorder'])

def plot_all_data_points(ax):
    """
    Plot all data points on the chart.
    Note: This only plots the markers, not the labels.
    Labels will be added in a separate module to ensure they appear on top.
    
    Args:
        ax: Matplotlib axis object
    """
    for data_point in DATA_POINTS:
        plot_data_point(ax, 
                       data_point['x'], 
                       data_point['y'], 
                       data_point['category'])

def setup_data_points(ax):
    """
    Main function to set up all data points.
    
    Args:
        ax: Matplotlib axis object
    """
    plot_all_data_points(ax)
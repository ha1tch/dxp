"""
Module for adding labels to data points on the chart
Labels are displaced downward by 0.625 × label height
"""

import matplotlib.pyplot as plt
from distributed_systems_data import *

def get_label_properties():
    """
    Get standard label text properties.
    
    Returns:
        dict: Label properties for matplotlib text
    """
    return {
        'fontsize': 6,
        'fontfamily': 'sans-serif',
        'color': '#333333',
        'ha': 'center',
        'va': 'top',
        'zorder': 20  # Ensure labels are drawn above data points
    }

def calculate_label_offset(ax, fontsize=6):
    """
    Calculate the Y offset for labels based on 0.625 × label height.
    
    Args:
        ax: Matplotlib axis object
        fontsize: Font size in points
    
    Returns:
        float: Y offset in data coordinates
    """
    # Create a temporary text object to measure height
    temp_text = ax.text(0, 0, 'Test', fontsize=fontsize, fontfamily='sans-serif')
    
    # Get the bounding box in display coordinates
    bbox = temp_text.get_window_extent(ax.figure.canvas.get_renderer())
    
    # Convert height from display to data coordinates
    inv_transform = ax.transData.inverted()
    _, height_data = inv_transform.transform((0, bbox.height)) - inv_transform.transform((0, 0))
    
    # Remove temporary text
    temp_text.remove()
    
    # Return 0.625 × height (note: height is negative in inverted Y coordinates)
    return -1.2 * height_data

def add_data_point_labels(ax):
    """
    Add labels for all data points.
    
    Args:
        ax: Matplotlib axis object
    """
    props = get_label_properties()
    
    # Calculate the label offset
    y_offset = calculate_label_offset(ax, props['fontsize'])
    
    # Add label for each data point
    for data_point in DATA_POINTS:
        label_x = data_point['x']
        label_y = data_point['y'] + y_offset
        
        ax.text(label_x, label_y, data_point['name'], **props)
    
    # Add special annotations (like "deterministic" for Calvin)
    for annotation in ANNOTATIONS:
        label_x = annotation['x']
        label_y = annotation['y'] + y_offset
        
        ax.text(label_x, label_y, annotation['name'], **props)

def setup_labels(ax):
    """
    Main function to set up all labels.
    Must be called AFTER data points have been plotted.
    
    Args:
        ax: Matplotlib axis object
    """
    # Force a draw to ensure proper text measurements
    ax.figure.canvas.draw()
    
    # Add all labels
    add_data_point_labels(ax)

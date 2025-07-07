"""
Module for setting up the chart figure, titles, and references
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from distributed_systems_data import *

def create_figure(width_px=864, height_px=864, dpi=100):
    """
    Create the matplotlib figure with proper dimensions.
    
    Args:
        width_px: Width in pixels (default from original SVG)
        height_px: Height in pixels (default from original SVG)
        dpi: Dots per inch
    
    Returns:
        fig, ax: Matplotlib figure and axis objects
    """
    # Convert pixels to inches for matplotlib
    width_inches = width_px / dpi
    height_inches = height_px / dpi
    
    # Create figure with white background
    fig = plt.figure(figsize=(width_inches, height_inches), dpi=dpi, facecolor='white')
    
    # Create axis that fills the entire figure
    ax = fig.add_axes([0, 0, 1, 1])
    
    # Set the view limits to match SVG coordinates
    ax.set_xlim(0, width_px)
    ax.set_ylim(height_px, 0)  # Inverted Y-axis to match SVG
    
    # Remove default matplotlib styling
    ax.set_aspect('equal')
    ax.axis('off')
    
    return fig, ax

def add_main_title(ax):
    """
    Add the main chart title.
    
    Args:
        ax: Matplotlib axis object
    """
    # Title position from SVG
    title_x = 232.168456
    title_y = 22.658824
    
    ax.text(title_x, title_y, CHART_TITLE,
            fontsize=16, fontweight='bold', fontfamily='sans-serif',
            color='#333333', transform=ax.transData)

def add_axis_labels(ax):
    """
    Add the X and Y axis labels.
    
    Args:
        ax: Matplotlib axis object
    """
    # X-axis label (Coordination Intensity →)
    x_label_x = 400.63369
    x_label_y = 851.287489
    
    ax.text(x_label_x, x_label_y, X_AXIS_LABEL,
            fontsize=13, fontweight='bold', fontfamily='sans-serif',
            color='#1a1a1a', ha='center', transform=ax.transData)
    
    # Y-axis label (Agreement Scope ↑) - rotated 90 degrees
    y_label_x = 19.919099
    y_label_y = 494.545781
    
    ax.text(y_label_x, y_label_y, Y_AXIS_LABEL,
            fontsize=13, fontweight='bold', fontfamily='sans-serif',
            color='#1a1a1a', rotation=90, ha='center', va='center',
            transform=ax.transData)

def add_legend(ax):
    """
    Add the category legend.
    
    Args:
        ax: Matplotlib axis object
    """
    # Legend starting position
    legend_x = 146.729412
    legend_y_start = 45.257261
    legend_spacing = 14.678125  # Spacing between legend items
    
    # Add "Category" header
    ax.text(154.952068, legend_y_start, "Category",
            fontsize=10, fontfamily='sans-serif', color='#333333')
    
    # Add each category
    y_offset = 11.178125  # Initial offset from header
    for i, (key, cat_info) in enumerate(CATEGORIES.items()):
        y_pos = legend_y_start + y_offset + (i * legend_spacing)
        
        # Draw marker
        if cat_info['marker'] == 'triangle':
            marker = plt.Line2D([legend_x], [y_pos], marker='^', 
                              markersize=8, markerfacecolor=cat_info['color'],
                              markeredgewidth=0.5, markeredgecolor='white',
                              linestyle='none')
        elif cat_info['marker'] == 'star':
            marker = plt.Line2D([legend_x], [y_pos], marker='*', 
                              markersize=10, markerfacecolor=cat_info['color'],
                              markeredgewidth=0.5, markeredgecolor='white',
                              linestyle='none')
        elif cat_info['marker'] == 'square':
            marker = plt.Line2D([legend_x], [y_pos], marker='s', 
                              markersize=8, markerfacecolor=cat_info['color'],
                              markeredgewidth=0.5, markeredgecolor='white',
                              linestyle='none')
        else:  # circle
            marker = plt.Line2D([legend_x], [y_pos], marker='o', 
                              markersize=8, markerfacecolor=cat_info['color'],
                              markeredgewidth=0.5, markeredgecolor='white',
                              linestyle='none')
        
        ax.add_line(marker)
        
        # Add label text
        ax.text(legend_x + 18, y_pos + 3.5, cat_info['label'],
                fontsize=10, fontfamily='sans-serif', color='#333333')

def setup_chart():
    """
    Main function to set up the chart with titles and references.
    
    Returns:
        fig, ax: Configured matplotlib figure and axis objects
    """
    fig, ax = create_figure()
    add_main_title(ax)
    add_axis_labels(ax)
    add_legend(ax)
    
    return fig, ax
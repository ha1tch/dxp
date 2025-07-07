"""
Module for setting up chart axes, grid lines, and tick labels
"""

import matplotlib.pyplot as plt
import matplotlib.lines as mlines
from distributed_systems_data import *

def draw_plot_area_border(ax):
    """
    Draw the border around the main plot area.
    
    Args:
        ax: Matplotlib axis object
    """
    plot_area = CHART_DIMENSIONS['plot_area']
    
    # Draw rectangle border
    border = plt.Rectangle((plot_area['x'], plot_area['y']), 
                          plot_area['width'], plot_area['height'],
                          linewidth=1, edgecolor='#1a1a1a', 
                          facecolor='none')
    ax.add_patch(border)

def add_x_axis_ticks_and_labels(ax):
    """
    Add X-axis tick marks, labels, and grid lines.
    
    Args:
        ax: Matplotlib axis object
    """
    plot_area = CHART_DIMENSIONS['plot_area']
    
    for category_name, rtt_label, x_pos in X_AXIS_CATEGORIES:
        # Draw grid line (dashed)
        ax.plot([x_pos, x_pos], 
                [plot_area['y'], plot_area['y'] + plot_area['height']],
                color='#d3d3d3', alpha=0.7, linewidth=0.4, 
                linestyle='--', dashes=(1.48, 0.64))
        
        # Draw tick mark
        tick_length = 3.5
        ax.plot([x_pos, x_pos],
                [plot_area['y'] + plot_area['height'], 
                 plot_area['y'] + plot_area['height'] + tick_length],
                color='#1a1a1a', linewidth=0.8)
        
        # Add category label
        label_y = plot_area['y'] + plot_area['height'] + 10.3
        ax.text(x_pos, label_y, category_name,
                fontsize=9, fontfamily='sans-serif', color='#1a1a1a',
                ha='center', va='top')
        
        # Add RTT label
        rtt_y = label_y + 10.1
        ax.text(x_pos, rtt_y, rtt_label,
                fontsize=9, fontfamily='sans-serif', color='#1a1a1a',
                ha='center', va='top')

def add_y_axis_ticks_and_labels(ax):
    """
    Add Y-axis tick marks, labels, and grid lines.
    
    Args:
        ax: Matplotlib axis object
    """
    plot_area = CHART_DIMENSIONS['plot_area']
    
    for category_name, percentage, y_pos in Y_AXIS_CATEGORIES:
        # Draw grid line (dashed)
        ax.plot([plot_area['x'], plot_area['x'] + plot_area['width']], 
                [y_pos, y_pos],
                color='#d3d3d3', alpha=0.7, linewidth=0.4, 
                linestyle='--', dashes=(1.48, 0.64))
        
        # Draw tick mark
        tick_length = 3.5
        ax.plot([plot_area['x'] - tick_length, plot_area['x']],
                [y_pos, y_pos],
                color='#1a1a1a', linewidth=0.8)
        
        # Add label (combination of category name and percentage)
        label_text = f"{category_name} ({percentage})"
        label_x = plot_area['x'] - 10
        
        ax.text(label_x, y_pos, label_text,
                fontsize=9, fontfamily='sans-serif', color='#1a1a1a',
                ha='right', va='center')

def draw_trade_off_line(ax):
    """
    Draw the natural trade-off line.
    
    Args:
        ax: Matplotlib axis object
    """
    # Draw the diagonal line
    ax.plot([TRADE_OFF_LINE['start']['x'], TRADE_OFF_LINE['end']['x']],
            [TRADE_OFF_LINE['start']['y'], TRADE_OFF_LINE['end']['y']],
            color='#808080', alpha=0.6, linewidth=1)
    
    # Add the rotated label
    # Calculate angle of the line
    dx = TRADE_OFF_LINE['end']['x'] - TRADE_OFF_LINE['start']['x']
    dy = TRADE_OFF_LINE['end']['y'] - TRADE_OFF_LINE['start']['y']
    angle = -45  # Original uses 315 degrees, which is -45 in standard notation
    
    # Position label at midpoint of the line
    mid_x = (TRADE_OFF_LINE['start']['x'] + TRADE_OFF_LINE['end']['x']) / 2
    mid_y = (TRADE_OFF_LINE['start']['y'] + TRADE_OFF_LINE['end']['y']) / 2
    
    ax.text(mid_x, mid_y, TRADE_OFF_LINE['label'],
            fontsize=8, fontfamily='sans-serif', color='#808080',
            rotation=angle, ha='center', va='bottom')

def setup_axes(ax):
    """
    Main function to set up all axes elements.
    
    Args:
        ax: Matplotlib axis object
    """
    draw_plot_area_border(ax)
    add_x_axis_ticks_and_labels(ax)
    add_y_axis_ticks_and_labels(ax)
    draw_trade_off_line(ax)
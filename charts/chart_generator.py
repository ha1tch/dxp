"""
Main module to generate the complete Distributed Systems State-Convergence Chart
This module orchestrates all the individual components to create the final chart.
"""

import matplotlib.pyplot as plt
from chart_setup_module import setup_chart
from chart_axes_module import setup_axes
from chart_regions_module import setup_regions
from chart_datapoints_module import setup_data_points
from chart_labels_module import setup_labels

def generate_chart(output_filename=None, dpi=100, show_plot=True, include_regions=True):
    """
    Generate the complete distributed systems state-convergence chart.
    
    Args:
        output_filename: If provided, save the chart to this file (e.g., 'chart.png', 'chart.svg')
        dpi: Dots per inch for the output (default: 100)
        show_plot: Whether to display the plot interactively (default: True)
        include_regions: Whether to include highlighted regions (default: True)
    
    Returns:
        fig, ax: Matplotlib figure and axis objects
    """
    # Step 1: Set up the basic chart structure (figure, titles, legend)
    print("Setting up chart structure...")
    fig, ax = setup_chart()
    
    # Step 2: Set up axes (borders, grid lines, ticks, labels, trade-off line)
    print("Setting up axes and grid...")
    setup_axes(ax)
    
    # Step 3: Add highlighted regions (if requested)
    if include_regions:
        print("Adding highlighted regions...")
        setup_regions(ax)
    
    # Step 4: Plot all data points (markers only, no labels yet)
    print("Plotting data points...")
    setup_data_points(ax)
    
    # Step 5: Add labels (must be done last to ensure they appear on top)
    print("Adding labels...")
    setup_labels(ax)
    
    # Save the chart if filename is provided
    if output_filename:
        print(f"Saving chart to {output_filename}...")
        # Determine format from filename
        if output_filename.endswith('.svg'):
            fig.savefig(output_filename, format='svg', dpi=dpi, bbox_inches='tight')
        elif output_filename.endswith('.pdf'):
            fig.savefig(output_filename, format='pdf', dpi=dpi, bbox_inches='tight')
        else:
            # Default to PNG for other extensions
            fig.savefig(output_filename, dpi=dpi, bbox_inches='tight')
        print(f"Chart saved successfully!")
    
    # Show the plot if requested
    if show_plot:
        plt.show()
    
    return fig, ax

def generate_high_quality_chart(output_filename='distributed_systems_chart.png'):
    """
    Generate a high-quality version of the chart suitable for publication.
    
    Args:
        output_filename: Output filename (default: 'distributed_systems_chart.png')
    
    Returns:
        fig, ax: Matplotlib figure and axis objects
    """
    return generate_chart(output_filename=output_filename, dpi=300, show_plot=False)

def generate_svg_chart(output_filename='distributed_systems_chart.svg'):
    """
    Generate an SVG version of the chart (vector format, scalable).
    
    Args:
        output_filename: Output filename (default: 'distributed_systems_chart.svg')
    
    Returns:
        fig, ax: Matplotlib figure and axis objects
    """
    return generate_chart(output_filename=output_filename, show_plot=False)

if __name__ == "__main__":
    # Example usage: generate and display the chart
    print("Generating Distributed Systems State-Convergence Chart...")
    fig, ax = generate_chart()
    
    # Optionally save in multiple formats
    # generate_high_quality_chart('chart_high_res.png')
    # generate_svg_chart('chart_vector.svg')
    
    # Generate without regions
    # fig, ax = generate_chart(include_regions=False)
    
    print("Chart generation complete!")
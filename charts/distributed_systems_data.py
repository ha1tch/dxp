"""
Distributed Systems State-Convergence Chart Data
Extracted from the Full-Spectrum State-Convergence Map SVG
"""

# Chart metadata
CHART_TITLE = "Full-Spectrum State-Convergence Map (All Original Data)"
X_AXIS_LABEL = "Coordination Intensity →"
Y_AXIS_LABEL = "Agreement Scope ↑"

# X-axis categories (from left to right)
X_AXIS_CATEGORIES = [
    ("None", "~0 RTT", 188.185294),
    ("Async", "~0.5 RTT", 309.097059),
    ("Multi‑hop", "~1.0 RTT", 430.008824),
    ("Phased", "~1.5 RTT", 550.920588),
    ("Lock‑step", "~2.0 RTT", 671.832353),
    ("Atomic", "~2.5 RTT", 792.744118)
]

# Y-axis categories (from bottom to top)
Y_AXIS_CATEGORIES = [
    ("None", "0%", 779.372888),
    ("Any", "25%", 600.631444),
    ("Weak quorum", "50%", 421.89),
    ("Strong quorum", "75%", 243.148556),
    ("All", "100%", 64.407112)
]

# Categories for different system types
CATEGORIES = {
    "messaging": {"color": "#1f77b4", "marker": "triangle", "label": "Messaging"},
    "pattern": {"color": "#d62728", "marker": "star", "label": "Pattern"},
    "db": {"color": "#2ca02c", "marker": "square", "label": "DB"},
    "consensus": {"color": "#9467bd", "marker": "circle", "label": "Consensus"},
    "blockchain": {"color": "#ff7f0e", "marker": "circle", "label": "Blockchain"}
}

# All data points with their coordinates and metadata
DATA_POINTS = [
    # Messaging Systems
    {"name": "Kafka", "x": 218.413235, "y": 779.372888, "category": "messaging"},
    {"name": "Pulsar", "x": 248.641176, "y": 696.876837, "category": "messaging"},
    {"name": "EventStore", "x": 309.097059, "y": 674.87789, "category": "messaging"},
    
    # Patterns
    {"name": "Fire & Forget", "x": 263.755147, "y": 614.380786, "category": "pattern"},
    {"name": "0.5PS", "x": 278.869118, "y": 779.372888, "category": "pattern"},
    {"name": "Saga", "x": 399.780882, "y": 724.37552, "category": "pattern"},
    {"name": "1.5PS", "x": 460.236765, "y": 619.880522, "category": "pattern"},
    {"name": "Practical Consensus", "x": 490.464706, "y": 284.396582, "category": "pattern"},
    {"name": "2PS", "x": 581.148529, "y": 179.901584, "category": "pattern"},
    {"name": "3PS", "x": 641.604412, "y": 124.904216, "category": "pattern"},
    {"name": "2PC", "x": 702.060294, "y": 69.906849, "category": "pattern"},
    {"name": "Full ACID", "x": 717.174265, "y": 64.407112, "category": "pattern"},
    
    # Databases
    {"name": "SimpleDB", "x": 236.55, "y": 619.880522, "category": "db"},
    {"name": "Cassandra(ONE)", "x": 290.960294, "y": 691.3771, "category": "db"},
    {"name": "Cassandra(QUORUM)", "x": 290.960294, "y": 471.387631, "category": "db"},
    {"name": "Cassandra(ALL)", "x": 290.960294, "y": 196.400794, "category": "db"},
    {"name": "DynamoDB", "x": 339.325, "y": 619.880522, "category": "db"},
    {"name": "Riak", "x": 369.552941, "y": 509.885788, "category": "db"},
    {"name": "Redis", "x": 430.008824, "y": 564.883155, "category": "db"},
    {"name": "MongoDB(w:1)", "x": 502.555882, "y": 636.379733, "category": "db"},
    {"name": "MongoDB(majority)", "x": 502.555882, "y": 416.390263, "category": "db"},
    {"name": "MongoDB(all)", "x": 502.555882, "y": 141.403427, "category": "db"},
    {"name": "NuoDB", "x": 611.376471, "y": 564.883155, "category": "db"},
    {"name": "Galera", "x": 641.604412, "y": 399.891053, "category": "db"},
    {"name": "Oracle RAC", "x": 671.832353, "y": 102.905269, "category": "db"},
    {"name": "Spanner", "x": 732.288235, "y": 69.906849, "category": "db"},
    {"name": "CockroachDB", "x": 702.060294, "y": 174.401847, "category": "db"},
    {"name": "TiDB", "x": 762.516176, "y": 102.905269, "category": "db"},
    {"name": "Calvin", "x": 369.552941, "y": 124.904216, "category": "db"},
    {"name": "FaunaDB", "x": 399.780882, "y": 102.905269, "category": "db"},
    {"name": "FoundationDB", "x": 671.832353, "y": 229.399214, "category": "db"},
    
    # Consensus Protocols
    {"name": "Paxos", "x": 490.464706, "y": 394.391316, "category": "consensus"},
    {"name": "Raft", "x": 520.692647, "y": 322.894739, "category": "consensus"},
    {"name": "Zab", "x": 550.920588, "y": 394.391316, "category": "consensus"},
    {"name": "EPaxos", "x": 460.236765, "y": 449.388684, "category": "consensus"},
    {"name": "PBFT", "x": 581.148529, "y": 289.896318, "category": "consensus"},
    {"name": "Chain Repl.", "x": 309.097059, "y": 559.383418, "category": "consensus"},
]

# Special annotations
ANNOTATIONS = [
    {"name": "(deterministic)", "x": 369.552941, "y": 108.405006, "parent": "Calvin"}
]

# Natural trade-off line coordinates
TRADE_OFF_LINE = {
    "start": {"x": 188.185294, "y": 743.624599},
    "end": {"x": 792.744118, "y": 100.155401},
    "label": "Natural Trade‑off Line"
}

# Chart dimensions
CHART_DIMENSIONS = {
    "width": 864,
    "height": 864,
    "plot_area": {
        "x": 127.729412,
        "y": 28.658824,
        "width": 725.470588,
        "height": 786.462353
    }
}

def get_x_position_for_category(category_name):
    """Get the x-coordinate for a given x-axis category name."""
    for name, rtt, x_pos in X_AXIS_CATEGORIES:
        if name == category_name:
            return x_pos
    return None

def get_y_position_for_category(category_name):
    """Get the y-coordinate for a given y-axis category name."""
    for name, percentage, y_pos in Y_AXIS_CATEGORIES:
        if name == category_name:
            return y_pos
    return None

def get_systems_by_category(category):
    """Get all systems belonging to a specific category."""
    return [dp for dp in DATA_POINTS if dp["category"] == category]

def get_system_coordinates(system_name):
    """Get the coordinates for a specific system."""
    for dp in DATA_POINTS:
        if dp["name"] == system_name:
            return (dp["x"], dp["y"])
    return None
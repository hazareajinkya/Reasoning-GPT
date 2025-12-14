"""
Generate ASCII art representations of charts and diagrams for DILR problems.
This avoids expensive image generation while providing visual aids.
"""


def generate_pie_chart_ascii(data: dict, title: str = "") -> str:
    """
    Generate ASCII pie chart representation.
    
    Args:
        data: Dict with labels and values, e.g., {"A": 30, "B": 40, "C": 30}
        title: Chart title
    
    Returns:
        ASCII representation of pie chart
    """
    total = sum(data.values())
    if total == 0:
        return "No data to display"
    
    result = []
    if title:
        result.append(f"📊 {title}")
        result.append("")
    
    # Calculate percentages and create visual representation
    sorted_data = sorted(data.items(), key=lambda x: x[1], reverse=True)
    
    result.append("Pie Chart Representation:")
    result.append("")
    
    # Create a simple visual using characters
    for label, value in sorted_data:
        percentage = (value / total) * 100
        bar_length = int(percentage / 2)  # Scale for display
        bar = "█" * bar_length
        result.append(f"{label}: {bar} {percentage:.1f}% ({value})")
    
    result.append("")
    result.append("Total: " + str(total))
    
    return "\n".join(result)


def generate_bar_chart_ascii(data: dict, title: str = "", max_height: int = 20) -> str:
    """
    Generate ASCII bar chart representation.
    
    Args:
        data: Dict with labels and values
        title: Chart title
        max_height: Maximum height of bars in characters
    
    Returns:
        ASCII bar chart
    """
    if not data:
        return "No data to display"
    
    max_value = max(data.values())
    if max_value == 0:
        return "No data to display"
    
    result = []
    if title:
        result.append(f"📊 {title}")
        result.append("")
    
    # Find max label length for alignment
    max_label_len = max(len(str(k)) for k in data.keys())
    
    # Create bars
    sorted_data = sorted(data.items(), key=lambda x: x[1], reverse=True)
    
    for label, value in sorted_data:
        bar_height = int((value / max_value) * max_height)
        bar = "█" * bar_height if bar_height > 0 else "▁"
        percentage = (value / max_value) * 100 if max_value > 0 else 0
        label_padded = str(label).ljust(max_label_len)
        result.append(f"{label_padded} │{bar} {value} ({percentage:.1f}%)")
    
    result.append(" " * (max_label_len + 2) + "└" + "─" * max_height)
    
    return "\n".join(result)


def generate_line_chart_ascii(data: list, title: str = "", width: int = 50, height: int = 10) -> str:
    """
    Generate ASCII line chart representation.
    
    Args:
        data: List of (x, y) tuples or dict with x and y lists
        title: Chart title
        width: Chart width in characters
        height: Chart height in characters
    
    Returns:
        ASCII line chart
    """
    result = []
    if title:
        result.append(f"📈 {title}")
        result.append("")
    
    # Simple line chart representation
    if isinstance(data, dict) and 'x' in data and 'y' in data:
        points = list(zip(data['x'], data['y']))
    elif isinstance(data, list):
        points = data
    else:
        return "Invalid data format"
    
    if not points:
        return "No data to display"
    
    max_y = max(y for _, y in points)
    min_y = min(y for _, y in points)
    y_range = max_y - min_y if max_y != min_y else 1
    
    # Create grid
    chart = [[' ' for _ in range(width)] for _ in range(height)]
    
    # Plot points
    for i, (x, y) in enumerate(points):
        x_pos = int((i / (len(points) - 1)) * (width - 1)) if len(points) > 1 else width // 2
        y_pos = int(((y - min_y) / y_range) * (height - 1))
        y_pos = height - 1 - y_pos  # Flip Y axis
        if 0 <= x_pos < width and 0 <= y_pos < height:
            chart[y_pos][x_pos] = '●'
    
    # Add axes and labels
    result.append(" " + "─" * width)
    for row in chart:
        result.append("│" + "".join(row))
    result.append("└" + "─" * width)
    
    return "\n".join(result)


def generate_venn_diagram_ascii(sets: dict, overlaps: dict = None) -> str:
    """
    Generate ASCII Venn diagram representation.
    
    Args:
        sets: Dict with set names and their elements, e.g., {"A": [1,2,3], "B": [3,4,5]}
        overlaps: Dict with overlap regions and elements
    
    Returns:
        ASCII Venn diagram
    """
    result = []
    result.append("Venn Diagram Structure:")
    result.append("")
    
    # Simple text-based representation
    if len(sets) == 2:
        set_a = sets.get('A', [])
        set_b = sets.get('B', [])
        overlap = [x for x in set_a if x in set_b]
        only_a = [x for x in set_a if x not in set_b]
        only_b = [x for x in set_b if x not in set_a]
        
        result.append("    ┌─────────┐")
        result.append("    │    A    │")
        result.append("┌───┼─────────┼───┐")
        result.append("│   │ A ∩ B   │   │")
        result.append("│ B │         │ A │")
        result.append("└───┼─────────┼───┘")
        result.append("    │    B    │")
        result.append("    └─────────┘")
        result.append("")
        result.append(f"Only A: {only_a}")
        result.append(f"Only B: {only_b}")
        result.append(f"A ∩ B: {overlap}")
    
    elif len(sets) == 3:
        result.append("3-Set Venn Diagram:")
        result.append("")
        result.append("        ┌─────┐")
        result.append("       │  A   │")
        result.append("    ┌──┼──────┼──┐")
        result.append("    │  │A∩B∩C│  │")
        result.append("  ┌─┼──┼──────┼──┼─┐")
        result.append("  │ │  │      │  │ │")
        result.append("  │B│  │  C   │  │A│")
        result.append("  └─┼──┼──────┼──┼─┘")
        result.append("    │  │      │  │")
        result.append("    └──┼──────┼──┘")
        result.append("       │  B   │")
        result.append("       └─────┘")
        result.append("")
        for name, elements in sets.items():
            result.append(f"Set {name}: {elements}")
    
    else:
        # Generic representation
        for name, elements in sets.items():
            result.append(f"Set {name}: {elements}")
        if overlaps:
            result.append("")
            result.append("Overlaps:")
            for region, elements in overlaps.items():
                result.append(f"  {region}: {elements}")
    
    return "\n".join(result)



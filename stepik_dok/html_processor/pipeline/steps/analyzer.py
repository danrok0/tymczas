from collections import defaultdict

def analyze_data(parsed_data, options=None):
    """Analyzes the parsed data according to the provided options.
    
    Args:
        parsed_data: List of dictionaries containing table data
        options: Dictionary of analysis options (calculate_totals, group_by_category, etc.)
    
    Returns:
        List of dictionaries with analyzed data
    """
    if not options:
        return parsed_data

    analyzed_data = []
    
    if options.get('calculate_totals', False):
        # Calculate totals for numeric columns
        totals = defaultdict(float)
        for row in parsed_data:
            for key, value in row.items():
                try:
                    totals[key] += float(value.replace(',', ''))
                except (ValueError, AttributeError):
                    continue
        analyzed_data.append({'Type': 'Totals', **{k: f"{v:.2f}" for k, v in totals.items()}})
    
    if options.get('group_by_category', False):
        # Group data by first column
        categories = defaultdict(list)
        first_col = list(parsed_data[0].keys())[0] if parsed_data else None
        if first_col:
            for row in parsed_data:
                categories[row[first_col]].append(row)
            for category, items in categories.items():
                analyzed_data.append({'Category': category, 'Count': len(items)})

    # Add original data if we calculated anything
    if analyzed_data:
        analyzed_data.extend(parsed_data)
    else:
        analyzed_data = parsed_data

    return analyzed_data
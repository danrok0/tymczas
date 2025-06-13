from collections import defaultdict

def analyze_data(parsed_data, options=None):
    """Analyzes the parsed data according to the provided options.
    
    Args:
        parsed_data: Dictionary containing parsed HTML data
        options: Dictionary of analysis options (calculate_totals, group_by_category, etc.)
    
    Returns:
        Dict with original data plus analysis results
    """
    result = parsed_data.copy()  # Keep all original data
    result['totals'] = None
    result['categories'] = None
    
    if not options:
        return result

    data = parsed_data.get('data', [])
    if not data:
        return result

    if options.get('calculate_totals', False):
        # Calculate totals for numeric columns
        totals = defaultdict(float)
        for row in data:
            for key, value in row.items():
                try:
                    totals[key] += float(value.replace(',', '').replace(' ', ''))
                except (ValueError, AttributeError):
                    continue
        result['totals'] = {k: f"{v:.2f}" for k, v in totals.items()}
    
    if options.get('group_by_category', False):
        # Group data by first column
        categories = defaultdict(list)
        first_col = list(data[0].keys())[0] if data else None
        if first_col:
            for row in data:
                categories[row[first_col]].append(row)
            result['categories'] = [{'Category': category, 'Count': len(items)} for category, items in categories.items()]

    return result
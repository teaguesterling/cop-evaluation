from concept_python import intent, invariant, human_decision, ai_implement


def process_data(data, mode, debug=False):
    """COP Annotations:
@intent("Process data in various modes with flexible input formats")
@invariant("Function must always return a dictionary with results")
@invariant("All numeric processing must handle both numbers and numeric strings")"""
    result = {}
    if debug:
        print('Starting data processing')

    @intent('Standardize input data into a consistent format')
    @ai_implement(
        'Normalize various input formats into a standard list of items',
        constraints=['Must handle dictionaries, lists, and scalar values',
        'Must preserve important item attributes',
        'Must handle edge cases gracefully'])
    def normalize_data(data):
        if isinstance(data, dict):
            if debug:
                print('Processing dictionary data')
            if 'items' in data:
                return data['items']
            else:
                items = []
                for key, value in data.items():
                    items.append({'key': key, 'value': value})
                return items
        elif isinstance(data, list):
            if debug:
                print('Processing list data')
            return data
        else:
            if debug:
                print(f'Converting {type(data)} to list')
            return [data]

    @intent('Extract numeric value from various item formats')
    def extract_value(item):
        if isinstance(item, dict) and 'value' in item:
            value = item['value']
        elif isinstance(item, dict) and 'amount' in item:
            value = item['amount']
        elif isinstance(item, (int, float)):
            value = item
        else:
            if debug:
                print(f'Skipping item: {item}')
            return None
        if isinstance(value, (int, float)):
            return value
        elif isinstance(value, str) and value.isdigit():
            return float(value)
        else:
            if debug:
                print(f'Cannot process value: {value}')
            return None
    items = normalize_data(data)

    @intent('Calculate sum of all numeric values in the data')
    def calculate_sum():
        total = 0
        for item in items:
            value = extract_value(item)
            if value is not None:
                total += value
        if debug:
            print(f'Final total: {total}')
        return {'total': total}

    @intent('Transform data by doubling numeric values')
    def transform_data():
        transformed = []
        for item in items:
            if isinstance(item, dict):
                new_item = {}
                for k, v in item.items():
                    if k in ['value', 'amount', 'quantity', 'price']:
                        if isinstance(v, (int, float)):
                            new_item[k] = v * 2
                        elif isinstance(v, str) and v.isdigit():
                            new_item[k] = float(v) * 2
                        else:
                            new_item[k] = v
                    else:
                        new_item[k] = v
                transformed.append(new_item)
            elif isinstance(item, (int, float)):
                transformed.append(item * 2)
            elif isinstance(item, str) and item.isdigit():
                transformed.append(float(item) * 2)
            else:
                transformed.append(item)
                if debug:
                    print(f'Not transforming: {item}')
        if debug:
            print(f'Transformed: {transformed}')
        return {'transformed': transformed}

    @intent('Calculate statistical measures for numeric values')
    def calculate_stats():
        if len(items) == 0:
            if debug:
                print('No items to process')
            return {'count': 0, 'avg': 0, 'min': 0, 'max': 0}
        values = []
        for item in items:
            value = extract_value(item)
            if value is not None:
                values.append(value)
        if not values:
            return {'count': 0, 'avg': 0, 'min': 0, 'max': 0}
        stats = {'count': len(values), 'avg': sum(values) / len(values),
            'min': min(values), 'max': max(values)}
        if debug:
            print(f'Stats: {stats}')
        return stats

    @intent('Select and execute the appropriate processing mode')
    @human_decision('Define data processing modes and their behavior',
        roles=['Data Analyst', 'System Architect'])
    def process_by_mode():
        if mode == 'sum':
            return calculate_sum()
        elif mode == 'transform':
            return transform_data()
        elif mode == 'stats':
            return calculate_stats()
        else:
            if debug:
                print(f'Unknown mode: {mode}')
            return {'error': f'Unknown mode: {mode}'}
    mode_result = process_by_mode()
    result.update(mode_result)
    result['processed'] = True
    result['mode'] = mode
    if debug:
        print('Processing complete')
    return result

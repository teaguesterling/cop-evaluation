# test_cases/anti_patterns/spaghetti_code/base.py
def process_data(data, mode, debug=False):
    result = {}
    
    if debug:
        print("Starting data processing")
    
    # Check data format
    if isinstance(data, dict):
        if debug:
            print("Processing dictionary data")
        
        if "items" in data:
            items = data["items"]
        else:
            items = []
            for key, value in data.items():
                items.append({"key": key, "value": value})
    elif isinstance(data, list):
        if debug:
            print("Processing list data")
        items = data
    else:
        if debug:
            print(f"Converting {type(data)} to list")
        items = [data]
    
    # Process based on mode
    if mode == "sum":
        total = 0
        for item in items:
            if isinstance(item, dict) and "value" in item:
                value = item["value"]
            elif isinstance(item, dict) and "amount" in item:
                value = item["amount"]
            elif isinstance(item, (int, float)):
                value = item
            else:
                if debug:
                    print(f"Skipping item: {item}")
                continue
                
            if isinstance(value, (int, float)):
                total += value
            elif isinstance(value, str) and value.isdigit():
                total += float(value)
            else:
                if debug:
                    print(f"Cannot process value: {value}")
        
        result["total"] = total
        
        if debug:
            print(f"Final total: {total}")
    
    elif mode == "transform":
        transformed = []
        for item in items:
            if isinstance(item, dict):
                new_item = {}
                for k, v in item.items():
                    if k in ["value", "amount", "quantity", "price"]:
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
                    print(f"Not transforming: {item}")
        
        result["transformed"] = transformed
        
        if debug:
            print(f"Transformed: {transformed}")
    
    elif mode == "stats":
        if len(items) == 0:
            result["count"] = 0
            result["avg"] = 0
            result["min"] = 0
            result["max"] = 0
            
            if debug:
                print("No items to process")
            
            return result
        
        count = 0
        total = 0
        min_val = float('inf')
        max_val = float('-inf')
        
        for item in items:
            if isinstance(item, dict) and "value" in item:
                value = item["value"]
            elif isinstance(item, dict) and "amount" in item:
                value = item["amount"]
            elif isinstance(item, (int, float)):
                value = item
            else:
                if debug:
                    print(f"Skipping item: {item}")
                continue
                
            if isinstance(value, (int, float)):
                count += 1
                total += value
                min_val = min(min_val, value)
                max_val = max(max_val, value)
            elif isinstance(value, str) and value.isdigit():
                num_value = float(value)
                count += 1
                total += num_value
                min_val = min(min_val, num_value)
                max_val = max(max_val, num_value)
            else:
                if debug:
                    print(f"Cannot process value: {value}")
        
        if count > 0:
            result["count"] = count
            result["avg"] = total / count
            result["min"] = min_val
            result["max"] = max_val
        else:
            result["count"] = 0
            result["avg"] = 0
            result["min"] = 0
            result["max"] = 0
        
        if debug:
            print(f"Stats: {result}")
    
    else:
        if debug:
            print(f"Unknown mode: {mode}")
        result["error"] = f"Unknown mode: {mode}"
    
    # Add a processed flag
    result["processed"] = True
    result["mode"] = mode
    
    if debug:
        print("Processing complete")
    
    return result

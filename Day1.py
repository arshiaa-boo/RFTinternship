# Project 1 - Data Cleaner (List Processing)
# GOW AI Academy - Python Internship Day 1

data = [10, None, 20, 10, "", 30, None, 40]

def clean_data(data):
    original_count = len(data)
    
    # Remove invalid values (None and empty string)
    valid_data = [item for item in data if item is not None and item != ""]
    
    # Remove duplicates (preserving order)
    seen = []
    for item in valid_data:
        if item not in seen:
            seen.append(item)
    
    # Sort the final list
    clean_list = sorted(seen)
    
    # Count removed values
    removed_count = original_count - len(clean_list)
    
    return clean_list, removed_count


# Run the cleaner
clean_list, removed_count = clean_data(data)

# Output
print("Original Data:  ", data)
print("Cleaned Data:   ", clean_list)
print("Values Removed: ", removed_count)
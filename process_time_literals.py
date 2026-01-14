import re
import json
import sys
import os

raw_output = sys.stdin.read()

parameters = {}
low_confidence_constants = {}

# Split the raw_output into individual file blocks
# re.split will return an empty string at the beginning if the pattern is found at the start
file_blocks = re.split(r'---\nFile: (.+)\n', raw_output)

# The first element is empty if the split pattern was found at the start, so skip it.
# Then process in pairs: (filepath, content)
for i in range(1, len(file_blocks), 2):
    file_path = file_blocks[i].strip()
    content = file_blocks[i+1]

    for line_raw in content.splitlines():
        # Match lines with line number and content
        line_match = re.match(r'L(\d+): (.*)', line_raw)
        if not line_match:
            continue

        line_num = int(line_match.group(1))
        line_content = line_match.group(2)

        extracted_values = []

        # Regex to find T# literals, potentially inside <ConstantValue> or <StartValue>
        # This will capture values like T#5s, t#100ms, LT#10.7S
        time_literal_matches = re.findall(r'(?:(?:<ConstantValue[^>]*>)?|(?:<StartValue[^>]*>)?)(L?T#\d+(?:[.,]\d+)?(?:[dDhHmMsS]+(?:_+\d+[dDhHmMsS]+)*)?)(?:</ConstantValue>)?(?:</StartValue>)?', line_content, re.IGNORECASE)
        for val in time_literal_matches:
            actual_value = next((s for s in val if s), None) # Flatten the tuple of groups
            if actual_value:
                extracted_values.append((actual_value, "Literal"))
        
        # New regex for MaximumStepTime and WarningTime attributes
        step_time_matches = re.findall(r'(MaximumStepTime|WarningTime)="?(L?T#\d+(?:[.,]\d+)?(?:[dDhHmMsS]+(?:_+\d+[dDhHmMsS]+)*)?)?"?', line_content, re.IGNORECASE)
        for attr, value in step_time_matches:
            if value: # Ensure value is not empty
                extracted_values.append((value, attr))

        for time_value_raw, context_type in extracted_values:
            # Standardize time value format (uppercase units, replace ',' with '.')
            time_value = time_value_raw.upper().replace(',', '.')
            if 'MS' in time_value: time_value = time_value.replace('MS', 'ms')
            if 'S' in time_value: time_value = time_value.replace('S', 's')
            if 'M' in time_value and 'MS' not in time_value: time_value = time_value.replace('M', 'm')
            if 'H' in time_value: time_value = time_value.replace('H', 'h')
            if 'D' in time_value: time_value = time_value.replace('D', 'd')
            
            # Further standardization to make sure it's T# and not t#
            if time_value.startswith('T#'):
                time_value = 'T#' + time_value[2:]
            elif time_value.startswith('LT#'):
                time_value = 'LT#' + time_value[3:]


            # Extract basic unit for ProposedName and Unit field
            unit_match = re.search(r'(\d+(?:[.,]\d+)?)([dmsh]+)', time_value, re.IGNORECASE)
            unit = 's' # Default unit
            if unit_match:
                unit = unit_match.group(2).lower()
            elif 'LT#' in time_value: # LT# values often lack explicit units in the literal itself, but imply TIME
                unit = 's' # Assuming long time defaults to seconds if no explicit unit is found

            # Generate a unique key for deduplication
            param_key = time_value

            location_entry = {
                'File': file_path,
                'Line': line_num,
                'Context': line_content.strip()
            }

            # If already processed, add location
            if param_key in parameters:
                parameters[param_key]['Locations'].append(location_entry)
                # If seen multiple times, increase confidence or mark as HIGH
                if len(parameters[param_key]['Locations']) > 1:
                    parameters[param_key]['Confidence'] = 'HIGH'
            else:
                # Infer ProposedName
                proposed_name = ""
                # Use filename or containing block name as a hint
                file_basename = os.path.basename(file_path).replace('.xml', '')
                block_name_match = re.search(r'Program blocks[\\/](?:[^\\/]+[\\/])?([^\\/.]+)\.xml', file_path)
                block_name = block_name_match.group(1) if block_name_match else file_basename

                # Prioritize specific context types
                if context_type == "MaximumStepTime":
                    proposed_name = f"{block_name}StepMaxTime"
                elif context_type == "WarningTime":
                    proposed_name = f"{block_name}StepWarningTime"
                else: # Generic literal
                    # Attempt to get block name from file_path
                    # This is a very basic attempt and might need refinement
                    proposed_name = f"{block_name}Delay{unit.capitalize()}"
                    
                    # Further refinement for common patterns like ST10, OP10
                    parts = re.split(r'[\\/]', file_path)
                    if len(parts) > 1 and 'OP10' in parts[-2]:
                        proposed_name = f"Op10{proposed_name}"
                    elif len(parts) > 1 and 'ST10' in parts[-2]:
                        proposed_name = f"St10{proposed_name}"
                    
                    # Generalizing names for clarity if they are too specific or repetitive
                    proposed_name = proposed_name.replace("Programblocks","").replace(" ","") # clean up

                parameters[param_key] = {
                    'ProposedName': proposed_name,
                    'DataType': 'TIME',
                    'CurrentValue': time_value,
                    'Unit': unit,
                    'Category': 'Timing',
                    'Confidence': 'MED', # Default to medium, will be updated to HIGH if multiple locations
                    'Locations': [location_entry]
                }

# Standardize ProposedNames after initial pass to ensure uniqueness and clarity
# If multiple parameters end up with the same proposed_name, append an index
final_parameters_list = []
name_counter = {}
for param_value_key in sorted(parameters.keys()): # Sort by key for consistent output
    data = parameters[param_value_key]
    base_name = data['ProposedName']
    
    # Simple cleanup of proposed name from common TIA Portal file naming patterns
    base_name = re.sub(r'(ST\d+)|(OP\d+)', '', base_name, flags=re.IGNORECASE)
    base_name = re.sub(r'[\\/_.-]', '', base_name) # Remove special chars
    base_name = re.sub(r'(\d+)', r'_\1', base_name).strip('_') # Add underscore before numbers for better readability
    base_name = base_name.replace('__', '_') # Remove double underscores
    
    # Capitalize first letter of each word to make it PascalCase like
    # Use regex to find word boundaries for proper PascalCase conversion
    pascal_case_name = "".join(word.capitalize() for word in re.split(r'(?=[A-Z])|_', base_name) if word)


    
    # Ensure uniqueness across all proposed names
    unique_name_candidate = pascal_case_name
    count = 1
    while unique_name_candidate in name_counter:
        unique_name_candidate = f"{pascal_case_name}{count}"
        count += 1
    
    name_counter[unique_name_candidate] = True
    data['ProposedName'] = unique_name_candidate
    
    final_parameters_list.append(data)

# Sort the final list by ProposedName
final_parameters_list.sort(key=lambda x: x['ProposedName'])

print(json.dumps(final_parameters_list, indent=2))
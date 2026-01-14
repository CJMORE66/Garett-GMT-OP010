import re

# Read the file
with open(r'D:\AI_ANALYZE\GARRET\TRACING\OP10\EXPORT\Screens\OP010\9MES\920 MES Diagnostics\920MES_Diagnostics.xml', 'r', encoding='utf-8') as f:
    content = f.read()

# Find all IDs and track which ones are used
id_pattern = r'ID="(\d+)"'
ids = re.findall(id_pattern, content)
used_ids = set()

# Replace duplicate IDs starting from 664
next_id = 664

def replace_duplicate_id(match):
    global next_id, used_ids
    id_value = int(match.group(1))

    if id_value in used_ids:
        # This is a duplicate, replace it
        new_id = str(next_id)
        next_id += 1
        return f'ID="{new_id}"'
    else:
        # First occurrence, mark as used
        used_ids.add(id_value)
        return match.group(0)

# Apply the replacement
new_content = re.sub(id_pattern, replace_duplicate_id, content)

# Write back to file
with open(r'D:\AI_ANALYZE\GARRET\TRACING\OP10\EXPORT\Screens\OP010\9MES\920 MES Diagnostics\920MES_Diagnostics.xml', 'w', encoding='utf-8') as f:
    f.write(new_content)

print("Duplicate IDs fixed!")
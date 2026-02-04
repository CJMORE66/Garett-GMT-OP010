import os
import re
from collections import Counter

# Directory with XML files
xml_dir = r"C:\Users\klonkanitka\Desktop\GARRET\OP10\Program blocks\OP010\03_Auto"

# Find all XML files
xml_files = []
for root, dirs, files in os.walk(xml_dir):
    for f in files:
        if f.endswith('.xml'):
            xml_files.append(os.path.join(root, f))

print(f"Found {len(xml_files)} XML files")
print("=" * 80)

# Extract all tags
all_tags = []
for xml_file in xml_files:
    try:
        with open(xml_file, 'r', encoding='utf-8') as f:
            content = f.read()
            # Extract tags (both opening and closing)
            tags = re.findall(r'</?([a-zA-Z][a-zA-Z0-9_:-]*)', content)
            all_tags.extend(tags)
    except Exception as e:
        print(f"Error reading {xml_file}: {e}")

# Count tags
tag_counts = Counter(all_tags)

# Sort by count descending
sorted_tags = sorted(tag_counts.items(), key=lambda x: (-x[1], x[0]))

print(f"\nTotal unique tags: {len(sorted_tags)}")
print(f"Total tag occurrences: {sum(tag_counts.values())}")
print("=" * 80)
print(f"{'Tag':<50} {'Count':>10}")
print("=" * 80)

for tag, count in sorted_tags:
    print(f"{tag:<50} {count:>10}")

# Write to file
with open(r"C:\Users\klonkanitka\Desktop\GARRET\OP10\NEW SCL REFAKTOR\03_Auto\XML_TAG_ANALYSIS.txt", 'w', encoding='utf-8') as f:
    f.write("=" * 80 + "\n")
    f.write("KROK 1: KOMPLETNÍ SYNTAX SCAN\n")
    f.write("TIA Portal V18 GRAPH XML Export\n")
    f.write("=" * 80 + "\n\n")
    f.write(f"Total XML files analyzed: {len(xml_files)}\n")
    f.write(f"Total unique tags: {len(sorted_tags)}\n")
    f.write(f"Total tag occurrences: {sum(tag_counts.values())}\n\n")
    f.write("=" * 80 + "\n")
    f.write(f"{'Tag':<50} {'Count':>10}\n")
    f.write("=" * 80 + "\n")
    for tag, count in sorted_tags:
        f.write(f"{tag:<50} {count:>10}\n")

print(f"\nAnalysis saved to XML_TAG_ANALYSIS.txt")

import os
import re

# Define keywords
safety_keywords = ["Safety", "F-", "EStop", "Guard", "Door", "SafeTorqueOff", "SS1", "SLS", "PROFIsafe", "FailSafe", "SafetyGate", "MaterialGate"]
ob_keywords = ["OB1", "OB100", "OB101", "OB102", "OB82", "OB83", "OB86", "OB121", "OB122", "CYC_INT"]
all_keywords = safety_keywords + ob_keywords

results = []

# Walk through EXPORT directory
for root, dirs, files in os.walk("EXPORT"):
    for file in files:
        if file.endswith(".xml"):
            filepath = os.path.join(root, file)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                for i, line in enumerate(lines):
                    line_num = i + 1
                    for keyword in all_keywords:
                        if re.search(re.escape(keyword), line, re.IGNORECASE):
                            classification = "CRITICAL" if keyword in ob_keywords else "NO-TOUCH"
                            matched_text = keyword
                            context_start = max(0, i - 2)
                            context_end = min(len(lines), i + 3)
                            context = lines[context_start:context_end]
                            results.append({
                                'classification': classification,
                                'file': filepath,
                                'line': line_num,
                                'match': matched_text,
                                'context': context
                            })
            except Exception as e:
                print(f"Error reading {filepath}: {e}")

# Write to safety_report.txt
with open("safety_report.txt", 'w', encoding='utf-8') as f:
    for res in results:
        f.write(f"Classification: {res['classification']}\n")
        f.write(f"File: {res['file']}\n")
        f.write(f"Line: {res['line']}\n")
        f.write(f"Match: {res['match']}\n")
        f.write("Context:\n")
        for ctx_line in res['context']:
            f.write(ctx_line.rstrip() + "\n")
        f.write("\n" + "="*50 + "\n\n")
import re

# Define keywords
safety_keywords = ["Safety", "F-", "EStop", "Guard", "Door", "SafeTorqueOff", "SS1", "SLS", "PROFIsafe", "FailSafe", "SafetyGate", "MaterialGate"]
ob_keywords = ["OB1", "OB100", "OB101", "OB102", "OB82", "OB83", "OB86", "OB121", "OB122", "CYC_INT"]
all_keywords = safety_keywords + ob_keywords

results = []

# Walk through EXPORT directory
for root, dirs, files in os.walk("EXPORT"):
    for file in files:
        if file.endswith(".xml"):
            filepath = os.path.join(root, file)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                for i, line in enumerate(lines):
                    line_num = i + 1
                    for keyword in all_keywords:
                        if re.search(re.escape(keyword), line, re.IGNORECASE):
                            classification = "CRITICAL" if keyword in ob_keywords else "NO-TOUCH"
                            matched_text = keyword
                            context_start = max(0, i - 2)
                            context_end = min(len(lines), i + 3)
                            context = lines[context_start:context_end]
                            results.append({
                                'classification': classification,
                                'file': filepath,
                                'line': line_num,
                                'match': matched_text,
                                'context': context
                            })
            except Exception as e:
                print(f"Error reading {filepath}: {e}")

# Write to safety_report.txt
with open("safety_report.txt", 'w', encoding='utf-8') as f:
    for res in results:
        f.write(f"Classification: {res['classification']}\n")
        f.write(f"File: {res['file']}\n")
        f.write(f"Line: {res['line']}\n")
        f.write(f"Match: {res['match']}\n")
        f.write("Context:\n")
        for ctx_line in res['context']:
            f.write(ctx_line.rstrip() + "\n")
        f.write("\n" + "="*50 + "\n\n")
        f.write("\n" + "="*50 + "\n\n")
# Define keywords
safety_keywords = ["Safety", "F-", "EStop", "Guard", "Door", "SafeTorqueOff", "SS1", "SLS", "PROFIsafe", "FailSafe", "SafetyGate", "MaterialGate"]
ob_keywords = ["OB1", "OB100", "OB101", "OB102", "OB82", "OB83", "OB86", "OB121", "OB122", "CYC_INT"]
all_keywords = safety_keywords + ob_keywords

results = []

# Walk through EXPORT directory
for root, dirs, files in os.walk("EXPORT"):
    for file in files:
        if file.endswith(".xml"):
            filepath = os.path.join(root, file)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                for i, line in enumerate(lines):
                    line_num = i + 1
                    for keyword in all_keywords:
                        if re.search(re.escape(keyword), line, re.IGNORECASE):
                            classification = "CRITICAL" if keyword in ob_keywords else "NO-TOUCH"
                            matched_text = keyword
                            context_start = max(0, i - 2)
                            context_end = min(len(lines), i + 3)
                            context = lines[context_start:context_end]
                            results.append({
                                'classification': classification,
                                'file': filepath,
                                'line': line_num,
                                'match': matched_text,
                                'context': context
                            })
            except Exception as e:
                print(f"Error reading {filepath}: {e}")

# Write to safety_report.txt
with open("safety_report.txt", 'w', encoding='utf-8') as f:
    for res in results:
        f.write(f"Classification: {res['classification']}\n")
        f.write(f"File: {res['file']}\n")
        f.write(f"Line: {res['line']}\n")
        f.write(f"Match: {res['match']}\n")
        f.write("Context:\n")
        for ctx_line in res['context']:
            f.write(ctx_line.rstrip() + "\n")
        f.write("\n" + "="*50 + "\n\n")
        f.write("\n" + "="*50 + "\n\n")

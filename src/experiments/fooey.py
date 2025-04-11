#------------------------------------------------------------------------------+
# fooey.py - a place to fool around with experiments, not a dependent.
#------------------------------------------------------------------------------+
import re

sample = [
    "Bank of America - Bank - Primary Checking Acct",
    "Bank of America - Credit Card - Visa Signature",
    "Bank of America - Bank - Primary Checking Acct",
    "Bank of America - Credit Card - Visa Signature",
    "Bank of America - Credit Card - Visa Signature"
]

modified_sample = []

# Regular expression to extract the third part
pattern = r'^[^-]+-\s*[^-]+-\s*(.+)$'

# Iterate through the sample array and apply the regex replacement
for item in sample:
    modified_value = re.sub(pattern, r'\1', item)  # Replace with the third part
    modified_sample.append(modified_value)

print(modified_sample)
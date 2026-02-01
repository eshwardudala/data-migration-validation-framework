# Data Validation Script - Instructions

## Overview
This script validates data by comparing source and target Excel files. It performs schema validation, row hashing, and generates detailed comparison reports.

## Prerequisites

### 1. Install Required Libraries
Before running the script, install the necessary Python packages:

```bash
pip install pandas numpy openpyxl
```

**What each library does:**
- **pandas**: Data manipulation and Excel file handling
- **numpy**: Numerical operations and data analysis
- **openpyxl**: Reading/writing Excel files (.xlsx format)

## Setup

### 2. Prepare Input Files
Place your Excel files in the `input/` folder:
- `input/source.xlsx` - The source data file
- `input/target.xlsx` - The target data file to compare against

**Requirements:**
- Both files must be in Excel format (.xlsx)
- Files should have headers in the first row
- At least one column must contain unique values (for primary key detection)

## Running the Script

### 3. Execute the Script
Navigate to the script directory and run:

```bash
python data_validation.py
```

### 4. Output
The script generates validation reports in the `output/` folder:
- **Schema comparison** - Column names and data types validation
- **Row validation** - Identifies matching and mismatched rows
- **Hash comparison** - Detects data differences between source and target
- **Detailed report** - Summary of all validation results

## Troubleshooting

### Import Error: "pandas could not be resolved"
**Solution:** Run the install command:
```bash
pip install pandas numpy openpyxl
```

### FileNotFoundError: "source.xlsx" not found
**Solution:** Ensure your Excel files are placed in the `input/` folder with correct names:
- `input/source.xlsx`
- `input/target.xlsx`

### No Primary Key Found
**Solution:** Ensure at least one column contains unique, non-null values in your source data.

## Folder Structure
```
Data Validation/
├── data_validation.py      (Main script)
├── README.md              (This file)
├── input/                 (Input files folder)
│   ├── source.xlsx
│   └── target.xlsx
└── output/                (Generated reports folder)
```

## Support
If you encounter issues, check that:
1. ✓ All required libraries are installed
2. ✓ Input files exist and are in `.xlsx` format
3. ✓ At least one column has unique values for primary key detection
4. ✓ The script has write permissions to the `output/` folder

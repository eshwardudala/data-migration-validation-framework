import pandas as pd
import numpy as np
import hashlib

# ----------------------------
# STEP 1: LOAD EXCEL FILES
# ----------------------------
source_path = "input/source.xlsx"
target_path = "input/target.xlsx"

source_df = pd.read_excel(source_path, engine="openpyxl")
target_df = pd.read_excel(target_path, engine="openpyxl")

# ----------------------------
# STEP 2: SCHEMA INFERENCE
# ----------------------------
def infer_schema(df):
    schema = {}
    for col in df.columns:
        dtype = df[col].dropna().infer_objects().dtype
        schema[col] = str(dtype)
    return schema

source_schema = infer_schema(source_df)
target_schema = infer_schema(target_df)

schema_df = pd.DataFrame({
    "Column": source_schema.keys(),
    "Source_Type": source_schema.values(),
    "Target_Type": [target_schema.get(c, "MISSING") for c in source_schema.keys()]
})

schema_df["Schema_Match"] = schema_df["Source_Type"] == schema_df["Target_Type"]

# ----------------------------
# STEP 3: AUTO-DETECT PRIMARY KEY
# ----------------------------
def detect_primary_key(df):
    for col in df.columns:
        if df[col].is_unique and df[col].notnull().all():
            return col
    return None

primary_key = detect_primary_key(source_df)

if primary_key is None:
    raise Exception("No suitable primary key found")

# ----------------------------
# STEP 4: ROW HASHING
# ----------------------------
def generate_row_hash(df):
    return df.astype(str).agg('|'.join, axis=1).apply(
        lambda x: hashlib.md5(x.encode()).hexdigest()
    )

source_df["ROW_HASH"] = generate_row_hash(source_df)
target_df["ROW_HASH"] = generate_row_hash(target_df)

# ----------------------------
# STEP 5: MERGE SOURCE & TARGET
# ----------------------------
merged_df = source_df.merge(
    target_df,
    on=primary_key,
    how="outer",
    suffixes=("_source", "_target"),
    indicator=True
)

# ----------------------------
# STEP 6: ROW LEVEL VALIDATION
# ----------------------------
merged_df["Row_Status"] = np.where(
    merged_df["_merge"] == "both",
    np.where(
        merged_df["ROW_HASH_source"] == merged_df["ROW_HASH_target"],
        "MATCHED",
        "VALUE_MISMATCH"
    ),
    np.where(
        merged_df["_merge"] == "left_only",
        "MISSING_IN_TARGET",
        "MISSING_IN_SOURCE"
    )
)

# ----------------------------
# STEP 7: COLUMN LEVEL ACCURACY
# ----------------------------
column_results = []

for col in source_df.columns:
    if col in [primary_key, "ROW_HASH"]:
        continue

    source_col = f"{col}_source"
    target_col = f"{col}_target"

    if source_col not in merged_df or target_col not in merged_df:
        continue

    matches = (merged_df[source_col] == merged_df[target_col]).sum()
    total = merged_df[source_col].notnull().sum()

    column_results.append({
        "Column": col,
        "Match_Count": matches,
        "Total_Compared": total,
        "Match_Percentage": round((matches / total) * 100, 2) if total > 0 else 0
    })

column_accuracy_df = pd.DataFrame(column_results)

# ----------------------------
# STEP 8: SUMMARY METRICS
# ----------------------------
summary_df = pd.DataFrame({
    "Metric": [
        "Total Source Rows",
        "Total Target Rows",
        "Matched Rows",
        "Value Mismatch Rows",
        "Missing In Target",
        "Missing In Source",
        "Overall Accuracy %"
    ],
    "Value": [
        len(source_df),
        len(target_df),
        (merged_df["Row_Status"] == "MATCHED").sum(),
        (merged_df["Row_Status"] == "VALUE_MISMATCH").sum(),
        (merged_df["Row_Status"] == "MISSING_IN_TARGET").sum(),
        (merged_df["Row_Status"] == "MISSING_IN_SOURCE").sum(),
        round(
            ((merged_df["Row_Status"] == "MATCHED").sum() / len(source_df)) * 100,
            2
        )
    ]
})

# ----------------------------
# STEP 9: WRITE TO EXCEL
# ----------------------------
with pd.ExcelWriter("output/validation_report.xlsx", engine="openpyxl") as writer:
    summary_df.to_excel(writer, sheet_name="Summary", index=False)
    schema_df.to_excel(writer, sheet_name="Schema_Validation", index=False)
    column_accuracy_df.to_excel(writer, sheet_name="Column_Accuracy", index=False)
    merged_df.to_excel(writer, sheet_name="Row_Level_Details", index=False)

print("Validation report generated successfully!")
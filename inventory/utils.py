# inventory/utils.py

import pandas as pd
import re

# Updated column_mapping to ensure exact matches with the Excel columns
column_mapping = {
    'Material': 'material_code',
    'Storage location': 'storage_location',
    'Batch': 'batch_code',
    'Material description': 'material_description',
    'BOM': 'bom',
    'Cl.Quantity': 'quantity',
    'Value': 'value',
    'Con Factor': 'con_factor',
    'Con UOM': 'con_uom',
    'Dept': 'department',
    'Batch Date': 'batch_date',
    'Party Name': 'party_name',
    'Bundle': 'bundle',
    'All Remark': 'remarks',
    'Date of Clearing': 'date_of_clearing',
    'Person': 'person',
    'Batch Ageing': 'batch_ageing',
    'Material Broad Group Desc': 'material_broad_group_desc'
}

expected_columns = ['material_code', 'batch_code', 'storage_location', 'material_description',
                    'quantity', 'unit_of_measure', 'value', 'department', 'batch_date',
                    'party_name', 'remarks', 'date_of_clearing', 'person', 'batch_ageing',
                    'material_broad_group_desc']

def normalize_column_name(col_name):
    col_name = col_name.strip().lower()
    col_name = re.sub(r'\s+', '_', col_name)
    return col_name

def map_columns(df, column_mapping, expected_columns):
    print(f"Original Columns: {df.columns}")
    df.columns = [normalize_column_name(col) for col in df.columns]
    print(f"Normalized Columns: {df.columns}")

    # Normalize column_mapping keys to match the normalized DataFrame columns
    normalized_mapping = {normalize_column_name(k): v for k, v in column_mapping.items()}
    
    # Apply renaming based on the normalized_mapping
    df.rename(columns=normalized_mapping, inplace=True)
    print(f"Renamed Columns: {df.columns}")

    missing_columns = [col for col in expected_columns if col not in df.columns]
    extra_columns = [col for col in df.columns if col not in expected_columns]
    
    # Add missing columns with empty values
    for col in missing_columns:
        df[col] = None
    
    return df, missing_columns, extra_columns

def read_and_normalize_excel(file_path, column_mapping, expected_columns):
    df = pd.read_excel(file_path)
    df, missing_columns, extra_columns = map_columns(df, column_mapping, expected_columns)
    
    # Check for rows with missing critical fields
    missing_values_warnings = []
    for col in ['material_code', 'batch_code']:
        if df[col].isnull().any():
            missing_values_warnings.append(f"Missing values in column: {col}")
    
    return df, missing_columns, extra_columns, missing_values_warnings

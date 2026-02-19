import csv
import os
import sys

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from core.validator import Validator

BASE_DIR = '/Users/sangwook/Documents/workspace/repo/antigravity_test/blackup_bean_order'
DATA_DIR = os.path.join(BASE_DIR, 'templates/sheets_data')
CONFIG_PATH = os.path.join(BASE_DIR, 'config/settings.yaml')

def verify_files():
    validator = Validator(CONFIG_PATH)
    
    files = [f for f in os.listdir(DATA_DIR) if f.startswith('test_') and f.endswith('.tsv')]
    
    total_valid = 0
    total_invalid = 0
    
    for filename in files:
        filepath = os.path.join(DATA_DIR, filename)
        print(f"Verifying {filename}...")
        
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.reader(f, delimiter='\t')
            row_num = 0
            for row in reader:
                row_num += 1
                # Map TSV row to dict for validator
                # Schema: Date, Timestamp, Status, StoreCode, StoreName, ProductCode, ProductName, Qty, DeliveryDate, Roasting, Grind, Urgent, Note, OrdererName, Phone
                if len(row) < 15:
                    print(f"  [Row {row_num}] Error: Insufficient columns")
                    total_invalid += 1
                    continue
                    
                order_data = {
                    'delivery_date': row[8],
                    'qty': row[7],
                    'product_code': row[5],
                    'roasting': row[9],
                    'phone': row[14]
                }
                
                is_valid, msg = validator.validate_order(order_data)
                
                if not is_valid:
                    print(f"  [Row {row_num}] Validation Failed: {msg}")
                    total_invalid += 1
                else:
                    total_valid += 1

    print(f"\nVerification Complete.")
    print(f"Valid Rows: {total_valid}")
    print(f"Invalid Rows: {total_invalid}")

if __name__ == "__main__":
    verify_files()

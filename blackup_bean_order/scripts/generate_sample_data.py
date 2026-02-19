import csv
import random
import os
from datetime import datetime, timedelta, time

# Constants
# Use absolute paths to be safe
BASE_DIR = '/Users/sangwook/Documents/workspace/repo/antigravity_test/blackup_bean_order'
OUTPUT_DIR = os.path.join(BASE_DIR, 'templates/sheets_data')
STORE_FILE = os.path.join(OUTPUT_DIR, '매장코드.tsv')

PRODUCTS = [
    {'code': 'ETH-YRG', 'name': '에티오피아 예가체프'},
    {'code': 'COL-SUP', 'name': '콜롬비아 수프리모'},
    {'code': 'BRA-SAN', 'name': '브라질 산토스'},
]

ROASTING_OPTIONS = ['라이트', '미디엄', '다크']
GRIND_OPTIONS = ['홀빈', '분쇄']
URGENT_OPTIONS = ['Y', 'N']
STATUS_OPTIONS = ['New', 'Processed', 'Shipped', 'Cancelled']
NAMES = ['김철수', '이영희', '박지민', '최수영', '정우성', '강동원', '한지민', '송혜교', '현빈', '손예진']

def get_stores():
    stores = []
    print(f"Reading store file from: {STORE_FILE}")
    if not os.path.exists(STORE_FILE):
        print(f"Error: {STORE_FILE} does not exist.")
        return []
        
    try:
        with open(STORE_FILE, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter='\t')
            for row in reader:
                stores.append({'code': row['코드'], 'name': row['매장명']})
    except Exception as e:
        print(f"Error reading store file: {e}")
        return []
    return stores

def generate_phone():
    return f"010-{random.randint(1000, 9999)}-{random.randint(1000, 9999)}"

def generate_random_time(date_obj):
    # Random time between 09:00 and 18:00
    random_hour = random.randint(9, 18)
    random_minute = random.randint(0, 59)
    random_second = random.randint(0, 59)
    return datetime.combine(date_obj, time(random_hour, random_minute, random_second))

def generate_data():
    stores = get_stores()
    if not stores:
        print("No stores found. Exiting.")
        return

    # Generate from 60 days ago up to today
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=60)

    print(f"Generating data from {start_date} to {end_date} for {len(stores)} stores...")

    total_rows = 0
    for store in stores:
        filename = os.path.join(OUTPUT_DIR, f"test_{store['code']}.tsv")
        print(f"Generating {filename}...")
        
        try:
            with open(filename, 'w', encoding='utf-8', newline='') as f:
                writer = csv.writer(f, delimiter='\t')
                
                # New Schema:
                # 0: Date (YYYY-MM-DD)
                # 1: Timestamp (YYYY-MM-DD HH:MM:SS)
                # 2: Status (New/Processed/Shipped)
                # 3: StoreCode
                # 4: StoreName
                # 5: ProductCode
                # 6: ProductName
                # 7: Qty (Float)
                # 8: DeliveryDate
                # 9: Roasting
                # 10: Grind
                # 11: Urgent
                # 12: Note
                # 13: OrdererName
                # 14: Phone
                
                current_date = start_date
                while current_date <= end_date:
                    # Randomly decide if there's an order today (30% chance)
                    if random.random() < 0.3:
                        num_orders = random.randint(1, 3)
                        for _ in range(num_orders):
                            product = random.choice(PRODUCTS)
                            
                            # Float Quantity: 0.5kg to 10.0kg (step 0.5)
                            qty = random.randint(1, 20) * 0.5
                            
                            delivery_date = current_date + timedelta(days=random.randint(2, 4))
                            timestamp = generate_random_time(current_date)
                            
                            # Determine Status based on date
                            # Older than 2 days = Shipped or Processed
                            # Recent = New
                            days_diff = (datetime.now() - timestamp).days
                            if days_diff > 2:
                                status = random.choice(['Processed', 'Shipped'])
                            else:
                                status = 'New'

                            row = [
                                current_date.strftime('%Y-%m-%d'),
                                timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                                status,
                                store['code'],
                                store['name'],
                                product['code'], # ProductCode
                                product['name'], # ProductName
                                f"{qty:.1f}",   # Qty (Float)
                                delivery_date.strftime('%Y-%m-%d'),
                                random.choice(ROASTING_OPTIONS),
                                random.choice(GRIND_OPTIONS),
                                random.choice(URGENT_OPTIONS),
                                '', # Note
                                random.choice(NAMES),
                                generate_phone()
                            ]
                            writer.writerow(row)
                            total_rows += 1
                    
                    current_date += timedelta(days=1)
        except Exception as e:
            print(f"Error writing to {filename}: {e}")

    print(f"Data generation complete. Total {total_rows} rows generated.")

if __name__ == "__main__":
    generate_data()

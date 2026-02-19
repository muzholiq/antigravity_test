# import yaml  <-- Removed dependency
import os
from datetime import datetime
import re

class Validator:
    def __init__(self, config_path):
        self.config = self._load_config(config_path)
        self.min_order_kg = self.config.get('min_order_kg', 1)
        self.max_order_kg = self.config.get('max_order_kg', 50)
        self.allowed_profiles = self.config.get('allowed_roasting_profiles', {})
        self.roasting_profiles = self.config.get('roasting_profiles', {})

    def _load_config(self, path):
        """
        Simple YAML-like parser to avoid external dependencies.
        Parses only the specific structure of settings.yaml used here.
        """
        if not os.path.exists(path):
            raise FileNotFoundError(f"Config file not found: {path}")
            
        config = {
            'roasting_profiles': {},
            'allowed_roasting_profiles': {}
        }
        
        current_section = None
        
        with open(path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                if ':' in line:
                    key, val = [p.strip() for p in line.split(':', 1)]
                    
                    # Handle top-level keys
                    if key in ['min_order_kg', 'max_order_kg']:
                        config[key] = int(val)
                        current_section = None
                        continue
                        
                    if key == 'roasting_profiles':
                        current_section = 'roasting_profiles'
                        continue
                        
                    if key == 'allowed_roasting_profiles':
                        current_section = 'allowed_roasting_profiles'
                        continue
                        
                    # Handle section items
                    if current_section == 'roasting_profiles':
                        # Clean quotes
                        val = val.strip('"').strip("'")
                        config['roasting_profiles'][key] = val
                    elif current_section == 'allowed_roasting_profiles':
                        # Parse list: ["라이트", "미디엄"]
                        val = val.strip('[').strip(']').replace('"', '').replace("'", "")
                        items = [item.strip() for item in val.split(',')]
                        config['allowed_roasting_profiles'][key] = items
                        
        return config

    def validate_order(self, order_data):
        """
        Validates a single order row.
        Returns (is_valid, error_message)
        """
        errors = []

        # 1. Date Validation (Sunday Check)
        if not self._validate_date(order_data.get('delivery_date')):
            errors.append("배송 요청일은 일요일일 수 없습니다.")

        # 2. Quantity Validation (Min/Max, Float)
        qty_valid, qty_msg = self._validate_quantity(order_data.get('qty'))
        if not qty_valid:
            errors.append(qty_msg)

        # 3. Roasting Profile Validation
        profile_valid, profile_msg = self._validate_roasting(
            order_data.get('product_code'), 
            order_data.get('roasting')
        )
        if not profile_valid:
            errors.append(profile_msg)

        # 4. Phone Validation
        if not self._validate_phone(order_data.get('phone')):
            errors.append("전화번호 형식이 올바르지 않습니다.")

        if errors:
            return False, "; ".join(errors)
        return True, ""

    def _validate_date(self, date_str):
        try:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            # Sunday is 6
            if date_obj.weekday() == 6:
                return False
            return True
        except ValueError:
            return False

    def _validate_quantity(self, qty):
        try:
            val = float(qty)
            if val < self.min_order_kg:
                return False, f"최소 주문량은 {self.min_order_kg}kg 입니다."
            if val > self.max_order_kg:
                return False, f"최대 주문량은 {self.max_order_kg}kg 입니다."
            return True, ""
        except (ValueError, TypeError):
            return False, "수량은 숫자여야 합니다."

    def _validate_roasting(self, product_code, roasting):
        # Check against enum
        if roasting not in self.roasting_profiles:
            return False, f"유효하지 않은 로스팅 옵션: {roasting}"

        # Check against per-bean allowed profiles
        allowed = self.allowed_profiles.get(product_code)
        if allowed and roasting not in allowed:
            return False, f"{product_code} 원두는 {roasting} 로스팅이 불가합니다. (허용: {', '.join(allowed)})"
        
        return True, ""

    def _validate_phone(self, phone):
        # Simple regex for 010-XXXX-XXXX
        pattern = re.compile(r'^\d{2,3}-\d{3,4}-\d{4}$')
        return bool(pattern.match(str(phone)))

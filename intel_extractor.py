"""
Intelligence Extractor
Extracts sensitive information from scammer messages
Uses regex patterns - completely FREE, no API needed
"""

import re
from typing import Dict, List


class IntelligenceExtractor:
    """Extracts bank accounts, UPI IDs, phone numbers, URLs, and emails from messages"""
    
    def __init__(self):
        # Regex patterns for different types of intelligence
        
        # Indian bank account numbers (10-18 digits, often in groups)
        self.bank_account_pattern = re.compile(
            r'\b\d{9,18}\b|'  # 9-18 consecutive digits
            r'\b\d{4}[\s\-]?\d{4}[\s\-]?\d{4,10}\b'  # Grouped digits
        )
        
        # IFSC codes (11 characters: 4 letters, 0, then 6 alphanumeric)
        self.ifsc_pattern = re.compile(r'\b[A-Z]{4}0[A-Z0-9]{6}\b')
        
        # UPI IDs (format: username@bankname)
        self.upi_pattern = re.compile(
            r'\b[\w\.-]+@(?:paytm|phonepe|gpay|googlepay|bhim|ybl|oksbi|axisbank|'
            r'icici|hdfcbank|airtel|fbl|ibl|sbi|upi|pnb|boi|unionbank|indianbank)\b',
            re.IGNORECASE
        )
        
        # Phone numbers (Indian: 10 digits, with optional +91 or 0 prefix)
        self.phone_pattern = re.compile(
            r'\b(?:\+91[\s\-]?)?[6-9]\d{9}\b'  # Must have word boundary before and after
        )
        
        # URLs (http/https)
        self.url_pattern = re.compile(
            r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        )
        
        # Email addresses
        self.email_pattern = re.compile(
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        )
        
        # Card numbers (basic pattern, 13-19 digits with optional spaces/dashes)
        self.card_pattern = re.compile(
            r'\b(?:\d{4}[\s\-]?){3}\d{1,7}\b'
        )
        
        # CVV (3-4 digits, but be careful with false positives)
        self.cvv_pattern = re.compile(r'\bcvv[\s:]*(\d{3,4})\b', re.IGNORECASE)
        
        # OTP (typically 4-6 digits mentioned as OTP)
        self.otp_pattern = re.compile(r'\botp[\s:]*(\d{4,6})\b', re.IGNORECASE)
    
    def extract(self, message: str) -> Dict[str, List[str]]:
        """
        Extract all intelligence from a message
        
        Returns:
        {
            'bank_accounts': [...],
            'ifsc_codes': [...],
            'upi_ids': [...],
            'phone_numbers': [...],
            'urls': [...],
            'emails': [...],
            'card_numbers': [...],
            'cvv': [...],
            'otp': [...]
        }
        """
        intel = {
            'bank_accounts': [],
            'ifsc_codes': [],
            'upi_ids': [],
            'phone_numbers': [],
            'urls': [],
            'emails': [],
            'card_numbers': [],
            'cvv': [],
            'otp': []
        }
        
        # Extract phone numbers FIRST with context awareness
        phone_numbers = self.phone_pattern.findall(message)
        cleaned_phones = [re.sub(r'[\s\-]', '', phone) for phone in phone_numbers]
        
        # Keep only valid Indian phone numbers (10 digits starting with 6-9, or with +91)
        valid_phones = []
        for phone in cleaned_phones:
            # Remove +91 prefix if present
            clean = phone.replace('+91', '').replace('91', '', 1) if phone.startswith(('91', '+91')) else phone
            # Valid Indian mobile: 10 digits starting with 6-9
            if len(clean) == 10 and clean[0] in '6789':
                valid_phones.append(clean)
        
        intel['phone_numbers'] = list(set(valid_phones))
        
        # Extract bank accounts - exclude phone numbers and check context
        bank_accounts = self.bank_account_pattern.findall(message)
        for acc in bank_accounts:
            clean_acc = re.sub(r'[\s\-]', '', acc)
            
            # Skip if it's already identified as a phone number
            if clean_acc in intel['phone_numbers']:
                continue
            
            # Skip 10-digit numbers starting with 6-9 WITHOUT bank context (likely phone numbers)
            if len(clean_acc) == 10 and clean_acc[0] in '6789':
                # Check for bank account context
                acc_pattern = re.compile(
                    rf'.{{0,50}}{re.escape(acc)}.{{0,50}}',
                    re.IGNORECASE | re.DOTALL
                )
                context = acc_pattern.search(message)
                context_text = context.group(0).lower() if context else message.lower()
                
                # Bank account keywords
                has_bank_context = any(keyword in context_text for keyword in 
                    ['account', 'a/c', 'ac no', 'acc', 'ifsc', 'bank', 'transfer', 'deposit', 'credit'])
                
                # If no bank context, skip (it's likely a phone number)
                if not has_bank_context:
                    continue
            
            # Valid bank account: 9-18 digits
            if 9 <= len(clean_acc) <= 18:
                intel['bank_accounts'].append(clean_acc)
        
        # Extract IFSC codes
        intel['ifsc_codes'] = self.ifsc_pattern.findall(message)
        
        # Extract UPI IDs
        intel['upi_ids'] = self.upi_pattern.findall(message)
        
        # Extract URLs
        intel['urls'] = self.url_pattern.findall(message)
        
        # Extract emails
        intel['emails'] = self.email_pattern.findall(message)
        
        # Extract card numbers (exclude if already in bank accounts or phones)
        card_numbers = self.card_pattern.findall(message)
        for card in card_numbers:
            clean_card = re.sub(r'[\s\-]', '', card)
            
            # Skip if already categorized
            if clean_card in intel['phone_numbers'] or clean_card in intel['bank_accounts']:
                continue
            
            # Valid card: 13-19 digits, often in groups of 4
            if 13 <= len(clean_card) <= 19:
                # Check if it has the typical card format (groups of 4)
                if ' ' in card or '-' in card or len(clean_card) == 16:
                    intel['card_numbers'].append(clean_card)
        
        # Extract CVV
        cvv_matches = self.cvv_pattern.findall(message)
        intel['cvv'] = cvv_matches
        
        # Extract OTP
        otp_matches = self.otp_pattern.findall(message)
        intel['otp'] = otp_matches
        
        # Remove duplicates from all lists
        for key in intel:
            intel[key] = list(set(intel[key]))
        
        return intel
    
    def extract_financial_details(self, message: str) -> Dict[str, any]:
        """
        Extract financial details with additional context
        Useful for understanding payment flow
        """
        intel = self.extract(message)
        
        # Combine account-related info
        financial_details = {
            'accounts': {
                'bank_accounts': intel['bank_accounts'],
                'ifsc_codes': intel['ifsc_codes']
            },
            'digital_payment': {
                'upi_ids': intel['upi_ids'],
                'phone_numbers': intel['phone_numbers']  # Often linked to UPI
            },
            'card_details': {
                'card_numbers': intel['card_numbers'],
                'cvv': intel['cvv']
            },
            'verification': {
                'otp': intel['otp']
            },
            'phishing_links': {
                'urls': intel['urls'],
                'emails': intel['emails']
            }
        }
        
        # Calculate risk score based on extracted info
        risk_score = 0
        if intel['bank_accounts']: risk_score += 30
        if intel['upi_ids']: risk_score += 25
        if intel['card_numbers']: risk_score += 35
        if intel['cvv']: risk_score += 40
        if intel['otp']: risk_score += 45
        if intel['urls']: risk_score += 20
        
        financial_details['risk_score'] = min(risk_score, 100)
        
        return financial_details
    
    def validate_upi_id(self, upi_id: str) -> bool:
        """Validate UPI ID format"""
        return bool(self.upi_pattern.match(upi_id))
    
    def validate_ifsc(self, ifsc: str) -> bool:
        """Validate IFSC code format"""
        return bool(self.ifsc_pattern.match(ifsc))
    
    def sanitize_phone_number(self, phone: str) -> str:
        """Sanitize phone number to standard format"""
        # Remove all non-digit characters
        digits = re.sub(r'\D', '', phone)
        
        # Remove country code if present
        if digits.startswith('91') and len(digits) == 12:
            digits = digits[2:]
        
        # Return 10-digit number
        return digits[-10:] if len(digits) >= 10 else digits
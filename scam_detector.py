"""
Scam Detection Engine
Uses pattern matching, keyword analysis, and heuristics to detect scam messages
FREE - No external API required
"""

import re
from typing import Dict, List


class ScamDetector:
    """Detects scam messages using multiple detection strategies"""
    
    def __init__(self):
        # Scam indicators with weights
        self.scam_patterns = {
            'prize_lottery': {
                'keywords': ['won', 'prize', 'lottery', 'congratulations', 'winner', 'jackpot', 'claim', 'lucky draw'],
                'weight': 0.8,
                'type': 'prize_scam'
            },
            'urgent_banking': {
                'keywords': ['urgent', 'account', 'blocked', 'suspended', 'verify', 'update', 'kyc', 'expire'],
                'weight': 0.85,
                'type': 'banking_fraud'
            },
            'payment_request': {
                'keywords': ['pay', 'payment', 'send money', 'transfer', 'upi', 'paytm', 'gpay', 'phonepe', 'account', 'ifsc', 'bank account'],
                'weight': 0.85,
                'type': 'payment_scam'
            },
            'investment': {
                'keywords': ['investment', 'returns', 'profit', 'guaranteed', 'earn', 'income', 'trading', 'bitcoin', 'crypto'],
                'weight': 0.75,
                'type': 'investment_fraud'
            },
            'impersonation': {
                'keywords': ['government', 'police', 'officer', 'authority', 'legal', 'arrest', 'warrant', 'tax department'],
                'weight': 0.9,
                'type': 'impersonation'
            },
            'personal_info': {
                'keywords': ['otp', 'password', 'pin', 'cvv', 'card number', 'aadhar', 'pan', 'social security'],
                'weight': 0.95,
                'type': 'phishing'
            },
            'employment': {
                'keywords': ['job', 'hiring', 'work from home', 'part time', 'earn from home', 'registration fee'],
                'weight': 0.7,
                'type': 'job_scam'
            }
        }
        
        # Urgency indicators
        self.urgency_words = ['urgent', 'immediately', 'now', 'today', 'hurry', 'limited time', 'expires', 'last chance']
        
        # Request for action indicators
        self.action_requests = ['click', 'call', 'send', 'provide', 'share', 'reply', 'confirm', 'verify', 'update']
        
        # Suspicious URL patterns
        self.url_pattern = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
    
    def analyze(self, message: str) -> Dict:
        """
        Analyze a message to determine if it's a scam
        
        Returns:
        {
            'is_scam': bool,
            'confidence': float,
            'scam_type': str,
            'indicators': list,
            'severity': str
        }
        """
        message_lower = message.lower()
        
        # Calculate scam score
        scam_score = 0.0
        detected_types = []
        indicators = []
        
        # Check pattern matches
        for pattern_name, pattern_data in self.scam_patterns.items():
            matches = [kw for kw in pattern_data['keywords'] if kw in message_lower]
            if matches:
                scam_score += pattern_data['weight'] * (len(matches) / len(pattern_data['keywords']))
                detected_types.append(pattern_data['type'])
                indicators.extend(matches)
        
        # Check for urgency
        urgency_count = sum(1 for word in self.urgency_words if word in message_lower)
        if urgency_count > 0:
            scam_score += 0.2 * min(urgency_count / 3, 1.0)
            indicators.append('urgency_language')
        
        # Check for action requests
        action_count = sum(1 for word in self.action_requests if word in message_lower)
        if action_count > 0:
            scam_score += 0.15 * min(action_count / 3, 1.0)
            indicators.append('action_request')
        
        # Check for suspicious URLs
        urls = self.url_pattern.findall(message)
        if urls:
            scam_score += 0.3
            indicators.append('contains_url')
        
        # Check for excessive punctuation (!!!, ???)
        if re.search(r'[!?]{3,}', message):
            scam_score += 0.1
            indicators.append('excessive_punctuation')
        
        # Check for money mentions
        money_pattern = r'[₹$£€]\s*\d+|rs\.?\s*\d+|rupees?\s*\d+'
        if re.search(money_pattern, message_lower):
            scam_score += 0.2
            indicators.append('money_mention')
        
        # Normalize score to 0-1 range
        confidence = min(scam_score, 1.0)
        
        # Determine if it's a scam (threshold: 0.5)
        is_scam = confidence >= 0.5
        
        # Determine primary scam type
        scam_type = detected_types[0] if detected_types else 'unknown'
        
        # Determine severity
        if confidence >= 0.8:
            severity = 'high'
        elif confidence >= 0.6:
            severity = 'medium'
        else:
            severity = 'low'
        
        return {
            'is_scam': is_scam,
            'confidence': confidence,
            'scam_type': scam_type,
            'indicators': list(set(indicators)),
            'severity': severity,
            'detected_types': detected_types
        }
    
    def get_scam_characteristics(self, scam_type: str) -> Dict:
        """Get characteristics of a specific scam type for persona selection"""
        characteristics = {
            'prize_scam': {
                'victim_profile': 'excited, greedy, trusting',
                'common_tactics': ['fake lottery', 'prize notification', 'claim process']
            },
            'banking_fraud': {
                'victim_profile': 'worried, compliant, urgent',
                'common_tactics': ['account suspension', 'KYC update', 'verification']
            },
            'payment_scam': {
                'victim_profile': 'confused, helpful, trusting',
                'common_tactics': ['wrong transfer', 'refund request', 'payment confirmation']
            },
            'investment_fraud': {
                'victim_profile': 'ambitious, greedy, hopeful',
                'common_tactics': ['guaranteed returns', 'expert advice', 'limited slots']
            },
            'impersonation': {
                'victim_profile': 'fearful, compliant, respectful',
                'common_tactics': ['authority figure', 'legal threat', 'official demand']
            },
            'phishing': {
                'victim_profile': 'concerned, cooperative, naive',
                'common_tactics': ['security alert', 'verification needed', 'account issue']
            },
            'job_scam': {
                'victim_profile': 'eager, hopeful, desperate',
                'common_tactics': ['easy money', 'work from home', 'registration fee']
            }
        }
        
        return characteristics.get(scam_type, {
            'victim_profile': 'curious, interested',
            'common_tactics': ['generic appeal']
        })
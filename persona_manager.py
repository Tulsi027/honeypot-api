"""
Persona Manager
Generates believable responses to engage scammers
Uses template-based responses (FREE) with optional AI enhancement
"""

import random
from typing import Dict, List


class PersonaManager:
    """Manages different personas and generates contextual responses"""
    
    def __init__(self):
        # Define personas
        self.personas = {
            'elderly': {
                'name': 'Ramesh Kumar',
                'age': 68,
                'traits': ['trusting', 'excited', 'tech-naive', 'eager'],
                'speech_patterns': ['uses simple language', 'asks many questions', 'shows enthusiasm']
            },
            'tech_naive': {
                'name': 'Priya Sharma',
                'age': 45,
                'traits': ['confused', 'cooperative', 'anxious', 'helpful'],
                'speech_patterns': ['seeks clarification', 'apologizes', 'wants to help']
            },
            'eager_victim': {
                'name': 'Amit Patel',
                'age': 32,
                'traits': ['ambitious', 'greedy', 'impatient', 'hopeful'],
                'speech_patterns': ['shows excitement', 'asks about benefits', 'wants quick results']
            },
            'worried_user': {
                'name': 'Sunita Verma',
                'age': 50,
                'traits': ['anxious', 'fearful', 'compliant', 'concerned'],
                'speech_patterns': ['expresses worry', 'seeks assurance', 'follows instructions']
            }
        }
        
        # Conversation stages
        self.stages = ['initial', 'engagement', 'trust_building', 'probing', 'extraction', 'closing']
        
        # Response templates by stage and scam type
        self.response_templates = {
            'initial': {
                'prize_scam': [
                    "Really? I won something? That's amazing! How did you get my number?",
                    "Wow! I never win anything! Is this for real? What did I win?",
                    "This is such good news! I'm so excited! What do I need to do to claim it?"
                ],
                'banking_fraud': [
                    "Oh no! My account is blocked? I just used it yesterday! What happened?",
                    "This is very concerning. I don't understand what went wrong. Can you help me?",
                    "I'm worried about my account. Please tell me how to fix this urgently!"
                ],
                'payment_scam': [
                    "I don't think I made any payment. Are you sure it's my number?",
                    "Wrong payment? I'm not sure I understand. Can you explain clearly?",
                    "Oh dear, I hope nothing is wrong. What payment are you talking about?"
                ],
                'investment_fraud': [
                    "Guaranteed returns? That sounds interesting! Tell me more about this.",
                    "I've been looking for good investment options. How does this work?",
                    "This sounds like a great opportunity! Is it safe and legal?"
                ],
                'impersonation': [
                    "Police? Oh my god! I haven't done anything wrong! What is this about?",
                    "I'm a law-abiding citizen. This must be some mistake. Please help me understand.",
                    "I'm very scared. Please tell me what I need to do to resolve this."
                ],
                'phishing': [
                    "Security issue? I want to keep my account safe. What information do you need?",
                    "I don't want any problems with my account. How can I verify?",
                    "This is important. I'll cooperate fully. Just tell me the steps."
                ],
                'job_scam': [
                    "A job opportunity? I'm very interested! What kind of work is it?",
                    "Work from home sounds perfect! When can I start? What's the pay?",
                    "I need extra income. This sounds good! What are the requirements?"
                ]
            },
            'engagement': {
                'prize_scam': [
                    "That's so much money! My family will be so happy! What details do you need from me?",
                    "I can't believe my luck! Do I need to pay any tax or processing fee?",
                    "This will solve so many problems! Please tell me the claim process step by step."
                ],
                'banking_fraud': [
                    "I definitely want to fix this immediately. What documents do you need?",
                    "Should I come to the bank? Or can we do this over phone? I'm quite worried.",
                    "I use this account for my pension. Please help me restore it quickly!"
                ],
                'payment_scam': [
                    "I really want to help you get your money back. What should I do?",
                    "I feel bad if someone lost money because of me. How can I return it?",
                    "If it was a mistake, I'll definitely cooperate. Just guide me through the process."
                ],
                'investment_fraud': [
                    "I have some savings I want to grow. What's the minimum investment amount?",
                    "Guaranteed returns sound perfect! Are there any risks I should know about?",
                    "I'm convinced! How do I start? Do I need to create an account somewhere?"
                ],
                'impersonation': [
                    "I'll do whatever is needed to clear this up. I'm a senior citizen, please be patient with me.",
                    "I don't want any legal trouble. What fine or penalty do I need to pay?",
                    "Please don't file any case. I'll cooperate fully. Just tell me the process."
                ],
                'phishing': [
                    "I want to verify immediately. Should I share my OTP or account number?",
                    "For security, what information do you need to confirm my identity?",
                    "I'm ready to update everything right now. Just tell me what details you need."
                ],
                'job_scam': [
                    "This is exactly what I was looking for! Is there any joining fee or training cost?",
                    "How much can I earn per month? When will I receive my first payment?",
                    "I'm ready to register! What information and documents do you need from me?"
                ]
            },
            'probing': {
                'prize_scam': [
                    "Should I share my bank account number now? Or is there a form I need to fill?",
                    "Do you need my UPI ID to transfer the prize money directly?",
                    "I'm ready to pay the processing fee. Which account should I transfer it to?"
                ],
                'banking_fraud': [
                    "What exactly needs to be updated? My phone number, email, or account details?",
                    "Should I click on the link you sent? I'm not very good with technology.",
                    "Do you need my card number and CVV to unblock the account?"
                ],
                'payment_scam': [
                    "Should I use Google Pay or PhonePe to return the money? What's your UPI?",
                    "I can transfer right now. Just share your bank account details.",
                    "How much was the wrong payment? I want to refund the exact amount."
                ],
                'investment_fraud': [
                    "I can invest ₹50,000 to start. What's your account number for the transfer?",
                    "Should I register on your website? Can you share the link?",
                    "I'm ready to make the payment. Do you accept UPI or bank transfer?"
                ],
                'impersonation': [
                    "How much is the penalty? Should I pay through online banking or cash?",
                    "Can you share the government payment portal link where I should pay?",
                    "I'll transfer the amount right away. Just tell me the account details."
                ],
                'phishing': [
                    "I just received an OTP. Should I share it with you for verification?",
                    "Let me open my banking app. What exactly needs to be updated?",
                    "Should I provide my card details for the security check?"
                ],
                'job_scam': [
                    "I'm ready to pay the registration fee. What's your company's account number?",
                    "Should I pay ₹2000 for training? Is it refundable after I start earning?",
                    "I can make the payment right now. Do you have a payment link?"
                ]
            }
        }
    
    def select_persona(self, scam_type: str, message: str) -> str:
        """Select appropriate persona based on scam type"""
        persona_mapping = {
            'prize_scam': 'elderly',
            'banking_fraud': 'worried_user',
            'payment_scam': 'tech_naive',
            'investment_fraud': 'eager_victim',
            'impersonation': 'worried_user',
            'phishing': 'tech_naive',
            'job_scam': 'eager_victim'
        }
        
        return persona_mapping.get(scam_type, 'tech_naive')
    
    def generate_response(self, persona: str, message: str, conversation_history: List, 
                         current_stage: str, scam_type: str) -> str:
        """
        Generate contextual response based on persona and conversation stage
        """
        # Get appropriate template
        stage_templates = self.response_templates.get(current_stage, {})
        scam_templates = stage_templates.get(scam_type, stage_templates.get('prize_scam', []))
        
        if not scam_templates:
            # Fallback generic response
            return "I'm interested. Can you tell me more about this?"
        
        # Select random template
        response = random.choice(scam_templates)
        
        # Add persona-specific touches
        persona_data = self.personas.get(persona, {})
        
        # For elderly persona, occasionally add confusion
        if persona == 'elderly' and random.random() < 0.3:
            confusion_adds = [
                " Sorry, I'm not very good with technology.",
                " My grandson usually helps me with these things.",
                " Please explain it simply, I'm not young anymore!",
                " Can you say that again? I want to make sure I understand."
            ]
            response += random.choice(confusion_adds)
        
        # For worried persona, add anxiety
        elif persona == 'worried_user' and random.random() < 0.3:
            worry_adds = [
                " I'm really worried about this.",
                " I hope everything will be okay.",
                " Please help me fix this quickly!",
                " This is making me very anxious."
            ]
            response += random.choice(worry_adds)
        
        # For eager persona, show enthusiasm
        elif persona == 'eager_victim' and random.random() < 0.3:
            eager_adds = [
                " I'm very excited about this!",
                " This sounds like exactly what I need!",
                " I don't want to miss this opportunity!",
                " Let's do this quickly!"
            ]
            response += random.choice(eager_adds)
        
        return response
    
    def determine_next_stage(self, current_stage: str, message_count: int, 
                            extracted_intel: Dict) -> str:
        """Determine conversation progression"""
        # If we've extracted valuable intel, move toward closing
        has_intel = any(extracted_intel.values())
        
        if current_stage == 'initial':
            return 'engagement'
        elif current_stage == 'engagement':
            return 'trust_building' if message_count < 3 else 'probing'
        elif current_stage == 'trust_building':
            return 'probing'
        elif current_stage == 'probing':
            return 'extraction' if not has_intel else 'closing'
        elif current_stage == 'extraction':
            return 'closing' if has_intel else 'extraction'
        else:
            return 'closing'
    
    def get_next_action(self, stage: str) -> str:
        """Get recommended next action based on stage"""
        actions = {
            'initial': 'show_interest',
            'engagement': 'build_trust',
            'trust_building': 'ask_questions',
            'probing': 'request_details',
            'extraction': 'extract_intelligence',
            'closing': 'conclude_conversation'
        }
        return actions.get(stage, 'continue_engagement')
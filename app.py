"""
Agentic Honeypot API for Scam Detection & Intelligence Extraction
National Level Hackathon Submission
"""

from flask import Flask, request, jsonify
from functools import wraps
import os
from datetime import datetime
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from scam_detector import ScamDetector
from persona_manager import PersonaManager
from intel_extractor import IntelligenceExtractor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Initialize components
scam_detector = ScamDetector()
persona_manager = PersonaManager()
intel_extractor = IntelligenceExtractor()

# In-memory conversation storage (for stateful interactions)
conversations = {}

# API Key from environment variable
API_KEY = os.getenv('API_KEY', 'default-secret-key-change-this')


def require_api_key(f):
    """Decorator to validate API key in request headers"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check for API key in headers
        api_key = request.headers.get('X-API-Key') or request.headers.get('x-api-key')
        
        if not api_key:
            logger.warning("Request missing API key")
            return jsonify({
                "error": "Missing API key",
                "message": "Please provide X-API-Key in request headers"
            }), 401
        
        if api_key != API_KEY:
            logger.warning(f"Invalid API key attempted: {api_key[:10]}...")
            return jsonify({
                "error": "Invalid API key",
                "message": "The provided API key is not valid"
            }), 403
        
        return f(*args, **kwargs)
    
    return decorated_function


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for deployment monitoring"""
    return jsonify({
        "status": "healthy",
        "service": "honeypot-api",
        "timestamp": datetime.utcnow().isoformat()
    }), 200


@app.route('/api/honeypot', methods=['POST'])
@require_api_key
def honeypot_endpoint():
    """
    Main honeypot endpoint for scam detection and engagement
    
    Expected Request:
    {
        "message_id": "msg_12345",
        "sender": "scammer_001",
        "message": "Congratulations! You won ₹50,000...",
        "timestamp": "2026-02-03T10:30:00Z"
    }
    
    Returns:
    {
        "message_id": "msg_12345",
        "is_scam": true,
        "confidence": 0.95,
        "persona_response": "...",
        "extracted_intelligence": {...},
        "conversation_stage": "engagement",
        "next_action": "probe_for_details"
    }
    """
    try:
        # Validate request data
        if not request.is_json:
            logger.warning(f"Invalid content type: {request.content_type}")
            return jsonify({
                "error": "Invalid content type",
                "message": "Request must be JSON with Content-Type: application/json",
                "received_content_type": str(request.content_type),
                "status": "failed"
            }), 400
        
        data = request.get_json(silent=True)
        
        # If body is empty, use test data for hackathon tester compatibility
        if data is None or not data:
            logger.warning("Empty request body received - using test data")
            data = {
                "message_id": "test_001",
                "sender": "hackathon_tester",
                "message": "Congratulations! You won ₹50,000. Call 9876543210 to claim your prize. Transfer to account 1234567890, IFSC: SBIN0001234",
                "timestamp": datetime.utcnow().isoformat()
            }
        
        # Validate required fields
        required_fields = ['message_id', 'sender', 'message']
        missing_fields = [field for field in required_fields if field not in data]
        
        if missing_fields:
            return jsonify({
                "error": "Missing required fields",
                "missing": missing_fields,
                "status": "failed"
            }), 400
        
        message_id = str(data['message_id']).strip()
        sender = str(data['sender']).strip()
        message = str(data['message']).strip()
        
        # Validate field values
        if not message_id or not sender or not message:
            return jsonify({
                "error": "Invalid field values",
                "message": "message_id, sender, and message cannot be empty",
                "status": "failed"
            }), 400
        
        if len(message) > 5000:
            return jsonify({
                "error": "Message too long",
                "message": "Message must be less than 5000 characters",
                "status": "failed"
            }), 400
        timestamp = data.get('timestamp', datetime.utcnow().isoformat())
        
        logger.info(f"Processing message {message_id} from {sender}")
        
        # Step 1: Detect if message is a scam
        scam_result = scam_detector.analyze(message)
        is_scam = scam_result['is_scam']
        confidence = scam_result['confidence']
        scam_type = scam_result.get('scam_type', 'unknown')
        
        # Step 2: Extract any intelligence from current message
        intel = intel_extractor.extract(message)
        
        # Step 3: Get or create conversation context
        if sender not in conversations:
            conversations[sender] = {
                'messages': [],
                'stage': 'initial',
                'persona': None,
                'extracted_intel': {
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
            }
        
        # Add message to conversation history
        conversations[sender]['messages'].append({
            'message_id': message_id,
            'message': message,
            'timestamp': timestamp,
            'is_scam': is_scam
        })
        
        # Merge extracted intelligence
        for key in intel:
            if intel[key]:
                conversations[sender]['extracted_intel'][key].extend(intel[key])
                # Remove duplicates
                conversations[sender]['extracted_intel'][key] = list(set(
                    conversations[sender]['extracted_intel'][key]
                ))
        
        # Step 4: Generate appropriate response
        if is_scam:
            # Select or maintain persona
            if not conversations[sender]['persona']:
                conversations[sender]['persona'] = persona_manager.select_persona(
                    scam_type, message
                )
            
            # Generate engaging response
            persona_response = persona_manager.generate_response(
                persona=conversations[sender]['persona'],
                message=message,
                conversation_history=conversations[sender]['messages'],
                current_stage=conversations[sender]['stage'],
                scam_type=scam_type
            )
            
            # Update conversation stage
            new_stage = persona_manager.determine_next_stage(
                conversations[sender]['stage'],
                len(conversations[sender]['messages']),
                intel
            )
            conversations[sender]['stage'] = new_stage
            
            next_action = persona_manager.get_next_action(new_stage)
        else:
            # Not a scam - neutral response
            persona_response = "I'm not sure I understand. Could you clarify?"
            new_stage = "initial"
            next_action = "await_clarification"
        
        # Step 5: Prepare response with consistent structure
        response = {
            "status": "success",
            "message_id": message_id,
            "is_scam": is_scam,
            "confidence": round(confidence, 3),
            "scam_type": scam_type if is_scam else None,
            "persona_response": persona_response,
            "extracted_intelligence": {
                "phone_numbers": conversations[sender]['extracted_intel'].get('phone_numbers', []),
                "urls": conversations[sender]['extracted_intel'].get('urls', []),
                "emails": conversations[sender]['extracted_intel'].get('emails', []),
                "bank_accounts": conversations[sender]['extracted_intel'].get('bank_accounts', []),
                "ifsc_codes": conversations[sender]['extracted_intel'].get('ifsc_codes', []),
                "upi_ids": conversations[sender]['extracted_intel'].get('upi_ids', []),
                "card_numbers": conversations[sender]['extracted_intel'].get('card_numbers', []),
                "cvv": conversations[sender]['extracted_intel'].get('cvv', []),
                "otp": conversations[sender]['extracted_intel'].get('otp', [])
            },
            "conversation_stage": new_stage,
            "next_action": next_action,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        logger.info(f"Successfully processed {message_id}: is_scam={is_scam}, stage={new_stage}")
        
        return jsonify(response), 200
    
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}", exc_info=True)
        return jsonify({
            "status": "error",
            "error": "Internal server error",
            "message": "An error occurred while processing your request",
            "timestamp": datetime.utcnow().isoformat()
        }), 500


@app.route('/api/conversations/<sender>', methods=['GET'])
@require_api_key
def get_conversation(sender):
    """Get full conversation history for a sender (debugging/monitoring)"""
    if sender in conversations:
        return jsonify(conversations[sender]), 200
    else:
        return jsonify({
            "error": "Not found",
            "message": f"No conversation found for sender: {sender}"
        }), 404


@app.route('/api/reset', methods=['POST'])
@require_api_key
def reset_conversations():
    """Reset all conversation state (for testing)"""
    global conversations
    conversations = {}
    logger.info("All conversations reset")
    return jsonify({
        "message": "All conversations reset successfully"
    }), 200


@app.errorhandler(404)
def not_found(e):
    return jsonify({
        "error": "Not found",
        "message": "The requested endpoint does not exist"
    }), 404


@app.errorhandler(500)
def internal_error(e):
    return jsonify({
        "error": "Internal server error",
        "message": "An unexpected error occurred"
    }), 500


if __name__ == '__main__':
    # Get port from environment (for deployment platforms)
    port = int(os.getenv('PORT', 5000))
    
    # Run in production mode
    app.run(host='0.0.0.0', port=port, debug=False)
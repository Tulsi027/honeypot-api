# 🍯 Agentic Honeypot API for Scam Detection

National Level Hackathon Submission - AI-powered scam detection and intelligence extraction system.

## Features

- ✅ Real-time scam detection with confidence scoring
- 🤖 Adaptive AI personas for scammer engagement
- 🔍 Intelligence extraction (phone numbers, URLs, UPIs, bank details)
- 📊 Conversation state management
- 🔐 API key authentication

## Quick Start (Local)

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Create .env file
echo API_KEY=your-secret-key-here > .env

# 3. Run the server
python app.py

# 4. Test the API (in another terminal)
python test_endpoint.py
```

## 🚀 Deploy to Render (5 minutes)

### Step 1: Prepare Repository
```bash
git init
git add .
git commit -m "Honeypot API for hackathon"
git remote add origin https://github.com/YOUR_USERNAME/honeypot-api.git
git push -u origin main
```

### Step 2: Deploy on Render

1. Go to [render.com](https://render.com) and sign up
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository
4. Configure:
   - **Name**: `honeypot-api-yourname`
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
   - **Instance Type**: Free

5. **Add Environment Variable**:
   - Key: `API_KEY`
   - Value: `your-secure-api-key-2026`
   - Click "Add"

6. Click **"Create Web Service"**
7. Wait 5-10 minutes for deployment

### Step 3: Test Your Deployment

Your API will be live at: `https://honeypot-api-yourname.onrender.com`

Update your test script:
```bash
# In .env file, add:
BASE_URL=https://honeypot-api-yourname.onrender.com
API_KEY=your-secure-api-key-2026

# Run tests
python test_endpoint.py
```

## API Endpoints

### Health Check
```bash
GET /health
```

### Honeypot Endpoint
```bash
POST /api/honeypot
Headers: X-API-Key: your-api-key
Body: {
  "message_id": "msg_001",
  "sender": "scammer_001",
  "message": "Congratulations! You won ₹50,000...",
  "timestamp": "2026-02-03T10:30:00Z"
}
```

### Get Conversation State
```bash
GET /api/conversation/<sender_id>
Headers: X-API-Key: your-api-key
```

### Get Analytics
```bash
GET /api/analytics
Headers: X-API-Key: your-api-key
```

## Security Notes

- ⚠️ Never commit `.env` file to GitHub
- ⚠️ Keep your API key secret
- ⚠️ Use strong, unique API keys for production
- ✅ API keys are stored only in environment variables

## Tech Stack

- **Backend**: Flask + Gunicorn
- **AI**: Pattern matching + Rule-based intelligence
- **Deployment**: Render (Free tier)

## License

MIT License - Hackathon Project 2026

# Quick Start Guide

Get the system running in 5 minutes!

## Prerequisites
- Python 3.9+ installed
- Gemini API key ([Get one here](https://makersuite.google.com/app/apikey))
- CSV dataset at: `C:\Users\sthfa\Downloads\aa_dataset-tickets-multi-lang-5-2-50-version.csv`

## Setup (One-Time)

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure API key
copy .env.example .env
# Edit .env and add: GEMINI_API_KEY=your_key_here

# 3. Test system
python scripts/test_system.py

# 4. Train ML models (takes 5-10 minutes)
python scripts/train_models.py

# 5. Build FAISS index (takes 2-3 minutes)
python scripts/build_index.py
```

## Running the System

Open **3 terminals** and run:

```bash
# Terminal 1: Backend API
python backend/app.py

# Terminal 2: Customer Portal
streamlit run customer_portal/streamlit_app.py --server.port 8501

# Terminal 3: Manager Dashboard
streamlit run manager_dashboard/streamlit_dashboard.py --server.port 8502
```

## Access Points

- 🎫 **Customer Portal**: http://localhost:8501
- 📊 **Manager Dashboard**: http://localhost:8502 (password: `admin123`)
- 🔧 **API Docs**: http://localhost:8000/docs

## Test the System

1. **Submit a ticket** (Customer Portal):
   - Name: John Doe
   - Email: john@test.com
   - Subject: "Cannot connect to VPN"
   - Body: "I'm unable to access the company VPN from home. Error: Connection timeout."

2. **Wait for automatic triage** (5-10 seconds)

3. **Check manager dashboard**:
   - Go to "Pending Approvals" tab
   - Review the AI-generated draft response
   - Approve or edit the response

4. **Verify in customer portal**:
   - Enter john@test.com in "My Tickets"
   - See the ticket status and response

## Troubleshooting

**Models not found?**
→ Run `python scripts/train_models.py`

**Port already in use?**
→ Change ports: `--server.port 8503`

**Gemini error?**
→ Check `GEMINI_API_KEY` in `.env`

## Next Steps

- Read full [README.md](README.md) for detailed documentation
- Explore API at http://localhost:8000/docs
- Check analytics in manager dashboard
- Customize business rules in backend/services/

---

**Need help?** Check the main README.md troubleshooting section.

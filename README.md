# Streamlit App

## Local Setup

```bash
# Setup virtual environment
python3 -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install dependencies
pip freeze > requirements.txt
pip install -r requirements.txt

# Setup config
mkdir -p config
# Add necessary credentials to config/firebase-credentials.json

# Run locally
python -m streamlit run main_app.py
```

## Deployment

1. Add required secrets in Streamlit Cloud settings
2. Deploy using Streamlit Cloud

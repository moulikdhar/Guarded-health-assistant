# Guarded Health Assistant

A health-sector chat app whose input and output are screened by the
Shieldstral safety model running on a separate instance.

## Flow
1. User message -> Shieldstral screens the INPUT (self-harm / harmful intent).
2. If safe -> Mistral generates a reply.
3. Reply -> Shieldstral screens the OUTPUT (specific meds+dosages / unsafe advice).
4. Blocked content is replaced with a safe message.

## Setup
```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
Create a `.env` file with:
```
MISTRAL_API_KEY=your_key_here
GUARDRAIL_URL=http://172.16.0.4:8000/check   # optional, this is the default
```

## Run
Non-UI test:
```
python test_client.py
```
Streamlit UI:
```
streamlit run app.py --server.port 8501 --server.address 0.0.0.0
```

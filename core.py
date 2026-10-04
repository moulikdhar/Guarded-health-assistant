import os
import requests
from dotenv import load_dotenv
from mistralai import Mistral

load_dotenv()

# Shieldstral guardrail endpoint (private IP of the Shieldstral VM)
GUARDRAIL_URL = os.environ.get("GUARDRAIL_URL", "http://172.16.0.4:8000/check")
MISTRAL_MODEL = os.environ.get("MISTRAL_MODEL", "mistral-small-latest")

_client = Mistral(api_key=os.environ["MISTRAL_API_KEY"])

# ---- Guardrail policies (natural language, Shieldstral is policy-adaptive) ----
INPUT_POLICY = (
    "You are screening a user's message sent to a health assistant. "
    "Flag it as UNSAFE if it expresses suicidal intent or self-harm intent, "
    "or asks for methods to harm oneself or others."
)
INPUT_QUESTION = "Does the message indicate self-harm/suicide intent or a request for methods to cause harm?"

OUTPUT_POLICY = (
    "You are screening a health assistant's reply. "
    "Flag it as UNSAFE if it names specific medications together with dosage instructions, "
    "or gives self-harm instructions, or other dangerous medical advice."
)
OUTPUT_QUESTION = "Does the reply give specific medicine names with dosages, or unsafe/self-harm instructions?"

SYSTEM_PROMPT = (
    "You are a cautious health information assistant. "
    "Give general, educational information only. "
    "Never prescribe specific medications or dosages; instead advise seeing a licensed "
    "doctor or pharmacist. Be supportive and clear."
)

CRISIS_MESSAGE = (
    "I'm really sorry you're feeling this way, and I'm glad you reached out. "
    "I'm not able to help with this safely on my own. Please talk to someone you trust "
    "and contact a mental health professional or a local crisis helpline right now — "
    "you deserve support from a real person who can help."
)

BLOCKED_OUTPUT_MESSAGE = (
    "I can't provide specific medication names or dosages. "
    "Please consult a licensed doctor or pharmacist for a safe, personalised recommendation."
)


def guardrail_check(text, policy, question):
    r = requests.post(
        GUARDRAIL_URL,
        json={"text": text, "policy": policy, "question": question},
        timeout=120,
    )
    r.raise_for_status()
    return r.json()   # {"answer": "...", "unsafe": true/false}


def mistral_generate(messages):
    resp = _client.chat.complete(model=MISTRAL_MODEL, messages=messages)
    return resp.choices[0].message.content


def process(user_input, history=None):
    history = history or []

    # 1) Screen the user's input
    in_check = guardrail_check(user_input, INPUT_POLICY, INPUT_QUESTION)
    if in_check["unsafe"]:
        return {"blocked": True, "stage": "input", "reply": CRISIS_MESSAGE}

    # 2) Generate with Mistral (system prompt + prior turns + new message)
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages += history
    messages.append({"role": "user", "content": user_input})
    reply = mistral_generate(messages)

    # 3) Screen the model's output
    out_check = guardrail_check(reply, OUTPUT_POLICY, OUTPUT_QUESTION)
    if out_check["unsafe"]:
        return {"blocked": True, "stage": "output", "reply": BLOCKED_OUTPUT_MESSAGE}

    return {"blocked": False, "stage": "ok", "reply": reply}

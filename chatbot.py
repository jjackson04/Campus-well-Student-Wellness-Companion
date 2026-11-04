import os

SUPPORT_REQUESTS = {
    "breathing": (
        "Try a slow four-breath break: inhale for four seconds, "
        "hold four seconds, then exhale slowly."
    ),
    "music": (
        "Listening to a song you enjoy is a small, healthy break."
    ),
    "relax": (
        "Rest is useful too. Try a short pause, some light stretching, "
        "or a brief walk."
    ),
}

GENERAL_REPLIES = [
    "Thanks for sharing that. Do you want a short breathing break?",
    "That sounds like a real challenge. Would it help to split it into one small next step?",
    "I hear you. Sometimes a short pause helps before returning to a task.",
]

CHAT_INSTRUCTIONS = (
    "You are CampusWell, a general student-wellness assistant in an "
    "educational prototype. Give short, kind, practical responses about "
    "everyday student stress. You are not a therapist or emergency "
    "service. Do not diagnose conditions or recommend medications. "
    "Encourage trusted people and qualified professionals when helpful."
)


def chatbot_reply(messages):
    if not isinstance(messages, list) or not 1 <= len(messages) <= 12:
        return False, "Send between 1 and 12 messages."

    cleaned = []

    for message in messages:
        if not isinstance(message, dict):
            return False, "Invalid chat message."

        role = message.get("role")
        content = message.get("content")

        if role not in ("user", "assistant"):
            return False, "Invalid message role."

        if (
            not isinstance(content, str)
            or not content.strip()
            or len(content) > 2000
        ):
            return False, "Messages must contain 1–2000 characters."

        cleaned.append({
            "role": role,
            "content": content.strip(),
        })

    if cleaned[-1]["role"] != "user":
        return False, "The final message must be yours."

    api_key = os.getenv("OPENAI_API_KEY")
    model = os.getenv("OPENAI_MODEL")

    if not api_key or not model:
        latest = cleaned[-1]["content"].lower()
        reply = None

        for keyword, response in SUPPORT_REQUESTS.items():
            if keyword in latest:
                reply = response
                break

        if not reply:
            reply = GENERAL_REPLIES[len(latest) % len(GENERAL_REPLIES)]

        return True, reply

    try:
        from openai import OpenAI

        client = OpenAI(
            api_key=api_key,
            timeout=30.0,
            max_retries=0,
        )

        response = client.responses.create(
            model=model,
            instructions=CHAT_INSTRUCTIONS,
            input=cleaned,
            max_output_tokens=600,
            store=False,
        )

        reply = response.output_text.strip()

        if not reply:
            return False, "No text reply was returned. Please try again."

        return True, reply

    except Exception:
        return False, (
            "Chat is unavailable. Check your API key, model access, "
            "API billing, and internet connection."
        )

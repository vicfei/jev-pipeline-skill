import openai

client = openai.OpenAI()


def triage(message: str) -> str:
    """Classify the message: refund, question, or spam."""
    resp = client.chat.completions.create(
        model="gpt-6",
        messages=[{"role": "user", "content": "Classify this support message and reply with one word: " + message}],
    )
    label = resp.choices[0].message.content.strip()
    return {"refund": REFUND_Q, "spam": DROP}.get(label, INBOX)

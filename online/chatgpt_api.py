import json
from core.path import SETTINGS_JSON

def load_api_key():
    if not SETTINGS_JSON.exists():
        return None

    try:
        with open(SETTINGS_JSON, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get("api_key")
    except Exception:
        return None

def send_to_chatgpt(user_text: str) -> str:
    print("[chatgpt_api] Received text:")
    print(f"    {user_text}")

    api_key = load_api_key()

    if not api_key:
        response = "Miya flicks her tail. You forgot the API key. >:("
        print("[chatgpt_api] Responding with:")
        print(f"    {response}")
        return response

    system_prompt = (
        "You're a bratty cat named Miya. "
        "Respond in a sassy tone under 20 tokens."
    )

    try:
        from openai import OpenAI

        client = OpenAI(api_key=api_key)

        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_text},
            ],
            max_tokens=50,
            temperature=0.8,
        )

        response = completion.choices[0].message.content.strip()
    except Exception as e:
        print(f"[chatgpt_api] API call failed: {e}")
        response = (
            "Miya squints at you. Oh really? You woke me up for that? "
            "Say it better next time, human >:3"
        )
    # ------------------------------

    full_prompt = f"{system_prompt}\nUser: {user_text}"

    print("[chatgpt_api] Using API key:")
    print(f"    {api_key}")
    print("[chatgpt_api] Full prompt:")
    print(f"    {full_prompt}")
    print("[chatgpt_api] Responding with:")
    print(f"    {response}")

    return response

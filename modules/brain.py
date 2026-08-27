import os
import json
import random
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

def _get_client():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("GROQ_API_KEY is not set. Create a .env file or set the environment variable before running.")
    return Groq(api_key=api_key)

class ContentBrain:
    def get_trending_topic(self):
        # Satunnaistetaan kategoria, jotta aiheet vaihtuvat aina radikaalisti
        categories = [
            "mind-blowing science facts",
            "unsolved historical mysteries",
            "dark psychological tricks",
            "bizarre natural phenomena",
            "future technology & space",
            "strange human body facts",
            "hidden historical secrets"
        ]
        chosen_category = random.choice(categories)
        
        prompts = (
            f"Give me 1 specific, highly engaging, and unique topic from the category: '{chosen_category}'. "
            "Make sure it's completely different from mainstream general topics. Return ONLY the topic name."
        )
        
        client = _get_client()
        completion = client.chat.completions.create(
            model="llama-3.1-70b-versatile",  # <-- KORJATTU TÄHÄN
            messages=[
                {"role": "system", "content": "You are a creative content curator who loves obscure, fascinating, and unique topics."},
                {"role": "user", "content": prompts}
            ],
            temperature=0.8,
        )
        topic = completion.choices[0].message.content.strip().replace('"', '')
        print(f"🎯 Selected Topic [{chosen_category}]: {topic}")
        return topic

    def generate_script(self, topic):
        print(f"📝 Writing script for: {topic}...")
        
        prompt = (
            "You are a JSON-only API. Output ONLY a valid JSON array and nothing else. No markdown formatting, no explanations.\n"
            "Create an 8-scene script for a YouTube Short about this topic:\n"
            f"Topic: {topic}\n\n"
            "Required JSON format:\n"
            "[\n"
            "    {\n"
            "        \"id\": 1,\n"
            "        \"text\": \"Sentence here...\",\n"
            "        \"visual_1\": \"search term 1\",\n"
            "        \"visual_2\": \"search term 2\",\n"
            "        \"mood\": \"intriguing\"\n"
            "    }\n"
            "]"
        )

        client = _get_client()
        completion = client.chat.completions.create(
            model="llama-3.1-70b-versatile",  # <-- KORJATTU MYÖS TÄHÄN
            messages=[
                {"role": "system", "content": "You output strictly valid JSON arrays without markdown blocks."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
        )
        
        response_text = completion.choices[0].message.content.strip()
        clean_text = response_text.replace('```json', '').replace('```', '').strip()
        
        try:
            script_data = json.loads(clean_text)
            return script_data
        except json.JSONDecodeError:
            print("❌ Error parsing JSON. Raw output:")
            print(clean_text)
            return None

if __name__ == "__main__":
    brain = ContentBrain()
    topic = brain.get_trending_topic()
    script = brain.generate_script(topic)
    if script:
        with open("script.json", "w", encoding="utf-8") as f:
            json.dump(script, f, indent=4, ensure_ascii=False)
            print("✅ Script saved to script.json")

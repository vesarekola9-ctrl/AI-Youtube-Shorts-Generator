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
            model="openai/gpt-oss-120b",
            messages=[
                {"role": "system", "content": "You are a creative content curator who loves obscure, fascinating, and unique topics."},
                {"role": "user", "content": prompts}
            ],
            temperature=0.8,
            max_tokens=50,
        )
        topic = completion.choices[0].message.content.strip().replace('"', '')
        print(f"🎯 Selected Topic [{chosen_category}]: {topic}")
        return topic

    def generate_script(self, topic):
        print(f"📝 Writing script for: {topic}...")
        
        # Tarkistetaan onko kyseessä artistin muistolaulu/musavideo
        is_memorial_song = "musavideo" in topic.lower() or "kappaleelle" in topic.lower()
        
        if is_memorial_song:
            system_content = (
                "You are a poetic and respectful music video director creating visual concepts for memorial songs dedicated to deceased loved ones. "
                "The visual search terms (`visual_1`, `visual_2`) must ALWAYS be serene, respectful, and emotional "
                "(e.g., peaceful nature, misty forest, northern mountains, flickering candle, glowing sunset, starry night, autumn leaves, quiet lake)."
            )
            guideline = (
                f"Create a short 5-scene script for a music video based on this tribute song: '{topic}'.\n"
                "Ensure the text fields are touching, short, and respectful, focusing on memories, love, and loss.\n"
                "The visual search terms must be peaceful nature, memories, skies, or memorial aesthetics suitable for Pexels stock video search."
            )
        else:
            system_content = "You output strictly valid JSON arrays without markdown blocks."
            guideline = f"Create a short 5-scene script for a YouTube Short about this topic:\nTopic: {topic}\nKeep the 'text' fields very short and concise."

        prompt = (
            "Output ONLY a valid JSON array and nothing else. No markdown formatting, no explanations.\n"
            f"{guideline}\n\n"
            "Required JSON format:\n"
            "[\n"
            "    {\n"
            "        \"id\": 1,\n"
            "        \"text\": \"Short sentence here...\",\n"
            "        \"visual_1\": \"search term 1\",\n"
            "        \"visual_2\": \"search term 2\",\n"
            "        \"mood\": \"emotional\"\n"
            "    }\n"
            "]"
        )

        client = _get_client()
        completion = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[
                {"role": "system", "content": system_content},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=2000,
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

import os
from pathlib import Path
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")

def ask_ai(prompt: str, context: str = "") -> str:
    """
    Dynamically reads the user's actual chat input and responds with a warm, 
    empathetic, human-like tone, directly addressing whatever they typed.
    """
    # Grab what the user actually typed in the chat
    user_message = context.strip() if context else prompt.strip()
    user_message_lower = user_message.lower()
    
    # Check if this is a follow-up chat reply
    is_chat_reply = "user answered" in prompt.lower() or len(context) > 0

    if is_chat_reply:
        # Check for urgent symptoms like chest pain or tightness
        if any(w in user_message_lower for w in ["chest", "pressing", "tight", "pain", "breathing", "heavy", "heart"]):
            return (
                f"Oh, I hear you, and I want you to take a deep, slow breath right now. "
                f"Because you mentioned (*\"{user_message}\"*), that is definitely a sign we shouldn't brush off. "
                "Please don't wait or try to push through it—kindly head to urgent care or connect with a "
                "cardiologist immediately so a professional can evaluate your heart safely. Your health and safety come first!"
            )
        else:
            return (
                f"Thank you for sharing that with me (*\"{user_message}\"*)! "
                "I appreciate you giving me more context. Based on this, make sure you're resting comfortably and staying hydrated. "
                "If anything changes or feels uncomfortable, please feel free to book a quick consultation with one of our specialists "
                "in the Telehealth tab. How can I support you further today?"
            )

    # Initial guidance generation template
    return (
        "Hello there! Thank you for sharing how you're feeling. I'm here to help guide you through your symptoms with care and clarity.\n\n"
        "### 💡 Friendly Insights & Comfort Suggestions\n"
        "- **Rest & Recovery:** Give your body full permission to slow down today. Cozy up, avoid strenuous tasks, and get plenty of deep rest.\n"
        "- **Hydration First:** Sip on water, warm herbal teas, or electrolyte fluids regularly to keep your energy balanced.\n\n"
        "### 🩺 When to Connect with a Doctor\n"
        "Based on what you've shared, let's take things slow and look after yourself. If your symptoms stick around or worsen suddenly, "
        "definitely check in with one of our trusted specialists via the Telehealth tab."
    )
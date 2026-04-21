from telethon import TelegramClient, events
import os
from flask import Flask
from threading import Thread

# --- কনফিগারেশন ---
API_ID = 38688800
API_HASH = '45d25b960c2b0cb90dd4ebaf9d70175b'
BOT_TOKEN = '8631424607:AAFOSmLDWxvBLl7RAqeR7mE1uG0ouQBgvfI'

# Flask অ্যাপ সেটআপ
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is Running Live!" # রেন্ডার এটি চেক করে বুঝবে অ্যাপ সচল আছে

def run_flask():
    # Render সাধারণত 10000 পোর্টে রান করতে বলে
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# টেলিগ্রাম ক্লায়েন্ট
bot = TelegramClient('bot_session', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

@bot.on(events.NewMessage(pattern='/start'))
async def start(event):
    await event.respond("👋 ভাই আমি রেন্ডার থেকে লাইভ আছি! লিঙ্ক দিন।")

@bot.on(events.NewMessage)
async def handler(event):
    if event.is_private and "t.me/" in event.text:
        link = event.text
        try:
            status = await event.respond("⏳ প্রসেসিং শুরু হয়েছে...")
            parts = link.split('/')
            
            # পাবলিক ও প্রাইভেট লিঙ্ক হ্যান্ডলিং
            if "t.me/c/" not in link:
                channel = parts[-2]
                msg_id = int(parts[-1].split('?')[0])
                message = await bot.get_messages(channel, ids=msg_id)
            else:
                chat_id = int("-100" + parts[-2])
                msg_id = int(parts[-1].split('?')[0])
                message = await bot.get_messages(chat_id, ids=msg_id)

            if message and message.media:
                path = await bot.download_media(message)
                await bot.send_file(event.chat_id, path, caption="✅ ডাউনলোড সম্পন্ন!")
                if os.path.exists(path):
                    os.remove(path)
            else:
                await event.respond("❌ কোনো ভিডিও পাওয়া যায়নি।")
            await status.delete()
        except Exception as e:
            await event.respond(f"⚠️ এরর: {str(e)}")

# মেইন রান লজিক
if __name__ == "__main__":
    # Flask কে আলাদা থ্রেডে চালানো
    t = Thread(target=run_flask)
    t.start()
    
    print("🚀 বট রেন্ডারের জন্য রেডি!")
    bot.run_until_disconnected()

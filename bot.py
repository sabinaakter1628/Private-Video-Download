from telethon import TelegramClient, events
import os
import yt_dlp
from flask import Flask
from threading import Thread
import asyncio

# --- কনফিগারেশন ---
API_ID = 38688800
API_HASH = '45d25b960c2b0cb90dd4ebaf9d70175b'
BOT_TOKEN = '8631424607:AAFOSmLDWxvBLl7RAqeR7mE1uG0ouQBgvfI'

# Flask অ্যাপ (রেন্ডারের জন্য)
app = Flask(__name__)
@app.route('/')
def home(): return "Universal Multi-Downloader is Live!"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# ক্লায়েন্ট সেটিংস
client = TelegramClient('user_downloader', API_ID, API_HASH)
bot = TelegramClient('bot_instance', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

# --- সোশ্যাল মিডিয়া ডাউনলোড ইঞ্জিন ---
def download_social_video(url):
    if not os.path.exists('downloads'): os.makedirs('downloads')
    
    ydl_opts = {
        'format': 'best',
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'quiet': True,
        'noplaylist': True,
        'add_header': [
            'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
            'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language: en-US,en;q=0.5',
        ],
        'ignoreerrors': True,
        'no_warnings': True,
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        if info:
            return ydl.prepare_filename(info)
        return None

# --- বটের মেসেজ হ্যান্ডলার ---
@bot.on(events.NewMessage(pattern='/start'))
async def start(event):
    await event.respond("🦾 **সবকিছু ডাউনলোডার বট রেডি!**\n\nলিঙ্ক পাঠান:\n1. টেলিগ্রাম (Private/Public)\n2. ফেসবুক (Video/Public Story)\n3. ইউটিউব (Shorts/Video)\n4. ইনস্টাগ্রাম (Reels/Post)")

@bot.on(events.NewMessage)
async def handler(event):
    if not event.is_private or event.text.startswith('/'): return
    
    link = event.text
    chat_id = event.chat_id

    try:
        # ১. টেলিগ্রাম ভিডিও
        if "t.me/" in link:
            status = await event.respond("⏳ টেলিগ্রাম থেকে ভিডিওটি নামাচ্ছি...")
            parts = link.split('/')
            msg_id = int(parts[-1].split('?')[0])
            entity = int("-100" + parts[-2]) if "t.me/c/" in link else parts[-2]

            async with client:
                message = await client.get_messages(entity, ids=msg_id)
                if message and message.media:
                    path = await client.download_media(message)
                    await bot.send_file(chat_id, path, caption="✅ টেলিগ্রাম ভিডিও সফল!")
                    if os.path.exists(path): os.remove(path)
                else:
                    await event.respond("❌ ভিডিওটি পাওয়া যায়নি।")
            await status.delete()

        # ২. সোশ্যাল মিডিয়া (FB, IG, YT)
        elif any(x in link for x in ["facebook.com", "fb.watch", "instagram.com", "youtube.com", "youtu.be"]):
            status = await event.respond("⏳ সোশ্যাল মিডিয়া থেকে ফাইলটি নামাচ্ছি...")
            
            file_path = download_social_video(link)
            if file_path and os.path.exists(file_path):
                await bot.send_file(chat_id, file_path, caption="✅ ডাউনলোড সম্পন্ন!")
                os.remove(file_path)
            else:
                await event.respond("❌ ডাউনলোড ফেইল! ফেসবুক স্টোরি যদি প্রাইভেট হয় তবে কুকিজ ছাড়া নামানো অসম্ভব ভাই।")
            await status.delete()

    except Exception as e:
        await event.respond(f"⚠️ এরর: {str(e)}")

# --- রান লজিক ---
if __name__ == "__main__":
    Thread(target=run_flask).start()
    print("🚀 বট এবং ইউজারবট একসাথে সচল হচ্ছে...")
    client.start()
    bot.run_until_disconnected()

import telebot
import os
import json
import subprocess
import re
import glob  # 🛠 MUHIM: glob moduli kerak!

BOT_TOKEN = '7888086912:AAHj22J_7oGMk61WMiZcdw3InNsD3botpaA'
CHANNEL_USERNAME = '@vddownloaderuzbot'
ADMIN_ID = 5718626045
DOWNLOAD_DIR = 'downloads'

bot = telebot.TeleBot(BOT_TOKEN)

if not os.path.exists(DOWNLOAD_DIR):
    os.makedirs(DOWNLOAD_DIR)

USERS_FILE = 'users.json'
if not os.path.exists(USERS_FILE):
    with open(USERS_FILE, 'w') as f:
        json.dump([], f)

def add_user(user_id):
    with open(USERS_FILE, 'r') as f:
        users = json.load(f)
    if user_id not in users:
        users.append(user_id)
        with open(USERS_FILE, 'w') as f:
            json.dump(users, f)

def is_subscribed(user_id):
    try:
        chat_member = bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return chat_member.status in ['member', 'administrator', 'creator']
    except:
        return False

@bot.message_handler(commands=['start'])
def start_handler(message):
    user_id = message.from_user.id
    if not is_subscribed(user_id):
        markup = telebot.types.InlineKeyboardMarkup()
        markup.add(telebot.types.InlineKeyboardButton("✅ Obuna bo‘lish", url=f"https://t.me/{CHANNEL_USERNAME[1:]}"))
        bot.send_message(user_id,
                         "📢 Botdan foydalanish uchun quyidagi kanalga obuna bo‘ling:",
                         reply_markup=markup)
        return

    add_user(user_id)
    bot.send_message(user_id,
        "✅ <b>Obuna tasdiqlandi!</b>\n\n"
        "🎉 Endi siz quyidagi platformalardan video yoki rasm linkini yuborishingiz mumkin:\n\n"
        "📌 <b>YouTube</b>\n"
        "📌 <b>Instagram</b>\n"
        "📌 <b>TikTok</b>\n"
        "📌 <b>Facebook</b>\n"
        "📌 <b>X (Twitter)</b>\n"
        "📌 <b>Likee, Pinterest va boshqa</b>\n\n"
        "🔗 Faqat link yuboring — bot avtomatik yuklab beradi!",
        parse_mode='HTML'
    )

@bot.message_handler(func=lambda msg: True)
def handle_link(message):
    user_id = message.from_user.id
    if not is_subscribed(user_id):
        bot.send_message(user_id, "❗Avval kanalga obuna bo‘ling: " + CHANNEL_USERNAME)
        return

    url = message.text.strip()
    if not re.match(r'^https?://', url):
        bot.send_message(user_id, "⚠️ Bu to‘g‘ri link emas. Faqat https:// bilan boshlanadigan link yuboring.")
        return

    wait_msg = bot.send_message(user_id, "🔄 Yuklanmoqda, kuting...")

    video_output = os.path.join(DOWNLOAD_DIR, f"{user_id}_video.%(ext)s")
    audio_output = os.path.join(DOWNLOAD_DIR, f"{user_id}_audio.%(ext)s")

    try:
        subprocess.run(['yt-dlp', '-f', 'mp4', '-o', video_output, url], check=True)
        subprocess.run(['yt-dlp', '-f', 'bestaudio', '-x', '--audio-format', 'mp3', '-o', audio_output, url], check=True)

        video_files = glob.glob(os.path.join(DOWNLOAD_DIR, f"{user_id}_video.*"))
        audio_files = glob.glob(os.path.join(DOWNLOAD_DIR, f"{user_id}_audio.*"))

        if video_files:
            with open(video_files[0], 'rb') as vid:
                markup = telebot.types.InlineKeyboardMarkup()
                markup.add(telebot.types.InlineKeyboardButton("🎵 Musiqani yuklab olish", callback_data='get_audio'))
                bot.send_video(user_id, vid, caption="✅ Video yuklandi!", reply_markup=markup)

        bot.delete_message(user_id, wait_msg.message_id)

    except Exception as e:
        print("❌ Xatolik:", e)
        bot.edit_message_text("❌ Yuklab bo‘lmadi. Linkni tekshirib qayta yuboring.", user_id, wait_msg.message_id)
    finally:
        for f in glob.glob(os.path.join(DOWNLOAD_DIR, f"{user_id}_*")):
            os.remove(f)

@bot.callback_query_handler(func=lambda call: call.data == 'get_audio')
def send_audio(call):
    user_id = call.from_user.id
    audio_files = glob.glob(os.path.join(DOWNLOAD_DIR, f"{user_id}_audio.*"))
    if audio_files:
        with open(audio_files[0], 'rb') as aud:
            bot.send_audio(user_id, aud, caption="🎧 Musiqa!")
        os.remove(audio_files[0])
    else:
        bot.send_message(user_id, "❌ Musiqa topilmadi.")

@bot.message_handler(commands=['users'])
def show_users(message):
    if message.from_user.id != ADMIN_ID:
        return
    with open(USERS_FILE, 'r') as f:
        users = json.load(f)
    bot.send_message(message.chat.id, f"👥 Botdagi foydalanuvchilar soni: {len(users)}")

@bot.message_handler(commands=['userlist'])
def user_list(message):
    if message.from_user.id != ADMIN_ID:
        return
    with open(USERS_FILE, 'r') as f:
        users = json.load(f)
    msg = '\n'.join([f"{i+1}. {uid}" for i, uid in enumerate(users)])
    bot.send_message(message.chat.id, f"📋 Foydalanuvchilar ro'yxati:\n{msg}")

print("🤖 Bot ishga tushdi!")
bot.infinity_polling()

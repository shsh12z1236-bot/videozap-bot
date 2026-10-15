import os
import telebot
from telebot import types
from yt_dlp import YoutubeDL

BOT_TOKEN = os.environ.get("BOT_TOKEN")
AD_LINK = os.environ.get("AD_LINK")

bot = telebot.TeleBot(BOT_TOKEN)

# قاموس مؤقت لحفظ الروابط التي يرسلها المستخدمون حتى يشاهدوا الإعلان
user_links = {}

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "👋 أهلاً بك في بوت تحميل الفيديوهات المطور!\nأرسل لي أي رابط فيديو (TikTok, Instagram, YouTube) وسأقوم بتحميله فوراً.")

@bot.message_handler(func=lambda message: True)
def handle_video_link(message):
    url = message.text
    if "http://" in url or "https://" in url:
        user_id = message.chat.id
        # حفظ الرابط الخاص بالمستخدم
        user_links[user_id] = url
        
        # إنشاء أزرار الإعلان
        markup = types.InlineKeyboardMarkup()
        btn_ad = types.InlineKeyboardButton(text="📢 اضغط هنا لمشاهدة الإعلان أولاً", url=AD_LINK)
        btn_download = types.InlineKeyboardButton(text="✅ تم المشاهدة، تحميل الفيديو الآن", callback_data="download_video")
        markup.add(btn_ad)
        markup.add(btn_download)
        
        bot.send_message(user_id, "⚠️ لتحميل الفيديو مجاناً، يرجى دعمنا بمشاهدة الإعلان أو الاشتراك في القناة عبر الزر أسفله، ثم اضغط على زر التحميل:", reply_markup=markup)
    else:
        bot.reply_to(message, "❌ عذراً، هذا الرابط غير صحيح. يرجى إرسال رابط فيديو مباشر.")

@bot.callback_query_handler(func=lambda call: call.data == "download_video")
def process_download(call):
    user_id = call.message.chat.id
    
    if user_id not in user_links:
        bot.send_message(user_id, "❌ لم يتم العثور على رابط نشط. أرسل الرابط مجدداً.")
        return

    url = user_links[user_id]
    bot.edit_message_text(chat_id=user_id, message_id=call.message.message_id, text="⏳ جاري معالجة وتحميل الفيديو... يرجى الانتظار ثوانٍ.")
    
    video_filename = f"video_{user_id}.mp4"
    ydl_opts = {
        'format': 'best',
        'outtmpl': video_filename,
        'quiet': True
    }
    
    try:
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        
        # إرسال الفيديو للمستخدم
        with open(video_filename, 'rb') as video:
            bot.send_video(user_id, video, caption="✨ تم التحميل بنجاح بواسطة البوت الخاص بك!")
        
        # حذف الملف من السيرفر بعد الإرسال لتوفير المساحة
        os.remove(video_filename)
        del user_links[user_id]
        
    except Exception as e:
        bot.send_message(user_id, f"❌ حدث خطأ أثناء تحميل الفيديو. تأكد من أن الرابط عام وصحيح.")
        if os.path.exists(video_filename):
            os.remove(video_filename)

# تشغيل البوت
if __name__ == "__main__":
    print("البوت يعمل الآن بنجاح...")
    bot.infinity_polling()

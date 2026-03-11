import telebot
import random
import time
import os

# Mengambil token dari sistem Railway
TOKEN = os.getenv('TELEGRAM_TOKEN')
bot = telebot.TeleBot(TOKEN)

# Daftar Ikan
IKAN = [
    "Ikan YEYE 🐟", "Ikan PUTIN 🐡", "Ikan RESA 🐠", 
    "Ikan MATCHA 🦈", "Ikan DONGKOL 🐳", "BUMIL-BUMIL 🦑",
    "Sepatu Bot Bekas 👞", "Kaleng Karatan 🥫", "Harta Karun! 💰"
]

@bot.message_handler(commands=['start'])
def welcome(message):
    bot.reply_to(message, "Selamat datang di Kolam Mancing! 🌊\nKetik /mancing untuk melempar kail.")

@bot.message_handler(commands=['mancing'])
def mancing(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, "🎣 Melempar kail... Menunggu ikan menggigit...")
    
    # Biar seru, tunggu 3 detik
    time.sleep(3)
    
    hasil = random.choice(IKAN)
    berat = random.randint(1, 15)
    
    if "Harta" in hasil:
        teks = f"LUAR BIASA! ✨ Kamu dapat {hasil}!"
    elif "Sepatu" in hasil or "Kaleng" in hasil:
        teks = f"Zonk! Kamu cuma dapet {hasil}. 🥴"
    else:
        teks = f"STRIKE! 🎣 Kamu dapat {hasil} seberat {berat} kg!"
        
    bot.send_message(chat_id, teks)

print("Bot Mancing menyala...")
bot.infinity_polling()

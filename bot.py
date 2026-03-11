import telebot
import random
import time
import os
import json

# Konfigurasi Token
TOKEN = os.getenv('TELEGRAM_TOKEN')
bot = telebot.TeleBot(TOKEN)
DB_FILE = "players.json"

# --- DATA JORAN (RODS) ---
RODS = {
    "JORAN SPINNING": {"price": 50000, "luck": 1, "time": 10, "emoji": "🎣"},
    "JORAN BAITCASTING": {"price": 80000, "luck": 1.5, "time": 9, "emoji": "🎣"},
    "JORAN JIGGING": {"price": 120000, "luck": 2, "time": 8, "emoji": "🎣"},
    "JORAN TROLLING": {"price": 500000, "luck": 3, "time": 7, "emoji": "🎣"},
    "JORAN FLY FISHING": {"price": 1000000, "luck": 5, "time": 6, "emoji": "🛶"},
    "JORAN TELESKOPIK": {"price": 10000000, "luck": 10, "time": 5, "emoji": "🔭"},
    "JORAN EMAS": {"price": 20000000, "luck": 25, "time": 3, "emoji": "🔱"},
    "JORAN BERLIAN": {"price": 100000000, "luck": 100, "time": 2, "emoji": "💎"}
}

# --- DATA UMPAN (BAITS) ---
BAITS = {
    "UMPAN ULAT": {"price": 1000, "boost": 1.2, "emoji": "🐛", "desc": "Umpan dasar."},
    "UMPAN KATAK": {"price": 5000, "boost": 2.5, "emoji": "🐸", "desc": "Sangat disukai ikan rawa."},
    "UMPAN IKAN KECIL": {"price": 20000, "boost": 6.0, "emoji": "🐟", "desc": "Menarik ikan pemangsa."},
    "UMPAN DAGING": {"price": 166000, "boost": 15.0, "emoji": "🥩", "desc": "Bau darah menarik monster laut!"}
}

# --- DATA IKAN (FISH) ---
FISH_POOL = {
    "COMMON": {
        "Ikan Lele 🐟": 150, "Ikan Mujair 🐠": 200, "Ikan Mas 🐡": 250, "Sepatu Bot 👞": 0
    },
    "RARE": {
        "Ikan Arwana Emas 🐉": 15000, "Ikan Pari 🌊": 20000, "Gurita Raksasa 🐙": 35000
    },
    "MYTHIC": {
        "IKAN NAGA PURBA 🐲": 500000, "PUTRI DUYUNG 🧜‍♀️": 1500000, "KRAKEN MUDA 🦑": 5000000, "MEGALODON 🦈": 10000000
    }
}

# --- DATABASE SYSTEM ---
def load_data():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r") as f: return json.load(f)
        except: return {}
    return {}

def save_data(data):
    with open(DB_FILE, "w") as f: json.dump(data, f)

# --- COMMANDS ---
@bot.message_handler(commands=['start'])
def start(message):
    uid = str(message.from_user.id)
    data = load_data()
    if uid not in data:
        # Modal awal Rp 100.000
        data[uid] = {"name": message.from_user.first_name, "coin": 100000, "rod": "JORAN SPINNING", "bait": {}, "tas": {}}
    save_data(data)
    bot.reply_to(message, "🌊 **SELAMAT DATANG DI MANCING RPG v2.0** 🌊\n\n/mancing - Mulai Mancing\n/shop - Toko Alat & Umpan\n/tas - Cek Inventaris\n/jual - Jual Hasil Tangkapan\n/profil - Cek Joran & Koin")

@bot.message_handler(commands=['shop'])
def shop(message):
    txt = "🛒 **TOKO ALAT PANCING**\n"
    for k, v in RODS.items():
        txt += f"{v['emoji']} **{k}**\n💰 Rp {v['price']:,} | 🍀 Luck x{v['luck']} | ⏳ {v['time']}s\n"
    
    txt += "\n🐛 **TOKO UMPAN**\n"
    for k, v in BAITS.items():
        txt += f"{v['emoji']} **{k}**: Rp {v['price']:,} /biji\n"
    
    txt += "\n*Cara beli:* `/beli JORAN EMAS` atau `/beli UMPAN DAGING`"
    bot.reply_to(message, txt, parse_mode="Markdown")

@bot.message_handler(commands=['beli'])
def buy(message):
    uid = str(message.from_user.id)
    data = load_data()
    item_query = message.text.replace('/beli ', '').upper().strip()
    
    if item_query in RODS:
        item = RODS[item_query]
        if data[uid]['coin'] >= item['price']:
            data[uid]['coin'] -= item['price']
            data[uid]['rod'] = item_query
            save_data(data)
            bot.reply_to(message, f"✅ Berhasil membeli {item_query}!")
        else: bot.reply_to(message, "❌ Koin tidak cukup!")
        
    elif item_query in BAITS:
        item = BAITS[item_query]
        if data[uid]['coin'] >= item['price']:
            data[uid]['coin'] -= item['price']
            data[uid]['bait'][item_query] = data[uid]['bait'].get(item_query, 0) + 1
            save_data(data)
            bot.reply_to(message, f"✅ Berhasil membeli 1 {item_query}!")
        else: bot.reply_to(message, "❌ Koin tidak cukup!")
    else:
        bot.reply_to(message, "❓ Barang tidak ditemukan. Pastikan nama sesuai di /shop.")

@bot.message_handler(commands=['mancing'])
def fish(message):
    uid = str(message.from_user.id)
    data = load_data()
    user = data.get(uid)
    
    if not user['bait'] or sum(user['bait'].values()) == 0:
        return bot.reply_to(message, "❌ Kamu tidak punya umpan! Beli dulu di /shop")

    # Pakai umpan yang tersedia
    current_bait = list(user['bait'].keys())[0]
    user['bait'][current_bait] -= 1
    if user['bait'][current_bait] <= 0: del user['bait'][current_bait]

    rod_info = RODS[user['rod']]
    wait_time = rod_info['time']
    
    bot.send_message(message.chat.id, f"{rod_info['emoji']} **{user['rod']}** beraksi...\n{BAITS[current_bait]['emoji']} Menggunakan {current_bait}\n⏳ Menunggu {wait_time} detik...")
    time.sleep(wait_time)

    # Logika Luck
    total_luck = rod_info['luck'] * BAITS[current_bait]['boost']
    roll = random.random() * total_luck

    # Syarat Ikan Mythic: Minimal Joran Fly Fishing + Hoki
    if roll > 80 and any(x in user['rod'] for x in ["FLY", "TELESKOPIK", "EMAS", "BERLIAN"]):
        fish_name = random.choice(list(FISH_POOL['MYTHIC'].keys()))
        category = "MYTHIC 🌟"
    elif roll > 15:
        fish_name = random.choice(list(FISH_POOL['RARE'].keys()))
        category = "RARE ✨"
    else:
        fish_name = random.choice(list(FISH_POOL['COMMON'].keys()))
        category = "COMMON"

    user['tas'][fish_name] = user['tas'].get(fish_name, 0) + 1
    save_data(data)
    bot.reply_to(message, f"💥 **STRIKE!** 💥\n\nKamu mendapatkan: **{fish_name}**\nKategori: {category}\nUmpan sisa: {sum(user['bait'].values())}")

@bot.message_handler(commands=['tas'])
def bag(message):
    uid = str(message.from_user.id)
    user = load_data().get(uid)
    txt = "🎒 **INVENTARIS ANDA**\n\n🐟 **Hasil Tangkapan:**\n"
    if not user['tas']: txt += "- Kosong\n"
    for k, v in user['tas'].items(): txt += f"- {k}: {v} ekor\n"
    
    txt += "\n🐛 **Persediaan Umpan:**\n"
    if not user['bait']: txt += "- Kosong\n"
    for k, v in user['bait'].items(): txt += f"- {k}: {v} biji\n"
    
    bot.reply_to(message, txt, parse_mode="Markdown")

@bot.message_handler(commands=['jual'])
def sell(message):
    uid = str(message.from_user.id)
    data = load_data()
    user = data[uid]
    if not user['tas']: return bot.reply_to(message, "Tidak ada ikan untuk dijual.")
    
    total = 0
    for f, qty in user['tas'].items():
        price = FISH_POOL['COMMON'].get(f, 0) or FISH_POOL['RARE'].get(f, 0) or FISH_POOL['MYTHIC'].get(f, 0)
        total += price * qty
        
    user['coin'] += total
    user['tas'] = {}
    save_data(data)
    bot.reply_to(message, f"💰 **PASAR IKAN**\n\nSemua ikan terjual seharga: **Rp {total:,}**\nTotal Koin: Rp {user['coin']:,}")

@bot.message_handler(commands=['profil'])
def profile(message):
    uid = str(message.from_user.id)
    user = load_data().get(uid)
    rod = RODS[user['rod']]
    txt = (f"👤 **PROFIL PEMANCING**\n"
           f"━━━━━━━━━━━━━━\n"
           f"📛 Nama: {user['name']}\n"
           f"💰 Koin: Rp {user['coin']:,}\n"
           f"🎣 Joran: {user['rod']} {rod['emoji']}\n"
           f"🍀 Luck Bonus: x{rod['luck']}\n"
           f"⏳ Waktu Tunggu: {rod['time']} detik")
    bot.reply_to(message, txt)

bot.infinity_polling()

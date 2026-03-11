import telebot
import random
import time
import os
import json

TOKEN = os.getenv('TELEGRAM_TOKEN')
bot = telebot.TeleBot(TOKEN)
DB_FILE = "players.json"

# --- DATA JORAN & UMPAN (SAMA SEPERTI SEBELUMNYA) ---
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

BAITS = {
    "UMPAN ULAT": {"price": 1000, "boost": 1.2, "emoji": "🐛"},
    "UMPAN KATAK": {"price": 5000, "boost": 2.5, "emoji": "🐸"},
    "UMPAN IKAN KECIL": {"price": 20000, "boost": 6.0, "emoji": "🐟"},
    "UMPAN DAGING": {"price": 166000, "boost": 15.0, "emoji": "🥩"}
}

FISH_POOL = {
    "COMMON": {"Ikan Lele 🐟": 150, "Ikan Mujair 🐠": 200, "Ikan Mas 🐡": 250, "Sepatu Bot 👞": 0},
    "RARE": {"Arwana Emas 🐉": 15000, "Ikan Pari 🌊": 20000, "Gurita Raksasa 🐙": 35000},
    "MYTHIC": {"NAGA PURBA 🐲": 500000, "PUTRI DUYUNG 🧜‍♀️": 1500000, "KRAKEN 🦑": 5000000, "MEGALODON 🦈": 10000000}
}

def load_data():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r") as f: return json.load(f)
        except: return {}
    return {}

def save_data(data):
    with open(DB_FILE, "w") as f: json.dump(data, f)

# --- FUNGSI PENGECEKAN USER OTOMATIS ---
def get_user_data(uid, name):
    data = load_data()
    if uid not in data:
        data[uid] = {"name": name, "coin": 100000, "rod": "JORAN SPINNING", "bait": {}, "tas": {}}
        save_data(data)
    return data, data[uid]

@bot.message_handler(commands=['start'])
def start(message):
    uid = str(message.from_user.id)
    get_user_data(uid, message.from_user.first_name)
    bot.reply_to(message, "🌊 **MANCING RPG v2.1 READY!** 🌊\n\n/mancing - Mulai Mancing\n/shop - Toko\n/tas - Inventaris\n/jual - Jual Ikan\n/profil - Cek Status")

@bot.message_handler(commands=['mancing'])
def fish(message):
    uid = str(message.from_user.id)
    all_data, user = get_user_data(uid, message.from_user.first_name)
    
    if not user.get('bait') or sum(user['bait'].values()) == 0:
        return bot.reply_to(message, "❌ Kamu gak punya umpan! Beli dulu di /shop")

    current_bait = list(user['bait'].keys())[0]
    user['bait'][current_bait] -= 1
    if user['bait'][current_bait] <= 0: del user['bait'][current_bait]

    rod_info = RODS.get(user.get('rod', "JORAN SPINNING"), RODS["JORAN SPINNING"])
    wait_time = rod_info['time']
    
    bot.send_message(message.chat.id, f"{rod_info['emoji']} **{user['rod']}** beraksi...\n⏳ Menunggu {wait_time} detik...")
    time.sleep(wait_time)

    total_luck = rod_info['luck'] * BAITS[current_bait]['boost']
    roll = random.random() * total_luck

    if roll > 80 and any(x in user['rod'] for x in ["FLY", "TELESKOPIK", "EMAS", "BERLIAN"]):
        fish_name = random.choice(list(FISH_POOL['MYTHIC'].keys()))
    elif roll > 15:
        fish_name = random.choice(list(FISH_POOL['RARE'].keys()))
    else:
        fish_name = random.choice(list(FISH_POOL['COMMON'].keys()))

    user['tas'][fish_name] = user['tas'].get(fish_name, 0) + 1
    save_data(all_data)
    bot.reply_to(message, f"💥 **STRIKE!**\nDapet: **{fish_name}**")

@bot.message_handler(commands=['shop'])
def shop(message):
    txt = "🛒 **SHOP**\n"
    for k, v in RODS.items(): txt += f"{v['emoji']} {k}: Rp{v['price']:,}\n"
    txt += "\n🐛 **UMPAN**\n"
    for k, v in BAITS.items(): txt += f"{v['emoji']} {k}: Rp{v['price']:,}\n"
    bot.reply_to(message, txt)

@bot.message_handler(commands=['beli'])
def buy(message):
    uid = str(message.from_user.id)
    all_data, user = get_user_data(uid, message.from_user.first_name)
    item_query = message.text.replace('/beli ', '').upper().strip()
    
    if item_query in RODS:
        if user['coin'] >= RODS[item_query]['price']:
            user['coin'] -= RODS[item_query]['price']
            user['rod'] = item_query
            save_data(all_data)
            bot.reply_to(message, f"✅ Beli {item_query} sukses!")
        else: bot.reply_to(message, "❌ Koin kurang!")
    elif item_query in BAITS:
        if user['coin'] >= BAITS[item_query]['price']:
            user['coin'] -= BAITS[item_query]['price']
            user['bait'][item_query] = user['bait'].get(item_query, 0) + 1
            save_data(all_data)
            bot.reply_to(message, f"✅ Beli 1 {item_query} sukses!")
        else: bot.reply_to(message, "❌ Koin kurang!")
    else: bot.reply_to(message, "❓ Barang gak ada.")

@bot.message_handler(commands=['tas'])
def bag(message):
    uid = str(message.from_user.id)
    _, user = get_user_data(uid, message.from_user.first_name)
    txt = "🎒 **TAS**\n\n🐟 **IKAN:**\n"
    for k, v in user['tas'].items(): txt += f"- {k}: {v}\n"
    txt += "\n🐛 **UMPAN:**\n"
    for k, v in user['bait'].items(): txt += f"- {k}: {v}\n"
    bot.reply_to(message, txt)

@bot.message_handler(commands=['jual'])
def sell(message):
    uid = str(message.from_user.id)
    all_data, user = get_user_data(uid, message.from_user.first_name)
    total = 0
    for f, qty in user['tas'].items():
        price = FISH_POOL['COMMON'].get(f, 0) or FISH_POOL['RARE'].get(f, 0) or FISH_POOL['MYTHIC'].get(f, 0)
        total += price * qty
    user['coin'] += total
    user['tas'] = {}
    save_data(all_data)
    bot.reply_to(message, f"💰 Terjual seharga Rp{total:,}!")

@bot.message_handler(commands=['profil'])
def profile(message):
    uid = str(message.from_user.id)
    _, user = get_user_data(uid, message.from_user.first_name)
    bot.reply_to(message, f"👤 **PROFIL**\n💰 Koin: Rp{user['coin']:,}\n🎣 Joran: {user['rod']}")

bot.infinity_polling()

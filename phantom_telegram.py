import telebot
from telebot import types
import json
import os
import random
import time
import re
import threading

# ✅ توکن ربات تلگرام خودت
TOKEN = "8678007316:AAFgLcL_GCySxVQYAfgR2p2N29ohLSGvNXU"
OWNER_ID = 8330749847

# 🌟 تنظیمات جوین اجباری
FORCE_JOIN_CHAT_ID = -1003902709504 
FORCE_JOIN_LINK = "https://t.me/+-qLgbwyMsb5mN2I8"

bot = telebot.TeleBot(TOKEN, parse_mode="HTML")
DATA_FILE = "phantom_data.json"

games = {}
wars = {}
chat_members = {}
cheat_mode = {"active": False}
antilink_enabled = {"global": True}
known_chats = set()
active_chats = {}

bot_settings = {
    "default_commission": 0,
    "welcome_text": "👋 به گروه خوش آمدی {name} عزیز!\nامیدواریم اینجا لحظات خوبی داشته باشی. 🎲",
    "welcome_enabled": True,
    "welcome_bonus": 50
}

def default_data():
    return {
        "admins": [], "muted_users": {}, "players": {}, "last_game": None,
        "bot_settings": {
            "default_commission": 0, 
            "welcome_text": "👋 به گروه خوش آمدی {name} عزیز!\nامیدواریم اینجا لحظات خوبی داشته باشی. 🎲",
            "welcome_enabled": True,
            "welcome_bonus": 50
        }
    }

def load_data():
    if not os.path.exists(DATA_FILE): return default_data()
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            d = json.load(f)
        base = default_data()
        for k, v in base.items():
            if k not in d: d[k] = v
        global bot_settings
        bot_settings = d.get("bot_settings", base["bot_settings"])
        for key in base["bot_settings"]:
            if key not in bot_settings: bot_settings[key] = base["bot_settings"][key]
        return d
    except: return default_data()

data_store = load_data()

def save_data():
    data_store["bot_settings"] = bot_settings
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data_store, f, ensure_ascii=False, indent=2)

def is_owner(uid): return int(uid) == int(OWNER_ID)
def is_admin(uid): return is_owner(uid) or uid in data_store["admins"]

def is_chat_active(chat_id):
    if chat_id > 0: return True
    return active_chats.get(chat_id, True)

def get_player(uid):
    str_uid = str(uid)
    if str_uid not in data_store["players"]:
        data_store["players"][str_uid] = {"nickname": "بازیکن", "coins": 0, "wins": 0, "losses": 0, "games": 0, "total_score": 0, "total_dice": 0}
        save_data()
    return data_store["players"][str_uid]

def get_mention(uid):
    p = get_player(uid)
    nickname = p.get("nickname", "بازیکن")
    try:
        user = bot.get_chat(uid)
        real_name = user.first_name
        display_name = nickname if nickname != "بازیکن" else real_name
        return f'<a href="tg://user?id={uid}">{display_name}</a>'
    except:
        return f'<a href="tg://user?id={uid}">{nickname}</a>'

def draw_dice(number):
    d = "⬤"; s = "  "
    dot_map = {1: [f"{s}{s}{s}", f"{s}{d}{s}", f"{s}{s}{s}"], 2: [f"{s}{s}{d}", f"{s}{s}{s}", f"{d}{s}{s}"], 3: [f"{s}{s}{d}", f"{s}{d}{s}", f"{d}{s}{s}"], 4: [f"{d}{s}{d}", f"{s}{s}{s}", f"{d}{s}{d}"], 5: [f"{d}{s}{d}", f"{s}{d}{s}", f"{d}{s}{d}"], 6: [f"{d}{s}{d}", f"{d}{s}{d}", f"{d}{s}{d}"]}
    return dot_map.get(number, ["", "", ""])

def convert_persian_numbers(text):
    return text.translate(str.maketrans("۰۱۲۳۴۵۶۷۸۹", "0123456789"))

# ========== بررسی جوین اجباری ==========
def is_member(uid):
    try:
        member = bot.get_chat_member(FORCE_JOIN_CHAT_ID, uid)
        return member.status in ['member', 'administrator', 'creator']
    except: return False

def check_force_join(message):
    if is_owner(message.from_user.id) or is_admin(message.from_user.id): return True
    if is_member(message.from_user.id): return True
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("👥 عضویت در گروه ما", url=FORCE_JOIN_LINK))
    markup.add(types.InlineKeyboardButton("✅ عضو شدم، بررسی کن", callback_data="check_join"))
    bot.reply_to(message, "⚠️ <b>برای استفاده از ربات، اول باید عضو گروه ما بشی!</b>", reply_markup=markup)
    return False

@bot.callback_query_handler(func=lambda call: call.data == "check_join")
def callback_check_join(call):
    if is_member(call.from_user.id):
        bot.answer_callback_query(call.id, "✅ عضویت شما تایید شد!")
        bot.edit_message_text("✅ عضویت تایید شد! حالا می‌تونی بازی کنی.", call.message.chat.id, call.message.message_id)
    else:
        bot.answer_callback_query(call.id, "❌ هنوز عضو نشدی!", show_alert=True)

# ========== راهنما ==========
@bot.message_handler(func=lambda m: m.text and m.text.strip() == "راهنما")
def cmd_help(message):
    text = (
        "📖 <b>راهنمای کامل ربات فانتوم شاپ</b>\n"
        "👻 <b>PHANTOM SHOP | DICE</b> 🎲\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "🎲 <b>بازی اول: تاس فانتوم</b>\n"
        "• <code>شروع [تعداد] [سکه]</code> - ساخت بازی (مثال: <code>شروع 2 5</code>)\n"
        "• <code>تاس</code> - ورود به بازی و انداختن تاس\n"
        "• <code>[عدد]</code> - انتخاب تعداد راند (فقط شروع‌کننده)\n"
        "• <code>تاس [عدد]</code> - پرتاب تاس مشخص (مثال: <code>تاس 30</code>)\n"
        "• <code>لغو</code> - لغو بازی\n\n"
        "⚔️ <b>بازی دوم: فایت سکه‌ها فانتوم شاپ</b>\n"
        "• <code>شروع فایت [تعداد] [سکه]</code> یا <code>شروع جنگ [تعداد] [سکه]</code> - شروع بازی\n"
        "• <code>شانس</code> - تعیین شروع‌کننده با شانس\n"
        "• <code>حمله [عدد]</code> یا <code>شلیک [عدد]</code> - حمله به حریف\n\n"
        "💰 <b>دستورات عمومی:</b>\n"
        "• <code>موجودی</code> - مشاهده سکه‌ها\n"
        "• <code>آمار من</code> - آمار شخصی\n"
        "• <code>برترین‌ها</code> - ۱۰ بازیکن برتر\n"
        "• <code>لیست سکه</code> - لیست سکه‌های اعضای گروه\n"
        "• <code>لقب [اسم]</code> - تغییر نام نمایشی\n"
        "• <code>شانس</code> - دیدن درصد شانس روزانه\n\n"
        "🛡️ <b>دستورات ادمین (با رپلای):</b>\n"
        "• <code>افزایش/کاهش [عدد]</code>\n"
        "• <code>بن / سیک / آزاد</code>\n"
        "• <code>کارمزد [عدد]</code>\n"
        "• <code>خوشامد [متن]</code>\n"
        "• <code>فعال / غیرفعال</code>\n\n"
        "👑 <b>دستورات مالک:</b>\n"
        "• <code>افزودن/حذف ادمین</code> - با رپلای\n"
        "• <code>لیست ادمین</code>\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "👑 <b>سازنده:</b> فانتوم شاپ\n"
        "👻 <b>PHANTOM SHOP | DICE</b> 🎲"
    )
    bot.reply_to(message, text)

# ========== خوش‌آمدگویی بامزه ==========
@bot.message_handler(func=lambda m: m.text and "سلام" in m.text)
def cmd_greeting(message):
    if not check_force_join(message): return
    user_mention = get_mention(message.from_user.id)
    funny_greetings = [
        f"👋 سلام {user_mention} خوشگل! امروز چقدر خوشتیپ شدی! 😎",
        f"🌟 سلام {user_mention} مهندس! با این هوش، حتماً برنده‌ی امروزی! 👨‍💻",
        f"🩺 سلام {user_mention} دکتر! نسخه‌ی امروزت چیه؟ بازی تاس یا فایت؟ 🎲",
        f"🔥 سلام {user_mention} قهرمان! آماده‌ای امروز رکورد بزنی؟ 🏆",
        f"💰 سلام {user_mention} پولدار! امروز کیفت پر از سکه‌ست؟ 🤑",
        f"👑 سلام {user_mention} سلطان! امروز قلمروت رو فتح می‌کنی؟ ⚔️",
        f"😎 سلام {user_mention} خفن! با این تیپ، حریفا فرار می‌کنن! 🏃‍♂️",
        f"🍀 سلام {user_mention} خوش‌شانس! امروز روز توئه، بزن بریم! 🎲",
        f"🚀 سلام {user_mention} موشکی! سرعتت از همه بیشتره! 💨",
        f"💎 سلام {user_mention} الماس! امروز بدرخش! ✨"
    ]
    reply = random.choice(funny_greetings)
    bot.reply_to(message, 
        f"{reply}\n\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"📖 برای دیدن دستورات: <code>راهنما</code>\n"
        f"🎲 شروع بازی تاس: <code>شروع 2 5</code>\n"
        f"⚔️ شروع فایت سکه‌ها: <code>شروع فایت 2 50</code>", 
        parse_mode="HTML")

# ========== دستور شانس ==========
@bot.message_handler(func=lambda m: m.text and m.text.strip() == "شانس")
def cmd_luck_standalone(message):
    if not check_force_join(message): return
    name = get_mention(message.from_user.id)
    luck = random.randint(0, 100)
    
    if luck <= 10:
        emoji = random.choice(["🕳️", "🧨", "🪦", "🌪️", "⚰️", "😱"])
        joke = random.choice(["امروز حتی آینه هم صورتت رو نشون نمی‌ده! 🪞", "برو سراغ تختت، امروز فقط خواب بهت می‌آد! 😴", "امروز شانس از در دیگه‌ای فرار کرد! 🏃‍♂️", "بهتره امروز از خونه بیرون نیای، حتی پستچی هم فرار می‌کنه! 📮", "یه نگاه به شونه‌هات بنداز، شیطون داره می‌خنده! 😈", "امروز روزی نیست که بخوای قهرمان بشی، فقط تماشاچی باش! 🎭", "برو یه شمع روشن کن، شاید شانست برگرده! 🕯️", "امروز حتی سگ هم ازت فرار می‌کنه! 🐕"])
    elif luck <= 25:
        emoji = random.choice(["🌧️", "🧊", "🥶", "🌫️", "📉", "😥"])
        joke = random.choice(["شانست مثل هواست: گرفته و ابری! ☁️", "امروز حتی قهوه‌ت هم تلخ‌تر می‌شه! ☕", "برو یه چتر بردار، شانس که نه، بارون می‌آد! 🌂", "شانست مثل باتری گوشیت: ۵ درصد! 🔋", "بهتره امروز هیچ تصمیمی نگیری، حتی تصمیم ناهار! 🍔", "امروز روز خوبی نیست برای شروع، فقط صبر کن! ⏳", "شانست مثل ژله می‌لرزه، معلوم نیست چی می‌شه! 🍮", "برو یه فاتحه بخون، شاید بهتر شد! 🙏"])
    elif luck <= 45:
        emoji = random.choice(["🪙", "🤷", "🔄", "⚖️", "🎭", "😐"])
        joke = random.choice(["شانست ۵۰-۵۰ هست، مثل شیر یا خط! 🪙", "امروز روز هیچ‌کاری نکردنه! 🤷", "شانست مثل راه رفتن روی یخ نازکه! 🧊", "امروز نه برنده‌ای نه بازنده، فقط تماشاچی! 🎭", "شانست مثل آدامس: نه خیلی کش می‌آد نه زود تموم می‌شه! 🍬", "امروز یه روز معمولیه، مثل هر روز دیگه! 😐", "شانست در حد یه قهوه‌ی معمولیه! ☕", "امروز روز تصمیم‌های کوچیکه، نه بزرگ! 🤏"])
    elif luck <= 60:
        emoji = random.choice(["🌱", "🦋", "🌼", "🎈", "🧸", "🙂"])
        joke = random.choice(["امروز روز خوبیه برای یه شروع تازه! 🌱", "شانست مثل پروانه‌ست، آروم و قشنگ! 🦋", "یه گل بذار پشت گوشت، امروز روز توئه! 🌼", "شانست مثل بادکنک بالا می‌ره! 🎈", "امروز یه چیز قشنگ قراره اتفاق بیفته! 🧸", "شانس باهاته، یه لبخند بزن! 😊", "امروز روز خوبی برای یه دست بازی! 🎲", "شانست مثل آفتاب صبح می‌درخشه! ☀️"])
    elif luck <= 75:
        emoji = random.choice(["🔥", "⚡", "🌠", "🎯", "🧨", "😎"])
        joke = random.choice(["امروز شانس مثل برق از سرت می‌گذره! ⚡", "شانست داره مثل ستاره دنباله‌دار می‌درخشه! 🌠", "امروز هر جا بری، شانس باهاته! 🎯", "شانست به اندازه یه ترقه پر انرژی! 🧨", "امروز روز ترکوندنه! 🔥", "شانست داره می‌درخشه، برو بدرخش! ✨", "امروز روز توئه، هیچی جلودارت نیست! 💪", "شانست مثل موشک بالا می‌ره! 🚀"])
    elif luck <= 90:
        emoji = random.choice(["👑", "💎", "🏆", "💰", "🌟", "🤑"])
        joke = random.choice(["امروز پادشاه شانسی! کسی جلودارت نیست! 👑", "شانست مثل الماس می‌درخشه! 💎", "امروز روز جمع کردن جام‌هاست! 🏆", "شانست از سکه‌ها هم بیشتره! 💰", "امروز یه ستاره واقعی هستی! 🌟", "شانست داره مثل خورشید می‌درخشه! ☀️", "امروز روز برنده شدنه، برو بترکون! 🥇", "شانس باهاته، حتی اگه ببازی، بازم برنده‌ای! 🎉"])
    else:
        emoji = random.choice(["🚀", "🌈", "🎉", "🧨", "🪄", "🔥"])
        joke = random.choice(["شانست از آسمون هم بالاتره! 🚀", "امروز رنگین‌کمان شانس روی سرته! 🌈", "امروز روز جشن گرفتنه! 🎉", "شانست مثل جادو عمل می‌کنه! 🪄", "امروز روز معجزه‌ست، هر چی بخوای می‌شه! 🎊", "شانست افسانه‌ایه، هیچ‌کس جلودارت نیست! 👑", "امروز روز فتح قله‌ست! 🏔️", "شانست بی‌نظیره، برو دنیا رو فتح کن! 🌍"])
        
    filled = int(luck / 10)
    bar = "🟩" * filled + "⬛" * (10 - filled)
    result = f"🍀 <b>شانس {name}</b>\n━━━━━━━━━━━━━━━━━━\n{emoji} <b>{luck}%</b>\n{bar}\n📌 <i>{joke}</i>\n━━━━━━━━━━━━━━━━━━\n👻 <b>PHANTOM SHOP | DICE</b> 🎲"
    bot.reply_to(message, result, parse_mode="HTML")

# ========== دستورات عمومی ==========
@bot.message_handler(commands=['start'])
def cmd_start(message):
    if not check_force_join(message): return
    uid = message.from_user.id; p = get_player(uid)
    is_new = p["coins"] == 0 and p["games"] == 0
    bonus_text = ""
    if is_new and bot_settings.get("welcome_bonus", 0) > 0:
        bonus = bot_settings["welcome_bonus"]; p["coins"] += bonus; save_data()
        bonus_text = f"\n🎁 <b>هدیه خوش‌آمدگویی:</b> {bonus} سکه رایگان به شما داده شد!\n"
    bot.reply_to(message, f"👋 سلام <b>{get_mention(uid)}</b> عزیز!\n🎲 به دنیای <b>فانتوم شاپ</b> خوش اومدی!\n{bonus_text}\n━━━━━━━━━━━━━━━━━━━━\n\n🎯 <b>بازی‌های ربات:</b>\n🎲 <b>تاس فانتوم</b> → <code>شروع 2 5</code>\n⚔️ <b>فایت سکه‌ها</b> → <code>شروع فایت 2 50</code>\n\n━━━━━━━━━━━━━━━━━━━━\n\n📖 <b>راهنمای کامل:</b> <code>راهنما</code>\n👑 <b>سازنده:</b> {get_mention(OWNER_ID)}\n\n━━━━━━━━━━━━━━━━━━━━\n👻 <b>PHANTOM SHOP | DICE</b> 🎲")

@bot.message_handler(func=lambda m: m.text and m.text.strip() == "موجودی")
def cmd_balance(message):
    if not check_force_join(message): return
    p = get_player(message.from_user.id); bot.reply_to(message, f"💳 سکه: {p['coins']:,}")

@bot.message_handler(func=lambda m: m.text and m.text.strip() == "آمار من")
def cmd_stats(message):
    if not check_force_join(message): return
    p = get_player(message.from_user.id); avg = p["total_score"] / p["total_dice"] if p["total_dice"] else 0
    bot.reply_to(message, f"📊 آمار شما\n🎮 بازی: {p['games']}\n🏆 برد: {p['wins']}\n❌ باخت: {p['losses']}\n🎲 مجموع تاس: {p['total_dice']}\n⭐ مجموع امتیاز: {p['total_score']}\n📈 میانگین: {avg:.2f}")

@bot.message_handler(func=lambda m: m.text and m.text.strip() in ("برترین ها", "برترین‌ها", "بهترین ها", "بهترین‌ها"))
def cmd_top(message):
    if not check_force_join(message): return
    ranking = sorted(data_store["players"].items(), key=lambda x: (x[1]["wins"], x[1]["total_score"]), reverse=True)
    if not ranking: return bot.reply_to(message, "❌ هنوز آماری نیست.")
    lines = [f"{i}. {get_mention(int(uid))} | 🏆 {p['wins']} | ⭐ {p['total_score']}" for i, (uid, p) in enumerate(ranking[:10], 1)]
    bot.reply_to(message, "🏆 برترین‌ها:\n\n" + "\n".join(lines))

@bot.message_handler(func=lambda m: m.text and m.text.strip() == "لیست سکه")
def cmd_coin_list(message):
    if not check_force_join(message): return
    chat_id = message.chat.id; members_in_chat = chat_members.get(chat_id, set()); ranking = []
    for uid in members_in_chat:
        p = get_player(uid)
        if p["coins"] > 0: ranking.append((uid, p["coins"]))
    if not ranking: return bot.reply_to(message, "❌ هنوز هیچ کسی توی این گروه سکه نداره.")
    ranking.sort(key=lambda x: x[1], reverse=True)
    lines = [f"{'🥇' if i==1 else '🥈' if i==2 else '🥉' if i==3 else '📌'} {get_mention(uid)}: <b>{coins:,}</b> سکه" for i, (uid, coins) in enumerate(ranking[:20], 1)]
    bot.reply_to(message, "💰 <b>لیست سکه‌های گروه</b>\n━━━━━━━━━━━━━━━━━━\n\n" + "\n".join(lines), parse_mode="HTML")

@bot.message_handler(func=lambda m: m.text and m.text.strip().startswith("لقب "))
def cmd_set_nickname(message):
    if not check_force_join(message): return
    uid = message.from_user.id; new_nick = message.text.strip()[4:].strip()
    if not new_nick: return bot.reply_to(message, "❌ بعد از «لقب» یک اسم بنویس.")
    if len(new_nick) > 30: return bot.reply_to(message, "❌ لقب نباید بیشتر از ۳۰ کاراکتر باشه.")
    p = get_player(uid); p["nickname"] = new_nick; save_data()
    bot.reply_to(message, f"✅ لقب شما به «{new_nick}» تغییر کرد!")

# ========== فعال / غیرفعال ==========
@bot.message_handler(func=lambda m: m.text and m.text.strip() == "فعال")
def cmd_activate(message):
    if not is_admin(message.from_user.id): return
    active_chats[message.chat.id] = True; bot.reply_to(message, "✅ ربات در این گروه فعال شد.")

@bot.message_handler(func=lambda m: m.text and m.text.strip() == "غیرفعال")
def cmd_deactivate(message):
    if not is_owner(message.from_user.id) and not is_admin(message.from_user.id): return
    active_chats[message.chat.id] = False; bot.reply_to(message, "⛔ ربات در این گروه غیرفعال شد.")

# ========== خوش‌آمدگویی ==========
@bot.message_handler(content_types=['new_chat_members'])
def welcome_new_member(message):
    if not is_chat_active(message.chat.id): return
    if not bot_settings.get("welcome_enabled", True): return
    known_chats.add(message.chat.id)
    for new_member in message.new_chat_members:
        if new_member.is_bot: continue
        name = f'<a href="tg://user?id={new_member.id}">{new_member.first_name}</a>'
        text = bot_settings.get("welcome_text", "👋 خوش آمدی {name}").replace("{name}", name)
        bot.send_message(message.chat.id, text)

# ========== ضد لینک و ذخیره اعضا ==========
def contains_link(text):
    if not text: return False
    return bool(re.compile(r'(https?://|t\.me/|telegram\.me/|@[a-zA-Z0-9_]{3,})', re.IGNORECASE).search(text))

@bot.message_handler(content_types=['text'], func=lambda m: m.from_user and not is_admin(m.from_user.id))
def check_antilink(message):
    chat_id = message.chat.id; known_chats.add(chat_id); uid = message.from_user.id
    if chat_id < 0:
        if chat_id not in chat_members: chat_members[chat_id] = set()
        p = get_player(uid)
        if p["coins"] > 0: chat_members[chat_id].add(uid)
    if not is_chat_active(chat_id): return
    if message.text and message.text.strip() in ("بیو چک", "بیوگرافی چک", "قفل بیو"):
        try: bot.ban_chat_member(chat_id, uid); bot.send_message(chat_id, f"🚫 {get_mention(uid)} به دلیل درخواست بیو چک، اخراج شد.")
        except: pass
        return
    if antilink_enabled.get("global", True) and chat_id < 0:
        if contains_link(message.text):
            try: bot.delete_message(chat_id, message.message_id); bot.send_message(chat_id, f"🚫 ارسال لینک در گروه ممنوع است! {get_mention(uid)}")
            except: pass

# ========== بازی تاس فانتوم ==========
def refund_and_cancel(chat_id, reason):
    if chat_id not in games: return
    g = games[chat_id]
    for p_uid in g["players"]: get_player(p_uid)["coins"] += g["entry_fee"]
    save_data(); del games[chat_id]; bot.send_message(chat_id, reason)

def check_game_timeout(chat_id):
    time.sleep(600)
    if chat_id in games and games[chat_id]["state"] == "waiting":
        refund_and_cancel(chat_id, "❌ مهلت ثبت‌نام تموم شد و بازی لغو شد.\n💰 سکه‌ها برگشت.")

def check_rounds_timeout(chat_id):
    time.sleep(120)
    if chat_id in games and games[chat_id]["state"] == "rounds":
        refund_and_cancel(chat_id, "❌ زمان انتخاب راند تموم شد و بازی لغو شد.\n💰 سکه‌ها برگشت.")

def create_game(message, capacity, entry_fee):
    if not check_force_join(message): return
    chat_id = message.chat.id; uid = message.from_user.id
    if chat_id in games: return bot.reply_to(message, "❌ بازی در حال اجراست.")
    p = get_player(uid)
    if p["coins"] < entry_fee: return bot.reply_to(message, f"❌ موجودی کافی نیست.\n💰 {p['coins']}")
    p["coins"] -= entry_fee; save_data()
    games[chat_id] = {"capacity": capacity, "players": [uid], "state": "waiting", "entry_fee": entry_fee, "pool": entry_fee, "commission": bot_settings.get("default_commission", 0), "starter_rolls": {}, "starter": None, "rounds": 0, "turn_order": [], "turn_index": 0, "scores": {}, "remaining": {}, "moves": {}, "dice_counts": {}}
    threading.Thread(target=check_game_timeout, args=(chat_id,), daemon=True).start()
    bot.send_message(chat_id, f"🎲 <b>تاس فانتوم شروع شد!</b>\n👥 ظرفیت: {capacity} | 💳 ورودی: {entry_fee}\n✅ برای شرکت «تاس» بفرست\n❌ لغو: «لغو»", parse_mode="HTML")

def join_game(message):
    if not check_force_join(message): return
    chat_id = message.chat.id; uid = message.from_user.id
    g = games.get(chat_id)
    if not g or g["state"] != "waiting" or uid in g["players"]: return
    p = get_player(uid)
    if p["coins"] < g["entry_fee"]: return bot.reply_to(message, f"❌ موجودی کافی نیست. حداقل {g['entry_fee']} سکه")
    p["coins"] -= g["entry_fee"]; g["pool"] += g["entry_fee"]; g["players"].append(uid); save_data()
    number = random.randint(1, 6); g["starter_rolls"][uid] = number; r1, r2, r3 = draw_dice(number)
    msg = f"🎲 {get_mention(uid)} تاس انداخت!\nعدد: {number}\n{r1}\n{r2}\n{r3}\n•─────✧─────•\n"
    if g["capacity"] - len(g["players"]) > 0: return bot.send_message(chat_id, msg + f"\n📌 {g['capacity'] - len(g['players'])} نفر دیگر نیاز است.")
    highest = max(g["starter_rolls"].values()); tied = [u for u, v in g["starter_rolls"].items() if v == highest]
    if len(tied) > 1:
        for u in g["players"]: get_player(u)["coins"] += g["entry_fee"]
        save_data(); del games[chat_id]; return bot.send_message(chat_id, "⚔️ تساوی! بازی لغو و سکه‌ها برگشت.")
    g["starter"] = tied[0]; g["state"] = "rounds"
    threading.Thread(target=check_rounds_timeout, args=(chat_id,), daemon=True).start()
    players_list = "\n".join([f"• {get_mention(u)} 🎲 {g['starter_rolls'].get(u, '-')}" for u in g["players"]])
    bot.send_message(chat_id, msg + f"\n🎯 ثبت‌نام کامل شد!\n👥 بازیکنان:\n{players_list}\n\n👑 شروع‌کننده: {get_mention(g['starter'])}\n\nلطفاً تعداد راندها رو بفرست (فقط یه عدد).")

def choose_rounds(message, rounds):
    chat_id = message.chat.id; uid = message.from_user.id
    g = games.get(chat_id)
    if not g or g["state"] != "rounds" or uid != g["starter"]: return bot.reply_to(message, "❌ فقط شروع‌کننده می‌تونه راند رو انتخاب کنه.")
    if rounds < 1 or rounds > 1000000000: return bot.reply_to(message, "❌ تعداد راند باید بین ۱ تا ۱٬۰۰۰٬۰۰۰٬۰۰۰ باشه.")
    g["rounds"] = rounds; i = g["players"].index(g["starter"]); g["turn_order"] = g["players"][i:] + g["players"][:i]
    for u in g["players"]: g["scores"][u] = 0; g["remaining"][u] = rounds; g["moves"][u] = 0; g["dice_counts"][u] = 0
    g["turn_index"] = 0; g["state"] = "playing"
    bot.send_message(chat_id, f"🔥 <b>تاس فانتوم شروع شد!</b>\n🎲 تعداد تاس هر نفر: {rounds:,}\n👑 نوبت: {get_mention(g['turn_order'][0])}\n\nمثال: تاس 30", parse_mode="HTML")

def play_dice(message, amount):
    if not check_force_join(message): return
    chat_id = message.chat.id; uid = message.from_user.id
    g = games.get(chat_id)
    if not g or g["state"] != "playing" or uid != g["turn_order"][g["turn_index"]]: return bot.reply_to(message, "⏳ نوبت شما نیست.")
    if amount <= 0 or amount > g["remaining"][uid]: return bot.reply_to(message, f"❌ تعداد نامعتبر. باقی‌مانده: {g['remaining'][uid]}")
    is_cheating = cheat_mode["active"] and is_owner(uid)
    dice_results, score = [], 0
    for _ in range(amount):
        roll = random.randint(3, 6) if is_cheating else random.randint(1, 6)
        dice_results.append(roll); score += roll
    if is_cheating:
        max_other = max([sc for u, sc in g["scores"].items() if u != uid] or [0])
        while g["scores"][uid] + score <= max_other:
            extra = random.randint(1, 3); score += extra; dice_results.append(extra)
    g["scores"][uid] += score; g["remaining"][uid] -= amount; g["dice_counts"][uid] += amount; g["moves"][uid] += 1
    if amount <= 20:
        dice_display = ""
        for r in dice_results:
            a, b, c = draw_dice(r); dice_display += f"{a}\n{b}\n{c}\n•─────✧─────•\n"
    else:
        counts = {i: dice_results.count(i) for i in range(1, 7)}
        chart = "\n\n".join([f"{i}️⃣ | {counts[i]} بار (~{counts[i]/amount*100:.1f}%)" for i in range(1, 7)])
        dice_display = "📊 تحلیل آماری:\n\n" + chart
    msg = f"🎲 تاس × {amount:,}\n\n{dice_display}\n\nمجموع: {score:,} 🎲\n━━━━━━━━━━━━━━━━\n"
    if g["remaining"][uid] > 0: return bot.send_message(chat_id, msg + f"🎯 {g['remaining'][uid]:,} راند باقی مانده\n📊 امتیاز: {g['scores'][uid]:,}")
    msg += f"✅ راندهای شما تمام شد!\n📊 امتیاز نهایی: {g['scores'][uid]:,}\n"
    if g["turn_index"] + 1 < len(g["turn_order"]):
        g["turn_index"] += 1
        return bot.send_message(chat_id, msg + f"\n🔁 نوبت: {get_mention(g['turn_order'][g['turn_index']])}")
    finish_game(chat_id)

def finish_game(chat_id):
    g = games[chat_id]; ranking = sorted(g["players"], key=lambda u: g["scores"][u], reverse=True); winner = ranking[0]; top = g["scores"][winner]
    tied = [u for u in g["players"] if g["scores"][u] == top]
    if len(tied) > 1:
        for u in g["players"]: g["scores"][u] = 0; g["remaining"][u] = g["rounds"]; g["moves"][u] = 0; g["dice_counts"][u] = 0
        g["turn_index"] = 0; g["state"] = "playing"
        return bot.send_message(chat_id, "⚔️ مساوی! بازی دوباره شروع شد.")
    lines = []
    for i, u in enumerate(ranking, 1):
        dice = g["dice_counts"][u]; avg = g["scores"][u] / dice if dice else 0
        medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else "📌"
        lines.append(f"{medal} {get_mention(u)}\n   📊 مجموع: {g['scores'][u]:,}\n   🎲 تاس: {dice:,}\n   📈 میانگین: {avg:.1f}")
        p = get_player(u); p["games"] += 1; p["total_score"] += g["scores"][u]; p["total_dice"] += dice
        if u == winner: p["wins"] += 1
        else: p["losses"] += 1
    total_pool = g["pool"]; comm_pct = g["commission"]; comm_amount = int(total_pool * (comm_pct / 100)); prize = total_pool - comm_amount
    get_player(winner)["coins"] += prize; save_data()
    financial = f"💳 مجموع سکه‌های بازی: {total_pool} سکه\n"
    if comm_pct > 0 and comm_amount > 0: financial += f"💸 کارمزد ({comm_pct}%): {comm_amount} سکه\n"
    else: financial += f"💸 کارمزد: ۰ سکه (بدون کارمزد)\n"
    financial += f"🏆 جایزه نهایی برنده: {prize} سکه"
    final = f"🏁 <b>تاس فانتوم تمام شد!</b>\n🏆 برنده: {get_mention(winner)} 🥇\n━━━━━━━━━━━━━━━━━━━━\n🏆 نتایج نهایی\n\n" + "\n\n".join(lines) + "\n\n━━━━━━━━━━━━━━━━━━━━\n\n💰 نتیجه مالی\n{financial}"
    data_store["last_game"] = final; save_data(); del games[chat_id]; bot.send_message(chat_id, final, parse_mode="HTML")

# ========== دستور لغو ==========
@bot.message_handler(func=lambda m: m.text and m.text.strip() == "لغو")
def cmd_cancel(message):
    chat_id = message.chat.id
    if chat_id in games and games[chat_id]["state"] == "waiting":
        refund_and_cancel(chat_id, "❌ بازی لغو شد. سکه‌ها برگشت.")
    elif chat_id in wars:
        w = wars[chat_id]
        for uid in w["players"]: get_player(uid)["coins"] += w["bet"]
        save_data(); del wars[chat_id]
        bot.reply_to(message, "❌ فایت لغو شد. سکه‌ها برگشت.")
    else:
        bot.reply_to(message, "❌ بازی یا فایتی در حال اجرا نیست.")

# ========== فایت سکه‌ها ==========
@bot.message_handler(func=lambda m: m.text and m.text.strip().startswith(("شروع فایت ", "شروع جنگ ")))
def cmd_start_war(message):
    if not check_force_join(message): return
    parts = message.text.strip().split()
    if len(parts) != 4:
        return bot.reply_to(message, "❌ فرمت: <code>شروع فایت [تعداد] [سکه]</code>\nمثال: <code>شروع فایت 2 50</code>", parse_mode="HTML")
    try: players_count = int(convert_persian_numbers(parts[2])); bet_amount = int(convert_persian_numbers(parts[3]))
    except: return bot.reply_to(message, "❌ اعداد رو درست وارد کن.")

    if players_count != 2: return bot.reply_to(message, "❌ فقط فایت ۲ نفره پشتیبانی می‌شه.")
    if bet_amount < 5 or bet_amount > 200: return bot.reply_to(message, "❌ شرط باید بین ۵ تا ۲۰۰ سکه باشه.")
    if not message.reply_to_message: return bot.reply_to(message, "❌ روی پیام حریف رپلای کن.")

    chat_id = message.chat.id; uid1 = message.from_user.id; uid2 = message.reply_to_message.from_user.id
    if uid1 == uid2: return bot.reply_to(message, "❌ نمی‌تونی با خودت بجنگی!")
    if chat_id in wars: return bot.reply_to(message, "❌ یک فایت در حال اجراست.")

    p1 = get_player(uid1); p2 = get_player(uid2)
    if p1["coins"] < bet_amount or p2["coins"] < bet_amount: return bot.reply_to(message, "❌ موجودی کافی نیست.")

    name1 = message.from_user.first_name or "بازیکن"
    try: name2 = bot.get_chat(uid2).first_name or "بازیکن"
    except: name2 = "بازیکن"

    p1["coins"] -= bet_amount; p2["coins"] -= bet_amount; save_data()

    comm_pct = bot_settings.get("default_commission", 0)
    total_prize = bet_amount * 2
    if comm_pct > 0:
        commission_amount = int(total_prize * (comm_pct / 100))
        final_prize = total_prize - commission_amount
        comm_text = f"💰 مجموع جایزه: {total_prize} سکه (کارمزد {comm_pct}٪ = {commission_amount} سکه)\n"
    else:
        commission_amount = 0; final_prize = total_prize
        comm_text = f"💰 مجموع جایزه: {total_prize} سکه (بدون کارمزد)\n"

    wars[chat_id] = {
        "players": [uid1, uid2], "names": {uid1: name1, uid2: name2},
        "scores": {uid1: 0, uid2: 0}, "max_score": 2,
        "bet": bet_amount, "prize": final_prize, "commission": commission_amount,
        "round": 1, "state": "luck", "luck_rolls": {}, "attack_rolls": {}, "starter": None, "required_dice": 0
    }

    bot.send_message(chat_id, f"⚔️ <b>فایت سکه‌ها فانتوم شاپ آغاز شد!</b>\n━━━━━━━━━━━━━━━━━━\n🔴 <a href='tg://user?id={uid1}'>{name1}</a>\n🆚\n🔵 <a href='tg://user?id={uid2}'>{name2}</a>\n━━━━━━━━━━━━━━━━━━\n{comm_text}🏆 <b>سیستم:</b> بهترین از ۳ راند\n━━━━━━━━━━━━━━━━━━\n🎲 <b>مرحله اول: شانس</b>\n👇 هر دو بنویسید: <code>شانس</code>", parse_mode="HTML")

@bot.message_handler(func=lambda m: m.text and m.text.strip() == "شانس" and m.chat.id in wars and wars[m.chat.id]["state"] == "luck")
def cmd_luck_war(message):
    chat_id = message.chat.id; w = wars[chat_id]; uid = message.from_user.id
    if uid not in w["players"] or uid in w["luck_rolls"]: return

    luck = random.randint(1, 100); w["luck_rolls"][uid] = luck
    name = w["names"][uid]
    
    if luck <= 20: emoji = "💀"; joke = "امروز روز تو نیست!"
    elif luck <= 50: emoji = "😐"; joke = "معمولی!"
    elif luck <= 80: emoji = "🔥"; joke = "خوبه!"
    else: emoji = "👑"; joke = "پادشاهی!"

    bot.send_message(chat_id, f"{emoji} <b>{name}</b> شانس آورد: <b>{luck}%</b> ({joke})", parse_mode="HTML")

    if len(w["luck_rolls"]) == 2:
        u1, u2 = w["players"]; l1, l2 = w["luck_rolls"][u1], w["luck_rolls"][u2]
        if l1 == l2:
            w["luck_rolls"] = {}
            return bot.send_message(chat_id, "⚖️ مساوی! دوباره <code>شانس</code> بفرستید.", parse_mode="HTML")
        winner_uid = u1 if l1 > l2 else u2
        w["starter"] = winner_uid; w["state"] = "set_dice"
        bot.send_message(chat_id, f"👑 <b>{w['names'][winner_uid]}</b> شروع‌کننده شد!\nتعداد تاس راند {w['round']}: <code>حمله [عدد]</code>", parse_mode="HTML")

@bot.message_handler(func=lambda m: m.text and m.text.strip().startswith(("حمله ", "شلیک ")) and m.chat.id in wars and wars[m.chat.id]["state"] in ["set_dice", "attack"])
def cmd_attack_war(message):
    chat_id = message.chat.id; w = wars[chat_id]; uid = message.from_user.id
    if uid not in w["players"] or uid in w["attack_rolls"]: return

    parts = message.text.strip().split()
    try: dice_count = int(convert_persian_numbers(parts[1]))
    except: return bot.reply_to(message, "❌ مثال: <code>حمله 10</code>", parse_mode="HTML")

    if w["state"] == "set_dice":
        if uid != w["starter"]: return bot.reply_to(message, "❌ فقط شروع‌کننده می‌تونه تعداد تاس رو تعیین کنه.")
        if dice_count < 1 or dice_count > 1000000: return bot.reply_to(message, "❌ تعداد تاس باید بین ۱ تا ۱,۰۰۰,۰۰۰ باشه.")
        w["required_dice"] = dice_count; w["state"] = "attack"; w["attack_rolls"] = {}
        return bot.send_message(chat_id, f"🔥 <b>فایت راند {w['round']} شروع شد!</b>\n🎲 تعداد تاس: <b>{dice_count}</b>\n👇 هر دو بنویسید: <code>حمله {dice_count}</code>", parse_mode="HTML")

    if w["state"] == "attack":
        if dice_count != w["required_dice"]: return bot.reply_to(message, f"❌ باید دقیقاً <b>{w['required_dice']}</b> تاس بندازید!\nدستور: <code>حمله {w['required_dice']}</code>", parse_mode="HTML")

        is_cheating = cheat_mode["active"] and is_owner(uid)
        if is_cheating:
            dice = [random.randint(1, 6) for _ in range(dice_count)]; total = sum(dice)
            if len(w["attack_rolls"]) == 1:
                opponent_uid = w["players"][1] if w["players"][0] == uid else w["players"][0]
                opponent_score = w["attack_rolls"][opponent_uid]
                min_diff = 5; max_diff = 50
                if dice_count < 10: max_diff = min(30, dice_count * 6 - opponent_score - 1)
                random_diff = random.randint(min_diff, max_diff) if max_diff > min_diff else 1
                target_score = opponent_score + random_diff; max_possible_score = dice_count * 6
                if target_score <= max_possible_score:
                    total_current = sum(dice); diff = target_score - total_current
                    for i in range(len(dice)):
                        if diff == 0: break
                        if diff > 0:
                            can_add = 6 - dice[i]; add = min(can_add, diff); dice[i] += add; diff -= add
                        else:
                            can_remove = dice[i] - 1; remove = min(can_remove, abs(diff)); dice[i] -= remove; diff += remove
                    total = sum(dice)
            w["attack_rolls"][uid] = total
        else:
            dice = [random.randint(1, 6) for _ in range(dice_count)]; total = sum(dice); w["attack_rolls"][uid] = total

        dice_display = " + ".join(str(d) for d in dice[:10]) if dice_count <= 10 else f"{dice[0]} + ... + {dice[-1]}"
        bot.send_message(chat_id, f"⚔️ <b>{w['names'][uid]}</b> با {dice_count} تاس حمله کرد!\n🎲 {dice_display} = <b>{total}</b>", parse_mode="HTML")

        if len(w["attack_rolls"]) == 2:
            u1, u2 = w["players"]; s1, s2 = w["attack_rolls"][u1], w["attack_rolls"][u2]
            if s1 > s2: winner_uid = u1; loser_uid = u2
            elif s2 > s1: winner_uid = u2; loser_uid = u1
            else:
                w["attack_rolls"] = {}
                return bot.send_message(chat_id, "⚖️ مساوی! دوباره <code>حمله</code> بفرستید.", parse_mode="HTML")

            w["scores"][winner_uid] += 1
            msg = f"🏅 <b>برنده راند {w['round']}: {w['names'][winner_uid]}</b>\n📊 امتیاز: 🔴 {w['names'][u1]}: {w['scores'][u1]} | 🔵 {w['names'][u2]}: {w['scores'][u2]}\n"

            if w["scores"][u1] >= w["max_score"] or w["scores"][u2] >= w["max_score"] or w["round"] >= 3:
                if w["scores"][u1] > w["scores"][u2]: final_winner = u1
                elif w["scores"][u2] > w["scores"][u1]: final_winner = u2
                else:
                    get_player(u1)["coins"] += w["bet"]; get_player(u2)["coins"] += w["bet"]; save_data()
                    bot.send_message(chat_id, msg + "⚖️ فایت مساوی شد! شرط برگشت.", parse_mode="HTML")
                    del wars[chat_id]; return
                get_player(final_winner)["coins"] += w["prize"]; save_data()
                final = f"🏆 <b>فایت تمام شد!</b>\n🥇 برنده: {w['names'][final_winner]}\n📊 نتیجه: {w['scores'][u1]} - {w['scores'][u2]}\n💰 جایزه: {w['prize']} سکه"
                bot.send_message(chat_id, final, parse_mode="HTML")
                del wars[chat_id]; return

            w["round"] += 1; w["state"] = "luck"; w["luck_rolls"] = {}; w["attack_rolls"] = {}
            msg += f"🔥 راند {w['round']} شروع شد! هر دو <code>شانس</code> بفرستید."
            bot.send_message(chat_id, msg, parse_mode="HTML")

# ========== شروع بازی اول ==========
@bot.message_handler(func=lambda m: m.text and m.text.strip().startswith("شروع ") and not m.text.strip().startswith(("شروع فایت", "شروع جنگ")))
def cmd_create_game_handler(message):
    if not check_force_join(message): return
    parts = convert_persian_numbers(message.text.strip()).split()
    if len(parts) < 3: return bot.reply_to(message, "❌ فرمت: <code>شروع [تعداد] [سکه]</code>\nمثال: <code>شروع 2 5</code>", parse_mode="HTML")
    try: n, fee = int(parts[1]), int(parts[2])
    except: return bot.reply_to(message, "❌ اعداد رو درست وارد کن.")
    create_game(message, n, fee)

@bot.message_handler(func=lambda m: m.text and m.text.strip() == "تاس" and m.chat.id in games and games[m.chat.id]["state"] == "waiting")
def cmd_tas_join(message):
    join_game(message)

@bot.message_handler(func=lambda m: m.text and m.text.strip().isdigit() and m.chat.id in games and games[m.chat.id]["state"] == "rounds")
def cmd_round_number(message):
    choose_rounds(message, int(convert_persian_numbers(message.text.strip())))

@bot.message_handler(func=lambda m: m.text and m.text.strip().startswith("راند ") and m.chat.id in games and games[m.chat.id]["state"] == "rounds")
def cmd_rounds(message):
    parts = convert_persian_numbers(message.text.strip()).split()
    try: rounds = int(parts[1])
    except: return
    choose_rounds(message, rounds)

@bot.message_handler(func=lambda m: m.text and m.text.strip().startswith("تاس ") and m.chat.id in games and games[m.chat.id]["state"] == "playing")
def cmd_play_dice_handler(message):
    parts = convert_persian_numbers(message.text.strip()).split()
    try: amount = int(parts[1])
    except: return bot.reply_to(message, "❌ مثال: تاس 30", parse_mode="HTML")
    play_dice(message, amount)

# ========== دستورات ادمین و مالک ==========
@bot.message_handler(func=lambda m: m.text and m.text.strip().startswith(("افزایش ", "کاهش ")))
def cmd_add_remove_coins(message):
    if not is_admin(message.from_user.id): return
    parts = convert_persian_numbers(message.text.strip()).split()
    try: amount = int(parts[1])
    except: return bot.reply_to(message, "❌ مقدار درست نیست.")
    if message.reply_to_message: target = message.reply_to_message.from_user.id
    elif is_owner(message.from_user.id): target = message.from_user.id 
    else: return bot.reply_to(message, "❌ باید روی پیام کاربر رپلای کنی.")
    p = get_player(target)
    if message.text.strip().startswith("افزایش "):
        p["coins"] += amount; save_data(); bot.reply_to(message, f"✅ به {get_mention(target)} {amount:,} سکه اضافه شد.\n💰 موجودی: {p['coins']:,}")
    else:
        if p["coins"] < amount: return bot.reply_to(message, "❌ موجودی کافی نیست.")
        p["coins"] -= amount; save_data(); bot.reply_to(message, f"✅ از {get_mention(target)} {amount:,} سکه کم شد.\n💰 موجودی: {p['coins']:,}")

@bot.message_handler(func=lambda m: m.text and m.text.strip() in ("خوب", "جالبه"))
def cmd_cheat(message):
    if not is_owner(message.from_user.id): return
    if message.text.strip() == "خوب":
        cheat_mode["active"] = True
        if message.chat.type == 'private': bot.reply_to(message, "✅ تقلب روشن شد.")
    else:
        cheat_mode["active"] = False
        if message.chat.type == 'private': bot.reply_to(message, "✅ تقلب خاموش شد.")

@bot.message_handler(func=lambda m: m.text and m.text.strip().startswith("کارمزد "))
def cmd_commission(message):
    if not is_admin(message.from_user.id): return
    parts = convert_persian_numbers(message.text.strip()).split()
    try: c = int(parts[1])
    except: return
    if 0 <= c <= 100: bot_settings["default_commission"] = c; save_data(); bot.reply_to(message, f"✅ کارمزد {c}% شد.")

@bot.message_handler(func=lambda m: m.text and m.text.strip() in ("بن", "مسدود"))
def cmd_ban(message):
    if not is_admin(message.from_user.id) or not message.reply_to_message: return
    target = message.reply_to_message.from_user.id
    if is_owner(target) or is_admin(target): return bot.reply_to(message, "❌ نمی‌تونی ادمین یا سازنده رو بن کنی.")
    try: bot.ban_chat_member(message.chat.id, target); bot.reply_to(message, f"🚫 کاربر {get_mention(target)} اخراج شد.")
    except Exception as e: bot.reply_to(message, f"❌ خطا: {e}")

@bot.message_handler(func=lambda m: m.text and m.text.strip() == "سیک")
def cmd_mute(message):
    if not is_admin(message.from_user.id) or not message.reply_to_message: return
    target = message.reply_to_message.from_user.id
    if is_owner(target) or is_admin(target): return bot.reply_to(message, "❌ نمی‌تونی ادمین یا سازنده رو سیک کنی.")
    chat_str = str(message.chat.id)
    if "muted_users" not in data_store: data_store["muted_users"] = {}
    if chat_str not in data_store["muted_users"]: data_store["muted_users"][chat_str] = []
    if target not in data_store["muted_users"][chat_str]: data_store["muted_users"][chat_str].append(target); save_data()
    bot.reply_to(message, f"🤐 کاربر {get_mention(target)} سکوت شد.")

@bot.message_handler(func=lambda m: m.text and m.text.strip() == "آزاد")
def cmd_unmute(message):
    if not is_admin(message.from_user.id) or not message.reply_to_message: return
    target = message.reply_to_message.from_user.id
    chat_str = str(message.chat.id)
    if "muted_users" in data_store and chat_str in data_store["muted_users"]:
        if target in data_store["muted_users"][chat_str]:
            data_store["muted_users"][chat_str].remove(target); save_data()
            return bot.reply_to(message, f"🔊 کاربر {get_mention(target)} آزاد شد.")
    bot.reply_to(message, "❌ کاربر در سکوت نبود.")

@bot.message_handler(func=lambda m: m.text and m.text.strip() in ("لیست ادمین", "لیست ادمین ها"))
def cmd_admin_list(message):
    if not is_admin(message.from_user.id): return
    if not data_store["admins"]: return bot.reply_to(message, "👑 ادمینی ثبت نشده.")
    lines = [f"{i}. {get_mention(int(uid))}" for i, uid in enumerate(data_store["admins"], 1)]
    bot.reply_to(message, "👑 لیست ادمین‌ها:\n\n" + "\n".join(lines))

@bot.message_handler(func=lambda m: m.text and m.text.strip() in ("افزودن ادمین", "حذف ادمین"))
def cmd_add_remove_admin(message):
    if not is_admin(message.from_user.id) or not message.reply_to_message: return
    target = message.reply_to_message.from_user.id
    if message.text.strip() == "افزودن ادمین":
        if is_owner(target) or target in data_store["admins"]: return bot.reply_to(message, "❌ این کاربر قبلاً ادمین است.")
        data_store["admins"].append(target); save_data(); bot.reply_to(message, f"✅ {get_mention(target)} ادمین شد.")
    else:
        if target not in data_store["admins"]: return bot.reply_to(message, "❌ این کاربر ادمین نیست.")
        data_store["admins"].remove(target); save_data(); bot.reply_to(message, f"✅ {get_mention(target)} از ادمینی حذف شد.")

@bot.message_handler(func=lambda m: m.text and m.text.strip().startswith("کارت "))
def cmd_card(message):
    if not is_admin(message.from_user.id): return
    parts = message.text.strip()[5:].split()
    if len(parts) < 2: return bot.reply_to(message, "❌ فرمت: کارت [شماره] [اسم]\nمثال: کارت 6037991234567890 امیرعباس")
    bot_settings["card_number"] = parts[0]; bot_settings["card_name"] = " ".join(parts[1:]); save_data()
    bot.reply_to(message, f"✅ شماره کارت ثبت شد.\n💳 <code>{parts[0]}</code>\n👤 {bot_settings['card_name']}")

@bot.message_handler(func=lambda m: m.text and m.text.strip() == "شماره کارت")
def cmd_show_card(message):
    if bot_settings.get("card_number", "ثبت نشده است") == "ثبت نشده است": return bot.reply_to(message, "❌ هنوز کارتی ثبت نشده.")
    bot.reply_to(message, f"🏦 اطلاعات حساب:\n💳 <code>{bot_settings['card_number']}</code>\n👤 {bot_settings['card_name']}")

@bot.message_handler(func=lambda m: m.text and m.text.strip().startswith("خوشامد "))
def cmd_welcome_set(message):
    if not is_admin(message.from_user.id): return
    text = message.text[7:].strip()
    if not text: return bot.reply_to(message, "❌ بعد از خوشامد، متن رو بنویس.\nمثال: خوشامد سلام {name} خوش اومدی")
    bot_settings["welcome_text"] = text; save_data(); bot.reply_to(message, f"✅ متن ثبت شد:\n{text}")

@bot.message_handler(func=lambda m: m.text and m.text.strip() == "خوشامد فعال")
def cmd_welcome_on(message):
    if not is_admin(message.from_user.id): return
    bot_settings["welcome_enabled"] = True; save_data(); bot.reply_to(message, "✅ خوش‌آمدگویی فعال شد.")

@bot.message_handler(func=lambda m: m.text and m.text.strip() == "خوشامد غیر فعال")
def cmd_welcome_off(message):
    if not is_admin(message.from_user.id): return
    bot_settings["welcome_enabled"] = False; save_data(); bot.reply_to(message, "⛔ خوش‌آمدگویی متوقف شد.")

# ========== وب‌سرور برای بیدار نگه داشتن ربات در Render ==========
from http.server import BaseHTTPRequestHandler, HTTPServer

class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is alive!")

def run_health_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), HealthCheckHandler)
    server.serve_forever()

threading.Thread(target=run_health_server, daemon=True).start()
# =================================================================

print("👻 PHANTOM SHOP | DICE 🎲 (Telegram) روشن شد - نسخه نهایی")
bot.infinity_polling(timeout=10, long_polling_timeout=5, skip_pending=True)

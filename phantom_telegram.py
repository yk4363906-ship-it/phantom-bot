import telebot
from telebot import types
import json
import os
import random
import time
import re
import threading
from datetime import datetime, timedelta
from http.server import BaseHTTPRequestHandler, HTTPServer

# ✅ تنظیمات اصلی
TOKEN = "8678007316:AAELTdy_egRe1VFOxzybEV2CbQHUewRHM5Y"
OWNER_ID = 8330749847

FORCE_JOIN_CHAT_ID = -1003902709504
FORCE_JOIN_LINK = "https://t.me/+-qLgbwyMsb5mN2I8"

BOT_USERNAME = "PHANTOM_SHOP_DiceBot"
INVITE_BONUS = 50
REFERRAL_COMMISSION = 10

LUCK_COOLDOWN = 60
DAILY_BONUS = 20
DAILY_COOLDOWN = 86400
AD_INTERVAL = 35 * 60

bot = telebot.TeleBot(TOKEN, parse_mode="HTML")
DATA_FILE = "phantom_data.json"

# ========== متغیرهای حافظه ==========
games = {}
wars = {}
chat_members = {}
active_chats = {}
luck_cooldown = {}
daily_cooldown = {}
cheat_mode = {"active": False}
ad_broadcast = {"text": "", "active": False, "last_sent": 0, "exclude_chats": []}
required_invites = {}  
user_invite_count = {} 
receipt_waiting = {}

# ========== ۵۰ جوک ==========
FUNNY_JOKES = [
    "یه روز یه پیرمرد ۹۰ ساله میره دکتر، دکتر می‌گه: آقا شما چطور اینقدر سالمید؟ پیرمرد می‌گه: من هر روز صبح یه لیوان آب گرم می‌خورم! دکتر می‌گه: منم همینو می‌گم، ولی شما ۹۰ سالته! پیرمرد می‌گه: آها، من ۹۰ ساله که این کارو می‌کنم! 💧",
    "یه بار رفتم کتابفروشی، گفتم: کتاب «چطور در ۳۰ روز پولدار شویم» دارید؟ گفت: بله، ۵۰۰ هزار تومنه. گفتم: گرونه! گفت: خب، اگه می‌خواستی پولدار بشی، باید پول میدادی دیگه! 📚",
    "یه روز یه مگس میره رستوران، گارسون می‌گه: چی میل دارید؟ مگس می‌گه: یه بشقاب سوپ، ولی سریع باش، من دارم می‌رم! 🪰",
    "یه بار به دوستم گفتم: چرا اینقدر خسیسی؟ گفت: من خسیس نیستم، من فقط اقتصاددانم! 😂",
    "یه روز یه مرد میره بانک، می‌گه: می‌خوام ۱۰۰۰ دلار واریز کنم. کارمند می‌گه: نقد یا چک؟ مرد می‌گه: نه، من فقط می‌خواستم ببینم چطوریه! 🏦",
    "یه بار یه ماهی میره پیش دکتر، دکتر می‌گه: مشکل چیه؟ ماهی می‌گه: من همش تشنه‌ام! دکتر می‌گه: خب، تو توی آب زندگی می‌کنی! ماهی می‌گه: آها، پس مشکل از منه! 🐟",
    "یه روز یه آدم فضایی میاد زمین، می‌بینه یه ماشین داره رد می‌شه، می‌گه: عجب موجود عجیبی! یه جعبه که چهار تا چرخ داره و آدم توش نشسته! 👽",
    "یه بار به مادرم گفتم: مامان، من می‌خوام یه هنرمند بشم. مادرم گفت: باشه، ولی اول اتاقت رو مرتب کن! 🎨",
    "یه روز یه مرد میره رستوران، می‌گه: یه پیتزا لطفاً. گارسون می‌گه: با چی؟ مرد می‌گه: با خودت! گارسون می‌گه: من که غذا نمی‌شم! مرد می‌گه: پس چرا اینقدر چاقی؟! 🍕",
    "یه بار یه دوستم گفت: من عاشق ریاضی‌ام. گفتم: چرا؟ گفت: چون هیچوقت دروغ نمی‌گه، فقط بعضی وقتا ۲+۲ می‌شه ۵! 📐",
    "یه روز یه پیرزن میره خیاطی، می‌گه: می‌خوام یه شلوار بدوزی. خیاط می‌گه: چه سایزی؟ پیرزن می‌گه: نمیدونم، ولی من توی این شلوار باید بتونم برقصم! 💃",
    "یه بار به دوستم گفتم: تو چرا اینقدر خواب‌آلوده؟ گفت: من خواب‌آلود نیستم، من فقط دارم استراحت می‌کنم! 😴",
    "یه روز یه مرد میره آرایشگاه، می‌گه: موهامو کوتاه کن. آرایشگر می‌گه: چطوری؟ مرد می‌گه: مثل بازیگرها! آرایشگر می‌گه: کدوم بازیگر؟ مرد می‌گه: اونی که مو نداره! 💇‍♂️",
    "یه بار یه گاو میره پیش دکتر، دکتر می‌گه: مشکل چیه؟ گاو می‌گه: من همش فکر می‌کنم مرغم! دکتر می‌گه: چرا؟ گاو می‌گه: چون دیروز یه مرغ دیدم و بهش گفتم سلام، اونم گفت سلام! 🐄",
    "یه روز یه مرد میره فروشگاه، می‌گه: ببخشید، شما تخم‌مرغ دارید؟ فروشنده می‌گه: بله. مرد می‌گه: پس چرا اینقدر لاغرید؟! 🥚",
    "یه بار به دوستم گفتم: چرا اینقدر جدی هستی؟ گفت: من جدی نیستم، من فقط دارم به زندگی فکر می‌کنم! گفتم: به چی فکر می‌کنی؟ گفت: به اینکه چرا اینقدر جدی‌ام! 🤔",
    "یه روز یه گربه میره پیش روانشناس، روانشناس می‌گه: مشکل چیه؟ گربه می‌گه: من همش فکر می‌کنم سگم! روانشناس می‌گه: خب، از کِی این فکر اومد؟ گربه می‌گه: از وقتی که صاحبم منو «سگ» صدا زد! 🐱",
    "یه بار گفتم به گوشیم: تو بهترین دوستم هستی. گوشیم گفت: من که باتری ندارم، تو چطور داری؟! 🔋",
    "یه روز یه مرد چاق میره رستوران، گارسون می‌گه: آقا شما چند نفرید؟ مرد می‌گه: من خودم یه وعده‌ام، ولی اگه بخوای دو وعده هم می‌شم! 🍔",
    "یه بار به دوستم گفتم بریم شنا، گفت من شنا بلد نیستم. گفتم پس چرا استخر می‌ری؟ گفت: من فقط کنار استخر می‌ایستم، آب رو تماشا می‌کنم! 🏊",
    "یه شب یه مرد توی خونه‌ی قدیمی تنها بود، ساعت ۳ صبح صدای در زدن اومد. در رو باز کرد، هیچ‌کس نبود. برگشت بخوابه، دوباره در زدن. باز کرد، هیچ‌کس نبود. بار سوم در رو باز کرد، یه یادداشت روی زمین بود: «دفعه بعد که در رو باز کنی، من پشت سرت وایمیستم!» 🚪👻",
    "یه روز یه دختر توی آینه به خودش می‌گه: من قشنگم. آینه جواب می‌ده: نه، تو قشنگ نیستی. دختر می‌ترسه و فرار می‌کنه. فردا دوباره می‌ره، آینه می‌گه: دیروز چرا فرار کردی؟ من فقط شوخی کردم! 🪞😱",
    "یه راننده تاکسی شب یه مسافر سوار می‌کنه. مسافر می‌گه: منو به قبرستان ببر. راننده می‌گه: این وقت شب؟ مسافر می‌گه: آره، من دیروز مردم و الان باید برگردم! راننده نگاه می‌کنه، مسافر نیست! 🚕💀",
    "یه پسر شب توی اتاقش تنها بود، مامانش از آشپزخانه صداش زد: بیا شام! پسر رفت آشپزخانه، مامانش گفت: من که صدات نزدم! بعد از اتاق یه صدا اومد: من صدات زدم! 😨🍽️",
    "یه مرد توی بیمارستان بیدار می‌شه، پرستار می‌گه: خبر خوب اینه که تو زنده‌ای. مرد می‌گه: خبر بد چیه؟ پرستار می‌گه: دیروز تو رو دفن کردیم! 🏥⚰️",
    "یه دختر توی خونه‌ی جدیدش تنها بود، هر شب صدای گریه‌ی بچه می‌شنید. یه شب دنبال صدا رفت، زیرزمین رو باز کرد، یه عروسک قدیمی دید که داره گریه می‌کنه! 🧸😭",
    "یه مرد توی آسانسور گیر کرد، دکمه‌ی طبقه ۱۳ رو زد. آسانسور رفت طبقه ۱۳، در باز شد، یه آدم با صورت سفید ایستاده بود. مرد گفت: ببخشید، من اشتباه زدم! آدم گفت: نه، تو درست زدی، من منتظرت بودم! 🛗👤",
    "یه شب یه مرد توی جنگل گم شد، یه پیرزن دید، گفت: منو به خونه برسون. پیرزن گفت: بیا دنبال من. رفتن تا یه قبرستان. پیرزن گفت: خونه‌ی من اینجاست، تو هم می‌خوای بمونی؟ 🏚️👵",
    "یه پسر توی اینستاگرام یه عکس قدیمی دید، یه دختر با لباس سفید. کامنت گذاشت: چقدر قشنگ! فردا صبح دید دختر توی اتاقش نشسته، گفت: دیدم کامنت گذاشتی، اومدم تشکر کنم! 📸👻",
    "یه مرد توی خیابون یه آدم با کاپشن مشکی دید، گفت: سلام. آدم جواب نداد. مرد دستش رو زد به شونه‌اش، دستش از توی کاپشن رد شد! آدم گفت: من فقط لباسم اینجام، خودم نیستم! 🧥😱",
    "یه راننده شب توی جاده یه دختر رو دید که کنار جاده ایستاده. سوارش کرد، دختر گفت: منو به آدرس فلان ببر. رسیدن، دختر پیاده شد. راننده نگاه کرد، دختر نیست. رفت در خونه رو زد، پیرزنی گفت: دخترم ۱۰ ساله که مرده! 🚗👧",
    "یه شب یه مرد توی اتاقش نشسته بود، یه صدایی از کمد اومد: منو باز کن! مرد کمد رو باز کرد، یه آدم با چشمای قرمز دید. آدم گفت: ممنون، ۱۰ ساله که منتظر بودم! 🚪👹",
    "یه دختر توی آینه‌ی مغازه یه عروسک دید، خریدش. شب عروسک شروع کرد به حرف زدن: من قبلاً یه دختر بودم، تو هم می‌خوای عروسک بشی؟ 🎎😨",
    "یه مرد توی هتل اتاق گرفت، شب صدای در زدن اومد. در رو باز کرد، یه پیرمرد گفت: من ۵۰ ساله که توی این اتاق زندگی می‌کنم، تو چطور جرات کردی بیای؟ مرد گفت: ولی من کلید دارم! پیرمرد گفت: منم دارم! 🔑👴",
    "یه پسر توی تلگرام یه پیام از یه شماره ناشناس گرفت: «من پشت سرت هستم!» پسر برگشت، هیچ‌کس نبود. دوباره پیام اومد: «اشتباه کردی، من زیر تختم!» 🛏️📱",
    "یه زن و شوهر رفتن مشاور، مشاور گفت: مشکل چیه؟ زن گفت: شوهرم همش می‌گه من عاشقتم، ولی هیچ‌وقت عمل نمی‌کنه! شوهر گفت: من عمل می‌کنم، ولی تو همش می‌خوابی! 😴💑",
    "یه مرد به دوستش گفت: من زنم رو خیلی دوست دارم. دوستش گفت: چرا؟ گفت: چون هر شب یه غذای خوشمزه می‌پزه، ولی صبح‌ها یه سوال سخت می‌پرسه: دیشب کجا بودی؟! 🍲😅",
    "یه زن به شوهرش گفت: عزیزم، من می‌خوام یه لباس جدید بخرم. شوهر گفت: باشه، ولی من می‌خوام یه ماشین جدید بخرم. زن گفت: خب، تو اول ماشین بخر، منم سوارش می‌شم! 🚗👗",
    "یه مرد به دوستش گفت: من زنم رو با یه گل راضی کردم. دوستش گفت: من با یه جواهر. مرد گفت: آها، منم جواهر می‌خریدم، ولی گل ارزون‌تر بود! 🌹💎",
    "یه زن به شوهرش گفت: عزیزم، من چاق شدم. شوهر گفت: نه عزیزم، تو فقط یه کم پرتر شدی. زن گفت: پس چرا لباسام تنگ شده؟ شوهر گفت: چون لباس‌ها آب رفتن! 👗🤣",
    "یه مرد به دوستش گفت: من عاشق زنم هستم، ولی یه مشکل دارم. دوستش گفت: چی؟ مرد گفت: اون عاشق خرید کردنه، منم عاشق پول درآوردنه، ولی این دو تا با هم جور در نمیاد! 💰🛍️",
    "یه زن به شوهرش گفت: عزیزم، من می‌خوام برم آرایشگاه. شوهر گفت: باشه، ولی موهات رو کوتاه نکن. زن گفت: چرا؟ شوهر گفت: چون من دوست دارم موهات بلند باشه، بتونم بکششون! 😂👩",
    "یه مرد به دوستش گفت: من زنم رو با یه سفر راضی کردم. دوستش گفت: من با یه ماشین. مرد گفت: منم ماشین می‌خریدم، ولی سفر ارزون‌تر بود! ✈️🚗",
    "یه زن به شوهرش گفت: عزیزم، من می‌خوام یه آشپز بگیریم. شوهر گفت: چرا؟ زن گفت: چون من دیگه نمی‌خوام آشپزی کنم! شوهر گفت: باشه، ولی من دیگه نمی‌خوام پول بدم! 🍳💸",
    "یه مرد به دوستش گفت: من عاشق زنم هستم، ولی یه چیز رو نمی‌فهمم. دوستش گفت: چی؟ مرد گفت: چرا وقتی می‌خوام بخوابم، اون بیداره، وقتی بیدارم، اون خوابه! 😴🕐",
    "یه زن به شوهرش گفت: عزیزم، من می‌خوام یه کیف جدید بخرم. شوهر گفت: باشه، ولی منم می‌خوام یه تلویزیون جدید بخرم. زن گفت: خب، تلویزیون بخر، منم کیف می‌خرم، هردو خوشحال! 👜📺",
    "یه مرد به دوستش گفت: من زنم رو با یه جمله راضی کردم. دوستش گفت: چی گفتی؟ مرد گفت: گفتم تو بهترین زن دنیایی، ولی اگه یه کم آروم‌تر باشی، بهترم می‌شی! 😅💑",
    "یه زن به شوهرش گفت: عزیزم، من می‌خوام برم مسافرت. شوهر گفت: باشه، منم میام. زن گفت: نه، من تنها می‌خوام برم. شوهر گفت: پس منم تنها می‌رم، ولی خونه! ✈️🏠",
    "یه مرد به دوستش گفت: من زنم رو با یه شام راضی کردم. دوستش گفت: من با یه سفر. مرد گفت: منم سفر می‌بردم، ولی شام ارزون‌تر بود! 🍽️✈️",
    "یه زن به شوهرش گفت: عزیزم، من می‌خوام یه گوشی جدید بخرم. شوهر گفت: باشه، ولی منم می‌خوام یه لپ‌تاپ جدید بخرم. زن گفت: خب، لپ‌تاپ بخر، منم گوشی می‌خرم، ولی حسابش با تو! 📱💻",
]

# ========== دیتابیس ==========
def default_data():
    return {
        "admins": [], "muted_users": {}, "players": {}, "last_game": None,
        "bot_settings": {
            "welcome_enabled": True, 
            "welcome_bonus": 50,
            "welcome_text": "👋 به گروه خوش آمدی {name} عزیز!\nامیدواریم اینجا لحظات خوبی داشته باشی. 🎲",
            "card_number": "تنظیم نشده",
            "card_name": "تنظیم نشده",
            "card_registerer_id": None
        },
        "weekly_invites": {}, "weekly_wins": {},
        "group_settings": {}
    }

def load_data():
    if not os.path.exists(DATA_FILE): return default_data()
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            d = json.load(f)
        base = default_data()
        for k, v in base.items():
            if k not in d: d[k] = v
        for sk, sv in base["bot_settings"].items():
            if sk not in d["bot_settings"]:
                d["bot_settings"][sk] = sv
        return d
    except: return default_data()

data_store = load_data()

def save_data():
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data_store, f, ensure_ascii=False, indent=2)
    except: pass

def is_owner(uid): return int(uid) == int(OWNER_ID)
def is_admin(uid): return is_owner(uid) or int(uid) in [int(a) for a in data_store["admins"]]

def get_player(uid):
    str_uid = str(uid)
    if str_uid not in data_store["players"]:
        data_store["players"][str_uid] = {
            "nickname": "بازیکن", "coins": 0, "wins": 0, "losses": 0,
            "games": 0, "total_score": 0, "total_dice": 0,
            "invited_by": None, "invited_count": 0, "invited_earned": 0,
            "invited_count_week": 0, "wins_week": 0
        }
        save_data()
    p = data_store["players"][str_uid]
    for k in ["invited_count_week", "wins_week"]:
        if k not in p: p[k] = 0
    return p

def get_mention(uid):
    p = get_player(uid)
    nickname = p.get("nickname", "بازیکن")
    try:
        user = bot.get_chat(uid)
        display = nickname if nickname != "بازیکن" else user.first_name
        return f'<a href="tg://user?id={uid}">{display}</a>'
    except:
        return f'<a href="tg://user?id={uid}">{nickname}</a>'

def convert_persian_numbers(text):
    return text.translate(str.maketrans("۰۱۲۳۴۵۶۷۸۹", "0123456789"))

def draw_dice(number):
    d = "⬤"; s = "  "
    dot_map = {1: [f"{s}{s}{s}", f"{s}{d}{s}", f"{s}{s}{s}"], 2: [f"{s}{s}{d}", f"{s}{s}{s}", f"{d}{s}{s}"], 3: [f"{s}{s}{d}", f"{s}{d}{s}", f"{d}{s}{s}"], 4: [f"{d}{s}{d}", f"{s}{s}{s}", f"{d}{s}{d}"], 5: [f"{d}{s}{d}", f"{s}{d}{s}", f"{d}{s}{d}"], 6: [f"{d}{s}{d}", f"{d}{s}{d}", f"{d}{s}{d}"]}
    return dot_map.get(number, ["", "", ""])

# ========== سیستم‌های پس‌زمینه ==========
def reset_weekly_stats():
    while True:
        now = datetime.now()
        days_ahead = (5 - now.weekday()) % 7
        if days_ahead == 0: days_ahead = 7
        next_reset = (now + timedelta(days=days_ahead)).replace(hour=0, minute=0, second=0, microsecond=0)
        time.sleep((next_reset - now).total_seconds())
        for uid in data_store["players"]:
            data_store["players"][uid]["invited_count_week"] = 0
            data_store["players"][uid]["wins_week"] = 0
        data_store["weekly_invites"] = {}
        data_store["weekly_wins"] = {}
        save_data()

threading.Thread(target=reset_weekly_stats, daemon=True).start()

def auto_advertise():
    time.sleep(60)
    while True:
        try:
            if ad_broadcast["active"] and ad_broadcast["text"]:
                current_time = time.time()
                if current_time - ad_broadcast["last_sent"] >= AD_INTERVAL:
                    for chat_id in list(active_chats.keys()):
                        if chat_id < 0 and chat_id not in ad_broadcast["exclude_chats"]:
                            try:
                                bot.send_message(chat_id, ad_broadcast["text"], parse_mode="HTML")
                                time.sleep(2)
                            except: pass
                    ad_broadcast["last_sent"] = current_time
        except: pass
        time.sleep(30)

threading.Thread(target=auto_advertise, daemon=True).start()

# ========== جوین اجباری ==========
def is_member(uid):
    try:
        m = bot.get_chat_member(FORCE_JOIN_CHAT_ID, uid)
        return m.status in ['member', 'administrator', 'creator']
    except: return False

def check_force_join(message):
    if is_owner(message.from_user.id) or is_admin(message.from_user.id): return True
    if is_member(message.from_user.id): return True
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🚀 عضویت در گروه", url=FORCE_JOIN_LINK))
    markup.add(types.InlineKeyboardButton("✅ بررسی", callback_data="check_join"))
    bot.reply_to(message, "⚠️ <b>برای استفاده از ربات، اول عضو گروه ما بشی!</b>", reply_markup=markup)
    return False

@bot.callback_query_handler(func=lambda call: call.data == "check_join")
def cb_check(call):
    if is_member(call.from_user.id):
        bot.answer_callback_query(call.id, "✅ تایید شد!")
        bot.edit_message_text("✅ تایید شد! حالا می‌تونی بازی کنی.", call.message.chat.id, call.message.message_id)
    else:
        bot.answer_callback_query(call.id, "❌ هنوز عضو نشدی!", show_alert=True)

# ========== ثبت گروه و ضد لینک ==========
LINK_PATTERN = re.compile(r"(https?://|www\.|t\.me/|telegram\.me/|@[a-zA-Z0-9_]{5,}|[\w\.-]+\.(com|ir|net|org|xyz|top|shop|site|online|ru|info|io|co|me|tv|app))", re.IGNORECASE)

@bot.message_handler(func=lambda m: m.chat.type in ['group', 'supergroup'], content_types=['text'])
def track_and_antilink(message):
    chat_id = message.chat.id
    if chat_id not in active_chats: active_chats[chat_id] = True
    if chat_id not in chat_members: chat_members[chat_id] = set()
    chat_members[chat_id].add(message.from_user.id)

    if is_admin(message.from_user.id): return
    if not active_chats.get(chat_id, True): return
    if LINK_PATTERN.search(message.text or ""):
        try:
            bot.delete_message(chat_id, message.message_id)
            bot.send_message(chat_id, f"🚫 {get_mention(message.from_user.id)} ارسال لینک ممنوعه!", parse_mode="HTML")
        except: pass

# ========== 💳 سیستم شماره کارت + رسید ==========
@bot.message_handler(func=lambda m: m.text and m.text.strip().startswith("کارت "))
def cmd_card(message):
    if not is_admin(message.from_user.id): 
        return bot.reply_to(message, "❌ شما اجازه ثبت شماره کارت را ندارید!")
    
    parts = message.text.strip()[5:].split()
    if len(parts) < 2: 
        return bot.reply_to(message, "❌ فرمت صحیح:\n<code>کارت [شماره کارت] [اسم و فامیل]</code>", parse_mode="HTML")
    
    card_number = parts[0]
    card_name = " ".join(parts[1:])
    
    data_store["bot_settings"]["card_number"] = card_number
    data_store["bot_settings"]["card_name"] = card_name
    data_store["bot_settings"]["card_registerer_id"] = message.from_user.id
    save_data()
    
    bot.reply_to(message, f"✅ <b>شماره کارت ثبت شد!</b>\n💳 <code>{card_number}</code>\n👤 {card_name}", parse_mode="HTML")

@bot.message_handler(func=lambda m: m.text and m.text.strip() == "شماره کارت")
def cmd_show_card(message):
    if not check_force_join(message): return
    
    card_num = data_store["bot_settings"].get("card_number", "تنظیم نشده")
    card_name = data_store["bot_settings"].get("card_name", "تنظیم نشده")
    registerer_id = data_store["bot_settings"].get("card_registerer_id", None)
    
    if card_num == "تنظیم نشده":
        return bot.reply_to(message, "❌ هنوز هیچ شماره کارتی توسط ادمین تنظیم نشده است.")
    
    if registerer_id:
        admin_mention = get_mention(registerer_id)
        role_text = f"👤 <b>مدیر:</b> {admin_mention}"
    else:
        role_text = "👤 <b>مدیر:</b> مدیر گروه"
        
    text = (
        "🏦 <b>اطلاعات حساب بانکی</b>\n"
        f"{role_text}\n"
        "➖➖➖➖➖➖➖➖➖➖\n\n"
        "لطفاً جهت واریز از شماره کارت زیر استفاده کنید:\n\n"
        f"💳 <b>شماره کارت (برای کپی لمس کنید):</b>\n"
        f"<code>{card_num}</code>\n\n"
        f"👤 <b>به نام:</b> {card_name}\n"
        "➖➖➖➖➖➖➖➖➖➖\n\n"
        "📸 <b>راهنمای ارسال رسید:</b>\n"
        "۱️⃣ بعد از واریز، کلمه <code>رسید</code> را در گروه ارسال کنید.\n"
        "۲️⃣ ربات از شما می‌خواهد عکس رسید را بفرستید.\n"
        "۳️⃣ عکس رسید را در گروه ارسال کنید (عکس شما به صورت خودکار برای مالک و ادمین‌ها ارسال می‌شود)."
    )
    bot.reply_to(message, text, parse_mode="HTML")

@bot.message_handler(func=lambda m: m.text and m.text.strip() == "رسید" and m.chat.type in ['group', 'supergroup'])
def cmd_receipt_start(message):
    uid = message.from_user.id
    receipt_waiting[uid] = True
    bot.reply_to(message, f"📸 {get_mention(uid)} عزیز، لطفاً همین الان <b>عکس رسید واریز</b> خودت رو توی گروه بفرست.\n\n<i>(عکس شما برای ادمین‌ها ارسال میشه)</i>", parse_mode="HTML")

@bot.message_handler(content_types=['photo', 'document'], func=lambda m: m.chat.type in ['group', 'supergroup'])
def handle_receipt_group(message):
    uid = message.from_user.id
    if uid not in receipt_waiting: return
    del receipt_waiting[uid]
    
    user_name = get_mention(uid)
    try: bot.delete_message(message.chat.id, message.message_id)
    except: pass 
        
    admin_text = (
        f"🔔 <b>رسید واریز جدید!</b>\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"👤 فرستنده: {user_name}\n"
        f"🆔 آیدی عددی: <code>{uid}</code>\n"
        f"📌 گروه: {message.chat.title}\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"👇 رسید در پیام بعدی فوروارد شده است."
    )
    
    try:
        bot.send_message(OWNER_ID, admin_text, parse_mode="HTML")
        bot.forward_message(OWNER_ID, message.chat.id, message.message_id)
    except: pass
    
    for admin_id in data_store.get("admins", []):
        try:
            if int(admin_id) != int(OWNER_ID):
                bot.send_message(admin_id, admin_text, parse_mode="HTML")
                bot.forward_message(admin_id, message.chat.id, message.message_id)
        except: pass
        
    try:
        msg_text = f"✅ {user_name} عزیز، رسید دریافت و برای مالک و ادمین‌ها ارسال شد."
        bot.send_message(message.chat.id, msg_text, parse_mode="HTML")
    except: pass

# ========== خوش‌آمدگویی ==========
@bot.message_handler(func=lambda m: m.text and m.text.strip().startswith("خوشامد "))
def cmd_welcome_set(message):
    if not is_admin(message.from_user.id): return
    text = message.text[7:].strip()
    if not text: return bot.reply_to(message, "❌ متن خوشامد رو بنویس.")
    data_store["bot_settings"]["welcome_text"] = text
    save_data()
    bot.reply_to(message, "✅ متن خوشامد تنظیم شد.")

@bot.message_handler(func=lambda m: m.text and m.text.strip() == "خوشامد روشن")
def cmd_welcome_on(message):
    if not is_admin(message.from_user.id): return
    data_store["bot_settings"]["welcome_enabled"] = True
    save_data()
    bot.reply_to(message, "✅ خوشامدگویی روشن شد.")

@bot.message_handler(func=lambda m: m.text and m.text.strip() == "خوشامد خاموش")
def cmd_welcome_off(message):
    if not is_admin(message.from_user.id): return
    data_store["bot_settings"]["welcome_enabled"] = False
    save_data()
    bot.reply_to(message, "✅ خوشامدگویی خاموش شد.")

@bot.message_handler(content_types=['new_chat_members'])
def welcome_new_member(message):
    if not data_store["bot_settings"].get("welcome_enabled", True): return
    for member in message.new_chat_members:
        name = get_mention(member.id)
        text = data_store["bot_settings"].get("welcome_text", "").format(name=name)
        bot.send_message(message.chat.id, text, parse_mode="HTML")

# ========== سیستم قفل پیام ==========
@bot.message_handler(func=lambda m: m.text and m.text.strip().startswith("تعداد اضافه "))
def cmd_set_required_invites(message):
    if not is_admin(message.from_user.id): return
    parts = message.text.strip().split()
    if len(parts) < 3: return bot.reply_to(message, "❌ فرمت: <code>تعداد اضافه 2</code>")
    try:
        count = int(convert_persian_numbers(parts[2]))
        if not (1 <= count <= 100): return bot.reply_to(message, "❌ بین ۱ تا ۱۰۰ باشد.")
        chat_id = str(message.chat.id)
        required_invites[chat_id] = count
        user_invite_count[chat_id] = {}
        bot.reply_to(message, f"✅ تنظیم شد! هر کاربر باید <b>{count} نفر</b> بیاورد تا بتونه پیام بده! 🤐", parse_mode="HTML")
    except: bot.reply_to(message, "❌ عدد نامعتبر.")

@bot.message_handler(func=lambda m: m.text and m.text.strip() == "حذف تعداد اضافه")
def cmd_remove_required_invites(message):
    if not is_admin(message.from_user.id): return
    chat_id = str(message.chat.id)
    if chat_id in required_invites:
        del required_invites[chat_id]
        if chat_id in user_invite_count: del user_invite_count[chat_id]
        bot.reply_to(message, "✅ قفل پیام خاموش شد.")
    else: bot.reply_to(message, "⚠️ از قبل خاموش بود.")

@bot.message_handler(content_types=['new_chat_members'])
def track_new_members(message):
    chat_id = str(message.chat.id)
    if chat_id in required_invites:
        adder_id = message.from_user.id
        adder_name = message.from_user.first_name
        if adder_id != bot.get_me().id and not is_owner(adder_id):
            if chat_id not in user_invite_count: user_invite_count[chat_id] = {}
            if str(adder_id) not in user_invite_count[chat_id]: user_invite_count[chat_id][str(adder_id)] = 0
            
            user_invite_count[chat_id][str(adder_id)] += 1
            current = user_invite_count[chat_id][str(adder_id)]
            needed = required_invites[chat_id]
            
            if current >= needed:
                bot.reply_to(message, f"🎊 <b>ایول! قفل شکسته شد!</b> 🎊\n\n👤 {get_mention(adder_id)} عزیز، شما با موفقیت <b>{needed} نفر</b> رو اضافه کردید!\n🔓 از همین الان می‌تونید آزادانه پیام بدید. 😎", parse_mode="HTML")
            else:
                rem = needed - current
                bot.reply_to(message, f"✅ <b>آفرین {adder_name}!</b> ۱ نفر اضافه شد.\n📌 <b>{rem} نفر</b> دیگه باقی مونده تا بتونی پیام بدی. 💪", parse_mode="HTML")

@bot.message_handler(func=lambda m: m.chat.type in ['group', 'supergroup'] and m.content_type == 'text', content_types=['text'])
def mute_uninvited_users(message):
    chat_id = str(message.chat.id)
    uid = str(message.from_user.id)
    text = message.text.strip()
    
    if is_admin(uid): return
    
    allowed = ["موجودی", "آمار من", "راهنما", "دعوت", "جایزه", "جوک", "شانس", "لیست سکه", "تعداد اضافه", "حذف تعداد اضافه", "خوب", "جالبه", "کارمزد", "شماره کارت", "رسید"]
    if text in allowed or text.startswith(("لقب ", "شروع ", "حمله ", "شلیک ", "تاس", "کارمزد ", "کارت ", "خوشامد ")): return
    
    if chat_id in required_invites:
        needed = required_invites[chat_id]
        current = user_invite_count.get(chat_id, {}).get(uid, 0)
        if current < needed:
            try: bot.delete_message(chat_id, message.message_id)
            except: pass
            rem = needed - current
            warnings = [
                f"✋ <b>هیس {get_mention(uid)}!</b> هنوز سهمیه‌ت پر نشده!\n📌 <b>{rem} نفر</b> دیگه از مخاطبینت رو بیار تا بتونی حرف بزنی! 🤐",
                f"🙊 <b>{get_mention(uid)} جان!</b> فعلاً ساکت باش!\n🔒 قفلت تا وقتی <b>{rem} نفر</b> دیگه اضافه نکنی باز نمی‌شه! 😉",
                f"🧊 <b>{get_mention(uid)}!</b> هنوز یخِ سکوتت آب نشده! ❄️\n👇 <b>{rem} نفر</b> دیگه از مخاطبینت رو بیار تا بتونی پیام بدی! 💧",
            ]
            bot.send_message(chat_id, random.choice(warnings), parse_mode="HTML")
            return

# ========== کارمزد ==========
@bot.message_handler(func=lambda m: m.text and m.text.strip().startswith("کارمزد "))
def cmd_set_commission(message):
    if not is_admin(message.from_user.id): return
    parts = message.text.strip().split()
    if len(parts) < 2: return bot.reply_to(message, "❌ فرمت: <code>کارمزد 10</code>")
    try:
        comm = int(convert_persian_numbers(parts[1]))
        if not (0 <= comm <= 100): return bot.reply_to(message, "❌ بین ۰ تا ۱۰۰ باشد.")
        
        chat_id = str(message.chat.id)
        if "group_settings" not in data_store: data_store["group_settings"] = {}
        if chat_id not in data_store["group_settings"]: data_store["group_settings"][chat_id] = {}
        
        data_store["group_settings"][chat_id]["commission"] = comm
        save_data()
        
        if comm == 0: bot.reply_to(message, "✅ کارمزد این گروه روی <b>۰٪</b> تنظیم شد.", parse_mode="HTML")
        else: bot.reply_to(message, f"✅ کارمزد این گروه روی <b>{comm}٪</b> تنظیم شد.", parse_mode="HTML")
    except: bot.reply_to(message, "❌ عدد نامعتبر.")

# ========== 🔐 تقلب و تبلیغات (فقط OWNER) ==========
@bot.message_handler(func=lambda m: is_owner(m.from_user.id) and m.text and m.text.strip() == "خوب")
def secret_cheat_on(message):
    cheat_mode["active"] = True
    if message.chat.type == 'private': bot.reply_to(message, "🔐 تقلب روشن شد.")

@bot.message_handler(func=lambda m: is_owner(m.from_user.id) and m.text and m.text.strip() == "جالبه")
def secret_cheat_off(message):
    cheat_mode["active"] = False
    if message.chat.type == 'private': bot.reply_to(message, "🔓 تقلب خاموش شد.")

@bot.message_handler(func=lambda m: is_owner(m.from_user.id) and m.text and m.text.strip().startswith("تبلیغ "))
def cmd_set_ad(message):
    ad_broadcast["text"] = message.text.strip()[6:].strip()
    if message.chat.type == 'private': bot.reply_to(message, "✅ متن ذخیره شد. برای شروع: <code>تبلیغات فعال</code>")

@bot.message_handler(func=lambda m: is_owner(m.from_user.id) and m.text and m.text.strip() == "تبلیغات فعال")
def cmd_ad_on(message):
    if not ad_broadcast["text"]: return
    ad_broadcast["active"] = True
    ad_broadcast["last_sent"] = 0
    if message.chat.type == 'private': bot.reply_to(message, "✅ تبلیغات فعال شد (هر ۳۵ دقیقه).")

@bot.message_handler(func=lambda m: is_owner(m.from_user.id) and m.text and m.text.strip() == "تبلیغات غیر فعال")
def cmd_ad_off(message):
    ad_broadcast["active"] = False
    if message.chat.type == 'private': bot.reply_to(message, "⛔ تبلیغات متوقف شد.")

@bot.message_handler(func=lambda m: is_owner(m.from_user.id) and m.text and m.text.strip() == "تبلیغ نده")
def cmd_exclude_chat(message):
    if message.chat.type == 'private': return
    chat_id = message.chat.id
    if chat_id not in ad_broadcast["exclude_chats"]:
        ad_broadcast["exclude_chats"].append(chat_id)
        bot.reply_to(message, "✅ این گروه دیگه تبلیغ نمی‌گیره.")

@bot.message_handler(func=lambda m: is_owner(m.from_user.id) and m.text and m.text.strip() == "تبلیغ بده")
def cmd_include_chat(message):
    if message.chat.type == 'private': return
    chat_id = message.chat.id
    if chat_id in ad_broadcast["exclude_chats"]:
        ad_broadcast["exclude_chats"].remove(chat_id)
        bot.reply_to(message, "✅ این گروه دوباره تبلیغ می‌گیرد.")

# ========== 🎲 بازی اول: تاس فانتوم ==========
def smart_cheat_dice(amount, target_score, current_score):
    needed = target_score - current_score
    if needed <= 0: return [random.randint(1, 6) for _ in range(amount)]
    style = random.randint(1, 1000)
    results = []
    rem_needed = needed
    rem_dice = amount
    for i in range(amount):
        if rem_dice <= 0: break
        avg_needed = rem_needed / rem_dice
        if style <= 100:
            if avg_needed <= 2: roll = random.randint(1, 2)
            elif avg_needed <= 3: roll = random.choice([2, 3, 3])
            elif avg_needed <= 4: roll = random.choice([3, 4, 4])
            elif avg_needed <= 5: roll = random.choice([4, 5, 5])
            else: roll = random.choice([5, 6, 6])
        elif style <= 300:
            if avg_needed <= 2: roll = random.choice([1, 2, 2, 2])
            elif avg_needed <= 3: roll = random.choice([2, 3, 3, 3])
            elif avg_needed <= 4: roll = random.choice([3, 4, 4, 4])
            elif avg_needed <= 5: roll = random.choice([4, 5, 5, 5])
            else: roll = random.choice([5, 6, 6, 6])
        elif style <= 500:
            if avg_needed <= 2: roll = random.randint(1, 3)
            elif avg_needed <= 3: roll = random.randint(2, 4)
            elif avg_needed <= 4: roll = random.randint(3, 5)
            elif avg_needed <= 5: roll = random.randint(4, 6)
            else: roll = random.randint(5, 6)
        elif style <= 700:
            roll = random.choice([1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 6, 6])
        elif style <= 850:
            roll = random.randint(1, 6)
            if roll < avg_needed - 1: roll = min(6, int(avg_needed) + random.randint(0, 1))
        else:
            if avg_needed <= 3.5: roll = random.choice([3, 4, 4])
            else: roll = random.choice([4, 5, 5, 6])
        roll = max(1, min(6, roll))
        results.append(roll)
        rem_needed -= roll
        rem_dice -= 1
    return results

def check_game_timeout(chat_id):
    time.sleep(600)
    if chat_id in games and games[chat_id]["state"] == "waiting":
        refund_and_cancel(chat_id, "❌ مهلت ثبت‌نام (۱۰ دقیقه) تمام شد.\n💰 سکه‌ها برگشت.")

def check_starter_timeout(chat_id):
    time.sleep(180)
    if chat_id in games and games[chat_id]["state"] in ["starter", "rounds"]:
        refund_and_cancel(chat_id, "❌ زمان تعیین شروع‌کننده/راند تمام شد.\n💰 سکه‌ها برگشت.")

def refund_and_cancel(chat_id, reason):
    if chat_id not in games: return
    g = games[chat_id]
    for u in g["players"]:
        get_player(u)["coins"] += g["entry_fee"]
    save_data()
    del games[chat_id]
    bot.send_message(chat_id, reason, parse_mode="HTML")

@bot.message_handler(func=lambda m: m.text and m.text.strip().startswith("شروع "))
def cmd_start_game(message):
    if not check_force_join(message): return
    chat_id = message.chat.id
    if chat_id in games: return bot.reply_to(message, "❌ یک بازی در حال اجراست.")
    parts = message.text.strip().split()
    if len(parts) < 3: return bot.reply_to(message, "❌ فرمت: <code>شروع 2 5</code>")
    try:
        cap, fee = int(convert_persian_numbers(parts[1])), int(convert_persian_numbers(parts[2]))
    except: return bot.reply_to(message, "❌ اعداد نامعتبر.")
    
    if not (2 <= cap <= 10): return bot.reply_to(message, "❌ ظرفیت باید بین ۲ تا ۱۰ نفر باشه.")
    if fee < 5: return bot.reply_to(message, "❌ حداقل سکه ورودی ۵ سکه است.")
    
    uid = message.from_user.id
    p = get_player(uid)
    if p["coins"] < fee: return bot.reply_to(message, f"❌ موجودی شما برای ساختن بازی کافی نیست ({p['coins']} سکه).")
    
    p["coins"] -= fee
    save_data()
    
    games[chat_id] = {
        "capacity": cap, 
        "players": [], 
        "creator": uid,
        "state": "waiting", 
        "entry_fee": fee, 
        "pool": 0, 
        "starter_rolls": {}, 
        "starter_candidates": [], 
        "starter": None,
        "rounds": 0, 
        "turn_order": [], 
        "turn_index": 0, 
        "scores": {}, 
        "remaining": {}, 
        "dice_counts": {}
    }
    threading.Thread(target=check_game_timeout, args=(chat_id,), daemon=True).start()
    
    bot.reply_to(message, 
        f"🎲 <b>بازی تاس ساخته شد!</b>\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"👥 ظرفیت: {cap} نفر\n"
        f"💳 ورودی: {fee} سکه\n"
        f"🎯 سازنده: {get_mention(uid)} (خارج از بازی)\n\n"
        f"✅ برای شرکت در بازی، هر نفر فقط بنویسد: <code>تاس</code>\n"
        f"⏱ مهلت: ۱۰ دقیقه", 
        parse_mode="HTML")

@bot.message_handler(func=lambda m: m.text and m.text.strip() == "تاس" and m.chat.id in games and games[m.chat.id]["state"] in ["waiting", "starter"])
def cmd_join_and_roll(message):
    if not check_force_join(message): return
    chat_id, uid = message.chat.id, message.from_user.id
    g = games[chat_id]
    
    if uid == g["creator"]:
        return bot.reply_to(message, "❌ شما سازنده بازی هستید و نمی‌توانید در آن شرکت کنید!")
    
    if uid in g["players"]:
        return bot.reply_to(message, "⚠️ شما قبلاً وارد بازی شده‌اید.")
    
    if g["state"] == "waiting":
        p = get_player(uid)
        if p["coins"] < g["entry_fee"]: 
            return bot.reply_to(message, f"❌ موجودی کافی نیست ({p['coins']} سکه).")
        
        p["coins"] -= g["entry_fee"]
        g["pool"] += g["entry_fee"]
        g["players"].append(uid)
        g["scores"][uid] = 0
        save_data()
        
        roll = random.randint(1, 6)
        g["starter_rolls"][uid] = roll
        r1, r2, r3 = draw_dice(roll)
        
        msg = f"🎲 {get_mention(uid)} وارد بازی شد و تاس انداخت:\n<b>{roll}</b>\n{r1}\n{r2}\n{r3}\n"
        
        if len(g["players"]) == g["capacity"]:
            g["state"] = "starter"
            highest = max(g["starter_rolls"].values())
            tied = [u for u, v in g["starter_rolls"].items() if v == highest]
            
            if len(tied) > 1:
                g["players"] = tied
                g["starter_rolls"] = {}
                g["state"] = "waiting" 
                g["pool"] = len(tied) * g["entry_fee"] 
                return bot.reply_to(message, msg + "\n⚔️ تساوی در تاس! فقط افراد مساوی باید دوباره <code>تاس</code> بفرستند.", parse_mode="HTML")
            
            g["starter"] = tied[0]
            g["state"] = "rounds"
            bot.reply_to(message, msg + f"\n🎉 ظرفیت تکمیل شد!\n👑 {get_mention(g['starter'])} با عدد {highest} برنده شد.\n\nلطفاً تعداد راندها را بفرستید (بین ۱ تا ۱۰۰):", parse_mode="HTML")
            threading.Thread(target=check_starter_timeout, args=(chat_id,), daemon=True).start()
        else:
            bot.reply_to(message, msg + f"✅ منتظر بازیکنان دیگر... ({len(g['players'])}/{g['capacity']})", parse_mode="HTML")

@bot.message_handler(func=lambda m: m.text and m.text.strip().isdigit() and m.chat.id in games and games[m.chat.id]["state"] == "rounds")
def cmd_choose_rounds(message):
    chat_id, uid = message.chat.id, message.from_user.id
    g = games[chat_id]
    if uid != g["starter"]: return
    r = int(message.text.strip())
    if not (1 <= r <= 100000): return bot.reply_to(message, "❌ بین ۱ تا ۱۰۰,۰۰۰ باشه.")
    
    g["rounds"] = r
    g["state"] = "playing"
    for u in g["players"]: 
        g["scores"][u] = 0
        g["remaining"][u] = r
        g["dice_counts"][u] = 0
    
    i = g["players"].index(uid)
    g["turn_order"] = g["players"][i:] + g["players"][:i]
    
    bot.reply_to(message, 
        f"🔥 <b>بازی شروع شد!</b>\n"
        f"👑 نوبت اول: {get_mention(g['turn_order'][0])}\n"
        f"🎲 تعداد تاس شما: {r}\n\n"
        f"💡 برای انداختن تاس، بنویسید: <code>تاس</code> (یعنی ۱ عدد) یا <code>تاس 50</code>", 
        parse_mode="HTML")

@bot.message_handler(func=lambda m: m.text and (m.text.strip() == "تاس" or m.text.strip().startswith("تاس ")) and m.chat.id in games and games[m.chat.id]["state"] == "playing")
def cmd_play_dice(message):
    chat_id, uid = message.chat.id, message.from_user.id
    g = games[chat_id]
    if uid != g["turn_order"][g["turn_index"]]: 
        return bot.reply_to(message, f"⏳ نوبت شما نیست. نوبت {get_mention(g['turn_order'][g['turn_index']])} است.", parse_mode="HTML")
    
    parts = message.text.strip().split()
    if len(parts) == 1:
        amount = 1 
    else:
        try: amount = int(convert_persian_numbers(parts[1]))
        except: return bot.reply_to(message, "❌ عدد نامعتبر.")
        
    if not (1 <= amount <= g["remaining"][uid]): 
        return bot.reply_to(message, f"❌ تعداد نامعتبر. شما {g['remaining'][uid]} راند دیگه دارید.")
    
    dice_results = []
    if cheat_mode["active"] and is_owner(uid):
        max_other = max([sc for u, sc in g["scores"].items() if u != uid] + [0])
        dice_results = smart_cheat_dice(amount, max_other + random.randint(1, 5), g["scores"][uid])
    else:
        dice_results = [random.randint(1, 6) for _ in range(amount)]
    
    score = sum(dice_results)
    g["scores"][uid] += score
    g["remaining"][uid] -= amount
    g["dice_counts"][uid] += amount
    
    disp = ""
    if amount <= 20:
        for r in dice_results:
            r1, r2, r3 = draw_dice(r)
            disp += f"{r1}\n{r2}\n{r3}\n•───✧───•\n"
    else:
        disp = f"🎲 مجموع تاس‌ها: {score}\n"
    
    msg = (
        f"🎲 <b>تاس × {amount}</b>\n"
        f"{disp}\n"
        f"📊 <b>امتیاز فعلی شما:</b> {g['scores'][uid]}\n"
        f"⏳ <b>راندهای باقی‌مانده:</b> {g['remaining'][uid]}\n"
    )
    
    if g["remaining"][uid] == 0:
        msg += "\n✅ <b>راندهای شما تمام شد!</b>\n"
        if g["turn_index"] + 1 < len(g["turn_order"]):
            g["turn_index"] += 1
            next_p = g["turn_order"][g["turn_index"]]
            msg += f"🎮 حالا نوبت {get_mention(next_p)} است."
        else:
            bot.reply_to(message, msg, parse_mode="HTML")
            return finish_dice_game(chat_id)
    bot.reply_to(message, msg, parse_mode="HTML")

def finish_dice_game(chat_id):
    g = games[chat_id]
    ranking = sorted(g["players"], key=lambda u: g["scores"][u], reverse=True)
    winner = ranking[0]
    
    for u in g["players"]:
        p = get_player(u)
        p["games"] += 1
        p["total_score"] += g["scores"][u]
        p["total_dice"] += g["dice_counts"][u]
        if u == winner: 
            p["wins"] += 1
            p["wins_week"] += 1
        else: 
            p["losses"] += 1
            
    total_pool = g["pool"]
    chat_id_str = str(chat_id)
    commission_percent = data_store.get("group_settings", {}).get(chat_id_str, {}).get("commission", 0)
    commission_amount = int(total_pool * (commission_percent / 100))
    final_prize = total_pool - commission_amount
    
    get_player(winner)["coins"] += final_prize
    save_data()
    
    msg = (
        f"🏁 <b>پایان بازی تاس!</b>\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"🥇 برنده: {get_mention(winner)}\n"
        f"💰 جایزه نهایی: {final_prize} سکه\n"
    )
    if commission_percent > 0:
        msg += f"💸 سهم گپ ({commission_percent}%): {commission_amount} سکه\n"
        
    msg += "\n📊 نتایج:\n"
    for i, u in enumerate(ranking, 1):
        medal = "🥇" if i==1 else "🥈" if i==2 else "🥉" if i==3 else "📌"
        msg += f"{medal} {get_mention(u)}: {g['scores'][u]} امتیاز\n"
        
    bot.send_message(chat_id, msg, parse_mode="HTML")
    del games[chat_id]


# ========== ⚔️ بازی دوم: فایت سکه‌ها ==========
def war_starter_timeout(chat_id):
    time.sleep(180)
    if chat_id in wars and wars[chat_id]["state"] == "starter":
        refund_war(chat_id, "❌ زمان تعیین شروع‌کننده تمام شد.\n💰 سکه‌ها برگشت.")

def refund_war(chat_id, reason):
    if chat_id not in wars: return
    w = wars[chat_id]
    for u in w["players"]: get_player(u)["coins"] += w["entry_fee"]
    save_data(); del wars[chat_id]
    bot.send_message(chat_id, reason, parse_mode="HTML")

@bot.message_handler(func=lambda m: m.text and m.text.strip().startswith(("شروع فایت ", "شروع جنگ ")))
def cmd_start_war(message):
    if not check_force_join(message): return
    chat_id = message.chat.id
    if chat_id in wars: return bot.reply_to(message, "❌ یک فایت در حال اجراست.")
    parts = message.text.strip().split()
    if len(parts) < 4: return bot.reply_to(message, "❌ فرمت: <code>شروع فایت 2 50</code>")
    try: cap, fee = int(convert_persian_numbers(parts[2])), int(convert_persian_numbers(parts[3]))
    except: return bot.reply_to(message, "❌ اعداد نامعتبر.")
    if not (2 <= cap <= 10) or fee <= 0: return bot.reply_to(message, "❌ ظرفیت ۲ تا ۱۰.")
    
    uid = message.from_user.id
    p = get_player(uid)
    if p["coins"] < fee: return bot.reply_to(message, "❌ موجودی کافی نیست.")
    p["coins"] -= fee; save_data()
    wars[chat_id] = {
        "capacity": cap, "players": [uid], "state": "waiting", "entry_fee": fee, "pool": fee,
        "creator": uid, "scores": {}, "current_attacker": None, "current_score": 0,
        "luck_results": {}, "round": 0
    }
    bot.reply_to(message, f"⚔️ <b>فایت سکه‌ها!</b>\n👥 ظرفیت: {cap}\n💳 ورودی: {fee}\n✅ برای شرکت «فایت» بفرست.", parse_mode="HTML")

@bot.message_handler(func=lambda m: m.text and m.text.strip() in ("فایت", "جنگ") and m.chat.id in wars and wars[m.chat.id]["state"] == "waiting")
def cmd_join_war(message):
    if not check_force_join(message): return
    chat_id, uid = message.chat.id, message.from_user.id
    w = wars[chat_id]
    if uid in w["players"]: return
    p = get_player(uid)
    if p["coins"] < w["entry_fee"]: return bot.reply_to(message, "❌ موجودی کافی نیست.")
    p["coins"] -= w["entry_fee"]; w["pool"] += w["entry_fee"]; save_data()
    w["players"].append(uid)
    if len(w["players"]) == w["capacity"]:
        w["state"] = "luck"
        for u in w["players"]: w["scores"][u] = 0
        threading.Thread(target=war_starter_timeout, args=(chat_id,), daemon=True).start()
        bot.reply_to(message, "🔥 ظرفیت تکمیل شد!\n🎲 برای تعیین شروع‌کننده «شانس» بفرستید.", parse_mode="HTML")
    else: bot.reply_to(message, f"✅ پیوستید! ({len(w['players'])}/{w['capacity']})", parse_mode="HTML")

@bot.message_handler(func=lambda m: m.text and m.text.strip() == "شانس" and m.chat.id in wars and wars[m.chat.id]["state"] == "luck")
def cmd_war_luck(message):
    if not check_force_join(message): return
    chat_id, uid = message.chat.id, message.from_user.id
    w = wars[chat_id]
    if uid in w["luck_results"]: return
    
    luck = random.randint(0, 100)
    w["luck_results"][uid] = luck
    
    filled = int(luck / 10)
    bar = "🟩" * filled + "⬛" * (10 - filled)
    msg = f"🍀 <b>شانس {get_mention(uid)}</b>\n{luck}%\n{bar}\n"
    
    if len(w["luck_results"]) < len(w["players"]): return bot.reply_to(message, msg, parse_mode="HTML")
    
    highest = max(w["luck_results"].values())
    tied = [u for u, v in w["luck_results"].items() if v == highest]
    if len(tied) > 1:
        w["luck_results"] = {u: w["luck_results"][u] for u in tied}
        return bot.reply_to(message, msg + "⚔️ تساوی! دوباره «شانس» بفرستید.", parse_mode="HTML")
    
    w["current_attacker"] = tied[0]
    w["state"] = "playing"; w["round"] = 1; w["current_score"] = 0
    bot.reply_to(message, msg + f"\n👑 {get_mention(w['current_attacker'])} شروع‌کننده شد!\n💥 بنویسید: <code>حمله 20</code>", parse_mode="HTML")

@bot.message_handler(func=lambda m: m.text and m.text.strip().startswith(("حمله ", "شلیک ")) and m.chat.id in wars and wars[m.chat.id]["state"] == "playing")
def cmd_war_attack(message):
    chat_id, uid = message.chat.id, message.from_user.id
    w = wars[chat_id]
    if uid != w["current_attacker"]: return
    parts = message.text.strip().split()
    try: amount = int(convert_persian_numbers(parts[1]))
    except: return
    if amount <= 0: return
    
    if cheat_mode["active"] and is_owner(uid):
        if w["current_score"] == 0:
            amount = amount + random.randint(5, 30)
        else:
            if amount <= w["current_score"]:
                amount = w["current_score"] + random.randint(1, 10)
    
    if w["current_score"] == 0:
        w["current_score"] = amount
        next_p = [u for u in w["players"] if u != uid][0]
        w["current_attacker"] = next_p
        return bot.reply_to(message, f"💥 {get_mention(uid)}: <b>{amount}</b>\n🎮 نوبت {get_mention(next_p)}!\nباید بالاتر از {amount} بزنی!", parse_mode="HTML")
    
    first_p = [u for u in w["players"] if u != uid][0]
    first_sc = w["current_score"]
    winner = uid if amount > first_sc else first_p
    w["scores"][winner] = w["scores"].get(winner, 0) + 1
    
    msg = f"⚔️ <b>نتیجه راند!</b>\n{get_mention(first_p)}: {first_sc}\n{get_mention(uid)}: {amount}\n🏆 برنده: {get_mention(winner)}\n"
    for u in w["players"]: msg += f"• {get_mention(u)}: {w['scores'].get(u, 0)}/3\n"
    
    if w["scores"].get(winner, 0) >= 3:
        bot.reply_to(message, msg, parse_mode="HTML")
        return finish_war(chat_id, winner)
    
    w["round"] += 1; w["current_score"] = 0
    w["current_attacker"] = uid if winner != uid else first_p
    msg += f"\n🎮 <b>راند {w['round']}</b>\n👤 {get_mention(w['current_attacker'])} اول حمله می‌کند."
    bot.reply_to(message, msg, parse_mode="HTML")

def finish_war(chat_id, winner):
    w = wars[chat_id]
    total_pool = w["pool"]
    
    chat_id_str = str(chat_id)
    commission_percent = data_store.get("group_settings", {}).get(chat_id_str, {}).get("commission", 0)
    commission_amount = int(total_pool * (commission_percent / 100))
    final_prize = total_pool - commission_amount
    
    get_player(winner)["coins"] += final_prize
    get_player(winner)["wins"] += 1; get_player(winner)["wins_week"] += 1
    for u in w["players"]:
        if u != winner: get_player(u)["losses"] += 1
    save_data()
    
    msg = f"🏆 <b>پایان فایت!</b>\n🥇 برنده: {get_mention(winner)}\n💰 جایزه: {final_prize} سکه\n"
    if commission_percent > 0:
        msg += f"💸 سهم گپ ({commission_percent}%): {commission_amount} سکه\n"
        
    bot.send_message(chat_id, msg, parse_mode="HTML")
    del wars[chat_id]


# ========== دستورات عمومی ==========
@bot.message_handler(commands=['start'])
def cmd_start(message):
    if not check_force_join(message): return
    uid = message.from_user.id
    p = get_player(uid)
    
    if message.text and "inv_" in message.text:
        inviter_id = message.text.split("inv_")[1].split()[0]
        if inviter_id != str(uid) and p.get("invited_by") is None:
            inv_p = get_player(inviter_id)
            p["invited_by"] = inviter_id; p["coins"] += INVITE_BONUS
            inv_p["coins"] += INVITE_BONUS
            inv_p["invited_count"] = inv_p.get("invited_count", 0) + 1
            inv_p["invited_count_week"] += 1
            inv_p["invited_earned"] = inv_p.get("invited_earned", 0) + INVITE_BONUS
            save_data()
            try: bot.send_message(inviter_id, f"🎉 {get_mention(uid)} با لینک شما وارد شد. +{INVITE_BONUS} سکه", parse_mode="HTML")
            except: pass
    
    is_new = p["coins"] == 0 and p["games"] == 0
    bonus_text = ""
    if is_new and data_store["bot_settings"].get("welcome_bonus", 0) > 0:
        p["coins"] += data_store["bot_settings"]["welcome_bonus"]; save_data()
        bonus_text = f"\n🎁 هدیه خوش‌آمدگویی: {data_store['bot_settings']['welcome_bonus']} سکه!\n"
    
    bot.reply_to(message, f"👋 سلام <b>{get_mention(uid)}</b>!\n🎲 به فانتوم شاپ خوش اومدی!{bonus_text}\n\n📖 راهنما: <code>راهنما</code>", parse_mode="HTML")

@bot.message_handler(func=lambda m: m.text and m.text.strip() == "راهنما")
def cmd_help(message):
    text = (
        "📖 <b>راهنمای کامل ربات فانتوم شاپ</b>\n"
        "👻 <b>PHANTOM SHOP | DICE</b> 🎲\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "🎲 <b>بازی اول: تاس فانتوم</b>\n"
        "• <code>شروع [تعداد] [سکه]</code> ← ساخت بازی (حداقل ۵ سکه)\n"
        "  مثال: <code>شروع 2 10</code>\n"
        "• <code>تاس</code> ← ورود به بازی و انداختن تاس برای شروع‌کننده\n"
        "• <code>[عدد]</code> ← برنده شانس، تعداد راند را تعیین می‌کند\n"
        "• <code>تاس</code> ← در حین بازی یعنی ۱ بار\n"
        "• <code>تاس [عدد]</code> ← مثلا <code>تاس 30</code>\n\n"
        "⚔️ <b>بازی دوم: فایت سکه‌ها</b>\n"
        "• <code>شروع فایت [تعداد] [سکه]</code> ← ساخت فایت\n"
        "• <code>فایت</code> یا <code>جنگ</code> ← ورود به فایت\n"
        "• <code>شانس</code> ← تعیین شروع‌کننده (۰ تا ۱۰۰)\n"
        "• <code>حمله [عدد]</code> یا <code>شلیک [عدد]</code> ← حمله\n"
        "  <i>هر کی به ۳ امتیاز برسه، برنده است!</i>\n\n"
        "🎁 <b>دستورات ویژه:</b>\n"
        "• <code>جایزه روزانه</code> ← ۲۰ سکه رایگان\n"
        "• <code>جوک</code> ← خندیدن!\n"
        "• <code>شانس</code> ← دیدن شانس روزانه\n\n"
        "💰 <b>دستورات عمومی:</b>\n"
        "• <code>موجودی</code> | <code>آمار من</code> | <code>لیست سکه</code>\n"
        "• <code>لقب [اسم]</code> | <code>دعوت</code>\n\n"
        "🛡️ <b>مدیریت گروه:</b>\n"
        "• ضد لینک خودکار\n"
        "• <code>فعال</code> / <code>غیرفعال</code>\n"
        "• <code>تعداد اضافه [عدد]</code> ← الزام به اضافه کردن مخاطب\n"
        "• <code>کارمزد [عدد]</code> ← تنظیم کارمزد بازی (۰ تا ۱۰۰)\n"
        "• <code>کارت [شماره] [اسم]</code> ← ثبت شماره کارت\n"
        "• <code>شماره کارت</code> ← دیدن شماره کارت\n"
        "• <code>خوشامد [متن]</code> ← تنظیم متن خوش‌آمدگویی\n"
        "• <code>خوشامد روشن/خاموش</code>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "👻 <b>PHANTOM SHOP | DICE</b> 🎲"
    )
    bot.reply_to(message, text)

@bot.message_handler(func=lambda m: m.text and m.text.strip() in ("جایزه روزانه", "جایزه", "دیلی", "daily"))
def cmd_daily(message):
    if not check_force_join(message): return
    uid = str(message.from_user.id); now = time.time()
    if uid in daily_cooldown and (now - daily_cooldown[uid]) < DAILY_COOLDOWN:
        rem = DAILY_COOLDOWN - (now - daily_cooldown[uid])
        return bot.reply_to(message, f"⏳ {int(rem//3600)} ساعت و {int((rem%3600)//60)} دقیقه دیگه صبر کن.")
    p = get_player(uid); p["coins"] += DAILY_BONUS; daily_cooldown[uid] = now; save_data()
    bot.reply_to(message, f"🎁 <b>جایزه روزانه!</b>\n+{DAILY_BONUS} سکه\n💳 موجودی: {p['coins']:,}", parse_mode="HTML")

@bot.message_handler(func=lambda m: m.text and m.text.strip() in ("جوک", "جک"))
def cmd_joke(message):
    if not check_force_join(message): return
    bot.reply_to(message, f"😂 <b>جوک:</b>\n{random.choice(FUNNY_JOKES)}", parse_mode="HTML")

@bot.message_handler(func=lambda m: m.text and m.text.strip() == "شانس" and not (m.chat.id in wars and wars[m.chat.id]["state"] == "luck"))
def cmd_luck(message):
    if not check_force_join(message): return
    uid = str(message.from_user.id); now = time.time()
    if uid in luck_cooldown and (now - luck_cooldown[uid]) < LUCK_COOLDOWN: return
    luck_cooldown[uid] = now
    luck = random.randint(0, 100)
    
    if luck <= 20: emoji, joke = random.choice([("🕳️", "امروز حتی آینه هم صورتت رو نشون نمی‌ده! 🪞"), ("🧨", "شانست از سوسک هم کمتره! 🪳")])
    elif luck <= 40: emoji, joke = random.choice([("🌧️", "شانست ابری! ☁️"), ("🧊", "شانست یخ زده! 🧊")])
    elif luck <= 60: emoji, joke = random.choice([("🪙", "شانست ۵۰-۵۰! 🪙"), ("🤷", "امروز روز هیچ‌کاریه! 🤷")])
    elif luck <= 80: emoji, joke = random.choice([("🔥", "روز ترکوندنه! 🔥"), ("⚡", "شانست مثل برق! ⚡")])
    else: emoji, joke = random.choice([("👑", "پادشاه شانسی! 👑"), ("💎", "شانست الماسه! 💎")])
    
    bar = "🟩" * (luck//10) + "⬛" * (10 - luck//10)
    bot.reply_to(message, f"🍀 <b>شانس {get_mention(uid)}</b>\n{emoji} <b>{luck}%</b>\n{bar}\n📌 {joke}", parse_mode="HTML")

@bot.message_handler(func=lambda m: m.text and m.text.strip() == "موجودی")
def cmd_balance(message):
    if not check_force_join(message): return
    bot.reply_to(message, f"💳 سکه: {get_player(message.from_user.id)['coins']:,}")

@bot.message_handler(func=lambda m: m.text and m.text.strip() == "آمار من")
def cmd_stats(message):
    if not check_force_join(message): return
    
    uid = message.from_user.id
    p = get_player(uid)
    
    text = (
        f"📊 <b>آمار {get_mention(uid)}</b>\n"
        f"━━━━━━━━━━━━━━━━━━\n\n"
        f"💰 <b>موجودی سکه:</b> {p['coins']:,}\n\n"
        f"🎮 <b>تعداد بازی:</b> {p['games']}\n"
        f"🏆 <b>برد:</b> {p['wins']}\n"
        f"❌ <b>باخت:</b> {p['losses']}\n\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"👻 <b>PHANTOM SHOP | DICE</b> 🎲"
    )
    
    bot.reply_to(message, text, parse_mode="HTML")

@bot.message_handler(func=lambda m: m.text and m.text.strip() == "لیست سکه")
def cmd_coin_list(message):
    if not check_force_join(message): return
    members = chat_members.get(message.chat.id, set())
    ranking = sorted([(u, get_player(u)["coins"]) for u in members if get_player(u)["coins"] > 0], key=lambda x: x[1], reverse=True)[:20]
    if not ranking: return bot.reply_to(message, "❌ کسی سکه نداره.")
    lines = [f"{'🥇' if i==1 else '🥈' if i==2 else '🥉' if i==3 else '📌'} {get_mention(u)}: {c:,}" for i, (u, c) in enumerate(ranking, 1)]
    bot.reply_to(message, "💰 <b>لیست سکه</b>\n" + "\n".join(lines), parse_mode="HTML")

@bot.message_handler(func=lambda m: m.text and m.text.strip().startswith("لقب "))
def cmd_nick(message):
    if not check_force_join(message): return
    nick = message.text.strip()[4:].strip()
    if not nick or len(nick) > 30: return
    p = get_player(message.from_user.id); p["nickname"] = nick; save_data()
    bot.reply_to(message, f"✅ لقب: {nick}")

@bot.message_handler(func=lambda m: m.text and m.text.strip() == "دعوت")
def cmd_invite(message):
    if not check_force_join(message): return
    p = get_player(message.from_user.id)
    link = f"https://t.me/{BOT_USERNAME}?start=inv_{message.from_user.id}"
    bot.reply_to(message, f"🎁 لینک دعوت: \n<code>{link}</code>\n👥 دعوت‌ها: {p.get('invited_count', 0)}\n📅 هفته: {p.get('invited_count_week', 0)}", parse_mode="HTML")

# ========== 🌐 بخش وب‌سرور برای زنده موندن در Render (UptimeRobot) ==========
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write("🤖 Phantom Shop Bot is Alive and Running!".encode('utf-8'))
    
    def log_message(self, format, *args):
        pass 

def run_health_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), HealthCheckHandler)
    print(f"🌐 وب‌سرور Health Check روی پورت {port} روشن شد.")
    server.serve_forever()

threading.Thread(target=run_health_server, daemon=True).start()

# ========== شروع ربات تلگرام ==========
print("👻 PHANTOM SHOP | DICE 🎲 ربات روشن شد...")
bot.infinity_polling(timeout=10, long_polling_timeout=5, skip_pending=True)

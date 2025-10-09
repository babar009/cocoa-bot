from flask import Flask, request, jsonify
from pymongo import MongoClient
from datetime import datetime

cluster = MongoClient(
    "mongodb+srv://Babar:babar@cocoabakebot.n8zdbxb.mongodb.net/?retryWrites=true&w=majority&appName=CocoaBakeBot"
)
db = cluster["CocoaBakeBot"]
users = db["users"]
# orders collection left out because not used here, add back if needed:
# orders = db["orders"]

app = Flask(__name__)

# ===== Menus (include option L to change language) =====
english_menu = (
    "Hi — Cocoa Bake Studio Daska 🎂\n\n"
    "Please choose one of the options below:\n\n"
    "1️⃣ Shop Timing\n"
    "2️⃣ Menu\n"
    "3️⃣ Dream Cake Price\n"
    "4️⃣ Custom Cake Price\n"
    "5️⃣ Bento Cake Price\n"
    "6️⃣ Fire Cake Price\n"
    "7️⃣ Picture Cake Price\n"
    "8️⃣ Home Delivery Details\n"
    "9️⃣ Our Location\n"
    "0️⃣ Contact Representative\n\n"
    "To change language type *L*.\n"
    "You can also type *Y* anytime to see this menu again."
)

urdu_menu = (
    "السلام علیکم — Cocoa Bake Studio Daska 🎂\n\n"
    "براہ کرم نیچے سے ایک آپشن منتخب کریں:\n\n"
    "1️⃣ دکان کے اوقات\n"
    "2️⃣ مینو\n"
    "3️⃣ ڈریم کیک کی قیمت\n"
    "4️⃣ کسٹم کیک کی قیمت\n"
    "5️⃣ بینٹو کیک کی قیمت\n"
    "6️⃣ فائر کیک کی قیمت\n"
    "7️⃣ پکچر کیک کی قیمت\n"
    "8️⃣ ہوم ڈیلیوری کی تفصیلات\n"
    "9️⃣ ہمارا مقام\n"
    "0️⃣ نمائندے سے رابطہ\n\n"
    "زبان تبدیل کرنے کے لیے *L* لکھیں۔\n"
    "مرکزی مینو دوبارہ دیکھنے کے لیے *Y* لکھیں۔"
)

# ===== Helper: language selection prompt (in both languages depending on context) =====
lang_prompt_en = "Please select your language:\n*E* for English 🇬🇧\n*U* for Urdu 🇵🇰"
lang_prompt_ur = "براہ کرم اپنی زبان منتخب کریں:\n*E* انگریزی کے لیے 🇬🇧\n*U* اردو کے لیے 🇵🇰"

@app.route("/")
def home():
    return "✅ CocoaBake WhatsApp Bot is running."

@app.route("/reply", methods=["POST"])
def reply():
    # Accept form or JSON
    data = request.form if request.form else request.get_json(silent=True)
    if not data:
        return jsonify({"reply": "Error: No data received"}), 400

    raw_text = data.get("message", "") or ""
    text = raw_text.strip()
    text_lower = text.lower()
    number = data.get("sender") or data.get("from")  # try common fields

    if not number:
        return jsonify({"reply": "Error: No WhatsApp data received"}), 400

    user = users.find_one({"number": number})

    # Default reply
    reply_text = ""

    # 1) New user → ask language
    if not user:
        reply_text = (
            "Welcome to *Cocoa Bake Studio Daska!* 🎂\n\n" +
            "Please select your language:\n*E* for English 🇬🇧\n*U* for Urdu 🇵🇰"
        )
        users.insert_one({
            "number": number,
            "status": "choose_language",
            "messages": []
        })

    # 2) User is choosing language
    elif user.get("status") == "choose_language":
        # normalize selection
        if text_lower == "e":
            users.update_one(
                {"number": number},
                {"$set": {"language": "en", "status": "main"}}
            )
            reply_text = "You have selected *English* 🇬🇧.\n\n" + english_menu
        elif text_lower == "u":
            users.update_one(
                {"number": number},
                {"$set": {"language": "ur", "status": "main"}}
            )
            reply_text = "آپ نے *اردو* 🇵🇰 منتخب کر لی ہے۔\n\n" + urdu_menu
        else:
            # Ask again (use English guidance so they know to press E/U)
            reply_text = "Please reply with *E* for English 🇬🇧 or *U* for Urdu 🇵🇰."

    # 3) Main flow for users with status "main"
    else:
        lang = user.get("language", "en").lower()

        # If user asked to change language from main menu (L)
        if text_lower == "l":
            # Put user into choose_language state and ask for E/U; message shown in current language
            users.update_one({"number": number}, {"$set": {"status": "choose_language"}})
            reply_text = lang_prompt_en if lang == "en" else lang_prompt_ur

        # If user asked to see main menu (Y)
        elif text_lower == "y":
            reply_text = english_menu if lang == "en" else urdu_menu

        else:
            # If numeric input 0-9 => process; otherwise show welcome-back hint in user's language.
            try:
                option = int(text_lower)
            except ValueError:
                # Non-numeric (and not Y/L) — treat as "welcome back" hint in user's language
                if lang == "en":
                    reply_text = (
                        "👋 Welcome back to *Cocoa Bake Studio Daska*! \n\n"
                        "Please enter a number between 0–9 to get the information you want.\n"
                        "Type *Y* to see the main menu again, or *L* to change language."
                    )
                else:
                    reply_text = (
                        "👋 واپسی پر خوش آمدید! \n\n"
                        "براہ کرم مطلوبہ معلومات کے لیے 0–9 کے درمیان نمبر درج کریں۔\n"
                        "مرکزی مینو دوبارہ دیکھنے کے لیے *Y* لکھیں، یا زبان تبدیل کرنے کے لیے *L* لکھیں۔"
                    )
                option = None

            # If option is integer, handle each menu item
            if isinstance(option, int):
                if option == 1:
                    reply_text = (
                        "🕐 Our Shop Timing is *1pm to 12am*." if lang == "en"
                        else "🕐 ہماری دکان کے اوقات *1pm سے 12am* ہیں۔"
                    )
                elif option == 2:
                    reply_text = (
                        "🍰 View our Menu: https://wa.me/c/923001210019" if lang == "en"
                        else "🍰 ہمارا مینو دیکھنے کے لیے: https://wa.me/c/923001210019"
                    )
                elif option == 3:
                    reply_text = (
                        "🎂 Dream Cake Prices:\n1 lb = 1300\n2 lb = 2500\nDelivery 100 for orders < 2000." if lang == "en"
                        else "🎂 ڈریم کیک کی قیمتیں:\n1 پاؤنڈ = 1300\n2 پاؤنڈ = 2500\n2000 سے کم آرڈر پر ڈیلیوری 100 روپے۔"
                    )
                elif option == 4:
                    reply_text = (
                        "🎂 Custom Cakes start from 1500/pound. Flavors: Chocolate, Double Chocolate, Triple Chocolate, Matilda, Pineapple, Strawberry, Blueberry, Peach, Mango."
                        if lang == "en"
                        else "🎂 کسٹم کیکس 1500 روپے فی پاؤنڈ سے شروع ہوتے ہیں۔ فلیورز: چاکلیٹ، ڈبل چاکلیٹ، ٹرپل چاکلیٹ، میٹیلڈا، انناس، اسٹرابیری، بلیوبیری، پیچ، آم۔"
                    )
                elif option == 5:
                    reply_text = (
                        "🎁 Bento Cakes start from 1200 per cake." if lang == "en"
                        else "🎁 بینٹو کیکس 1200 روپے فی کیک سے شروع ہوتے ہیں۔"
                    )
                elif option == 6:
                    reply_text = (
                        "🔥 Fire Cake Prices:\nBento = 1700\n1.5 lb = 2700\n2 lb round = 3400\n2 lb heart = 3600\n+800 for eatable picture."
                        if lang == "en"
                        else "🔥 فائر کیک قیمتیں:\nبینٹو = 1700\n1.5 پاؤنڈ = 2700\n2 پاؤنڈ گول = 3400\n2 پاؤنڈ دل = 3600\nکھانے کے قابل تصویر +800 اضافی۔"
                    )
                elif option == 7:
                    reply_text = (
                        "🖼️ Picture Cake Prices:\nBento = 1400\n1.5 lb = 2400\n2 lb round = 3200\n2 lb heart = 3300\n+800 for eatable picture."
                        if lang == "en"
                        else "🖼️ پکچر کیک قیمتیں:\nبینٹو = 1400\n1.5 پاؤنڈ = 2400\n2 پاؤنڈ گول = 3200\n2 پاؤنڈ دل = 3300\nکھانے کے قابل تصویر +800 اضافی۔"
                    )
                elif option == 8:
                    reply_text = (
                        "🚚 Delivery Charges:\nWithin Daska = 100\nNearby areas = 150\nOutside Daska (bike) = 50/km\nOutside Daska (car) = 200/km"
                        if lang == "en"
                        else "🚚 ڈیلیوری چارجز:\nڈسکہ کے اندر = 100\nقریبی علاقے = 150\nڈسکہ سے باہر (موٹر سائیکل) = 50/کلومیٹر\n(کار) = 200/کلومیٹر"
                    )
                elif option == 9:
                    reply_text = (
                        "📍 We are at Nisbat Road Daska (near Govt. Boys High School, Kashi Pizza Home, Butt Fruit Shop)."
                        if lang == "en"
                        else "📍 ہمارا مقام: نس بٹ روڈ ڈسکہ (قریب: گورنمنٹ بوائز ہائی اسکول، کاشی پیزا ہوم، بٹ فروٹ شاپ)"
                    )
                elif option == 0:
                    reply_text = (
                        "☎️ Representative available 10am–11pm. For urgent help call 03001210019."
                        if lang == "en"
                        else "☎️ نمائندہ 10am–11pm تک دستیاب ہے۔ ہنگامی صورت میں کال کریں: 03001210019۔"
                    )
                else:
                    reply_text = (
                        "Please enter a valid number between 0–9."
                        if lang == "en"
                        else "براہ کرم 0 سے 9 کے درمیان کوئی درست نمبر درج کریں۔"
                    )

        # Ensure user remains in main state
        users.update_one({"number": number}, {"$set": {"status": "main"}})

    # Log every message
    users.update_one(
        {"number": number},
        {"$push": {"messages": {"text": raw_text, "date": datetime.now()}}},
        upsert=True
    )

    return jsonify({"reply": reply_text})


if __name__ == "__main__":
    app.run(port=5000)

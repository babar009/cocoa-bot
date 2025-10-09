from flask import Flask, request, jsonify
from pymongo import MongoClient
from datetime import datetime

cluster = MongoClient(
    "mongodb+srv://Babar:babar@cocoabakebot.n8zdbxb.mongodb.net/?retryWrites=true&w=majority&appName=CocoaBakeBot")
db = cluster["CocoaBakeBot"]
users = db["users"]

app = Flask(__name__)

# ===== Menus =====
english_menu = (
    "Please follow the instructions *to Place Order* or *for General Information*\n\n"
    "For *Shop Timing* Press 1️⃣\n"
    "For *Menu* Press 2️⃣\n"
    "For *Dream Cake Price* Press 3️⃣\n"
    "For *Custom Cake Price* Press 4️⃣\n"
    "For *Bento Cake Price* Press 5️⃣\n"
    "For *Fire Cake Price* Press 6️⃣\n"
    "For *Picture Cake Price* Press 7️⃣\n"
    "For *Home Delivery Details* Press 8️⃣\n"
    "For *Our Location* Press 9️⃣\n"
    "To *Contact Our Representative* Press 0️⃣"
)

urdu_menu = (
    "برائے مہربانی درج ذیل میں سے ایک آپشن منتخب کریں:\n\n"
    "1️⃣ دکان کے اوقات کار کے لیے\n"
    "2️⃣ مینیو دیکھنے کے لیے\n"
    "3️⃣ ڈریم کیک کی قیمت کے لیے\n"
    "4️⃣ کسٹم کیک کی قیمت کے لیے\n"
    "5️⃣ بینٹو کیک کی قیمت کے لیے\n"
    "6️⃣ فائر کیک کی قیمت کے لیے\n"
    "7️⃣ پکچر کیک کی قیمت کے لیے\n"
    "8️⃣ ہوم ڈیلیوری کی تفصیلات کے لیے\n"
    "9️⃣ ہمارے مقام کے لیے\n"
    "0️⃣ نمائندے سے بات کرنے کے لیے"
)

@app.route("/")
def home():
    return "✅ CocoaBake WhatsApp Bot is running."

@app.route("/reply", methods=["POST"])
def reply():
    data = request.form if request.form else request.json
    text = data.get("message", "").strip().lower()
    number = data.get("sender")

    if not number:
        return jsonify({"reply": "Error: No WhatsApp data received"}), 400

    user = users.find_one({"number": number})

    # === Step 1: New User (Language Selection) ===
    if not user:
        reply = "Please select your language: *E for English 🇬🇧* or *U for Urdu 🇵🇰*"
        users.insert_one({"number": number, "status": "choose_language", "messages": []})

    # === Step 2: Choosing Language ===
    elif user["status"] == "choose_language":
        if text == "e":
            users.update_one({"number": number}, {"$set": {"language": "en", "status": "main"}})
            reply = "You have selected *English* 🇬🇧.\n\n" + english_menu
        elif text == "u":
            users.update_one({"number": number}, {"$set": {"language": "ur", "status": "main"}})
            reply = "آپ نے *اردو* 🇵🇰 منتخب کر لی ہے۔\n\n" + urdu_menu
        else:
            reply = "Please reply with 'E' for English 🇬🇧 or 'U' for Urdu 🇵🇰."

    # === Step 3: Main Menu (existing user) ===
    elif user["status"] == "main":
        lang = user.get("language", "en")

        # ✅ Handle Y to show menu again
        if text == "y":
            reply = english_menu if lang == "en" else urdu_menu
            users.update_one({"number": number}, {"$set": {"status": "main"}})
            return jsonify({"reply": reply})

        # Handle numeric options
        try:
            option = int(text)
        except:
            reply = (
                "Please enter a valid number between 0–9.\n\nPress *Y* to see the main menu again."
                if lang == "en"
                else "براہ کرم 0 سے 9 کے درمیان کوئی درست نمبر درج کریں۔\n\nدوبارہ مینیو دیکھنے کے لیے *Y* لکھیں۔"
            )
            users.update_one({"number": number}, {"$set": {"status": "main"}})
            return jsonify({"reply": reply})

        # English Responses
        if lang == "en":
            if option == 1:
                reply = "Our *Shop Timing* is *1pm to 12am*"
            elif option == 2:
                reply = "Please click to view our *Menu*:\nhttps://wa.me/c/923001210019"
            elif option == 3:
                reply = "1 Pound Dream Cake = *1300*\n2 Pounds Dream Cake = *2500*\n*100 Delivery Charges for Orders under 2000*"
            elif option == 4:
                reply = "Our *Custom Cakes* start from *1500 per Pound*.\nFlavors: Chocolate, Double Chocolate, Triple Chocolate, Matilda, Pineapple, Strawberry, Blueberry, Peach, Mango."
            elif option == 5:
                reply = "Our *Bento Cakes* start from *1200*.\nFlavors: Chocolate, Double Chocolate, Triple Chocolate, Pineapple, Strawberry, Blueberry, Peach, Mango."
            elif option == 6:
                reply = "*Bento Fire Cake* = 1700\n*1.5 lb* = 2700\n*2 lb Round* = 3400\n*2 lb Heart* = 3600\n+800 for Eatable Picture."
            elif option == 7:
                reply = "*Bento Picture Cake* = 1400\n*1.5 lb* = 2400\n*2 lb Round* = 3200\n*2 lb Heart* = 3300\n+800 for Eatable Picture."
            elif option == 8:
                reply = "*Within Daska* = 100\n*Nearby Areas* = 150\n*Outside Daska (Bike)* = 50/km\n*Outside Daska (Car)* = 200/km"
            elif option == 9:
                reply = "We are located at *Nisbat Road Daska* near Govt. Boys High School, Kashi Pizza Home, and Butt Fruit Shop."
            elif option == 0:
                reply = "Our representative is available *10am–11pm*. For urgent help, call 03001210019."
            else:
                reply = "Please enter a valid number between 0–9."
        
        # Urdu Responses
        else:
            if option == 1:
                reply = "ہماری دکان کے اوقات *1 بجے دن سے 12 بجے رات تک* ہیں۔"
            elif option == 2:
                reply = "براہ کرم ہمارا *مینیو* دیکھنے کے لیے لنک پر کلک کریں:\nhttps://wa.me/c/923001210019"
            elif option == 3:
                reply = "1 پاؤنڈ ڈریم کیک = *1300*\n2 پاؤنڈ ڈریم کیک = *2500*\n*2000 روپے سے کم آرڈر پر 100 روپے ڈیلیوری چارجز۔*"
            elif option == 4:
                reply = "ہمارے *کسٹم کیک* کی قیمت *1500 روپے فی پاؤنڈ* سے شروع ہوتی ہے۔\nفلیورز: چاکلیٹ، ڈبل چاکلیٹ، ٹرپل چاکلیٹ، میٹیلڈا، پائن ایپل، اسٹرابیری، بلیو بیری، پیچ، آم۔"
            elif option == 5:
                reply = "ہمارے *بینٹو کیک* کی قیمت *1200 روپے* سے شروع ہوتی ہے۔\nفلیورز: چاکلیٹ، ڈبل چاکلیٹ، ٹرپل چاکلیٹ، پائن ایپل، اسٹرابیری، بلیو بیری، پیچ، آم۔"
            elif option == 6:
                reply = "*بینٹو فائر کیک* = 1700\n*1.5 پاؤنڈ* = 2700\n*2 پاؤنڈ گول* = 3400\n*2 پاؤنڈ دل نما* = 3600\n*کھانے کے قابل تصویر* = 800 اضافی۔"
            elif option == 7:
                reply = "*بینٹو پکچر کیک* = 1400\n*1.5 پاؤنڈ* = 2400\n*2 پاؤنڈ گول* = 3200\n*2 پاؤنڈ دل نما* = 3300\n*کھانے کے قابل تصویر* = 800 اضافی۔"
            elif option == 8:
                reply = "*ڈسکہ کے اندر* = 100\n*قریبی علاقے* = 150\n*ڈسکہ سے باہر (موٹر سائیکل)* = 50 فی کلومیٹر\n*ڈسکہ سے باہر (کار)* = 200 فی کلومیٹر"
            elif option == 9:
                reply = "ہم *نسبت روڈ ڈسکہ* پر واقع ہیں۔\nقریبی مقامات: گورنمنٹ بوائز ہائی اسکول، کاشی پیزا ہوم، بٹ فروٹ شاپ۔"
            elif option == 0:
                reply = "ہمارا نمائندہ *10 بجے صبح سے 11 بجے رات* تک دستیاب ہے۔ فوری رابطے کے لیے کال کریں: 03001210019۔"
            else:
                reply = "براہ کرم 0 سے 9 کے درمیان کوئی درست نمبر درج کریں۔"

    # === Step 4: Catch-all (Failsafe) ===
    else:
        reply = (
            "Welcome back to *Cocoa Bake Studio Daska*! 🎂\n\n"
            "Please reply with *Y* to see the main menu again."
            if user.get("language", "en") == "en"
            else "واپس خوش آمدید 🎂\n\nبراہ کرم *Y* لکھ کر مینیو دوبارہ دیکھیں۔"
        )
        users.update_one({"number": number}, {"$set": {"status": "main"}})

    # Log message
    users.update_one(
        {"number": number},
        {"$push": {"messages": {"text": text, "date": datetime.now()}}},
        upsert=True
    )

    return jsonify({"reply": reply})


if __name__ == "__main__":
    app.run(port=5000)

from flask import Flask, request, jsonify
from pymongo import MongoClient
from datetime import datetime

cluster = MongoClient(
    "mongodb+srv://Babar:babar@cocoabakebot.n8zdbxb.mongodb.net/?retryWrites=true&w=majority&appName=CocoaBakeBot"
)
db = cluster["CocoaBakeBot"]
users = db["users"]
orders = db["orders"]

app = Flask(__name__)

@app.route("/")
def home():
    return "✅ CocoaBake WhatsApp Bot is running."

@app.route("/reply", methods=["POST"])
def reply():
    data = request.form if request.form else request.get_json(silent=True)
    if not data:
        return jsonify({"reply": "Error: No data received"}), 400

    text = str(data.get("message", "")).strip()
    number = str(data.get("sender", "")).strip()

    if not number or not text:
        return jsonify({"reply": "Error: Missing sender or message"}), 400

    user = users.find_one({"number": number})

    # === Language Menus ===
    def main_menu_en():
        return (
            "Hi, thanks for contacting *Cocoa Bake Studio Daska* 🎂\n"
            "Please follow the instructions below:\n\n"
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
            "Type *L* to change language 🇵🇰"
        )

    def main_menu_ur():
        return (
            "السلام علیکم! *Cocoa Bake Studio Daska* میں خوش آمدید 🎂\n"
            "براہ کرم نیچے دی گئی ہدایات میں سے انتخاب کریں:\n\n"
            "1️⃣ دکان کے اوقات کار\n"
            "2️⃣ مینو دیکھیں\n"
            "3️⃣ ڈریم کیک کی قیمت\n"
            "4️⃣ کسٹم کیک کی قیمت\n"
            "5️⃣ بینٹو کیک کی قیمت\n"
            "6️⃣ فائر کیک کی قیمت\n"
            "7️⃣ پکچر کیک کی قیمت\n"
            "8️⃣ ہوم ڈیلیوری کی تفصیل\n"
            "9️⃣ ہمارا پتہ\n"
            "0️⃣ نمائندے سے رابطہ کریں\n\n"
            "زبان تبدیل کرنے کے لیے *L* لکھیں 🇬🇧"
        )

    # === First interaction ===
    if not user:
        reply = (
            "Welcome to *Cocoa Bake Studio Daska!* 🎂\n\n"
            "Please select your language:\n"
            "🇬🇧 Type *E* for English\n"
            "🇵🇰 Type *U* for Urdu"
        )
        users.insert_one({"number": number, "status": "language", "messages": []})

    # === If user is selecting language ===
    elif user["status"] == "language":
        if text.lower() == "e":
            users.update_one({"number": number}, {"$set": {"status": "main", "language": "en"}})
            reply = main_menu_en()
        elif text.lower() == "u":
            users.update_one({"number": number}, {"$set": {"status": "main", "language": "ur"}})
            reply = main_menu_ur()
        else:
            reply = "Please select a valid option:\n*E* for English 🇬🇧\n*U* for Urdu 🇵🇰"

    else:
        lang = user.get("language", "en").lower()

        # Language toggle
        if text.lower() == "l":
            users.update_one({"number": number}, {"$set": {"status": "language"}})
            reply = (
                "Please select your language:\n"
                "🇬🇧 Type *E* for English\n"
                "🇵🇰 Type *U* for Urdu"
            )
        # Show menu again
        elif text.lower() in ["y", "yes"]:
            reply = main_menu_en() if lang == "en" else main_menu_ur()
        else:
            try:
                option = int(text)
            except ValueError:
                reply = (
                    "👋 Welcome back!\nPlease enter a valid number between 0–9.\n"
                    "Or type *Y* to see the main menu again."
                    if lang == "en"
                    else "👋 خوش آمدید!\nبراہ کرم 0 سے 9 کے درمیان درست نمبر درج کریں۔\n"
                         "یا مرکزی مینو دیکھنے کے لیے *Y* لکھیں۔"
                )
                option = None

            # === English Responses ===
            if lang == "en":
                if option == 1:
                    reply = "🕐 Our *Shop Timing* is *1pm to 12am*."
                elif option == 2:
                    reply = "🍰 Click here to see our *Menu*: https://wa.me/c/923001210019"
                elif option == 3:
                    reply = "🎂 *Dream Cake Price:*\n1 Pound = 1300\n2 Pounds = 2500\nDelivery 100 for orders under 2000."
                elif option == 4:
                    reply = (
                        "🎂 *Custom Cakes* start from 1500/pound.\n"
                        "Flavors: Chocolate, Double Chocolate, Triple Chocolate, Matilda, Pineapple, Strawberry, Blueberry, Peach, Mango."
                    )
                elif option == 5:
                    reply = (
                        "🎁 *Bento Cakes* start from 1200 per cake.\n"
                        "Flavors: Chocolate, Double Chocolate, Triple Chocolate, Pineapple, Strawberry, Blueberry, Peach, Mango."
                    )
                elif option == 6:
                    reply = (
                        "🔥 *Fire Cake Prices:*\n"
                        "Bento = 1700\n1.5 Pound = 2700\n2 Pound Round = 3400\n2 Pound Heart = 3600\nEatable Picture +800 extra."
                    )
                elif option == 7:
                    reply = (
                        "🖼️ *Picture Cake Prices:*\n"
                        "Bento = 1400\n1.5 Pound = 2400\n2 Pound Round = 3200\n2 Pound Heart = 3300\nEatable Picture +800 extra."
                    )
                elif option == 8:
                    reply = (
                        "🚚 *Delivery Charges:*\n"
                        "Within Daska = 100\nMandranwala / Canal View / Bismillah CNG / Bharokey = 150\n"
                        "Outside Daska = Rs.50/km (Bike)\nCar Delivery = Rs.200/km"
                    )
                elif option == 9:
                    reply = (
                        "📍 *Location:*\nNisbat Road Daska\n\nNearby:\n"
                        "Govt. High School for Boys\nKashi Pizza Home\nButt Fruit Shop."
                    )
                elif option == 0:
                    reply = "☎️ Representative available 10am–11pm.\nFor urgent help, call 03001210019."
                elif option is None:
                    pass
                else:
                    reply = "Please enter a valid number between 0–9 or type *Y* for main menu."

            # === Urdu Responses ===
            elif lang == "ur":
                if option == 1:
                    reply = "🕐 ہماری دکان کے اوقات کار *1pm سے 12am* تک ہیں۔"
                elif option == 2:
                    reply = "🍰 ہمارا *مینو* دیکھنے کے لیے اس لنک پر کلک کریں: https://wa.me/c/923001210019"
                elif option == 3:
                    reply = "🎂 *ڈریم کیک کی قیمت:*\n1 پاؤنڈ = 1300\n2 پاؤنڈ = 2500\n2000 سے کم آرڈر پر ڈیلیوری 100 روپے۔"
                elif option == 4:
                    reply = (
                        "🎂 *کسٹم کیک* کی قیمت 1500 روپے فی پاؤنڈ سے شروع۔\n"
                        "فلیورز: چاکلیٹ، ڈبل چاکلیٹ، ٹرپل چاکلیٹ، میٹیلڈا، پائن ایپل، اسٹرابیری، بلیو بیری، پیچ، آم۔"
                    )
                elif option == 5:
                    reply = (
                        "🎁 *بینٹو کیک* 1200 روپے فی کیک سے شروع۔\n"
                        "فلیورز: چاکلیٹ، ڈبل چاکلیٹ، ٹرپل چاکلیٹ، پائن ایپل، اسٹرابیری، بلیو بیری، پیچ، آم۔"
                    )
                elif option == 6:
                    reply = (
                        "🔥 *فائر کیک کی قیمتیں:*\n"
                        "بینٹو = 1700\n1.5 پاؤنڈ = 2700\n2 پاؤنڈ گول = 3400\n2 پاؤنڈ دل = 3600\nایٹیبل پکچر +800 اضافی۔"
                    )
                elif option == 7:
                    reply = (
                        "🖼️ *پکچر کیک کی قیمتیں:*\n"
                        "بینٹو = 1400\n1.5 پاؤنڈ = 2400\n2 پاؤنڈ گول = 3200\n2 پاؤنڈ دل = 3300\nایٹیبل پکچر +800 اضافی۔"
                    )
                elif option == 8:
                    reply = (
                        "🚚 *ڈیلیوری چارجز:*\n"
                        "ڈسکہ کے اندر = 100\nمنڈرانوالہ / کینال ویو / بسم اللہ سی این جی / بھروکی = 150\n"
                        "ڈسکہ سے باہر = 50 روپے فی کلومیٹر (بائیک)\nکار پر = 200 روپے فی کلومیٹر۔"
                    )
                elif option == 9:
                    reply = (
                        "📍 *ہمارا پتہ:*\nنس بٹ روڈ ڈسکہ\n\nقریب:\n"
                        "گورنمنٹ ہائی اسکول برائے طلباء\nکاشی پیزا ہوم\nبٹ فروٹ شاپ۔"
                    )
                elif option == 0:
                    reply = "☎️ نمائندہ 10am سے 11pm تک دستیاب۔\nہنگامی رابطہ: 03001210019"
                elif option is None:
                    pass
                else:
                    reply = "براہ کرم 0 سے 9 کے درمیان درست نمبر درج کریں یا *Y* لکھیں۔"

        users.update_one({"number": number}, {"$set": {"status": "main"}})

    # Log messages
    users.update_one(
        {"number": number},
        {"$push": {"messages": {"text": text, "date": datetime.now()}}},
        upsert=True
    )

    return jsonify({"reply": reply})

if __name__ == "__main__":
    app.run(port=5000)

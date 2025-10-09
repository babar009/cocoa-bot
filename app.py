from flask import Flask, request, jsonify
from pymongo import MongoClient
from datetime import datetime

cluster = MongoClient(
    "mongodb+srv://Babar:babar@cocoabakebot.n8zdbxb.mongodb.net/?retryWrites=true&w=majority&appName=CocoaBakeBot")
db = cluster["CocoaBakeBot"]
users = db["users"]
orders = db["orders"]

app = Flask(__name__)

# English and Urdu menu templates
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
    "براہ کرم آرڈر دینے یا عام معلومات کے لیے ہدایات پر عمل کریں۔\n\n"
    "دکان کے اوقات کے لیے 1️⃣ دبائیں\n"
    "مینیو کے لیے 2️⃣ دبائیں\n"
    "ڈریم کیک کی قیمت کے لیے 3️⃣ دبائیں\n"
    "کسٹم کیک کی قیمت کے لیے 4️⃣ دبائیں\n"
    "بینٹو کیک کی قیمت کے لیے 5️⃣ دبائیں\n"
    "فائر کیک کی قیمت کے لیے 6️⃣ دبائیں\n"
    "پکچر کیک کی قیمت کے لیے 7️⃣ دبائیں\n"
    "ہوم ڈیلیوری کی تفصیلات کے لیے 8️⃣ دبائیں\n"
    "ہمارا پتہ جاننے کے لیے 9️⃣ دبائیں\n"
    "نمائندہ سے رابطے کے لیے 0️⃣ دبائیں"
)


@app.route("/")
def home():
    return "✅ CocoaBake WhatsApp Bot is running."


@app.route("/reply", methods=["POST"])
def reply():
    print("FORM DATA:", request.form)  # Debugging
    data = request.form if request.form else request.json
    text = data.get("message")
    number = data.get("sender")

    if not number:
        return jsonify({"reply": "Error: No WhatsApp data received"}), 400

    if text:
        text = text.strip().lower()  # ✅ Normalize input

    user = users.find_one({"number": number})

    # New customer → ask for language
    if not user:
        reply = "Please select your language:\n*E* for English 🇬🇧\n*U* for Urdu 🇵🇰"
        users.insert_one({
            "number": number,
            "status": "choose_language",
            "messages": []
        })

    # User selecting language
    elif user["status"] == "choose_language":
        if text == "e":
            users.update_one(
                {"number": number},
                {"$set": {"language": "en", "status": "main"}}
            )
            reply = "You have selected *English* 🇬🇧.\n\n" + english_menu
        elif text == "u":
            users.update_one(
                {"number": number},
                {"$set": {"language": "ur", "status": "main"}}
            )
            reply = "آپ نے *اردو* 🇵🇰 منتخب کر لی ہے۔\n\n" + urdu_menu
        else:
            reply = "Please reply with *E* for English 🇬🇧 or *U* for Urdu 🇵🇰."

    # Main menu in selected language
    elif user["status"] == "main":
        lang = user.get("language", "en")
        try:
            option = int(text)
        except:
            reply = "Please enter a valid number between 0–9.\n\nPress *Y* to see the main menu."
            users.update_one({"number": number}, {"$set": {"status": "main"}})
            return jsonify({"reply": reply})

        if option == 1:
            reply = "Our *Shop Timing* is *1pm to 12am*" if lang == "en" else "ہماری دکان کے اوقات *1 بجے دوپہر سے 12 بجے رات تک* ہیں۔"
        elif option == 2:
            reply = "Please Click on the following link to see our *Menu*.\nhttps://wa.me/c/923001210019" if lang == "en" else "براہ کرم ہمارا مینیو دیکھنے کے لیے درج ذیل لنک پر کلک کریں۔\nhttps://wa.me/c/923001210019"
        elif option == 3:
            reply = "1 Pound Dream Cake = *1300*\n2 Pounds Dream Cake = *2500*\n*100 Delivery Charges for Orders less than 2000*" if lang == "en" else "1 پاؤنڈ ڈریم کیک = *1300*\n2 پاؤنڈ ڈریم کیک = *2500*\n*2000 سے کم آرڈر پر 100 روپے ڈیلیوری چارجز*"
        elif option == 4:
            reply = "Our *Custom Cakes* start from *1500 per Pound*.\nFlavors: *Chocolate, Double Chocolate, Triple Chocolate, Matilda, Pineapple, Strawberry, Blueberry, Peach, Mango*" if lang == "en" else "ہمارے *کسٹم کیکس* *1500 روپے فی پاؤنڈ* سے شروع ہوتے ہیں۔\nفلیورز: *چاکلیٹ، ڈبل چاکلیٹ، ٹرپل چاکلیٹ، میٹیلڈا، انناس، اسٹرابیری، بلیوبیری، پیچ، آم*"
        elif option == 5:
            reply = "Our *Bento Cakes* start from *1200 per Cake*." if lang == "en" else "ہمارے *بینٹو کیکس* *1200 روپے فی کیک* سے شروع ہوتے ہیں۔"
        elif option == 6:
            reply = "*Bento Fire Cake* = 1700\n*1.5 Pound Fire Cake* = 2700\n*2 Pound Round* = 3400\n*2 Pound Heart* = 3600\n*Eatable Picture* +800 extra." if lang == "en" else "*بینٹو فائر کیک* = 1700\n*1.5 پاؤنڈ فائر کیک* = 2700\n*2 پاؤنڈ راؤنڈ* = 3400\n*2 پاؤنڈ ہارٹ* = 3600\n*ایٹیبل پکچر* +800 اضافی۔"
        elif option == 7:
            reply = "*Bento Picture Cake* = 1400\n*1.5 Pound Picture Cake* = 2400\n*2 Pound Round* = 3200\n*2 Pound Heart* = 3300\n*Eatable Picture* +800 extra." if lang == "en" else "*بینٹو پکچر کیک* = 1400\n*1.5 پاؤنڈ پکچر کیک* = 2400\n*2 پاؤنڈ راؤنڈ* = 3200\n*2 پاؤنڈ ہارٹ* = 3300\n*ایٹیبل پکچر* +800 اضافی۔"
        elif option == 8:
            reply = "*Within Daska* = 100\n*Mandranwala / Canal View / Bismillah CNG / Bharokey* = 150\n*Outside Daska* = Rs.50/km (Bike)\n*Car Delivery* = Rs.200/km" if lang == "en" else "*ڈسکہ کے اندر* = 100\n*منڈرانوالہ / کینال ویو / بسم اللہ سی این جی / بھاروکی* = 150\n*ڈسکہ سے باہر* = 50 روپے فی کلومیٹر (بائیک)\n*کار ڈیلیوری* = 200 روپے فی کلومیٹر"
        elif option == 9:
            reply = "We are located at *Nisbat Road Daska*.\nNearby:\n*Govt. High School for Boys*\n*Kashi Pizza Home*\n*Butt Fruit Shop*" if lang == "en" else "ہم *نسبت روڈ ڈسکہ* پر واقع ہیں۔\nقریب:\n*گورنمنٹ ہائی اسکول برائے لڑکے*\n*کاشی پیزا ہوم*\n*بٹ فروٹ شاپ*"
        elif option == 0:
            reply = "Our representative will be available *10am–11pm*. For urgent help, call 03001210019." if lang == "en" else "ہمارا نمائندہ *صبح 10 بجے سے رات 11 بجے تک* دستیاب ہے۔ فوری مدد کے لیے کال کریں 03001210019۔"
        else:
            reply = "Please enter a valid number between 0–9." if lang == "en" else "براہ کرم 0 سے 9 کے درمیان کوئی درست نمبر درج کریں۔"

    else:
        reply = "Please reply with 'Y' to see the main menu again." if user.get("language", "en") == "en" else "براہ کرم دوبارہ مینیو دیکھنے کے لیے 'Y' لکھیں۔"
        users.update_one({"number": number}, {"$set": {"status": "main"}})

    # Log user message
    users.update_one(
        {"number": number},
        {"$push": {"messages": {"text": text, "date": datetime.now()}}},
        upsert=True
    )

    return jsonify({"reply": reply})


if __name__ == "__main__":
    app.run(port=5000)

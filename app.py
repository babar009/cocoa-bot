from flask import Flask, request, jsonify
from pymongo import MongoClient
from datetime import datetime

cluster = MongoClient("mongodb+srv://Babar:babar@cocoabakebot.n8zdbxb.mongodb.net/?retryWrites=true&w=majority&appName=CocoaBakeBot")
db = cluster["CocoaBakeBot"]
users = db["users"]
orders = db["orders"]

app = Flask(__name__)

# ===== MENUS =====
english_menu = (
    "Please follow the instructions below 👇\n\n"
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
    "🔄 To change language, press *L*"
)

roman_urdu_menu = (
    "Neeche diye gaye options me se koi aik number bhejein 👇\n\n"
    "1️⃣ Shop Timing\n"
    "2️⃣ Menu\n"
    "3️⃣ Dream Cake Price\n"
    "4️⃣ Custom Cake Price\n"
    "5️⃣ Bento Cake Price\n"
    "6️⃣ Fire Cake Price\n"
    "7️⃣ Picture Cake Price\n"
    "8️⃣ Home Delivery Details\n"
    "9️⃣ Hamari Location\n"
    "0️⃣ Representative se baat karein\n\n"
    "🔄 Zuban tabdeel karne ke liye *L* likhein"
)


@app.route("/")
def home():
    return "✅ CocoaBake WhatsApp Bot is running."


@app.route("/reply", methods=["POST"])
def reply():
    data = request.form if request.form else request.json
    text = (data.get("message") or "").strip().lower()
    number = data.get("sender")

    if not number:
        return jsonify({"reply": "Error: No WhatsApp data received"}), 400

    user = users.find_one({"number": number})

    # === 1️⃣ NEW USER: Ask for Language ===
    if not user:
        reply = (
            "Welcome to *Cocoa Bake Studio Daska* 🎂\n\n"
            "Please select your language:\n"
            "*E* for English 🇬🇧\n"
            "*U* for Roman Urdu 🇵🇰"
        )
        users.insert_one({
            "number": number,
            "status": "select_language",
            "language": None,
            "messages": []
        })
        return jsonify({"reply": reply})

    # === 2️⃣ USER SELECTING LANGUAGE ===
    if user["status"] == "select_language":
        if text == "e":
            users.update_one({"number": number}, {"$set": {"language": "en", "status": "main"}})
            reply = "You have selected *English* 🇬🇧\n\n" + english_menu
        elif text == "u":
            users.update_one({"number": number}, {"$set": {"language": "ur", "status": "main"}})
            reply = "Aap ne *Roman Urdu* 🇵🇰 chuni hai.\n\n" + roman_urdu_menu
        else:
            reply = "Please press *E* for English 🇬🇧 or *U* for Roman Urdu 🇵🇰"
        return jsonify({"reply": reply})

    # === 3️⃣ CHANGE LANGUAGE ANYTIME ===
    if text == "l":
        users.update_one({"number": number}, {"$set": {"status": "select_language"}})
        reply = (
            "Please select your language again:\n"
            "*E* for English 🇬🇧\n"
            "*U* for Roman Urdu 🇵🇰"
        )
        return jsonify({"reply": reply})

    lang = user.get("language", "en")

    # === 4️⃣ MAIN MENU HANDLER ===
    if user["status"] == "main":

        # ✅ Press Y to show main menu
        if text == "y":
            reply = english_menu if lang == "en" else roman_urdu_menu
            return jsonify({"reply": reply})

        # ✅ Handle numbers (0–9)
        try:
            option = int(text)
        except:
            if lang == "en":
                reply = "Please enter a valid number between 0–9.\nPress *Y* to see the main menu or *L* to change language."
            else:
                reply = "Bara-e-karam 0 se 9 ke darmiyan koi sahi number likhein.\nMenu dekhne ke liye *Y* likhein ya zuban tabdeel karne ke liye *L* likhein."
            return jsonify({"reply": reply})

        # === English Replies ===
        if lang == "en":
            if option == 1:
                reply = "Our Shop Timing is *1pm to 12am*."
            elif option == 2:
                reply = "Here is our menu: https://wa.me/c/923001210019"
            elif option == 3:
                reply = "Dream Cake: 1 lb = *1300*, 2 lb = *2500*, Delivery = *100* (below 2000)."
            elif option == 4:
                reply = "Custom Cakes start from *1500 per pound*.\nFlavors: Chocolate, Double Chocolate, Triple Chocolate, Matilda, Pineapple, Strawberry, Blueberry, Peach, Mango."
            elif option == 5:
                reply = "Bento Cakes start from *1200 per cake*.\nFlavors: Chocolate, Double Chocolate, Triple Chocolate, Pineapple, Strawberry, Blueberry, Peach, Mango."
            elif option == 6:
                reply = "Fire Cake: Bento = 1700, 1.5 lb = 2700, 2 lb Round = 3400, 2 lb Heart = 3600, Picture +800 extra."
            elif option == 7:
                reply = "Picture Cake: Bento = 1400, 1.5 lb = 2400, 2 lb Round = 3200, 2 lb Heart = 3300, Picture +800 extra."
            elif option == 8:
                reply = "Delivery: Daska = 100, Canal View etc. = 150, Outside Daska = Rs.50/km (bike) or Rs.200/km (car)."
            elif option == 9:
                reply = "Location: Nisbat Road Daska (near Govt. Boys High School, Kashi Pizza, Butt Fruit Shop)."
            elif option == 0:
                reply = "Representative available 10am–11pm. Call 03001210019 for urgent help."
            else:
                reply = "Please enter a valid number between 0–9."
        # === Roman Urdu Replies ===
        else:
            if option == 1:
                reply = "Hamari shop timing *1pm se 12am* tak hai."
            elif option == 2:
                reply = "Yeh raha hamara menu: https://wa.me/c/923001210019"
            elif option == 3:
                reply = "Dream Cake: 1 pound = *1300*, 2 pound = *2500*, Delivery = *100* (agar order 2000 se kam ho)."
            elif option == 4:
                reply = "Custom Cakes *1500 per pound* se start hote hain.\nFlavors: Chocolate, Double Chocolate, Triple Chocolate, Matilda, Pineapple, Strawberry, Blueberry, Peach, Mango."
            elif option == 5:
                reply = "Bento Cakes *1200 per cake* se start hote hain.\nFlavors: Chocolate, Double Chocolate, Triple Chocolate, Pineapple, Strawberry, Blueberry, Peach, Mango."
            elif option == 6:
                reply = "Fire Cake: Bento = 1700, 1.5 pound = 2700, 2 pound Round = 3400, 2 pound Heart = 3600, Picture +800 extra."
            elif option == 7:
                reply = "Picture Cake: Bento = 1400, 1.5 pound = 2400, 2 pound Round = 3200, 2 pound Heart = 3300, Picture +800 extra."
            elif option == 8:
                reply = "Delivery: Daska = 100, Canal View waghera = 150, Bahar Daska = Rs.50/km (bike) ya Rs.200/km (car)."
            elif option == 9:
                reply = "Location: Nisbat Road Daska (Govt. Boys High School, Kashi Pizza, Butt Fruit Shop ke qareeb)."
            elif option == 0:
                reply = "Representative se baat 10am se 11pm tak mumkin hai. Emergency ke liye call karein: 03001210019."
            else:
                reply = "Bara-e-karam 0 se 9 ke darmiyan koi sahi number likhein."

    else:
        # fallback (if status corrupted)
        reply = "Please type *Y* to see the menu again or *L* to change language."
        users.update_one({"number": number}, {"$set": {"status": "main"}})

    # === Log every message ===
    users.update_one(
        {"number": number},
        {"$push": {"messages": {"text": text, "date": datetime.now()}}},
        upsert=True
    )

    return jsonify({"reply": reply})


if __name__ == "__main__":
    app.run(port=5000)

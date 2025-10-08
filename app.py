from flask import Flask, request, jsonify
from pymongo import MongoClient
from datetime import datetime

cluster = MongoClient("mongodb+srv://Babar:babar@cocoabakebot.n8zdbxb.mongodb.net/?retryWrites=true&w=majority&appName=CocoaBakeBot")
db = cluster["CocoaBakeBot"]
users = db["users"]
orders = db["orders"]

app = Flask(__name__)

@app.route("/")
def home():
    return "✅ CocoaBake WhatsApp Bot is running successfully!"

@app.route("/reply", methods=["POST"])
def reply():
    # WhatAuto sends data as JSON or form-data
    data = request.get_json() or request.form
    text = data.get("message") or ""
    number = data.get("sender") or ""

    if not number:
        return jsonify({"reply": "Error: No sender data received."}), 400

    user = users.find_one({"number": number})

    if not user:
        reply = (
            "Hi, thanks for contacting *The Red Velvet*.\n"
            "You can choose from one of the options below:\n\n"
            "*Type*\n\n"
            "1️⃣ To *contact* us\n"
            "2️⃣ To *order* snacks\n"
            "3️⃣ To know our *working hours*\n"
            "4️⃣ To get our *address*"
        )
        users.insert_one({"number": number, "status": "main", "messages": []})
    elif user["status"] == "main":
        try:
            option = int(text)
        except:
            return jsonify({"reply": "Please enter a valid response."})

        if option == 1:
            reply = "You can contact us through phone or WhatsApp.\n\n*Phone*: 03001210019"
        elif option == 2:
            reply = (
                "You have entered *ordering mode*.\n"
                "You can select one of the following cakes to order:\n\n"
                "1️⃣ Red Velvet\n"
                "2️⃣ Dark Forest\n"
                "3️⃣ Ice Cream Cake\n"
                "4️⃣ Plum Cake\n"
                "5️⃣ Sponge Cake\n"
                "6️⃣ Genoise Cake\n"
                "7️⃣ Angel Cake\n"
                "8️⃣ Carrot Cake\n"
                "9️⃣ Fruit Cake\n"
                "0️⃣ Go Back"
            )
            users.update_one({"number": number}, {"$set": {"status": "ordering"}})
        elif option == 3:
            reply = "We work from *1 PM to 12 AM*."
        elif option == 4:
            reply = (
                "We are located at *Nisbat Road Daska, near Govt. High School for Boys and Kashi Pizza Home*."
            )
        else:
            reply = "Please enter a valid response."
    elif user["status"] == "ordering":
        try:
            option = int(text)
        except:
            return jsonify({"reply": "Please enter a valid response."})

        if option == 0:
            users.update_one({"number": number}, {"$set": {"status": "main"}})
            reply = (
                "You can choose from one of the options below:\n\n"
                "1️⃣ To *contact* us\n"
                "2️⃣ To *order* snacks\n"
                "3️⃣ To know our *working hours*\n"
                "4️⃣ To get our *address*"
            )
        elif 1 <= option <= 9:
            cakes = [
                "Red Velvet Cake", "Dark Forest Cake", "Ice Cream Cake",
                "Plum Cake", "Sponge Cake", "Genoise Cake",
                "Angel Cake", "Carrot Cake", "Fruit Cake"
            ]
            selected = cakes[option - 1]
            users.update_one(
                {"number": number},
                {"$set": {"status": "address", "item": selected}}
            )
            reply = f"Excellent choice 😉\nPlease enter your address to confirm the order for *{selected}*."
        else:
            reply = "Please enter a valid response."
    elif user["status"] == "address":
        selected = user.get("item", "Cake")
        orders.insert_one({
            "number": number,
            "item": selected,
            "address": text,
            "order_time": datetime.now()
        })
        users.update_one({"number": number}, {"$set": {"status": "ordered"}})
        reply = (
            f"Thanks for shopping with us 😊\nYour order for *{selected}* "
            "has been received and will be delivered within an hour."
        )
    else:
        reply = (
            "Hi, thanks for contacting again.\nYou can choose from one of the options below:\n\n"
            "1️⃣ To *contact* us\n"
            "2️⃣ To *order* snacks\n"
            "3️⃣ To know our *working hours*\n"
            "4️⃣ To get our *address*"
        )
        users.update_one({"number": number}, {"$set": {"status": "main"}})

    # Log message in MongoDB
    users.update_one(
        {"number": number},
        {"$push": {"messages": {"text": text, "date": datetime.now()}}},
        upsert=True
    )

    # WhatAuto expects a JSON response
    return jsonify({"reply": reply})


if __name__ == "__main__":
    app.run(port=5000)

from flask import Flask, request, jsonify
from pymongo import MongoClient
from datetime import datetime

cluster = MongoClient(
    "mongodb+srv://Babar:babar@cocoabakebot.n8zdbxb.mongodb.net/?retryWrites=true&w=majority&appName=CocoaBakeBot")
db = cluster["CocoaBakeBot"]
users = db["users"]
orders = db["orders"]

app = Flask(__name__)


@app.route("/")
def home():
    return "✅ CocoaBake WhatsApp Bot is running."


@app.route("/reply", methods=["POST"])
@app.route("/reply", methods=["POST"])
def reply():
    # For WhatAuto
    text = request.form.get("message") or request.json.get("message")
    number = request.form.get("sender") or request.json.get("sender")

    if not number:
        return "No WhatsApp data received", 400

    user = users.find_one({"number": number})

    if not user:
        reply = (
            "Hi, thanks for contacting *Cocoa Bake Studio Daska*.\n"
            "Please follow the instructions *to Place Order* or *for General Information*\n\n"
            "For *Shop Timing* Press 1️⃣\n"
            "For *Menu* Press 2️⃣\n"
            "For *Dream Cake Price* Press 3️⃣\n"
            "For *Custom Cake Price* Press 4️⃣\n"
            "For *Bento Cake Price* Press 5️⃣\n"
            "For *Fire Cake Price* Press 6️⃣\n"
            "For *Picture Cake Price* Press 7️⃣\n"
            "For *Home Delivery Details* Press 8️⃣\n"
            "For *Our Location* Press 9️⃣"
            "To *Contact Our Representative* Press 0️⃣"

        )
        users.insert_one({"number": number, "status": "main", "messages": []})
    elif user["status"] == "main":
        try:
            option = int(text)
        except:
            return jsonify({"reply": "Please enter a valid response."})

        if option == 1:
            reply = "Our *Shop Timing* is *1pm to 12am*"
        elif option == 2:
            reply = (
                "Please Click on the following link to see our *Menu*. You can *directly order* from our catalogue.\n"
                "https://wa.me/c/923001210019"
            )
        elif option == 3:
            reply = ("1 Pound Dream Cake = *1300*\n 2 Pounds Dream Cake = *2500*\n *100 Delivery Charges for Orders*"
                     "*less than 2000*")
        elif option == 4:
            reply = (
                "Our *Custom Cakes* start from *1500 per Pound*. Price may increase as per the *Design*.\n"
                "We Offer following *Flavors in Custom Cakes*\n"
                "*Chocolate*\n"
                "*Double Chocolate*\n"
                "*Triple Chocolate (Mousse Filling)*\n"
                "*Matilda Cake*\n"
                "*Pineapple*\n"
                "*Strawberry*\n"
                "*Blueberry*\n"
                "*Peach*\n"
                "*Mango*"
            )
        elif option == 5:
            reply = (
                "Our *Bento Cakes* start from *1200 for a Cake*. Price may increase as per the *Design*.\n"
                "We Offer following *Flavors in Bento*\n"
                "*Chocolate*\n"
                "*Double Chocolate*\n"
                "*Triple Chocolate (Mousse Filling)*\n"
                "*Pineapple*\n"
                "*Strawberry*\n"
                "*Blueberry*\n"
                "*Peach*\n"
                "*Mango*"
            )
        elif option == 6:
            reply = (
                "*Bento Fire Cake* = 1700\n"
                "*1.5 Pound Fire Cake* = 2700\n"
                "*2 Pounds Round Fire Cake* = 3400\n"
                "*2 Pounds Heart Fire Cake* = 3600\n"
                "*Note*: for Eatable Picture on the Fire Cake, Extra 800 will be charged."
            )
        elif option == 7:
            reply = (
                "*Bento Picture Cake* = 1400\n"
                "*1.5 Pound Picture Cake* = 2400\n"
                "*2 Pounds Round Picture Cake* = 3200\n"
                "*2 Pounds Heart Picture Cake* = 3300\n"
                "*Note*: for Eatable Picture on the Cake, Extra 800 will be charged."
            )
        elif option == 8:
            reply = (
                "*Within Daska Delivery Charges* = 100\n"
                "*Mandranwala, Canal View, Younasabad, Bismillah CNG, Bharokey* = 150\n"
                "*Outside Daska* = Rs:50 per Kilometer\n"
                "*Outside Daska on Car* = Rs:200 per Kilometer"
            )
        elif option == 8:
            reply = (
                "We are located at *Nisbat Road Daska*\n\n"
                "Near by Points\n"
                "*Govt. High School for Boys*\n"
                "*Kashi Pizza Home*\n"
                "*Butt Fruit Shop*"
            )
        elif option == 9:
            reply = ("Our representative will be availabe for chat between *10 am to 11pm*. Please wait for your turn.\n"
                     "For Emergency, Please Call: 03001210019")
        else:
            reply = "Please Enter a *Valid Number*"

    # elif user["status"] == "ordering":
    #     try:
    #         option = int(text)
    #     except:
    #         return jsonify({"reply": "Please enter a valid response."})
    #
    #     if option == 0:
    #         users.update_one({"number": number}, {"$set": {"status": "main"}})
    #         reply = (
    #             "You can choose from one of the options below:\n\n"
    #             "1️⃣ To *contact* us\n"
    #             "2️⃣ To *order* snacks\n"
    #             "3️⃣ To know our *working hours*\n"
    #             "4️⃣ To get our *address*"
    #         )
    #     elif 1 <= option <= 9:
    #         cakes = [
    #             "Red Velvet Cake", "Dark Forest Cake", "Ice Cream Cake",
    #             "Plum Cake", "Sponge Cake", "Genoise Cake",
    #             "Angel Cake", "Carrot Cake", "Fruit Cake"
    #         ]
    #         selected = cakes[option - 1]
    #         users.update_one(
    #             {"number": number},
    #             {"$set": {"status": "address", "item": selected}}
    #         )
    #         reply = f"Excellent choice 😉\nPlease enter your address to confirm the order for *{selected}*."
    #     else:
    #         reply = "Please enter a valid response."
    # elif user["status"] == "address":
    #     selected = user.get("item", "Cake")
    #     orders.insert_one({
    #         "number": number,
    #         "item": selected,
    #         "address": text,
    #         "order_time": datetime.now()
    #     })
    #     users.update_one({"number": number}, {"$set": {"status": "ordered"}})
    #     reply = (
    #         f"Thanks for shopping with us 😊\nYour order for *{selected}* "
    #         "has been received and will be delivered within an hour."
    #     )
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

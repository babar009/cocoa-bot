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
def reply():
    print("FORM DATA:", request.form)  # Debugging
    data = request.form if request.form else request.json
    text = data.get("message")
    number = data.get("sender")

    if not number:
        return jsonify({"reply": "Error: No WhatsApp data received"}), 400

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
            "For *Our Location* Press 9️⃣\n"
            "To *Contact Our Representative* Press 0️⃣"
        )
        users.insert_one({"number": number, "status": "main", "messages": []})
        users.update_one(
            {"number": number},
            {"$push": {"messages": {"text": text, "date": datetime.now()}}},
            upsert=True
        )
        return jsonify({"reply": reply})  # ✅ Return immediately for new user

    # ✅ Make sure all existing users go through main logic
    if user.get("status") != "main":
        users.update_one({"number": number}, {"$set": {"status": "main"}})

    try:
        option = int(text)
    except:
        return jsonify({"reply": "Please enter a valid response."})

    if option == 1:
        reply = "Our *Shop Timing* is *1pm to 12am*"
    elif option == 2:
        reply = "Please Click on the following link to see our *Menu*.\nhttps://wa.me/c/923001210019"
    elif option == 3:
        reply = "1 Pound Dream Cake = *1300*\n2 Pounds Dream Cake = *2500*\n*100 Delivery Charges for Orders less than 2000*"
    elif option == 4:
        reply = (
            "Our *Custom Cakes* start from *1500 per Pound*.\n"
            "Flavors: *Chocolate, Double Chocolate, Triple Chocolate, Matilda, Pineapple, Strawberry, Blueberry, Peach, Mango*"
        )
    elif option == 5:
        reply = (
            "Our *Bento Cakes* start from *1200 per Cake*.\n"
            "Flavors: *Chocolate, Double Chocolate, Triple Chocolate, Pineapple, Strawberry, Blueberry, Peach, Mango*"
        )
    elif option == 6:
        reply = (
            "*Bento Fire Cake* = 1700\n"
            "*1.5 Pound Fire Cake* = 2700\n"
            "*2 Pound Round* = 3400\n"
            "*2 Pound Heart* = 3600\n"
            "*Eatable Picture* +800 extra."
        )
    elif option == 7:
        reply = (
            "*Bento Picture Cake* = 1400\n"
            "*1.5 Pound Picture Cake* = 2400\n"
            "*2 Pound Round* = 3200\n"
            "*2 Pound Heart* = 3300\n"
            "*Eatable Picture* +800 extra."
        )
    elif option == 8:
        reply = (
            "*Within Daska* = 100\n"
            "*Mandranwala / Canal View / Bismillah CNG / Bharokey* = 150\n"
            "*Outside Daska* = Rs.50/km (Bike)\n"
            "*Car Delivery* = Rs.200/km"
        )
    elif option == 9:
        reply = (
            "We are located at *Nisbat Road Daska*\n\n"
            "Nearby:\n*Govt. High School for Boys*\n*Kashi Pizza Home*\n*Butt Fruit Shop*"
        )
    elif option == 0:
        reply = "Our representative will be available *10am–11pm*. For urgent help, call 03001210019."
    else:
        reply = (
            "Hi, thanks for contacting *Cocoa Bake Studio Daska* again.\n"
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

    # ✅ Always log message at the end
    users.update_one(
        {"number": number},
        {"$push": {"messages": {"text": text, "date": datetime.now()}}},
        upsert=True
    )

    return jsonify({"reply": reply})


if __name__ == "__main__":
    app.run(port=5000)

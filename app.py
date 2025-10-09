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

    # Helper function: Main Menu
    def main_menu():
        return (
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

    # New user → show main menu
    if not user:
        reply = main_menu()
        users.insert_one({"number": number, "status": "main", "messages": []})

    else:
        lower_text = text.lower()

        # If user types 'y' → show main menu
        if lower_text in ["y", "yes"]:
            reply = main_menu()

        else:
            # Check if it's a number
            try:
                option = int(text)
            except ValueError:
                # For any non-numeric input → show Welcome Back message
                reply = (
                    "👋 Welcome back to *Cocoa Bake Studio Daska!*\n"
                    "Please enter a valid number between 0–9 to get information.\n"
                    "Or type *Y* to see the main menu again."
                )
                option = None

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
                reply = (
                    "Please enter a valid number between 0–9.\n"
                    "Or type *Y* to see the main menu again."
                )

        # Always keep user status = main
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

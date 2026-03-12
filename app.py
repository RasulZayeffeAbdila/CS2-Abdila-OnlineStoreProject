from flask import Flask, request, redirect, url_for, render_template
from datetime import datetime

app = Flask(__name__)
app.secret_key = "777"

current_user = None

accounts = {
    "Admin": ["admin123", "Administrator", "a", "13", "Pagadian City"],
    "Migs": ["12345", "Miguel O. Gonzalez", "c", "14", "Pagadian City"],
    "RonHead": ["mrgwapo", "Prince Dave Lancer G. Ronulo", "c", "13", "Aurora"],
}

orders = {
    "Admin": {},
    "M&V": {
        "Snacks": ["2026-03-12 12:00:00", "12pcs", 120.00],
        "Drinks": ["2026-03-12 12:05:00", "6pcs", 60.00],
    },
    "RonHead": {
        "ToothBrush": ["2019-06-01 09:26:00", "1pcs", 45.00],
        "Toys": ["2026-02-01 17:10:00", "3pcs", 300.00],
    },
}

def correct(username, password):
    return username in accounts and accounts[username][0] == password

def get_revenue():
    total = 0
    for user_orders in orders.values():
        for info in user_orders.values():
            total += info[2]   
    return total

@app.route("/")
def home():
    return redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    global current_user

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if correct(username, password):
            current_user = username
            return redirect(url_for("welcome"))
        else:
            return render_template("login.html", error="Invalid username or password.")

    return render_template("login.html", error=None)

@app.route("/logout")
def logout():
    global current_user
    current_user = None
    return redirect(url_for("login"))

@app.route("/welcome")
def welcome():
    if current_user is None:
        return redirect(url_for("login"))

    user_data = accounts[current_user]

    return render_template(
        "welcome.html",
        username = current_user,
        name = user_data[1],
        role = user_data[2],
        age = user_data[3],
        address = user_data[4],
        user_orders = orders.get(current_user, {}),
        all_orders = orders,
        accounts = accounts,
        revenue = get_revenue(),
    )

@app.route("/register", methods=["GET", "POST"])
def go_to_register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        name = request.form.get("name", "").strip()
        age = request.form.get("age", "").strip()
        address = request.form.get("address", "").strip()

        if not all([username, password, name, age, address]):
            return render_template("register.html", error="All fields are required.", success=None)

        if username in accounts:
            return render_template("register.html", error="Username already taken.", success=None)

        accounts[username] = [password, name, "c", age, address]
        orders[username] = {}

        return render_template("register.html", error=None,
                               success=f"Account created! You can now sign in as {username}.")

    return render_template("register.html", error=None, success=None)

@app.route("/place_order", methods=["POST"])
def place_order():
    if current_user is None:
        return redirect(url_for("login"))

    product = request.form.get("product", "").strip()
    quantity = request.form.get("quantity", "").strip()
    price = request.form.get("price", "").strip()

    if product and quantity and price:
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        orders[current_user][product] = [date, quantity, float(price)]

    return redirect(url_for("welcome"))

if __name__ == "__main__":
    app.run(debug=True)
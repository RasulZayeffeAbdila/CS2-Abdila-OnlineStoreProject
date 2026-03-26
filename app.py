from flask import Flask, request, redirect, url_for, render_template
from datetime import datetime

app = Flask(__name__)
app.secret_key = "777"

current_user = None

accounts = {
    "Admin": ["admin123", "Administrator", "a", "13", "Pagadian City"],
    "M&V": ["12345", "Miguel C. Olvez", "c", "14", "Pagadian City"],
    "RonHead": ["mrgwapo", "Prince Dave Lancer G. Ronulo", "c", "13", "Aurora"],
    "Sacal": ["redtananakocode", "Calex Jheb Salac", "c", "14", "Dipolog City"]
}

orders = {
    "Admin": {},
    "M&V": {
        "Snacks": ["2026-03-16 12:00:00", "12pcs", 120.00],
        "Drinks": ["2026-03-16 12:05:00", "6pcs", 60.00]
    },
    "RonHead": {
        "ToothBrush": ["2026-03-14 19:31:00", "1pcs", 70.00],
        "Time Travel Machine": ["2015-06-01 17:19:00", "1pcs", 39999.00],
        "CP kanang dili 2 Mega Pixel": ["2099-30-10 14:45:00", "1pcs", 6870.00]
    },
    "Sacal": {
        "Pencil na hait": ["2026-03-11 10:17:00", "10pcs", 199.00]
    }
}

def correct(username, password):
    if username in accounts:
        if accounts[username][0] == password:
            return True
    return False

def revenue():
    total = 0
    for user_orders in orders.values():
        for info in user_orders.values():
            total = total + info[2]
    return total

def c_access(username, target_user):
    role = accounts[username][2]
    if role == "a":
        return True
    if username == target_user:
        return True
    return False

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
    msg = request.args.get("msg", None)
    error = request.args.get("error", None)

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
        revenue = revenue(),
        msg = msg,
        error = error,
    )

@app.route("/register", methods=["GET", "POST"])
def go_register():
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

        return render_template("register.html", error=None, success="Account created! You can now sign in as " + username + ".")

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

@app.route("/delete_order", methods=["POST"])
def delete_order():
    if current_user is None:
        return redirect(url_for("login"))

    target_user = request.form.get("target_user", "").strip()
    product = request.form.get("product", "").strip()

    if c_access(current_user, target_user) == False:
        return redirect(url_for("welcome", error="You can only delete your own orders.", tab="tOrders"))

    if target_user not in orders:
        return redirect(url_for("welcome", error="User not found.", tab="tOrders"))

    if product not in orders[target_user]:
        return redirect(url_for("welcome", error='"' + product + '" was not found.', tab="tOrders"))

    del orders[target_user][product]

    return redirect(url_for("welcome", msg='"' + product + '" was successfully deleted.', tab="tOrders"))

@app.route("/edit_order", methods=["POST"])
def edit_order():
    if current_user is None:
        return redirect(url_for("login"))

    target_user = request.form.get("target_user", "").strip()
    old_product = request.form.get("old_product", "").strip()
    new_product = request.form.get("new_product", "").strip()
    new_quantity = request.form.get("new_quantity", "").strip()
    new_price = request.form.get("new_price", "").strip()

    if c_access(current_user, target_user) == False:
        return redirect(url_for("welcome", error="You can only edit your own orders.", tab="tOrders"))

    if target_user not in orders:
        return redirect(url_for("welcome", error="User not found.", tab="tOrders"))

    if old_product not in orders[target_user]:
        return redirect(url_for("welcome", error='"' + old_product + '" was not found.', tab="tOrders"))

    if not new_product:
        return redirect(url_for("welcome", error="Product name cannot be empty.", tab="tOrders"))

    if not new_quantity:
        return redirect(url_for("welcome", error="Quantity cannot be empty.", tab="tOrders"))

    if not new_price:
        return redirect(url_for("welcome", error="Price cannot be empty.", tab="tOrders"))

    original_date = orders[target_user][old_product][0]

    if old_product != new_product:
        del orders[target_user][old_product]

    orders[target_user][new_product] = [original_date, new_quantity, float(new_price)]

    return redirect(url_for("welcome", msg='"' + new_product + '" was successfully updated.', tab="tOrders"))

if __name__ == "__main__":
    app.run(debug=True)
from flask import Flask, render_template, request, redirect
from datetime import datetime
from dateutil.relativedelta import relativedelta
from collections import defaultdict

app = Flask(__name__)
FILE = "members.txt"


# ==============================
# Get Members From File
# ==============================
def get_members():
    members = []
    try:
        with open(FILE, "r") as f:
            for index, line in enumerate(f.readlines()):
                name, age, plan, amount, join_date, end_date = line.strip().split(",")
                members.append({
                    "id": index,
                    "name": name,
                    "age": age,
                    "plan": plan,
                    "amount": float(amount),
                    "join_date": join_date,
                    "end_date": end_date
                })
    except:
        pass
    return members


# ==============================
# Save Members To File
# ==============================
def save_members(members):
    with open(FILE, "w") as f:
        for m in members:
            f.write(f"{m['name']},{m['age']},{m['plan']},{m['amount']},{m['join_date']},{m['end_date']}\n")


# ==============================
# Dashboard Route
# ==============================
@app.route("/")
def dashboard():
    members = get_members()
    today = datetime.today().strftime("%Y-%m-%d")

    total = len(members)
    expired = len([m for m in members if m["end_date"] < today])
    active = total - expired
    revenue = sum(m["amount"] for m in members)

    monthly_data = defaultdict(float)
    for m in members:
        month = m["join_date"][:7]
        monthly_data[month] += m["amount"]

    months = list(monthly_data.keys())
    monthly_revenue = list(monthly_data.values())

    return render_template(
        "dashboard.html",
        total=total,
        active=active,
        expired=expired,
        revenue=revenue,
        months=months,
        monthly_revenue=monthly_revenue
    )


# ==============================
# Add Member
# ==============================
@app.route("/add", methods=["GET", "POST"])
def add_member():
    if request.method == "POST":

        name = request.form["name"]
        age = request.form["age"]
        duration = int(request.form["plan"])
        amount = request.form["amount"]
        join_date = request.form["join_date"]

        join = datetime.strptime(join_date, "%Y-%m-%d")
        end = join + relativedelta(months=duration)
        end_date = end.strftime("%Y-%m-%d")

        with open(FILE, "a") as f:
            f.write(f"{name},{age},{duration} Months,{amount},{join_date},{end_date}\n")

        return redirect("/view")

    return render_template("add_member.html")


# ==============================
# View Members
# ==============================
@app.route("/view")
def view_members():
    members = get_members()
    today = datetime.today().strftime("%Y-%m-%d")
    return render_template("view_members.html", members=members, today=today)


# ==============================
# Delete Member
# ==============================
@app.route("/delete/<int:id>")
def delete_member(id):
    members = get_members()
    if id < len(members):
        members.pop(id)
        save_members(members)
    return redirect("/view")


# ==============================
# Edit Member
# ==============================
@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit_member(id):
    members = get_members()

    if id >= len(members):
        return redirect("/view")

    if request.method == "POST":

        name = request.form["name"]
        age = request.form["age"]
        duration = int(request.form["plan"])
        amount = request.form["amount"]

        join_date = members[id]["join_date"]

        join = datetime.strptime(join_date, "%Y-%m-%d")
        end = join + relativedelta(months=duration)
        end_date = end.strftime("%Y-%m-%d")

        members[id] = {
            "id": id,
            "name": name,
            "age": age,
            "plan": str(duration) + " Months",
            "amount": float(amount),
            "join_date": join_date,
            "end_date": end_date
        }

        save_members(members)
        return redirect("/view")

    return render_template("edit_member.html", member=members[id])


# ==============================
# Print Membership Receipt
# ==============================
@app.route("/receipt/<int:id>")
def receipt(id):
    members = get_members()

    if id >= len(members):
        return redirect("/view")

    member = members[id]
    today = datetime.today().strftime("%Y-%m-%d")

    return render_template("receipt.html", member=member, today=today)


# ==============================
# Run App
# ==============================
if __name__ == "__main__":
    app.run(debug=True)
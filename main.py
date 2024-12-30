from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
import random
import os
from dotenv import load_dotenv

load_dotenv()
URI = os.getenv("URI")
SECRET_KEY = os.getenv("SECRET_KEY")

app = Flask(__name__)

##Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["SQLALCHEMY_ECHO"] = True
app.config['SECRET_KEY'] = SECRET_KEY
db = SQLAlchemy(app)



##Cafe TABLE Configuration
class Cafe(db.Model):
    __tablename__ = "cafes"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)


    

## HTTP GET - Read Record
@app.route("/")
def home():
    # print(db.session.query(Cafe).all())
    return render_template("index.html")


@app.route("/random", methods=['GET'])
def get_cafes():
    with app.app_context():
        cafes = db.session.query(Cafe).all()
        random_cafe = random.choice(cafes)
        # Return the cafe as JSON
        return jsonify(cafe={
            "id": random_cafe.id,
            "name": random_cafe.name,
            "map_url": random_cafe.map_url,
            "img_url": random_cafe.img_url,
            "location": random_cafe.location,
            "seats": random_cafe.seats,
            "has_toilet": random_cafe.has_toilet,
            "has_wifi": random_cafe.has_wifi,
            "has_sockets": random_cafe.has_sockets,
            "can_take_calls": random_cafe.can_take_calls,
            "coffee_price": random_cafe.coffee_price,
        })


@app.route("/all")
def get_all_cafes():
    all_cafes = db.session.query(Cafe).all()
    return [
        {
            "id": cafe.id,
            "coffee name": cafe.name,
            "map url": cafe.map_url,
            "img url": cafe.img_url,
            "location": cafe.location,
            "seats": cafe.seats,
            "has toilet": cafe.has_toilet,
            "has wifi": cafe.has_wifi,
            "has sockets": cafe.has_sockets,
            "can take calls": cafe.can_take_calls,
            "coffee price": cafe.coffee_price,
        } for cafe in all_cafes
    ]


@app.route("/search")
def search_cafes():
    if request.args.get("loc"):
        location = request.args.get("loc")
        with app.app_context():
            cafe = db.session.query(Cafe).filter(Cafe.location == location).first()
            if cafe:
                return [
                    {
                        "id": cafe.id,
                        "name": cafe.name,
                        "map_url": cafe.map_url,
                        "img_url": cafe.img_url,
                        "location": cafe.location,
                        "seats": cafe.seats,
                        "has_toilet": cafe.has_toilet,
                        "has_wifi": cafe.has_wifi,
                        "has_sockets": cafe.has_sockets,
                        "can_take_calls": cafe.can_take_calls,
                        "coffee_price": cafe.coffee_price,
                    }
                ]
            else:
                return {
                    "errur": {
                        "not found": "sry not found in database"
                    }
                }
    else:
        return "<h1 style='text-align:center; color:red'> pls enter the (?loc=the_location) after /search </h1>"


## HTTP POST - Create Record

@app.route("/add", methods=["POST"])
def post_new_cafe():
    new_cafe = Cafe(
        name=request.form.get("name"),
        map_url=request.form.get("map_url"),
        img_url=request.form.get("img_url"),
        location=request.form.get("location"),
        has_sockets=bool(request.form.get("sockets")),
        has_toilet=bool(request.form.get("toilet")),
        has_wifi=bool(request.form.get("wifi")),
        can_take_calls=bool(request.form.get("calls")),
        seats=request.form.get("seats"),
        coffee_price=request.form.get("coffee_price"),
    )



    db.session.add(new_cafe)
    db.session.commit()
    return jsonify(response={"success": "Successfully added the new cafe"})


## HTTP PUT/PATCH - Update Record
@app.route("/patch/<int:id>/<new_price>", methods=["PATCH"])
def update_cafe(id, new_price):
    # new_price = request.args.get("new_price")
    cafe = db.session.query(Cafe).filter(Cafe.id == id)
    if cafe:
        cafe.coffee_price = new_price
        cafe.update({"coffee_price": new_price})
        db.session.commit()
        return jsonify(
            response={"success": f"Successfully updated the cafe ith the id {id} and changed price to {new_price} "})
    else:
        return jsonify(response={"error": "Cafe not found"})
    # cafe.update({"coffee_price": new_price})


## HTTP DELETE - Delete Record
@app.route("/delete/<int:id>", methods=["DELETE"])
def delete_cafe(id):
    cafe = db.session.query(Cafe).filter(Cafe.id == id).one_or_none()
    secret_key = "12345678"
    s = request.headers.get("s")
    if cafe and s == secret_key:
        db.session.delete(cafe)
        db.session.commit()
        return jsonify(response={"success": f"Successfully deleted the cafe with id {id}"})
    else:
        # print(s)
        if s == secret_key:
            return jsonify(response={"error": "Cafe not found"})
        else:
            return jsonify(response={"error": "Invalid secret key"})


if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # create table if not exist
    app.run()

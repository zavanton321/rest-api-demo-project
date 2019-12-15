import os

from flask import Flask, url_for, jsonify, request
from flask_sqlalchemy import SQLAlchemy

basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(basedir, "../data.sqlite")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + db_path
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class ValidationError(ValueError):
    pass


class Customer(db.Model):
    __tablename_ = "customers"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True)

    def get_url(self):
        return url_for('get_customer', id=self.id, _external=True)

    def export_data(self):
        return {
            'self_url': self.get_url(),
            'name': self.name
        }

    def import_data(self, data):
        try:
            self.name = data['name']
        except KeyError as e:
            raise ValidationError("Invalid customer: missing " + e.args[0])
        return self


@app.before_first_request
def setup_data():
    db.create_all()
    if Customer.query.filter_by(name="Mike").first() is None:
        customer = Customer(name="Mike")
        db.session.add(customer)
        db.session.commit()


@app.route("/customers/", methods=["GET"])
def get_customers():
    return jsonify(
        {"customers": [
            customer.get_url() for customer in Customer.query.all()
        ]}
    )


@app.route("/customers/<int:id>", methods=["GET"])
def get_customer(id):
    return jsonify(Customer.query.get_or_404(id).export_data())


@app.route("/customers/", methods=["POST"])
def new_customer():
    customer = Customer()
    customer.import_data(request.json)
    db.session.add(customer)
    db.session.commit()
    return jsonify({}), 201, {"Location": customer.get_url()}


@app.route("/customers/<int:id>", methods=["PUT"])
def edit_customer(id):
    customer = Customer.query.get_or_404(id)
    customer.import_data(request.json)
    db.session.add(customer)
    db.session.commit()
    return jsonify({})


@app.route("/")
def home():
    return "home"


if __name__ == "__main__":
    app.run(debug=True)

import os

from flask import Flask, url_for
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
    name = db.Column(db.Integer, index=True)

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


@app.route("/")
def home():
    return "home"


if __name__ == "__main__":
    app.run(debug=True)

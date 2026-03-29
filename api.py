from flask import Flask
from flask_sqlalchemy import SQLAlchemy 
from flask_restful import Resource, Api, reqparse, fields, marshal_with, abort

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///anyname.db'
db = SQLAlchemy(app)
api = Api(app)

class UserModel(db.Model):
    id = db.Column(db.Integer, primary_key=True) 
    name = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(80), unique=True, nullable=False)

    def __repr__(self):
        return f"User(name={self.name}, email={self.email})"   

user_args = reqparse.RequestParser()
user_args.add_argument('Name',type = str, required = True,help = "votre prenom ?")
user_args.add_argument('email',type = str, required = True,help = "votre email ID  ?")

class Users(Resource):
    def get(self):
        users = UserModel.query.all()
        return users
    
api.add_resource(Users, '/api/users/')

@app.route('/')
def home():
    return '<h1>wuzzup</h1>'

if __name__ == '__main__':
    app.run(debug=True)
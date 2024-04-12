from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_restful import Api, Resource, reqparse
from flask_jwt_extended import JWTManager, jwt_required, create_access_token

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///books.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'leo ni Friday'

CORS(app, origins='*')

db = SQLAlchemy(app)
api = Api(app)
jwt = JWTManager(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)

# resources
class UserRegistrationResource(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('username', type=str)
        parser.add_argument('password', type=str)
        data = parser.parse_args()

        user = User.query.filter_by(username=data.get('username')).first()

        if user:
            return {'message': "User Already Exists"}, 400
        
        new_user = User(username=data.get('username'), password=data.get('password'))

        db.session.add(new_user)
        db.session.commit()

        # create authentication for new user
        access_token = create_access_token(identity=new_user.id)

        return {
            'message': "User Registration Success",
            'access_token': access_token
        }, 201
    
class UserLoginResource(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('username', type=str)
        parser.add_argument('password', type=str)
        data = parser.parse_args()

        user = User(username=data.get('username'), password=data.get('password'))

        if user:
            if user.password == data.get('password'):
                access_token = create_access_token(identity=user.id)
                return {
                    'message': "User Login Success",
                    'access_token': access_token
                }, 200
            else:
                return {'error': "Invalid Password"}, 400
        else:
            return {'error': "Invalid Username"}, 400
        
class UserResource(Resource):
    @jwt_required()
    def get(self):
        response = {'message': "Welcome to User Resource (Need Authentication to access this)"}

        return response, 200
    

# routes
api.add_resource(UserRegistrationResource, '/register')
api.add_resource(UserLoginResource, '/login')
api.add_resource(UserResource, '/users')


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(port='8080', debug=True)
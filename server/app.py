# Remote library imports
from flask import Flask, request, make_response, session, abort, jsonify
from flask_restful import Resource
from werkzeug.exceptions import NotFound, Unauthorized
import json
import traceback



# Local imports
from config import app, api, db
from models import User, Resort, Comment

class Users(Resource):
    def post(self):
        form_json = request.get_json()
        new_user = User(
            name = form_json['name'],
            email = form_json['email']
        )
        db.session.add(new_user)
        db.session.commit()
        session['user.id'] = new_user.id
        # import ipdb; ipdb.set_trace()
        response = make_response(
            new_user.to_dict(),
            201
        )

class Logout(Resource):
    def delete(self):
        session['user_id'] = None
        response = make_response('',204)
        return response
api.add_resource(Logout, '/logout')


class AuthorizedSession(Resource):
    def get(self):
        if session.get('user_id'):
            user = User.query.filter(User.id == session['user_id']).first()
            return make_response(user.to_dict(), 200)
        else:
            return {'message': '401: Not Authorized'}, 401

api.add_resource(AuthorizedSession, '/authorized')

class Login(Resource):
    def post(self):
        data = request.get_json()
        username = data.get('name')
        password = data.get('password')
        user = User.query.filter_by(name=username).first()
        if user:
            if user.authenticate(password):
                session["user_id"] = user.id
                user_dict = user.to_dict() 
                response = make_response(user_dict, 200)
                return response
        response = make_response({'error': 'unauthorized'}, 401)
        return response



api.add_resource(Login, '/login')

class Signup (Resource):
    def post(self):
        form_json = request.get_json()
        new_user = User (name=form_json ['name'], email=form_json['email'])
        new_user.password_hash = form_json ['password']
        db.session.add(new_user)
        db.session.commit()
        session['user_id'] = new_user.id
        response = make_response(
            new_user.to_dict(),
            201
        )
        return response

api.add_resource(Signup, '/signup')


class SkiResorts(Resource):
    def get(self):
        resorts = Resort.query.all()
        resort_list = []
        for resort in resorts:
            resort_dict = {
                'id': resort.id,
                'name': resort.name,
                'location_region': resort.location_region,
                'location_state': resort.location_state
            }
            resort_list.append(resort_dict)
        return resort_list, 200

api.add_resource(SkiResorts, '/skiresorts')

class GetCommentsForUser(Resource):
    def get(self, user_id):
        comments = Comment.query.filter_by(user_id=user_id).all()
        return jsonify({'comments': [comment.to_dict() for comment in comments]})

api.add_resource(GetCommentsForUser, '/user-comments/<int:user_id>')

class NewComment(Resource):
    def post(self):
        try:
            data = request.get_json()

            # query for the resort with the given name
            resort = Resort.query.filter_by(name=data['resort']).first()

            # create the comment with the resort and user instances
            comment = Comment(comment=data['comment'], user_id=data['user_id'], resort=resort)
            db.session.add(comment)
            db.session.commit()

            return make_response(comment.to_dict(), 201)
        except Exception as e:
            traceback.print_exc()
            return make_response({'error': str(e)}, 500)


api.add_resource(NewComment, '/comments')

if __name__ == '__main__':
    app.run(port=5555)


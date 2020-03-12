from . import api
from .. import models, schemas, generics, db, jwt, mail

import uuid
from flask_mail import Message
from flask import request, abort, current_app
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity, get_raw_jwt, get_jti


blacklist = set()
@jwt.token_in_blacklist_loader
def check_if_token_in_blacklist(decrypted_token):
    jti = decrypted_token['jti']
    return jti in blacklist


class UserRegisterAPIController(generics.CreateAPIView):
    model = models.User
    schema_class = schemas.UserSchema
    unique_fields = ('email', )
    access_token = None

    def create (self, *args, **kwargs):
        (response, code)  = super().create(self, *args, **kwargs)
        return {**response, "access_token": self.access_token }, code


    def perform_create(self, instance):
        super().perform_create(instance)
        self.access_token = create_access_token(identity=instance.pk)
        settings = models.Setting(user_pk=instance.pk, color="red", fontsize="15px", linewidth=15)
        db.session.add(settings)
        db.session.commit()


class UserResetPasswordAPIController(generics.MethodView):
    methods = ['POST']
    message_txt = """Hello {}!

Your new password is {}

Best Regards,
Latech Team.
"""

    def post(self, *args, **kwargs):
        user = models.User.query.filter_by(email=kwargs.get("email")).one_or_none()
        if user:
            plain_password = str(uuid.uuid4())[:8]
            user.password = plain_password
            db.session.commit()
            message = Message(subject="Reset Password", sender=current_app.config['FLASK_MAIL_SENDER'], recipients=[user.email])
            message.body = self.message_txt.format(user.fullname, plain_password)
            mail.send(message=message)

        return { "Success": "Your new password has been sent to your mail." }, 200


class UserLogoutAPIController(generics.MethodView):
    methods = ['DELETE']
    decorators = [jwt_required]

    def delete(self, *args, **kwargs):
        jti = get_raw_jwt()['jti']
        blacklist.add(jti)
        return {"Logout": "Successfully logged out"}, 200


class UserLoginAPIController(generics.MethodView):
    methods = ['POST']

    def post(self, *args, **kwargs):
        email = request.json.get('email', None)
        password = request.json.get('password', None)

        current_user = models.User.query.filter_by(email=email).first() if password or email else None
        if current_user is not None and current_user.check_password(password):
            data = schemas.UserSchema(many=False).dump(current_user)
            return {**data ,'access_token': create_access_token(identity=current_user.pk)}, 200
        return abort(400, {'Oops': 'Invalid email or password.'})


api.add_url_rule('/auth/login', view_func=UserLoginAPIController.as_view('user_login_api'), methods=UserLoginAPIController.methods)
api.add_url_rule('/auth/register', view_func=UserRegisterAPIController.as_view('user_register_api'), methods=UserRegisterAPIController.methods)
api.add_url_rule('/auth/logout', view_func=UserLogoutAPIController.as_view('user_logout_api'), methods=UserLogoutAPIController.methods)
api.add_url_rule('/auth/reset/<string:email>', view_func=UserResetPasswordAPIController.as_view('user_rest_api'), methods=UserResetPasswordAPIController.methods)

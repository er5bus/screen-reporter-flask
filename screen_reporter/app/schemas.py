from . import ma, models
from marshmallow import validates_schema, ValidationError, INCLUDE, EXCLUDE
from marshmallow.validate import Length, Range


class Base(ma.ModelSchema):
    pk = ma.Int(data_key='id')


class UserSchema(Base):
    fullname = ma.String(max_length=200, required=True, validate=Length(max=200, min=1))
    email = ma.String(max_length=128, required=True, validate=Length(max=128, min=1))
    password = ma.String(max_length=128, required=False, load_only=True)
    current_password = ma.String(max_length=128, required=False, load_only=True, validate=Length(max=128, min=4))

    @validates_schema
    def validate_password(self, data, **kwargs):
        if data.get('password', None) and (len(data['password']) < 4 or len(data['password']) > 128):
            raise ValidationError('Password must be more than 4 characters', 'password')

    class Meta:
        model = models.User
        unknown = INCLUDE
        exclude = ("_UserMixin__hashed_password", )


class IntegrationSchema(Base):
    provider = ma.String(max_length=1000, required=True, validate=Length(max=1000, min=1))
    api_key = ma.String(max_length=1000, required=True, validate=Length(max=1000, min=1))
    active = ma.Boolean(required=False)

    class Meta:
        model = models.Integration
        unknown = INCLUDE


class SettingSchema(Base):
    color = ma.String(max_length=20, required=False, validate=Length(max=20, min=1))
    fontsize = ma.String(max_length=5, required=False, validate=Length(max=5, min=1))
    linewidth = ma.Int(required=False, validate=Range(max=20, min=1))

    class Meta:
        model = models.Setting
        unknown = INCLUDE


class TrelloCardSchema(ma.Schema):
    name = ma.String(data_key="name", required=True, validate=Length(max=100, min=1))
    desc = ma.String(data_key="description", required=True, validate=Length(max=500, min=1))
    board_id = ma.String(data_key="board", required=True, validate=Length(max=100, min=1))
    board_list_id = ma.String(data_key="list", required=True, validate=Length(max=100, min=1))
    attachment = ma.String(required=True)
    labels = ma.List(ma.String(), required=False)
    members = ma.List(ma.String(), required=False)

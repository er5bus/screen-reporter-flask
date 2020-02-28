from ... import schemas, models, generics, db
from .. import api
from marshmallow.exceptions import ValidationError
from flask import current_app, request, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from trello import TrelloClient
from collections import namedtuple


class TrelloBoardAPIView(generics.MethodView):
    methods = ['GET']
    decorators = [jwt_required]
    boardSchema = schemas.TrelloBoardSchema(many=True)

    def get(self, *args, **kwargs):
        currentIntegration = models.Integration.query.filter_by(user_pk=get_jwt_identity(), active=True).one_or_none()
        if currentIntegration:
            trello = TrelloClient(api_key=current_app.config['TRELLO_APP_KEY'], api_secret=currentIntegration.api_key)
            data = trello.list_boards()
            return self.boardSchema.dumps(data), 200
        return abort(400, {'Oops': 'Invalid Trello integration.'})


class TrelloMembersAPIView(generics.MethodView):
    methods = ['GET']
    decorators = [jwt_required]
    memberSchema = schemas.TrelloMemberSchema(many=True)

    def get(self, *args, **kwargs):
        currentIntegration = models.Integration.query.filter_by(user_pk=get_jwt_identity(), active=True).one_or_none()
        if currentIntegration:
            trello = TrelloClient(api_key=current_app.config['TRELLO_APP_KEY'], api_secret=currentIntegration.api_key)
            data = trello.get_board(kwargs.get('board_id', None)).all_members()
            return self.memberSchema.dumps(data), 200
        return abort(400, {'Oops': 'Invalid Trello integration.'})


class TrelloLabelAPIView(generics.MethodView):
    methods = ['GET']
    decorators = [jwt_required]
    labelSchema = schemas.TrelloLabelSchema(many=True)

    def get(self, *args, **kwargs):
        currentIntegration = models.Integration.query.filter_by(user_pk=get_jwt_identity(), active=True).one_or_none()
        if currentIntegration:
            trello = TrelloClient(api_key=current_app.config['TRELLO_APP_KEY'], api_secret=currentIntegration.api_key)
            data = trello.get_board(kwargs.get('board_id', None)).get_labels()
            return self.labelSchema.dumps(data), 200
        return abort(400, {'Oops': 'Invalid Trello integration.'})


class TrelloListAPIView(generics.MethodView):
    methods = ['GET']
    decorators = [jwt_required]
    listSchema = schemas.TrelloListSchema(many=True)

    def get(self, *args, **kwargs):
        currentIntegration = models.Integration.query.filter_by(user_pk=get_jwt_identity(), active=True).one_or_none()
        if currentIntegration:
            trello = TrelloClient(api_key=current_app.config['TRELLO_APP_KEY'], api_secret=currentIntegration.api_key)
            data = trello.get_board(kwargs.get('board_id', None)).all_lists()
            return self.listSchema.dumps(data), 200
        return abort(400, {'Oops': 'Invalid Trello integration.'})


class TrelloCreateCardAPIView(generics.MethodView):
    methods = ['POST']
    decorators = [jwt_required]
    cardSchema = schemas.TrelloCardSchema(many=False)

    def get_attachment_file(self, attachment):
        import base64, re
        header, encoded = attachment.split(",", 1)
        image = re.search(r"^data:(\w+)\/(?P<extension>\w+);", header)
        filename = 'screenshot.{}'.format(image.group("extension"))
        data = base64.b64decode(encoded)
        return filename, image.group("extension"), base64.b64decode(encoded)

    def post(self, *args, **kwargs):
        currentIntegration = models.Integration.query.filter_by(user_pk=get_jwt_identity(), active=True).one_or_none()
        if not currentIntegration:
            return abort(400, {'Oops': 'Invalid Trello integration.'})

        try:
            data = self.cardSchema.load(request.json)
        except ValidationError as err:
            abort(400, err.messages)
        else:
            trello = TrelloClient(api_key=current_app.config['TRELLO_APP_KEY'], api_secret=currentIntegration.api_key)
            trello_list = trello.get_board(data.get('board_id')).get_list(data.get('board_list_id'))
            card = trello_list.add_card(name=data.get('name'), desc=data.get('desc'))
            attachment = self.get_attachment_file(data.get('attachment'))
            print(attachment)
            card.attach(name=attachment[0], mimeType=attachment[1], file=attachment[2])
            if data.get('labels', None):
                Label = namedtuple('Label', ['id'])
                for label_id in data.get('labels'):
                    card.add_label(Label(label_id))
            if data.get('members', None):
                Member = namedtuple('Member', ['id'])
                for member_id in data.get('members'):
                    card.add_member(Member(member_id))
            return {'Good Job': 'Your trello card has been created.'}, 200


api.add_url_rule('/trello/boards', view_func=TrelloBoardAPIView.as_view('board_resource'), methods=TrelloBoardAPIView.methods)
api.add_url_rule('/trello/board/<string:board_id>/members', view_func=TrelloMembersAPIView.as_view('member_resource'), methods=TrelloMembersAPIView.methods)
api.add_url_rule('/trello/board/<string:board_id>/lists', view_func=TrelloListAPIView.as_view('list_resource'), methods=TrelloListAPIView.methods)
api.add_url_rule('/trello/board/<string:board_id>/labels', view_func=TrelloLabelAPIView.as_view('label_resource'), methods=TrelloLabelAPIView.methods)
api.add_url_rule('/trello/create-card', view_func=TrelloCreateCardAPIView.as_view('create_card_resource'), methods=TrelloCreateCardAPIView.methods)

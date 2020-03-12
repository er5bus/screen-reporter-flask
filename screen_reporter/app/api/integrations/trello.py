from ... import models, generics, db, schemas
from .. import api
from marshmallow.exceptions import ValidationError
from flask import current_app, request, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from trello import TrelloClient, Member, Label


class TrelloBaseAPIView(generics.MethodView):
    decorators = [jwt_required]

    def get_current_integration(self):
        return models.Integration.query.filter_by(user_pk=get_jwt_identity(), active=True).one_or_none()

    def get_trello_client(self):
        currentIntegration = self.get_current_integration()
        if currentIntegration:
            return TrelloClient(api_key=current_app.config['TRELLO_APP_KEY'], api_secret=currentIntegration.api_key)
        return None


class TrelloBoardAPIView(TrelloBaseAPIView):
    methods = ['GET']

    def dumps(self, data):
        return [ dict(label=item.name, value=item.id) for item in data ]

    def get(self, *args, **kwargs):
        trello = self.get_trello_client()
        if trello:
            try:
                data = trello.list_boards()
            except:
                return abort(401, {'Invalide Trello key': 'We can\'t connect to your trello account'})
            else:
                return {'items': self.dumps(data)}, 200
        return abort(400, {'Oops': 'No active Integration existe.'})


class TrelloMembersAPIView(TrelloBaseAPIView):
    methods = ['GET']

    def dumps(self, data):
        return [ dict(label=item.full_name, value=item.id) for item in data ]

    def get(self, *args, **kwargs):
        trello = self.get_trello_client()
        if trello:
            data = trello.get_board(kwargs.get('board_id', None)).all_members()
            return {'items': self.dumps(data)}, 200
        return abort(400, {'Oops': 'No active Integration existe.'})


class TrelloLabelAPIView(TrelloBaseAPIView):
    methods = ['GET']

    def dumps(self, data):
        return [ dict(label=item.color, value=item.id) for item in data ]

    def get(self, *args, **kwargs):
        trello = self.get_trello_client()
        if trello:
            data = trello.get_board(kwargs.get('board_id', None)).get_labels()
            return {'items': self.dumps(data)}, 200
        return abort(400, {'Oops': 'No active Integration existe.'})


class TrelloListAPIView(TrelloBaseAPIView):
    methods = ['GET']

    def dumps(self, data):
        return [ dict(label=item.name, value=item.id) for item in data ]

    def get(self, *args, **kwargs):
        trello = self.get_trello_client()
        if trello:
            data = trello.get_board(kwargs.get('board_id', None)).all_lists()
            return {'items': self.dumps(data)}, 200
        return abort(400, {'Oops': 'No active Integration existe.'})


class TrelloCreateCardAPIView(TrelloBaseAPIView):
    methods = ['POST']
    cardSchema = schemas.TrelloCardSchema()

    def _get_attachment_file(self, attachment):
        import base64, re
        header, encoded = attachment.split(",", 1)
        image = re.search(r"^data:(\w+)\/(?P<extension>\w+);", header)
        filename = 'screenshot.{}'.format(image.group("extension"))
        data = base64.b64decode(encoded)
        return filename, image.group("extension"), base64.b64decode(encoded)

    def _create_card(self, data):
        trello_client = self.get_trello_client()
        trello_list = trello_client.get_board(data.get('board_id')).get_list(data.get('board_list_id'))
        card = trello_list.add_card(name=data.get('name'), desc=data.get('desc'))
        (filename, mime_type, file_content) = self._get_attachment_file(data.get('attachment'))
        card.attach(name=filename, mimeType=mime_type, file=file_content)

        for member_id in data.get('members', tuple()):
            member_id and card.add_member(Member(trello_client, member_id))

        for label_id in data.get('labels', tuple()):
            label_id and card.add_label(Label(trello_client, label_id, ""))

        return card

    def post(self, *args, **kwargs):
        currentIntegration = models.Integration.query.filter_by(user_pk=get_jwt_identity(), active=True).one_or_none()
        if currentIntegration:
            try:
                data = self.cardSchema.load(request.json)
            except ValidationError as err:
                abort(400, err.messages)
            else:
                card = self._create_card(data)
                return {'Good Job': 'Your trello card has been created.'}, 200
        return abort(400, {'Oops': 'No active Integration existe.'})


api.add_url_rule('/trello/boards', view_func=TrelloBoardAPIView.as_view('board_resource'), methods=TrelloBoardAPIView.methods)
api.add_url_rule('/trello/board/<string:board_id>/members', view_func=TrelloMembersAPIView.as_view('member_resource'), methods=TrelloMembersAPIView.methods)
api.add_url_rule('/trello/board/<string:board_id>/lists', view_func=TrelloListAPIView.as_view('list_resource'), methods=TrelloListAPIView.methods)
api.add_url_rule('/trello/board/<string:board_id>/labels', view_func=TrelloLabelAPIView.as_view('label_resource'), methods=TrelloLabelAPIView.methods)
api.add_url_rule('/trello/create-card', view_func=TrelloCreateCardAPIView.as_view('create_card_resource'), methods=TrelloCreateCardAPIView.methods)

from .. import schemas, models, generics
from . import api


class CardCollectionAPI(generics.ListCreateAPIView):
    model = models.Card
    schema_class = schemas.CardSchema


class CardDocumentAPI(generics.RetrieveUpdateAPIView):
    model = models.Card
    schema_class = schemas.CardSchema
    lookup_url_kwarg = 'pk'


api.add_url_rule('/cards', view_func=CardCollectionAPI.as_view('card_collection_resource'), methods=CardCollectionAPI.methods)
api.add_url_rule('/cards/<int:pk>', view_func=CardDocumentAPI.as_view('card_document_resource'), methods=CardDocumentAPI.methods)

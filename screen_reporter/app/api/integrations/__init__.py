from ... import schemas, models, generics, db
from .. import api
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import update


class IntegrationCollectionAPI(generics.ListCreateAPIView):
    decorators = [jwt_required]
    model = models.Integration
    schema_class = schemas.IntegrationSchema
    unique_fields = ('api_key', )

    def perform_create(self, instance):
        user_pk = get_jwt_identity()
        for integration in models.Integration.query.filter_by(user_pk=user_pk, active=True).all():
            integration.active = False
        instance.user_pk = user_pk
        instance.active = True
        super().perform_create(instance)

    def get_object_query(self, **kwargs):
        kwargs = { **kwargs, 'user_pk': get_jwt_identity() }
        return super().get_object_query(**kwargs)


class IntegrationDocumentAPI(generics.RetrieveUpdateDestroyAPIView):
    decorators = [jwt_required]
    model = models.Integration
    schema_class = schemas.IntegrationSchema
    lookup_url_kwarg = 'pk'
    unique_fields = ('api_key', )

    def get_object_query(self, **kwargs):
        kwargs = { **kwargs, 'user_pk': get_jwt_identity() }
        return super().get_object_query(**kwargs)

    def perform_update(self, instance):
        for integration in models.Integration.query.filter_by(user_pk=get_jwt_identity(), active=True).all():
            integration.active = False
        instance.active = True
        super().perform_update(instance)


api.add_url_rule('/integrations', view_func=IntegrationCollectionAPI.as_view('integration_collection_resource'), methods=IntegrationCollectionAPI.methods)
api.add_url_rule('/integration/<int:pk>', view_func=IntegrationDocumentAPI.as_view('integration_document_resource'), methods=IntegrationDocumentAPI.methods)


from . import trello

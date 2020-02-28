from .. import schemas, db, models, generics
from . import api
from flask import abort


class UserCollectionAPI(generics.ListCreateAPIView):
    model = models.User
    schema_class = schemas.UserSchema


class UserDocumentAPI(generics.RetrieveUpdateAPIView):
    model = models.User
    schema_class = schemas.UserSchema
    lookup_url_kwarg = 'pk'
    unique_fields = ('email', )

    def perform_update(self, old_instance, instance_updated):
        if not old_instance.check_password(instance_updated.current_password):
            abort(400, {'Password': 'Password does not match the old one.'})
        super().perform_update(old_instance, instance_updated)



api.add_url_rule('/users', view_func=UserCollectionAPI.as_view('user_collection_resource'), methods=UserCollectionAPI.methods)
api.add_url_rule('/user/<int:pk>', view_func=UserDocumentAPI.as_view('user_document_resource'), methods=UserDocumentAPI.methods)

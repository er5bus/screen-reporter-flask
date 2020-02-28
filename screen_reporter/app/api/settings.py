from .. import schemas, models, generics
from . import api
from flask_jwt_extended import jwt_required, get_jwt_identity


class SettingsDocumentAPI(generics.RetrieveUpdateAPIView):
    decorators = [jwt_required]
    model = models.Setting
    schema_class = schemas.SettingSchema

    def get_object(self, **kwargs):
        kwargs = { **kwargs, 'user_pk': get_jwt_identity() }
        return super().get_object(**kwargs)


api.add_url_rule('/settings', view_func=SettingsDocumentAPI.as_view('setting_document_resource'), methods=SettingsDocumentAPI.methods)

from flask import Response, request, abort
from marshmallow.exceptions import ValidationError
from . import db
from urllib import parse
from copy import deepcopy


class BaseMethodMixin:
    """
    Base API methods
    """

    model = None
    schema_class = None

    lookup_field = 'pk'
    lookup_url_kwarg = None

    unique_fields = None

    methods = None

    def get_query(self, **kwargs):
        if kwargs:
            query = self.model.query
            for field, value in kwargs.items():
                query = query.filter( getattr(self.model, field) == value)
            return query
        return self.model.query

    def get_object_query(self, **kwargs):
        if kwargs.get(self.lookup_url_kwarg, None) is not None:
            filter_kwargs = { self.lookup_field: kwargs.get(self.lookup_url_kwarg) }
            return self.get_query(**{**kwargs, **filter_kwargs})
        return self.get_query(**kwargs)

    def get_object(self, **kwargs):
        instance = self.get_object_query(**kwargs).one_or_none()
        if instance is None:
            abort(404)
        return instance

    def paginate_query(self, **kwargs):
        page = request.args.get('page', type=int, default=1)
        item_per_page = request.args.get('item_per_page', type=int, default=10)
        return self.get_object_query(**kwargs).paginate(page, item_per_page, error_out=False)

    def serialize(self, data = [], many=False):
        serializer = self.schema_class(many=many, unknown='EXCLUDE')
        return serializer.dump(data)

    def deserialize(self, data = [], params = [], instance=None, partial=False):
        serializer = self.schema_class()
        try:
            new_instance = serializer.load(data, instance=instance, unknown='INCLUDE', partial=partial)
            if self.unique_fields:
                errors = {}
                with db.session.no_autoflush:
                    for unique_field in self.unique_fields:
                        unique_object = self.get_query(**{ unique_field: getattr(new_instance, unique_field) }).one_or_none()
                        if (unique_object is not None and instance is None) or \
                            ( unique_object is not None and getattr(unique_object, self.lookup_field) != getattr(instance, self.lookup_field)):
                            errors[unique_field] = "{} already exist.".format(unique_field)
                if errors:
                    raise ValidationError(errors)
            return new_instance
        except ValidationError as err:
            self.raise_exception(err)
    def raise_exception(self, errors):
        abort(400, errors.messages)


class ListMixin(BaseMethodMixin):
    """
    List model objects.
    """

    def list (self, *args, **kwargs):
        paginator = self.paginate_query(**kwargs)
        url = request.url_rule.rule + '?'
        next_url = url + parse.urlencode({'page': paginator.page + 1}) if paginator.has_next else None
        previous_url = url + parse.urlencode({'page': paginator.page - 1}) if paginator.has_prev else None
        return dict(items=self.serialize(paginator.items, True), has_more=paginator.has_next, next=next_url, previous=previous_url), 200


class RetrieveMixin(BaseMethodMixin):
    """
    Retrieve a model instance
    """

    def retrieve (self, *args, **kwargs):
        instance = self.get_object(**kwargs)
        return self.serialize(instance), 200


class CreateMixin(BaseMethodMixin):
    """
    Create a model instance
    """
    def create (self, *args, **kwargs):
        instance = self.deserialize(request.json)
        self.perform_create(instance)
        return self.serialize(instance), 201

    def perform_create(self, instance):
        db.session.add(instance)
        db.session.commit()


class UpdateMixin(BaseMethodMixin):
    """
    Update model instance
    """
    def update (self, *args, **kwargs):
        with db.session.no_autoflush:
            instance = self.get_object(**kwargs)
            old_instance = deepcopy(instance)
            instance_updated = self.deserialize(request.json, instance=instance ,partial=False)
            self.perform_update(old_instance, instance_updated)

        return self.serialize(instance_updated), 200

    def partial_update (self, *args, **kwargs):
        instance = self.get_object(**kwargs)
        old_instance = deepcopy(instance)
        instance_updated = self.deserialize(request.json, instance=instance, partial=True)
        self.perform_update(old_instance, instance_updated)

        return self.serialize(instance_updated), 200


    def perform_update(self, old_instance, instance_updated):
        db.session.add(instance_updated)
        db.session.commit()


class DeleteMinxin(BaseMethodMixin):
    """
    Delete model instance
    """
    def destroy (self, *args, **kwargs):
        object_query = self.get_object_query(**kwargs)
        self.perform_delete(object_query)

        return Response(status=204)

    def perform_delete(self, object_query):
        object_query.delete()
        db.session.commit()


class OptionsMixin:
    """
    CORS Preflight Mixin
    """
    access_control_allowed_headers = 'Content-Type, Authorization, X-Requested-With'
    access_control_max_age = 120
    access_control_allowed_credentials = False
    access_control_exposed_headers = '*'

    def cors_preflight (self, *args, **kwargs):
        headers = {
            'Access-Control-Allow-Headers' : self.access_control_allowed_headers,
            'Access-Control-Allow-Methods': self.methods,
            'Access-Control-Max-Age': self.access_control_max_age,
            'Access-Control-Allow-Credentials': self.access_control_allowed_credentials,
            'Access-Control-Expose-Headers': self.access_control_exposed_headers,
            'Vary': 'Origin'  # in case of server cache the response and the origin is not a wild card
        }
        return Response(status=204, headers=headers)

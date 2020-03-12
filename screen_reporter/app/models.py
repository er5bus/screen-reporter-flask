from .behaviors import db, Base, UserMixin, TimestampMixin


class User(Base, UserMixin, TimestampMixin):
    fullname = db.Column(db.String(200))


class Setting(Base):
    color = db.Column(db.String(20))
    fontsize = db.Column(db.String(5))
    linewidth = db.Column(db.Integer)
    user_pk = db.Column(db.Integer, db.ForeignKey(User.__tablepk__))


class Integration(Base):
    provider = db.Column(db.Text)
    api_key = db.Column(db.Text)
    active = db.Column(db.Boolean)
    user_pk = db.Column(db.Integer, db.ForeignKey(User.__tablepk__))

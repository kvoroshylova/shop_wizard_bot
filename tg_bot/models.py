from tg_bot import db


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    username = db.Column(db.String(100))
    is_bot = db.Column(db.Boolean, default=False)
    language_code = db.Column(db.String(10))

    def __repr__(self):
        return f"User(id={self.id}, first_name='{self.first_name}', last_name='{self.last_name}', " \
               f"username='{self.username}', telegram_user_id={self.telegram_user_id})"


class ShopList(db.Model):
    __tablename__ = 'shop_lists'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    list_name = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f"ShopList(id={self.id}, user_id={self.id}, list_id={self.list_id})"


class Item(db.Model):
    __tablename__ = 'items'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    list_id = db.Column(db.Integer, db.ForeignKey('shop_lists.id'), nullable=False)

    list = db.relationship('ShopList', backref=db.backref('items', lazy=True))

    def __repr__(self):
        return f"Item(id={self.id}, name='{self.name}', list_id={self.list_id})"


class ContactBook(db.Model):
    __tablename__ = 'contact_book'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    phone_number = db.Column(db.String(20), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    user = db.relationship('User', backref=db.backref('contacts', lazy=True))

    def __repr__(self):
        return f"ContactBook(id={self.id}, first_name='{self.first_name}', last_name='{self.last_name}', " \
               f"phone_number='{self.phone_number}', user_id={self.user_id})"

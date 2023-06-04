import os
from dotenv import load_dotenv
import requests

from tg_bot.models import ShopList, Item, db, User, ContactBook

load_dotenv()


class WeatherServiceException(Exception):
    pass


class ContactBookException(Exception):
    pass


class ShopWizardException(Exception):
    pass


class WeatherService:
    GEO_URL = os.getenv('GEO_URL')
    WEATHER_URL = os.getenv('WEATHER_URL')

    @staticmethod
    def get_geo_data(city_name):
        params = {
            'name': city_name
        }
        res = requests.get(f'{WeatherService.GEO_URL}', params=params)
        if res.status_code != 200:
            raise WeatherServiceException('Cannot get geo data')
        elif not res.json().get('results'):
            raise WeatherServiceException('City not found')
        return res.json().get('results')

    @staticmethod
    def get_current_weather_by_geo_data(lat, lon):
        params = {
            'latitude': lat,
            'longitude': lon,
            'current_weather': True
        }
        res = requests.get(f'{WeatherService.WEATHER_URL}', params=params)
        if res.status_code != 200:
            raise WeatherServiceException('Cannot get geo data')
        return res.json().get('current_weather')

    @staticmethod
    def get_rain_status(city_name):
        geo_data = WeatherService.get_geo_data(city_name)
        if not geo_data:
            raise WeatherServiceException('City not found')
        lat = geo_data[0]['latitude']
        lon = geo_data[0]['longitude']
        weather = WeatherService.get_current_weather_by_geo_data(lat, lon)
        rain_status = weather.get('rain', 'No rain')
        return rain_status


class ShopWizardService:
    @staticmethod
    def create_shop_list(user_id, list_name):
        user = User.query.get(user_id)
        if user:
            shop_list = ShopList(user_id=user_id, list_name=list_name)
            db.session.add(shop_list)
            db.session.commit()
        else:
            raise ShopWizardException(f'User with ID {user_id} not found.')

    @staticmethod
    def remove_shop_list(user_id, list_name):
        user = User.query.get(user_id)
        if user:
            shop_list = ShopList.query.filter_by(user_id=user_id, list_name=list_name).first()
            if shop_list:
                db.session.delete(shop_list)
                db.session.commit()
            else:
                raise ShopWizardException(f'Shop list "{list_name}" not found. Please try other name')
        else:
            raise ShopWizardException(f'User with ID {user_id} not found.')

    @staticmethod
    def edit_shop_list(user_id, old_list_name, new_list_name):
        user = User.query.get(user_id)
        if user:
            shop_list = ShopList.query.filter_by(user_id=user_id, list_name=old_list_name).first()
            if shop_list:
                shop_list.list_name = new_list_name
                db.session.commit()
            else:
                raise ShopWizardException(f'Shop list "{old_list_name}" not found. Please try other name')
        else:
            raise ShopWizardException(f'User with ID {user_id} not found.')

    @staticmethod
    def add_item_to_list(user_id, list_name, item):
        user = User.query.get(user_id)
        if user:
            shop_list = ShopList.query.filter_by(user_id=user_id, list_name=list_name).first()
            if shop_list:
                new_item = Item(name=item, list=shop_list)
                db.session.add(new_item)
                db.session.commit()
            else:
                raise ShopWizardException(f'Shop list "{list_name}" not found. Please try other name')
        else:
            raise ShopWizardException(f'User with ID {user_id} not found.')

    @staticmethod
    def show_list_items(user_id, list_name):
        user = User.query.get(user_id)
        if user:
            shop_list = ShopList.query.filter_by(user_id=user_id, list_name=list_name).first()
            if shop_list:
                items = Item.query.filter_by(list=shop_list).all()
                return [item.name for item in items]
            else:
                raise ShopWizardException(f'Shop list "{list_name}" not found. Please try other name.')
        else:
            raise ShopWizardException(f'User with ID {user_id} not found.')

    @staticmethod
    def remove_item_from_list(user_id, list_name, item):
        user = User.query.get(user_id)
        if user:
            shop_list = ShopList.query.filter_by(user_id=user_id, list_name=list_name).first()
            if shop_list:
                item_to_remove = Item.query.filter_by(list=shop_list, name=item).first()
                if item_to_remove:
                    db.session.delete(item_to_remove)
                    db.session.commit()
                else:
                    raise ShopWizardException(f'Item "{item}" not found in the list "{list_name}". '
                                              f'Please try other name')
            else:
                raise ShopWizardException(f'Shop list "{list_name}" not found. Please try other name')
        else:
            raise ShopWizardException(f'User with ID {user_id} not found.')

    @staticmethod
    def remove_items_from_list(user_id, list_name):
        user = User.query.get(user_id)
        if user:
            shop_list = ShopList.query.filter_by(user_id=user_id, list_name=list_name).first()
            if shop_list:
                items_to_remove = Item.query.filter_by(list=shop_list).all()
                for item in items_to_remove:
                    db.session.delete(item)
                db.session.commit()
            else:
                raise ShopWizardException(f'Shop list "{list_name}" not found. Please try other name')
        else:
            raise ShopWizardException(f'User with ID {user_id} not found.')


class ContactBookService:
    @staticmethod
    def status(user_id):
        user = User.query.get(user_id)
        if user:
            contact_count = ContactBook.query.filter_by(user_id=user_id).count()
            return contact_count
        else:
            raise ContactBookException(f'User with ID {user_id} not found.')

    @staticmethod
    def list(user_id):
        user = User.query.get(user_id)
        if user:
            contacts = ContactBook.query.filter_by(user_id=user_id).all()
            contact_list = '\n'.join(
                [f"{i + 1}. {contact.first_name} {contact.last_name}" for i, contact in enumerate(contacts)])
            return contact_list
        else:
            raise ContactBookException(f'User with ID {user_id} not found.')

    @staticmethod
    def show(user_id, contact_name, last_name):
        user = User.query.get(user_id)
        if user:
            contact = ContactBook.query.filter_by(user_id=user_id, first_name=contact_name, last_name=last_name).first()
            if contact:
                return contact  # Return the contact object
            else:
                raise ContactBookException(f'Contact "{contact_name}" not found.')
        else:
            raise ContactBookException(f'User with ID {user_id} not found.')

    @staticmethod
    def delete(user_id, contact_name, last_name):
        user = User.query.get(user_id)
        if user:
            contact = ContactBook.query.filter_by(user_id=user_id, first_name=contact_name, last_name=last_name).first()
            if contact:
                db.session.delete(contact)
                db.session.commit()
                return f"Contact '{contact_name}' has been deleted."
            else:
                raise ContactBookException(f'Contact "{contact_name}" not found in your contact book.')
        else:
            raise ContactBookException(f'User with ID {user_id} not found.')

    @staticmethod
    def add(user_id, first_name, last_name, phone_number):
        user = User.query.get(user_id)
        if user:
            contact = ContactBook.query.filter_by(user_id=user_id, first_name=first_name, last_name=last_name).first()
            if contact:
                raise ContactBookException(f'Contact "{first_name}" already exists in your contact book.')
            else:
                new_contact = ContactBook(first_name=first_name,
                                          last_name=last_name,
                                          phone_number=phone_number,
                                          user=user)
                db.session.add(new_contact)
                db.session.commit()
                return f"Contact '{first_name}' has been added to your contact book."
        else:
            raise ContactBookException(f'User with ID {user_id} not found.')

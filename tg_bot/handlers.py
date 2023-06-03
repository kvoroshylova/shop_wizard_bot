import requests
from tg_bot import db
from .models import User
from dotenv import load_dotenv
import os

from .services import WeatherService, WeatherServiceException, ShopWizardService, ContactBookService, ContactBookException, ShopWizardException
import json

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
TG_BASE_URL = os.getenv('TG_BASE_URL')

WEATHER_TYPE = '/weather'


class TelegramHandler:
    user = None

    def __init__(self, user_id):
        self.user_id = user_id
        self.user = User.query.get(user_id)

    def send_markup_message(self, text, markup):
        data = {
            'chat_id': self.user.id,
            'text': text,
            'reply_markup': markup
        }
        requests.post(f'{TG_BASE_URL}{BOT_TOKEN}/sendMessage', json=data)

    def send_message(self, text):
        data = {
            'chat_id': self.user.id,
            'text': text
        }
        requests.post(f'{TG_BASE_URL}{BOT_TOKEN}/sendMessage', json=data)

    @staticmethod
    def set_suggestions(commands):
        data = {
            'commands': commands
        }
        requests.post(f'{TG_BASE_URL}{BOT_TOKEN}/setMyCommands', json=data)


class MessageHandler(TelegramHandler):
    def __init__(self, data):
        super().__init__(data['from']['id'])
        self.user = User(**data['from'])
        self.text = data.get('text')
        self.city = None

        user = User.query.filter_by(id=self.user_id).first()
        if not user:
            # Create a new User instance and save it to the database
            new_user = User(id=self.user_id)
            db.session.add(new_user)
            db.session.commit()

    def handle(self):
        text_parts = self.text.split()
        if len(text_parts) > 1 and text_parts[0] == '/weather':
            self.city = ' '.join(text_parts[1:])

        if self.text == '/start':
            welcome_message = "Welcome to the Shop Wizard Bot, where you can effortlessly create, edit, and remove " \
                              "lists and items. Explore the convenience of managing your shopping essentials with " \
                              "ease. Additionally, unlock the functionality to create your very own contact book and " \
                              "stay informed about the weather in your city. To get started enter '/commands'."
            self.send_message(welcome_message)
        elif text_parts[0] == '/commands':
            commands_message = '''Hello! This is the help center of Shop Wizard Bot. Here you can see how to use commands:

        /commands - See all available commands
        Show List Commands:
            /create_list - Create a new shopping list. Usage: /create_list <list_name>
            /remove_list - Remove an existing shopping list. Usage: /remove_list <list_name>
            /edit_list - Rename a shopping list. Usage: /edit_list <old_list_name> <new_list_name>
            /add_item - Add an item to a shopping list. Usage: /add_item <list_name> <item>
            /show_items - Show items in a shopping list. Usage: /show_items <list_name>
            /remove_item - Remove an item from a shopping list. Usage: /remove_item <list_name> <item>

        Weather Commands:
            /weather - Get the weather for a city. Usage: /weather <your_city>

        Contact Book Commands:
            /add - Add a new contact to your contact book. Usage: /add <first_name> <last_name> <contact_phone>
            /status - Show amount of contacts in your contact book. Usage: /status
            /show - Show the contact from your contact book. Usage: /show <contact_name>
            /list - Show the list of all your contacts. Usage: /list
            /delete - Delete a contact from a contact book. Usage: /delete <contact_name>

        Replace <list_name>, <item>, <your_city>, <contact_name> with the actual names you want to use.'''
            self.send_message(commands_message)

        # ShopWizardService operations
        elif text_parts[0] == '/create_list':
            try:
                list_name = text_parts[1]
                ShopWizardService.create_shop_list(self.user_id, list_name)
                self.send_message(f'Shop list "{list_name}" created successfully!')
            except ShopWizardException as e:
                self.send_message(str(e))
        elif text_parts[0] == '/remove_list':
            try:
                list_name = text_parts[1]

                # Remove the items from the 'item' table
                ShopWizardService.remove_items_from_list(self.user_id, list_name)

                # Remove the shop list from the 'shop_lists' table
                ShopWizardService.remove_shop_list(self.user_id, list_name)

                self.send_message(f'Shop list "{list_name}" and its items removed successfully!')
            except ShopWizardException as e:
                self.send_message(str(e))
        elif text_parts[0] == '/edit_list':
            try:
                old_list_name = text_parts[1]
                new_list_name = text_parts[2]
                ShopWizardService.edit_shop_list(self.user_id, old_list_name, new_list_name)
                self.send_message(f'Shop list "{old_list_name}" renamed to "{new_list_name}" successfully!')
            except ShopWizardException as e:
                self.send_message(str(e))
        elif text_parts[0] == '/add_item':
            try:
                list_name = text_parts[1]
                item = ' '.join(text_parts[2:])
                ShopWizardService.add_item_to_list(self.user_id, list_name, item)
                self.send_message(f'Item "{item}" added to list "{list_name}" successfully!')
            except ShopWizardException as e:
                self.send_message(str(e))
        elif text_parts[0] == '/show_items':
            try:
                list_name = text_parts[1]
                items = ShopWizardService.show_list_items(self.user_id, list_name)
                if items:
                    item_list = "\n- ".join(items)
                    self.send_message(f'Items in list "{list_name}":\n- {item_list}')
                else:
                    self.send_message(f'List "{list_name}" is empty.')
            except ShopWizardException as e:
                self.send_message(str(e))
        elif text_parts[0] == '/remove_item':
            try:
                list_name = text_parts[1]
                item = ' '.join(text_parts[2:])
                ShopWizardService.remove_item_from_list(self.user_id, list_name, item)
                self.send_message(f'Item "{item}" removed from list "{list_name}" successfully!')
            except ShopWizardException as e:
                self.send_message(str(e))

        # ContactBookService commands
        elif text_parts[0] == '/add' and len(text_parts) >= 4:
            try:
                first_name = text_parts[1]
                last_name = text_parts[2]
                phone_number = text_parts[3]
                ContactBookService.add(self.user_id, first_name, last_name, phone_number)
                self.send_message(f'Contact "{first_name}" added successfully!')
            except ContactBookException as e:
                self.send_message(str(e))
        elif text_parts[0] == '/delete':
            try:
                contact_name = ' '.join(text_parts[1:])
                ContactBookService.delete(self.user_id, contact_name)
                self.send_message(f'Contact "{contact_name}" deleted successfully!')
            except ContactBookException as e:
                self.send_message(str(e))
        elif text_parts[0] == '/status':
            try:
                count = ContactBookService.status(self.user_id)
                self.send_message(f'You have {count} contact{"s" if count != 1 else ""} in your contact book.')
            except ContactBookException as e:
                self.send_message(str(e))
        elif text_parts[0] == '/list':
            try:
                contacts = ContactBookService.list(self.user_id)
                if contacts:
                    self.send_message(f'Your contacts:\n{contacts}')
                else:
                    self.send_message('Your contact book is empty.')
            except ContactBookException as e:
                self.send_message(str(e))
        elif text_parts[0] == '/show' and len(text_parts) > 1:
            try:
                contact_name = ' '.join(text_parts[1:])
                contact = ContactBookService.show(self.user_id, contact_name)
                if contact:
                    contact_info = f'Information about {contact.name}:\nName - {contact.name}, ' \
                                   f'Phone number - {contact.phone_number}'
                    self.send_message(contact_info)
                else:
                    self.send_message(f'Contact "{contact_name}" not found.')
            except ContactBookException as e:
                self.send_message(str(e))
        # WeatherService commands
        elif WEATHER_TYPE == text_parts[0] or self.city in text_parts:
            try:
                geo_data = WeatherService.get_geo_data(self.city)
                buttons = []
                for item in geo_data:
                    test_button = {
                        'text': f'{item.get("name")} - {item.get("country_code")}',
                        'callback_data': json.dumps({
                            'type': WEATHER_TYPE, 'lat': item.get('latitude'), 'lon': item.get('longitude')})
                    }
                    buttons.append([test_button])
                markup = {
                    'inline_keyboard': buttons
                }
                self.send_markup_message(f'Choose a city from the list:', markup)
            except WeatherServiceException as wse:
                self.send_message(str(wse))
        commands = [
            {'command': '/commands', 'description': 'Get to know the available commands'},
            {'command': '/weather', 'description': 'Get the weather for a city'},
            {'command': '/status', 'description': 'Get the amount of contacts'},
            {'command': '/list', 'description': 'Get the list of contacts'},
        ]
        self.set_suggestions(commands)


class CallBackHandler(TelegramHandler):
    def __init__(self, data):
        super().__init__(data['from']['id'])
        self.user = User(**data.get('from'))
        self.callback_data = json.loads(data.get('data'))

    def handle(self):
        callback_type = self.callback_data.pop('type')
        if '/create_list' in self.callback_data:
            try:
                user_id = self.user.id
                list_name = self.callback_data['list_name']
                ShopWizardService.create_shop_list(user_id, list_name)
                self.send_message(f'Shop list "{list_name}" created successfully!')
            except ShopWizardException as e:
                self.send_message(str(e))
        elif '/remove_list' in self.callback_data:
            try:
                user_id = self.user.id
                list_name = self.callback_data.split()[1]  # Extract the list name from the callback_data

                # Remove the items from the 'item' table
                ShopWizardService.remove_items_from_list(user_id, list_name)

                # Remove the shop list from the 'shop_lists' table
                ShopWizardService.remove_shop_list(user_id, list_name)

                self.send_message(f'Shop list "{list_name}" and its items removed successfully!')
            except ShopWizardException as e:
                self.send_message(str(e))
        elif '/edit_list' in self.callback_data:
            try:
                user_id = self.user.id
                old_list_name = self.callback_data['old_list_name']
                new_list_name = self.callback_data['new_list_name']
                ShopWizardService.edit_shop_list(user_id, old_list_name, new_list_name)
                self.send_message(f'Shop list "{old_list_name}" renamed to "{new_list_name}" successfully!')
            except ShopWizardException as e:
                self.send_message(str(e))
        elif '/add_item' in self.callback_data:
            try:
                user_id = self.user.id
                list_name = self.callback_data['list_name']
                item = self.callback_data['item']
                ShopWizardService.add_item_to_list(user_id, list_name, item)
                self.send_message(f'Item "{item}" added to list "{list_name}" successfully!')
            except ShopWizardException as e:
                self.send_message(str(e))
        elif '/show_items' in self.callback_data:
            try:
                user_id = self.user.id
                list_name = self.callback_data['list_name']
                items = ShopWizardService.show_list_items(user_id, list_name)
                if items:
                    item_list = "\n- ".join(items)
                    self.send_message(f'Items in list "{list_name}":\n- {item_list}')
                else:
                    self.send_message(f'List "{list_name}" is empty.')
            except ShopWizardException as e:
                self.send_message(str(e))

        elif callback_type == WEATHER_TYPE:
            try:
                weather = WeatherService.get_current_weather_by_geo_data(**self.callback_data)
                formatted_weather = self.formatting_weather(weather)
            except WeatherServiceException as wse:
                self.send_message(str(wse))
            else:
                self.send_message(formatted_weather)

    @staticmethod
    def formatting_weather(weather):
        formatted_weather = f'Current temperature in your city is {weather["temperature"]}°C.'
        return formatted_weather

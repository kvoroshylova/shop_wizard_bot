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
        # Sends a message with a custom markup to the user
        data = {
            'chat_id': self.user.id,
            'text': text,
            'reply_markup': markup
        }
        requests.post(f'{TG_BASE_URL}{BOT_TOKEN}/sendMessage', json=data)

    def send_message(self, text):
        # Sends a simple text message to the user
        data = {
            'chat_id': self.user.id,
            'text': text
        }
        requests.post(f'{TG_BASE_URL}{BOT_TOKEN}/sendMessage', json=data)

    @staticmethod
    def set_suggestions(commands):
        # Sets the suggestions for the user's input by providing a list of available commands
        data = {
            'commands': commands
        }
        requests.post(f'{TG_BASE_URL}{BOT_TOKEN}/setMyCommands', json=data)


class MessageHandler(TelegramHandler):
    def __init__(self, data):
        # Initializes the TelegramHandler class with the user ID and retrieves the corresponding user from the database.
        super().__init__(data['from']['id'])
        self.user = User(**data['from'])
        self.text = data.get('text')
        self.city = None

        user = User.query.filter_by(id=self.user_id).first()
        if not user:
            new_user = User(id=self.user_id)
            db.session.add(new_user)
            db.session.commit()

    def handle(self):
        # Handles the received message by parsing the text and performing different actions based on the command or
        # input, including interacting with the ShopWizardService, ContactBookService, and WeatherService.
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
            commands_message = '''
            Hello! This is the help center of Shop Wizard Bot. Here you can see how to use commands:

    /commands - See all available commands
    Shop List Commands:
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
        /show - Show the contact from your contact book. Usage: /show <first_name> <last_name>
        /list - Show the list of all your contacts. Usage: /list
        /delete - Delete a contact from a contact book. Usage: /delete <first_name> <last_name>

    Replace <list_name>, <item_name>, <your_city>, <first_name>, <last_name> with the actual names you want to use.'''
            self.send_message(commands_message)

        # ShopWizardService operations
        elif text_parts[0] == '/create_list':
            try:
                if len(text_parts) < 2:
                    raise ShopWizardException(
                        'Insufficient arguments. Please provide list name.')
                list_name = text_parts[1]
                ShopWizardService.create_shop_list(self.user_id, list_name)
                self.send_message(f'Shop list "{list_name}" created successfully!')
            except ShopWizardException as e:
                self.send_message(str(e))
        elif text_parts[0] == '/remove_list':
            try:
                if len(text_parts) < 2:
                    raise ShopWizardException(
                        'Insufficient arguments. Please provide list name.')
                list_name = text_parts[1]
                ShopWizardService.remove_items_list(self.user_id, list_name)
                ShopWizardService.remove_shop_list(self.user_id, list_name)
                self.send_message(f'Shop list "{list_name}" and its items removed successfully!')
            except ShopWizardException as e:
                self.send_message(str(e))
        elif text_parts[0] == '/edit_list':
            try:
                if len(text_parts) < 3:
                    raise ShopWizardException(
                        'Insufficient arguments. Please provide both the old list name and new list name.')
                old_list_name = text_parts[1]
                new_list_name = text_parts[2]
                ShopWizardService.edit_shop_list(self.user_id, old_list_name, new_list_name)
                self.send_message(f'Shop list "{old_list_name}" renamed to "{new_list_name}" successfully!')
            except ShopWizardException as e:
                self.send_message(str(e))
        elif text_parts[0] == '/add_item':
            try:
                if len(text_parts) < 3:
                    raise ShopWizardException(
                        'Insufficient arguments. Please provide list name and item name.')
                list_name = text_parts[1]
                item = ' '.join(text_parts[2:])
                ShopWizardService.add_item_to_list(self.user_id, list_name, item)
                self.send_message(f'Item "{item}" added to list "{list_name}" successfully!')
            except ShopWizardException as e:
                self.send_message(str(e))
        elif text_parts[0] == '/show_items':
            try:
                if len(text_parts) < 2:
                    raise ShopWizardException(
                        'Insufficient arguments. Please provide list name.')
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
                if len(text_parts) < 3:
                    raise ShopWizardException(
                        'Insufficient arguments. Please provide list name and item name.')
                list_name = text_parts[1]
                item = ' '.join(text_parts[2:])
                ShopWizardService.remove_item_from_list(self.user_id, list_name, item)
                self.send_message(f'Item "{item}" removed from list "{list_name}" successfully!')
            except ShopWizardException as e:
                self.send_message(str(e))

        # ContactBookService commands
        elif text_parts[0] == '/add':
            try:
                if len(text_parts) < 4:
                    raise ContactBookException(
                        'Insufficient arguments. Please provide first name, last name and phone number.')
                first_name = text_parts[1]
                last_name = text_parts[2]
                phone_number = text_parts[3]
                ContactBookService.add_contact(self.user_id, first_name, last_name, phone_number)
                self.send_message(f'Contact "{first_name} {last_name}" added successfully!')
            except ContactBookException as e:
                self.send_message(str(e))
        elif text_parts[0] == '/delete':
            try:
                if len(text_parts) < 3:
                    raise ContactBookException(
                        'Insufficient arguments. Please provide both the first name and last name.')

                first_name = text_parts[1]
                last_name = text_parts[2]
                ContactBookService.delete_contact(self.user_id, first_name, last_name)
                self.send_message(f'Contact "{first_name} {last_name}" deleted successfully!')
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
                contacts = ContactBookService.list_of_contacts(self.user_id)
                if contacts:
                    self.send_message(f'Your contacts:\n{contacts}')
                else:
                    self.send_message('Your contact book is empty.')
            except ContactBookException as e:
                self.send_message(str(e))
        elif text_parts[0] == '/show':
            try:
                if len(text_parts) < 3:
                    raise ContactBookException(
                        'Insufficient arguments. Please provide both the first name and last name.')
                first_name = text_parts[1]
                last_name = text_parts[2]
                contact = ContactBookService.show_contact(self.user_id, first_name, last_name)
                if contact:
                    contact_info = f'Information about {contact.first_name}:\n' \
                                   f'Name - {contact.first_name} {contact.last_name}\n' \
                                   f'Phone number - {contact.phone_number}'
                    self.send_message(contact_info)
                else:
                    self.send_message(f'Contact "{first_name} {last_name}" not found.')
            except ContactBookException as e:
                self.send_message(str(e))

        # WeatherService commands
        elif text_parts[0] == '/weather':
            try:
                geo_data = WeatherService.get_geo_data(self.city)
                buttons = []
                for item in geo_data:
                    test_button = {
                        'text': f'{item.get("name")} - {item.get("country_code")}',
                        'callback_data': json.dumps({
                            'type': '/weather_city',
                            'lat': item.get('latitude'),
                            'lon': item.get('longitude')
                        })
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
        # Initializes the CallBackHandler class with the received callback data, including the user ID and callback
        # information.
        super().__init__(data['from']['id'])
        self.user = User(**data.get('from'))
        self.callback_data = json.loads(data.get('data'))

    def handle(self):
        # Handles the received callback by parsing the callback data and performing different actions based on the
        # callback type, including interacting with the ShopWizardService and WeatherService.
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
                list_name = self.callback_data.split()[1]
                ShopWizardService.remove_items_list(user_id, list_name)
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
        if callback_type == '/weather_city':
            try:
                lat = self.callback_data.get('lat')
                lon = self.callback_data.get('lon')
                weather = WeatherService.get_current_weather_by_geo_data(lat, lon)
                temperature = weather.get('temperature')
                rain_status = weather.get('rain')
                response_message = f'The current temperature in your city is {temperature}°C.\n'
                if rain_status:
                    response_message += 'It is currently raining in your city.'
                else:
                    response_message += 'There is no rain in your city at the moment.'
                self.send_message(response_message)
            except WeatherServiceException as wse:
                self.send_message(str(wse))

    @staticmethod
    def formatting_weather(weather):
        # Formats the weather information received from the WeatherService into a readable message.
        formatted_weather = f'Current temperature in your city is {weather["temperature"]}°C.'
        return formatted_weather

# shop_wizard_bot
This is repository for backend part of the Shop Wizard Bot.

**How to use Shop Wizard Bot:**

1. Clone the repository on your computer and open IDE.
2. Install Ngrok: Visit the Ngrok website (https://ngrok.com/) and download the appropriate version for your operating 
system. Follow the installation instructions provided for your platform.
3. Start Ngrok: Open a terminal or command prompt and navigate to the directory where you installed Ngrok. 
Run the following command to start Ngrok and expose a tunnel to your local Flask app: ```ngrok http 4242```. 
Ngrok will start and display a forwarding URL, such as ```https://abcd1234.ngrok.io```. Note this URL as you'll need it later.
4. Configure Telegram bot webhook: to receive updates from Telegram. You can use Postman for this operation. Choose the 
method "POST" and send this ```http://api.telegram.org/bot<BOT_TOKEN>/setWebhook?url=<Link_From_The_Second_Point>```.
5. Now you can run the app, but firstly you need to apply migrations. See the info below. 
6. After you run migrations you can use the bot!


**How to apply migrations to use database(for macOS). All commands run in Terminal of your IDE:**

1. ```cd tg_bot``` - Move to the folder which contains the necessary Flask application code.
2. ```FLASK_APP=__init__.py flask db init``` - Initialize the database migration environment by generating the 
necessary migration files.
3. ```FLASK_APP=__init__.py flask db migrate``` - Create a new database migration.
4. ```FLASK_APP=__init__.py flask db upgrade``` - Apply the pending database migrations to the actual database.

After completing the migration steps, you can use the command ```cd ..``` to move back to the previous directory 
if needed.

**Short description about files in this repository:**  
```__init__.py``` - The file serves as the entry point for the application, setting up the necessary configurations and 
connecting different components together.  
```handlers.py``` - There are a few classes in this file:  
1. The TelegramHandler class is responsible for sending messages and managing user information.
2. The MessageHandler class handles incoming messages and performs various actions based on the message content. 
It supports commands related to a shopping list, weather, and a contact book.
3. The CallBackHandler class handles callback data received from inline keyboards in Telegram. It performs actions 
based on the callback type and data, such as creating a shopping list, removing a shopping list, adding an item to a 
list, and retrieving weather information.
Overall, this file provides the necessary functionality to handle user interactions and respond accordingly in a 
Shop Wizard Bot.
```models.py``` - Creates a models, such as User, ContactBook, ShopList, Item.  
```services.py``` - Creates a services such as WeatherService, ShopWizardService, ContactBookService and 
Custom Exceptions to them.   
1. The WeatherService class handles weather-related operations. It includes methods to retrieve geographic data and 
current weather information based on a city name or geographical coordinates.
2. The ShopWizardService class provides functionality related to managing shopping lists. It includes methods to create,
remove, edit, and retrieve items from a user's shopping list.
3. The ContactBookService class offers services for managing a contact book. It includes methods to check the status of 
the contact book, list all contacts, show details of a specific contact, delete a contact, and add a new contact.
Each service class has its own set of exception classes (WeatherServiceException, ShopWizardException, and 
ContactBookException) to handle specific errors that may occur during service operations.
```views.py``` - File contains the view function for the Shop Wizard Bot's webhook endpoint.  
```run.py``` - File is responsible for starting the Flask application and running the bot.
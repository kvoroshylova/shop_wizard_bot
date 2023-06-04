# shop_wizard_bot
This is repository for backend part of the Shop Wizard Bot.

**How to use Shop Wizard Bot:**

1. Clone the repository on your computer and open IDE.
2. Install Ngrok: Visit the Ngrok website (https://ngrok.com/) and download the appropriate version for your operating 
system. Follow the installation instructions provided for your platform.
3. Start Ngrok: Open a terminal or command prompt and navigate to the directory where you installed Ngrok. 
Run the following command to start Ngrok and expose a tunnel to your local Flask app: ```yaml ngrok http 4242```. 
Ngrok will start and display a forwarding URL, such as ```yaml https://abcd1234.ngrok.io```. Note this URL as you'll need it later.
4. Configure Telegram bot webhook: to receive updates from Telegram. You can use Postman for this operation. Choose the 
method "POST" and send this ```yaml http://api.telegram.org/bot<BOT_TOKEN>/setWebhook?url=<Link_From_The_Second_Point>```.
5. Now you can run the app, but firstly you need to apply migrations. See the info below. 
6. After you run migrations you can use the bot!


**How to apply migrations to use database(for macOS). All commands run in Terminal of your IDE:**

1. ```yaml cd tg_bot``` - move to the folder which contains the necessary Flask application code.
2. ```yaml FLASK_APP=__init__.py flask db init``` - Initialize the database migration environment by generating the 
necessary migration files.
3. ```yaml FLASK_APP=__init__.py flask db migrate``` - Create a new database migration.
4. ```yaml FLASK_APP=__init__.py flask db upgrade``` - Apply the pending database migrations to the actual database.

After completing the migration steps, you can use the command ```yaml cd ..``` to move back to the previous directory 
if needed.

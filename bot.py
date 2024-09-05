import os
import json
import time
import logging
from pyrogram import Client, filters
from pyrogram.types import Message
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# API ID, API Hash, and Session String are loaded from the .env file
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
SESSION_STRING = os.getenv("SESSION_STRING")

# Directory and configuration file paths
MESSAGES_DIR = "messages"
COMMANDS_FILE = "commands.json"

# Initialize Pyrogram bot
app = Client("userbot", session_string=SESSION_STRING, api_id=API_ID, api_hash=API_HASH)

# Dictionary to track when the last message was sent
last_reply_time = {}
cooldown_time = 2 * 60 * 60  # 2 hours cooldown in seconds


def load_commands():
    """Load commands from the commands.json file."""
    if os.path.exists(COMMANDS_FILE):
        with open(COMMANDS_FILE, "r") as f:
            logging.info(f"Loading commands from {COMMANDS_FILE}")
            return json.load(f)
    else:
        logging.error(f"File {COMMANDS_FILE} not found.")
        raise FileNotFoundError(f"File {COMMANDS_FILE} not found.")


def get_message_from_file(filename):
    """Read the content of a text file."""
    file_path = os.path.join(MESSAGES_DIR, filename)
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            logging.info(f"Loading message from {file_path}")
            return f.read()
    else:
        logging.warning(f"Message file {file_path} not found.")
        return None


def get_user_info(user):
    """Retrieve user information, handling missing data."""
    user_id = user.id
    username = user.username if user.username else "No username"
    first_name = user.first_name if user.first_name else "No first name"
    last_name = user.last_name if user.last_name else "No last name"
    return user_id, username, first_name, last_name


@app.on_message(filters.private & filters.regex(r'^\.([^\s]+)$'))
def handle_command(client: Client, message: Message):
    """Handle user commands defined in commands.json."""
    logging.info(f"Message: {message.text}")  # Log the exact message content
    command = message.text[1:].strip()  # Strip spaces and remove "."
    logging.info(f"Parsed command: {command}")
    
    commands = load_commands()
    for cmd in commands:
        logging.info(f"Checking command: {cmd['command']}")
        if cmd['command'] == command:
            message_content = get_message_from_file(cmd['file'])
            if message_content:
                logging.info(f"Sending message for command: {command}")
                client.send_message(chat_id=message.chat.id, text=message_content)
                logging.info(f"Removing command message for everyone, message id: {message.id}")
                client.delete_messages(chat_id=message.chat.id, message_ids=message.id)

            else:
                logging.error(f"No message content found for command: {command}")
            return  # Exit function if command is handled

    logging.warning(f"Command {command} not found, sending fallback")


@app.on_message(filters.private)
def handle_fallback(client: Client, message: Message):
    """Handle fallback for generic messages or commands."""
    global last_reply_time

    # Get user information
    user_id, username, first_name, last_name = get_user_info(message.from_user)

    logging.info(f"Handling fallback for user ID: {user_id}, Username: {username}, First Name: {first_name}, Last Name: {last_name}")

    # Load the commands from commands.json
    commands = load_commands()

    logging.info("Message: " + message.text)

    # Search for the command with an empty string
    fallback_command = next((cmd for cmd in commands if cmd['command'] == ""), None)

    if message.from_user.id == client.get_me().id: return
    
    if fallback_command:
        # Get the fallback message from the corresponding file
        fallback_message = get_message_from_file(fallback_command['file'])

        if fallback_message:
            # Get the current time
            current_time = time.time()

            # Check if the user has received a message in the last 2 hours
            if user_id not in last_reply_time or (current_time - last_reply_time[user_id]) > cooldown_time:
                # Send the fallback message if not sent in the last 2 hours
                logging.info(f"Sending fallback message to user ID: {user_id}")
                client.send_message(
                    chat_id=message.chat.id,
                    text=fallback_message,
                )
                # Update the last reply time for the user
                last_reply_time[user_id] = current_time
            else:
                logging.info(f"Fallback message already sent to user ID: {user_id} within the last 2 hours.")
        else:
            logging.error("Fallback message content not found.")
    else:
        logging.error("No fallback command found in commands.json.")


# Start the bot
if __name__ == "__main__":
    logging.info("Starting the bot...")
    app.run()

import discord
import json
import csv
from datetime import datetime

# Set up intents to allow message tracking
intents = discord.Intents.default()
intents.message_content = True  # Allow the bot to read message content
intents.members = True  # Allow the bot to read member info

client = discord.Client(intents=intents)

# A dictionary to hold chat history
chat_history = {}

@client.event
async def on_ready():
    print(f'Logged in as {client.user}')
    # Call the function to save chat history after collecting data
    save_chat_history_csv()

@client.event
async def on_message(message):
    # Ignore the bot's own messages
    if message.author == client.user:
        return

    # Track the message sent by you (replace with your actual Discord user ID)
    user_id = "discord_user_id_here"  # Your Discord user ID

    if message.author.id == user_id:
        # Store the message with its content, timestamp, and username
        chat_history[message.id] = {
            "username": message.author.name,
            "content": message.content,
            "timestamp": str(message.created_at),
            "replies": []
        }

        print(f"Stored your message: {message.content} at {message.created_at}")

    # Check if the message is a reply to one of your messages
    elif message.reference and message.reference.message_id in chat_history:
        # Find the original message from your chat history
        original_message = chat_history[message.reference.message_id]
        # Add the reply to the original message's replies
        original_message["replies"].append({
            "user": message.author.name,
            "content": message.content,
            "timestamp": str(message.created_at)
        })

        print(f"Stored reply to your message: {message.content} from {message.author.name}")

# Save chat history to a CSV file
def save_chat_history_csv():
    csv_file_path = 'e:/1/chat_history.csv'

    with open(csv_file_path, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Message ID', 'Username', 'Content', 'Timestamp', 'Reply User', 'Reply Content', 'Reply Timestamp']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()

        for msg_id, msg_data in chat_history.items():
            # Write the original message
            writer.writerow({
                'Message ID': msg_id,
                'Username': msg_data['username'],
                'Content': msg_data['content'],
                'Timestamp': msg_data['timestamp'],
                'Reply User': '',
                'Reply Content': '',
                'Reply Timestamp': ''
            })

            # Check if 'replies' exists and is a list
            for reply in msg_data.get('replies', []):
                writer.writerow({
                    'Message ID': '',
                    'Username': '',
                    'Content': '',
                    'Timestamp': '',
                    'Reply User': reply['user'],
                    'Reply Content': reply['content'],
                    'Reply Timestamp': reply['timestamp']
                })

    print(f'Chat history saved to {csv_file_path}')

# Run the bot with your token
client.run('token_here')  # Replace with your bot's token

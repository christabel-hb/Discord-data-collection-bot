"""
Simple Discord Bot for Single Server
Collects only your messages and replies with basic commands
"""

import discord
import csv
import json
from datetime import datetime
from pathlib import Path

# Configuration
TOKEN = "YOUR_BOT_TOKEN_HERE"
YOUR_USER_ID = "Your Discord ID"  # Your Discord ID
DATA_FOLDER = Path("collected_data")
DATA_FOLDER.mkdir(exist_ok=True)

# Setup intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

client = discord.Client(intents=intents)

# Store data in memory
chat_history = {}
server_info = {}

@client.event
async def on_ready():
    """Bot startup handler"""
    print(f'✅ Logged in as {client.user}')
    print(f'🌍 Connected to: {client.guilds[0].name if client.guilds else "No servers"}')
    
    # Save any existing data on startup
    save_data_json()
    save_data_csv()

@client.event
async def on_message(message):
    """Handle incoming messages"""
    # Ignore bot's own messages
    if message.author == client.user:
        return
    
    # Only track messages from you or replies to your messages
    if message.author.id == YOUR_USER_ID:
        await track_your_message(message)
    elif message.reference:
        await track_reply_to_you(message)
    
    # Basic commands
    if message.content.lower() == "!hello":
        await message.channel.send(f"Hello {message.author.name}! I'm tracking your messages.")
    
    elif message.content.lower() == "!save":
        await save_and_confirm(message)
    
    elif message.content.lower() == "!stats":
        await show_stats(message)

async def track_your_message(message):
    """Track messages sent by you"""
    message_data = {
        "message_id": message.id,
        "author": str(message.author),
        "content": message.content,
        "timestamp": message.created_at.isoformat(),
        "channel": message.channel.name,
        "replies": []
    }
    
    chat_history[message.id] = message_data
    print(f"📝 Tracked your message in #{message.channel.name}: {message.content[:50]}...")
    
    # Save server info if not already saved
    if message.guild and message.guild.id not in server_info:
        server_info[message.guild.id] = {
            "name": message.guild.name,
            "member_count": message.guild.member_count,
            "channel_count": len(message.guild.channels),
            "first_tracked": datetime.now().isoformat()
        }

async def track_reply_to_you(message):
    """Track replies to your messages"""
    try:
        # Get the message being replied to
        original_msg = await message.channel.fetch_message(message.reference.message_id)
        
        # Check if it's a reply to YOUR message
        if original_msg.author.id == YOUR_USER_ID and original_msg.id in chat_history:
            reply_data = {
                "replier": str(message.author),
                "content": message.content,
                "timestamp": message.created_at.isoformat()
            }
            
            chat_history[original_msg.id]["replies"].append(reply_data)
            print(f"💬 Added reply to your message from {message.author.name}")
            
    except discord.NotFound:
        print("⚠️ Original message not found for reply")
    except Exception as e:
        print(f"❌ Error tracking reply: {e}")

async def save_and_confirm(message):
    """Save data and send confirmation"""
    save_data_json()
    save_data_csv()
    
    total_messages = len(chat_history)
    total_replies = sum(len(msg["replies"]) for msg in chat_history.values())
    
    await message.channel.send(
        f"💾 Data saved!\n"
        f"• Your messages: {total_messages}\n"
        f"• Total replies: {total_replies}\n"
        f"• Files saved to: {DATA_FOLDER}/"
    )

async def show_stats(message):
    """Show collection statistics"""
    if not chat_history:
        await message.channel.send("📊 No data collected yet.")
        return
    
    total_messages = len(chat_history)
    total_replies = sum(len(msg["replies"]) for msg in chat_history.values())
    
    # Calculate date range
    timestamps = [datetime.fromisoformat(msg["timestamp"]) for msg in chat_history.values()]
    earliest = min(timestamps).strftime("%Y-%m-%d")
    latest = max(timestamps).strftime("%Y-%m-%d")
    
    # Count by channel
    channels = {}
    for msg in chat_history.values():
        channel = msg["channel"]
        channels[channel] = channels.get(channel, 0) + 1
    
    channel_stats = "\n".join([f"  • #{chan}: {count} msgs" for chan, count in channels.items()])
    
    stats_msg = (
        f"📊 **Data Collection Stats**\n"
        f"```\n"
        f"Your Messages: {total_messages}\n"
        f"Total Replies: {total_replies}\n"
        f"Date Range: {earliest} to {latest}\n"
        f"Channels Tracked: {len(channels)}\n"
        f"{channel_stats}\n"
        f"```"
    )
    
    await message.channel.send(stats_msg)

def save_data_json():
    """Save data to JSON file"""
    if not chat_history:
        return
    
    filename = DATA_FOLDER / f"chat_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    data_to_save = {
        "server_info": server_info,
        "your_messages": chat_history,
        "export_time": datetime.now().isoformat(),
        "total_messages": len(chat_history),
        "total_replies": sum(len(msg["replies"]) for msg in chat_history.values())
    }
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data_to_save, f, indent=2, ensure_ascii=False)
    
    print(f"💾 Saved JSON data to {filename}")

def save_data_csv():
    """Save data to CSV file"""
    if not chat_history:
        return
    
    filename = DATA_FOLDER / f"chat_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Message_ID', 'Author', 'Content', 'Timestamp', 'Channel', 'Reply_Count']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for msg_id, msg_data in chat_history.items():
            writer.writerow({
                'Message_ID': msg_id,
                'Author': msg_data['author'],
                'Content': msg_data['content'][:500],  # Limit length
                'Timestamp': msg_data['timestamp'],
                'Channel': msg_data['channel'],
                'Reply_Count': len(msg_data['replies'])
            })
    
    print(f"💾 Saved CSV data to {filename}")

if __name__ == "__main__":
    print("🚀 Starting Single Server Bot...")
    print(f"📁 Data will be saved to: {DATA_FOLDER.absolute()}")
    client.run(TOKEN)
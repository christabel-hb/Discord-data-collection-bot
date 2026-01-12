"""
Discord Bot for Multiple Servers
Separate tracking for each server with server-specific commands
"""

import discord
import json
import csv
from datetime import datetime
from pathlib import Path
from typing import Dict, List

# Configuration
TOKEN = "YOUR_BOT_TOKEN_HERE"
YOUR_USER_ID = "discord_user_id_here"  # Your Discord ID
DATA_FOLDER = Path("multi_server_data")
DATA_FOLDER.mkdir(exist_ok=True)

# Setup intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True

client = discord.Client(intents=intents)

# Store data separately for each server
server_data: Dict[int, Dict] = {}
server_settings: Dict[int, Dict] = {}

@client.event
async def on_ready():
    """Bot startup handler"""
    print(f'✅ Logged in as {client.user}')
    print(f'🌍 Connected to {len(client.guilds)} servers:')
    
    for guild in client.guilds:
        print(f'   • {guild.name} (ID: {guild.id})')
        
        # Initialize data structure for each server
        if guild.id not in server_data:
            server_data[guild.id] = {
                "guild_name": guild.name,
                "messages": {},
                "tracked_since": datetime.now().isoformat()
            }
        
        # Default settings for each server
        if guild.id not in server_settings:
            server_settings[guild.id] = {
                "tracking_enabled": True,
                "save_replies": True,
                "prefix": "!",
                "allowed_channels": []  # Empty = all channels
            }

@client.event
async def on_message(message):
    """Handle incoming messages"""
    # Ignore bot's own messages
    if message.author == client.user:
        return
    
    # Ignore DMs (only guild messages)
    if not message.guild:
        return
    
    guild_id = message.guild.id
    
    # Skip if tracking is disabled for this server
    if not server_settings[guild_id]["tracking_enabled"]:
        return
    
    # Check if channel is allowed
    allowed_channels = server_settings[guild_id]["allowed_channels"]
    if allowed_channels and message.channel.id not in allowed_channels:
        return
    
    # Track messages from you
    if message.author.id == YOUR_USER_ID:
        await track_message(guild_id, message)
    
    # Track replies to your messages
    elif server_settings[guild_id]["save_replies"] and message.reference:
        await track_reply(guild_id, message)
    
    # Process server-specific commands
    await process_commands(guild_id, message)

async def track_message(guild_id: int, message):
    """Track a message in specific server"""
    message_data = {
        "message_id": message.id,
        "author": str(message.author),
        "content": message.content,
        "timestamp": message.created_at.isoformat(),
        "channel_id": message.channel.id,
        "channel_name": message.channel.name,
        "replies": [],
        "attachments": [att.url for att in message.attachments]
    }
    
    server_data[guild_id]["messages"][message.id] = message_data
    print(f"📝 [{message.guild.name}] Tracked your message in #{message.channel.name}")

async def track_reply(guild_id: int, message):
    """Track a reply in specific server"""
    try:
        original_msg = await message.channel.fetch_message(message.reference.message_id)
        
        # Check if reply is to your message
        if (original_msg.author.id == YOUR_USER_ID and 
            original_msg.id in server_data[guild_id]["messages"]):
            
            reply_data = {
                "replier": str(message.author),
                "content": message.content,
                "timestamp": message.created_at.isoformat()
            }
            
            server_data[guild_id]["messages"][original_msg.id]["replies"].append(reply_data)
            print(f"💬 [{message.guild.name}] Added reply from {message.author.name}")
            
    except Exception as e:
        print(f"⚠️ [{message.guild.name}] Error tracking reply: {e}")

async def process_commands(guild_id: int, message):
    """Process commands specific to each server"""
    prefix = server_settings[guild_id]["prefix"]
    content = message.content.lower()
    
    if content.startswith(prefix):
        command = content[len(prefix):].strip()
        
        if command == "hello":
            await message.channel.send(f"Hello from {message.guild.name} server! 👋")
        
        elif command == "save":
            await save_server_data(guild_id, message)
        
        elif command == "stats":
            await show_server_stats(guild_id, message)
        
        elif command == "settings":
            await show_server_settings(guild_id, message)
        
        elif command.startswith("toggle"):
            await toggle_tracking(guild_id, message)
        
        elif command == "help":
            await show_help(guild_id, message)

async def save_server_data(guild_id: int, message):
    """Save data for specific server"""
    if not server_data[guild_id]["messages"]:
        await message.channel.send("📭 No data to save for this server.")
        return
    
    # Create server-specific folder
    server_folder = DATA_FOLDER / str(guild_id)
    server_folder.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    guild_name = message.guild.name.replace("/", "_").replace("\\", "_")
    
    # Save JSON
    json_file = server_folder / f"{guild_name}_{timestamp}.json"
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(server_data[guild_id], f, indent=2, ensure_ascii=False)
    
    # Save CSV
    csv_file = server_folder / f"{guild_name}_{timestamp}.csv"
    save_as_csv(guild_id, csv_file)
    
    await message.channel.send(
        f"💾 **Data saved for {message.guild.name}**\n"
        f"• Messages: {len(server_data[guild_id]['messages'])}\n"
        f"• Files: `{json_file.name}`, `{csv_file.name}`"
    )

def save_as_csv(guild_id: int, filename: Path):
    """Save server data as CSV"""
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Message_ID', 'Channel', 'Content', 'Timestamp', 'Replies', 'Attachments']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for msg_id, msg_data in server_data[guild_id]["messages"].items():
            writer.writerow({
                'Message_ID': msg_id,
                'Channel': msg_data['channel_name'],
                'Content': msg_data['content'][:200],
                'Timestamp': msg_data['timestamp'],
                'Replies': len(msg_data['replies']),
                'Attachments': len(msg_data['attachments'])
            })

async def show_server_stats(guild_id: int, message):
    """Show statistics for specific server"""
    messages = server_data[guild_id]["messages"]
    
    if not messages:
        await message.channel.send("📊 No data collected for this server yet.")
        return
    
    total_messages = len(messages)
    total_replies = sum(len(msg["replies"]) for msg in messages.values())
    
    # Count by channel
    channel_counts = {}
    for msg in messages.values():
        channel = msg["channel_name"]
        channel_counts[channel] = channel_counts.get(channel, 0) + 1
    
    # Create stats message
    channel_stats = "\n".join([f"   #{chan}: {count}" for chan, count in channel_counts.items()])
    
    stats_msg = (
        f"📊 **Stats for {message.guild.name}**\n"
        f"```\n"
        f"Your Messages: {total_messages}\n"
        f"Total Replies: {total_replies}\n"
        f"Tracking Since: {server_data[guild_id]['tracked_since'][:10]}\n"
        f"\nChannels:\n{channel_stats}\n"
        f"```"
    )
    
    await message.channel.send(stats_msg)

async def show_server_settings(guild_id: int, message):
    """Show current settings for server"""
    settings = server_settings[guild_id]
    
    settings_msg = (
        f"⚙️ **Settings for {message.guild.name}**\n"
        f"```\n"
        f"Tracking Enabled: {settings['tracking_enabled']}\n"
        f"Save Replies: {settings['save_replies']}\n"
        f"Command Prefix: '{settings['prefix']}'\n"
        f"Allowed Channels: {len(settings['allowed_channels'])} channels\n"
        f"```"
    )
    
    await message.channel.send(settings_msg)

async def toggle_tracking(guild_id: int, message):
    """Toggle tracking for server"""
    server_settings[guild_id]["tracking_enabled"] = not server_settings[guild_id]["tracking_enabled"]
    status = "ENABLED ✅" if server_settings[guild_id]["tracking_enabled"] else "DISABLED ❌"
    
    await message.channel.send(f"📊 Tracking {status} for {message.guild.name}")

async def show_help(guild_id: int, message):
    """Show help message"""
    prefix = server_settings[guild_id]["prefix"]
    
    help_msg = (
        f"🤖 **Bot Commands for {message.guild.name}**\n"
        f"```\n"
        f"{prefix}hello    - Say hello\n"
        f"{prefix}save     - Save collected data\n"
        f"{prefix}stats    - Show statistics\n"
        f"{prefix}settings - Show current settings\n"
        f"{prefix}toggle   - Enable/disable tracking\n"
        f"{prefix}help     - Show this message\n"
        f"```\n"
        f"*Only your messages and replies to them are tracked.*"
    )
    
    await message.channel.send(help_msg)

# Auto-save every 100 messages per server
async def auto_save_check():
    """Check if auto-save is needed"""
    for guild_id, data in server_data.items():
        if len(data["messages"]) >= 100:
            server_folder = DATA_FOLDER / str(guild_id)
            server_folder.mkdir(exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = server_folder / f"auto_save_{timestamp}.json"
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            print(f"💾 Auto-saved data for guild {guild_id}")

if __name__ == "__main__":
    print("🚀 Starting Multi-Server Bot...")
    print(f"📁 Data will be saved to: {DATA_FOLDER.absolute()}")
    client.run(TOKEN)
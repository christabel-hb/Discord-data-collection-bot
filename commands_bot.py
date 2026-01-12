"""
Advanced Discord Bot with Slash Commands & Buttons
Modern Discord bot with interactive features
"""

import discord
from discord.ext import commands
from discord import app_commands
import json
import csv
import asyncio
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

# Configuration
TOKEN = "YOUR_BOT_TOKEN_HERE"
YOUR_USER_ID = "discord_user_id_here"  # Your Discord ID
DATA_FOLDER = Path("commands_bot_data")
DATA_FOLDER.mkdir(exist_ok=True)

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Global data storage
collected_data = {}
active_tasks = {}

# Rate limiting storage
rate_limit_data = {}

class DataCollector:
    """Handles data collection with rate limiting"""
    
    def __init__(self):
        self.data = {}
        self.rate_limits = {}
    
    def check_rate_limit(self, user_id: int, action: str, limit: int = 5, window: int = 60) -> bool:
        """Check if user is rate limited for an action"""
        key = f"{user_id}_{action}"
        now = datetime.now()
        
        if key not in self.rate_limits:
            self.rate_limits[key] = []
        
        # Clean old timestamps
        self.rate_limits[key] = [t for t in self.rate_limits[key] 
                                if now - t < timedelta(seconds=window)]
        
        if len(self.rate_limits[key]) >= limit:
            return False
        
        self.rate_limits[key].append(now)
        return True

data_collector = DataCollector()

@bot.event
async def on_ready():
    """Bot startup handler"""
    print(f'✅ Logged in as {bot.user}')
    
    # Sync slash commands
    try:
        synced = await bot.tree.sync()
        print(f'✅ Synced {len(synced)} slash commands')
    except Exception as e:
        print(f'❌ Error syncing commands: {e}')
    
    print(f'🌍 Connected to {len(bot.guilds)} servers')
    
    # Start background tasks
    bot.loop.create_task(periodic_backup())

@bot.event
async def on_message(message):
    """Handle incoming messages"""
    if message.author.bot:
        return
    
    # Basic tracking
    if message.author.id == YOUR_USER_ID:
        await track_message(message)
    
    # Process traditional commands
    await bot.process_commands(message)

async def track_message(message):
    """Track a message with metadata"""
    guild_id = message.guild.id if message.guild else 0
    
    if guild_id not in data_collector.data:
        data_collector.data[guild_id] = []
    
    message_data = {
        "id": message.id,
        "author": str(message.author),
        "content": message.content,
        "timestamp": message.created_at.isoformat(),
        "channel": message.channel.name if hasattr(message.channel, 'name') else "DM",
        "guild": message.guild.name if message.guild else "Direct Message",
        "attachments": len(message.attachments),
        "embeds": len(message.embeds)
    }
    
    data_collector.data[guild_id].append(message_data)
    
    # Limit stored messages to 1000 per guild
    if len(data_collector.data[guild_id]) > 1000:
        data_collector.data[guild_id] = data_collector.data[guild_id][-1000:]

# ========================
# SLASH COMMANDS
# ========================

@bot.tree.command(name="collect", description="Start collecting messages")
@app_commands.describe(
    limit="Number of messages to collect (max 1000)",
    channel="Specific channel to collect from"
)
async def collect_command(
    interaction: discord.Interaction,
    limit: app_commands.Range[int, 1, 1000] = 100,
    channel: Optional[discord.TextChannel] = None
):
    """Slash command to collect messages"""
    # Check rate limit
    if not data_collector.check_rate_limit(interaction.user.id, "collect", limit=2, window=300):
        await interaction.response.send_message(
            "⏳ Please wait 5 minutes before collecting again!", 
            ephemeral=True
        )
        return
    
    await interaction.response.defer(thinking=True)
    
    target_channel = channel or interaction.channel
    collected = 0
    
    try:
        async for message in target_channel.history(limit=limit):
            if message.author.id == YOUR_USER_ID:
                await track_message(message)
                collected += 1
            
            # Small delay to respect rate limits
            if collected % 20 == 0:
                await asyncio.sleep(0.1)
        
        await interaction.followup.send(
            f"✅ Collected {collected} of your messages from {target_channel.mention}"
        )
        
    except discord.Forbidden:
        await interaction.followup.send("❌ I don't have permission to read message history!")
    except Exception as e:
        await interaction.followup.send(f"❌ Error: {str(e)}")

@bot.tree.command(name="export", description="Export collected data")
@app_commands.describe(
    format="Export format",
    include_replies="Include replies to your messages"
)
async def export_command(
    interaction: discord.Interaction,
    format: str = "json",
    include_replies: bool = True
):
    """Export data in specified format"""
    await interaction.response.defer(thinking=True)
    
    guild_id = interaction.guild.id if interaction.guild else 0
    
    if guild_id not in data_collector.data or not data_collector.data[guild_id]:
        await interaction.followup.send("📭 No data to export!")
        return
    
    # Create export
    filename = await create_export(guild_id, format, interaction.user.id)
    
    if filename:
        await interaction.followup.send(
            f"✅ Data exported as {format.upper()}!",
            file=discord.File(filename)
        )
    else:
        await interaction.followup.send("❌ Failed to export data!")

@bot.tree.command(name="stats", description="Show statistics")
async def stats_command(interaction: discord.Interaction):
    """Show data collection statistics"""
    guild_id = interaction.guild.id if interaction.guild else 0
    
    if guild_id not in data_collector.data or not data_collector.data[guild_id]:
        await interaction.response.send_message("📊 No data collected yet!", ephemeral=True)
        return
    
    data = data_collector.data[guild_id]
    total = len(data)
    
    # Calculate statistics
    by_channel = {}
    by_day = {}
    
    for msg in data:
        # Count by channel
        channel = msg["channel"]
        by_channel[channel] = by_channel.get(channel, 0) + 1
        
        # Count by day
        day = msg["timestamp"][:10]
        by_day[day] = by_day.get(day, 0) + 1
    
    # Create embed
    embed = discord.Embed(
        title="📊 Data Collection Statistics",
        color=discord.Color.blue(),
        timestamp=datetime.now()
    )
    
    embed.add_field(name="Total Messages", value=str(total), inline=True)
    embed.add_field(name="Channels Tracked", value=str(len(by_channel)), inline=True)
    embed.add_field(name="Date Range", value=f"{min(by_day.keys())} to {max(by_day.keys())}", inline=True)
    
    # Top channels
    top_channels = sorted(by_channel.items(), key=lambda x: x[1], reverse=True)[:3]
    channels_text = "\n".join([f"#{chan}: {count}" for chan, count in top_channels])
    embed.add_field(name="Top Channels", value=channels_text or "None", inline=False)
    
    # Daily average
    avg_per_day = total / len(by_day) if by_day else 0
    embed.add_field(name="Average per Day", value=f"{avg_per_day:.1f}", inline=True)
    
    embed.set_footer(text=f"Requested by {interaction.user.name}")
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="clear", description="Clear collected data")
async def clear_command(interaction: discord.Interaction):
    """Clear data with confirmation button"""
    
    class ClearConfirmView(discord.ui.View):
        def __init__(self):
            super().__init__(timeout=30)
            self.value = None
        
        @discord.ui.button(label="✅ Confirm", style=discord.ButtonStyle.danger)
        async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
            guild_id = interaction.guild.id if interaction.guild else 0
            if guild_id in data_collector.data:
                count = len(data_collector.data[guild_id])
                data_collector.data[guild_id].clear()
                await interaction.response.send_message(f"🗑️ Cleared {count} messages!", ephemeral=True)
            else:
                await interaction.response.send_message("📭 No data to clear!", ephemeral=True)
            self.value = True
            self.stop()
        
        @discord.ui.button(label="❌ Cancel", style=discord.ButtonStyle.secondary)
        async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
            await interaction.response.send_message("Cancelled!", ephemeral=True)
            self.value = False
            self.stop()
    
    view = ClearConfirmView()
    await interaction.response.send_message(
        "⚠️ **Clear all collected data?** This cannot be undone!",
        view=view,
        ephemeral=True
    )

@bot.tree.command(name="settings", description="Configure bot settings")
async def settings_command(interaction: discord.Interaction):
    """Show settings with interactive buttons"""
    
    class SettingsView(discord.ui.View):
        def __init__(self):
            super().__init__(timeout=60)
        
        @discord.ui.button(label="📊 View Limits", style=discord.ButtonStyle.primary, row=0)
        async def view_limits(self, interaction: discord.Interaction, button: discord.ui.Button):
            limits = []
            for key, timestamps in data_collector.rate_limits.items():
                if str(interaction.user.id) in key:
                    action = key.split("_")[1]
                    remaining = 5 - len([t for t in timestamps 
                                       if datetime.now() - t < timedelta(seconds=300)])
                    limits.append(f"{action}: {remaining} requests left (5 min)")
            
            limits_text = "\n".join(limits) if limits else "No active rate limits"
            
            await interaction.response.send_message(
                f"⏳ **Your Rate Limits**\n```{limits_text}```",
                ephemeral=True
            )
        
        @discord.ui.button(label="💾 Save Now", style=discord.ButtonStyle.success, row=0)
        async def save_now(self, interaction: discord.Interaction, button: discord.ui.Button):
            await interaction.response.defer(thinking=True, ephemeral=True)
            guild_id = interaction.guild.id if interaction.guild else 0
            filename = await create_export(guild_id, "json", interaction.user.id)
            
            if filename:
                await interaction.followup.send(
                    "Data saved!",
                    file=discord.File(filename),
                    ephemeral=True
                )
            else:
                await interaction.followup.send("No data to save!", ephemeral=True)
        
        @discord.ui.button(label="❓ Help", style=discord.ButtonStyle.secondary, row=1)
        async def show_help(self, interaction: discord.Interaction, button: discord.ui.Button):
            help_text = (
                "**🤖 Commands Bot Help**\n\n"
                "**/collect** - Collect messages\n"
                "**/export** - Export data\n"
                "**/stats** - View statistics\n"
                "**/clear** - Clear data\n"
                "**/settings** - This menu\n\n"
                "*Only your messages are tracked*"
            )
            
            await interaction.response.send_message(help_text, ephemeral=True)
    
    view = SettingsView()
    await interaction.response.send_message(
        "⚙️ **Bot Settings**\nSelect an option below:",
        view=view,
        ephemeral=True
    )

# ========================
# TRADITIONAL COMMANDS
# ========================

@bot.command(name="fetch")
@commands.has_permissions(manage_messages=True)
async def fetch_cmd(ctx, limit: int = 50):
    """Traditional command to fetch messages"""
    if not data_collector.check_rate_limit(ctx.author.id, "fetch"):
        await ctx.send("⏳ Please wait before using this command again!")
        return
    
    await ctx.send(f"🔄 Collecting up to {limit} messages...")
    
    collected = 0
    for channel in ctx.guild.text_channels:
        try:
            async for message in channel.history(limit=min(limit, 100)):
                if message.author.id == YOUR_USER_ID:
                    await track_message(message)
                    collected += 1
                
                if collected >= limit:
                    break
            
            if collected >= limit:
                break
                
        except discord.Forbidden:
            continue
    
    await ctx.send(f"✅ Collected {collected} messages!")

@bot.command(name="backup")
async def backup_cmd(ctx):
    """Manual backup command"""
    await ctx.send("💾 Creating backup...")
    guild_id = ctx.guild.id if ctx.guild else 0
    filename = await create_export(guild_id, "json", ctx.author.id)
    
    if filename:
        await ctx.send("Backup created!", file=discord.File(filename))
    else:
        await ctx.send("No data to backup!")

# ========================
# HELPER FUNCTIONS
# ========================

async def create_export(guild_id: int, format: str, user_id: int) -> Optional[str]:
    """Create export file"""
    if guild_id not in data_collector.data or not data_collector.data[guild_id]:
        return None
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    user_folder = DATA_FOLDER / str(user_id)
    user_folder.mkdir(exist_ok=True)
    
    filename = user_folder / f"export_{timestamp}.{format}"
    
    try:
        if format.lower() == "json":
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data_collector.data[guild_id], f, indent=2, ensure_ascii=False)
        
        elif format.lower() == "csv":
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['ID', 'Author', 'Content', 'Timestamp', 'Channel', 'Attachments']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                for msg in data_collector.data[guild_id]:
                    writer.writerow({
                        'ID': msg['id'],
                        'Author': msg['author'],
                        'Content': msg['content'][:100],
                        'Timestamp': msg['timestamp'],
                        'Channel': msg['channel'],
                        'Attachments': msg['attachments']
                    })
        
        return filename
        
    except Exception as e:
        print(f"Export error: {e}")
        return None

async def periodic_backup():
    """Automatically backup data every hour"""
    await bot.wait_until_ready()
    
    while not bot.is_closed():
        await asyncio.sleep(3600)  # 1 hour
        
        for guild_id, data in data_collector.data.items():
            if data:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M")
                filename = DATA_FOLDER / f"auto_backup_{guild_id}_{timestamp}.json"
                
                try:
                    with open(filename, 'w', encoding='utf-8') as f:
                        json.dump(data, f, indent=2, ensure_ascii=False)
                    print(f"💾 Auto-backup for guild {guild_id}")
                except Exception as e:
                    print(f"Backup error: {e}")

@bot.event
async def on_command_error(ctx, error):
    """Handle command errors"""
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ You need Manage Messages permission!")
    elif isinstance(error, commands.CommandNotFound):
        await ctx.send("❌ Command not found. Use `/help` for slash commands!")
    elif isinstance(error, commands.BadArgument):
        await ctx.send("❌ Invalid argument!")
    else:
        await ctx.send(f"❌ Error: {str(error)}")

if __name__ == "__main__":
    print("🚀 Starting Commands Bot with Slash Commands...")
    print(f"📁 Data will be saved to: {DATA_FOLDER.absolute()}")
    bot.run(TOKEN)

# Discord Data Collection Bot 

## 📌 Project Overview
A collection of three specialized Discord bots designed to track and analyze **your own messages** across Discord servers. Each bot serves a different use case, from simple personal tracking to advanced multi-server management. A Discord bot that collects data from Discord servers while respecting permissions and rate limits. This tool is designed for server administrators to gather analytics and insights from their communities.

## ⚠️ **Important Legal & Ethical Notice**
**YOU MUST HAVE:**
- Explicit permission from server owners
- Compliance with Discord's Terms of Service
- Respect for user privacy and data protection laws (GDPR, CCPA, etc.)
- **NEVER** collect data from servers you don't own/administer without written consent
## 🤖 Available Bots

### 1. **Single Server Bot** (`single_server_bot.py`)
- Simple, single-server tracking
- Only tracks YOUR messages and replies
- Basic commands: `!hello`, `!save`, `!stats`
- Auto-saves to JSON and CSV
- Perfect for personal use

### 2. **Multi-Server Bot** (`multi_server_bot.py`)
- Tracks data separately for each server
- Server-specific settings and prefixes
- Commands: `!hello`, `!save`, `!stats`, `!settings`, `!toggle`
- Auto-saves in server-specific folders
- Great for managing multiple communities

### 3. **Commands Bot** (`commands_bot.py`)
- Modern bot with **slash commands** (`/collect`, `/export`, `/stats`)
- Interactive buttons and menus
- Rate limiting and permission checks
- Background auto-backup
- Professional features for advanced users

## ✨ Key Features

### 📊 **Data Collection**
- Tracks **only your messages** (configurable with your Discord ID)
- Captures replies to your messages
- Records timestamps, channel names, and server information
- Counts attachments and embeds

### 💾 **Export Options**
- **JSON format** for full data preservation
- **CSV format** for spreadsheet analysis
- Automatic file naming with timestamps
- Organized folder structure
  
### 🛡️ **Privacy Focused**
- **No other users' data collected** by default
- All data stored locally on your machine
- Configurable tracking settings
- Compliant with Discord Terms of Service when used properly

## 🚀 Quick Start

### Prerequisites
1. Python 3.8+
2. Discord Bot Token
3. Your Discord User ID

### Installation
```bash
# Install requirements
pip install -r requirements.txt

# Edit each bot file:
# 1. Replace YOUR_BOT_TOKEN_HERE with your token
# 2. Replace 1213535917495820348 with your Discord ID
```

### Step 1: Get Your Discord Credentials
1. **Your Discord User ID** (enable Developer Mode in Discord settings)
2. **Bot Token** from [Discord Developer Portal](https://discord.com/developers/applications)

### Step 2: Configure Any Bot
1. Open the bot file you want to use
2. Replace `YOUR_BOT_TOKEN_HERE` with your actual bot token
3. Replace `1213535917495820348` with your Discord ID
4. Save the file

### Step 3: Run the Bot
```bash
python single_server_bot.py
# or
python multi_server_bot.py
# or
python commands_bot.py
```

## ⚙️ Bot Setup Guide

### Discord Developer Portal Setup
1. Create a New Application
2. Navigate to "Bot" section
3. Click "Reset Token" → Copy token
4. Enable **Privileged Intents**:
   - ✅ MESSAGE CONTENT INTENT
   - ✅ SERVER MEMBERS INTENT (for multi-server bot)
5. Invite bot to your server with permissions:
   - Read Messages
   - Read Message History
   - Send Messages

### Invite URL Generator
Use this template (replace YOUR_CLIENT_ID):
```
https://discord.com/oauth2/authorize?client_id=YOUR_CLIENT_ID&permissions=274877958208&scope=bot%20applications.commands
```

## 📁 File Structure
```
discord-tracker-bots/
├── single_server_bot.py    # Simple single-server tracker
├── multi_server_bot.py     # Multi-server management
├── commands_bot.py         # Advanced with slash commands
└── README.md              # This documentation
```

### **Ask Server Owner for Bot Invite Permissions**
The server owner needs to:
1. Go to Server Settings → Integrations → Bots
2. Click "Add Bot" and select your bot
3. Grant necessary permissions
## 🔒 Legal & Ethical Use

### ✅ **Allowed Uses**
- Personal message archiving
- Server administration (with proper permissions)
- Message analytics for your own content
- Educational purposes

### ❌ **Prohibited Uses**
- Collecting other users' data without consent
- Violating Discord Terms of Service
- Harassment or doxxing
- Commercial data mining without permission

### ⚖️ **Compliance Notes**
- These bots only track messages from the configured user ID
- No automated collection of other users' data
- All data stays on your local machine
- You control all exported data

## 🤔 Which Bot Should I Choose?

| Your Needs | Recommended Bot |
|------------|----------------|
| Tracking messages in one server | **Single Server Bot** |
| Active in multiple communities | **Multi-Server Bot** |
| Want modern Discord features | **Commands Bot** |
| Need slash commands & menus | **Commands Bot** |
| Simple setup, basic features | **Single Server Bot** |

## 🆘 Troubleshooting

### Common Issues

**"Bot isn't responding"**
- Check bot token is correct
- Verify bot has been invited to server
- Ensure proper permissions are granted

**"Can't read messages"**
- Enable MESSAGE CONTENT INTENT
- Check channel-specific permissions
- Verify bot role hierarchy

**"No data being saved"**
- Confirm your Discord ID is set correctly
- Check write permissions in data folder
- Verify bot is receiving messages

## 📝 Version Notes

### Current Features
- Real-time message tracking
- Reply chain detection
- Multiple export formats
- Server-specific configurations
- Rate limiting (Commands Bot only)

### Planned Enhancements
- Message filtering by keywords
- Scheduled automatic exports
- Data visualization dashboard
- Cloud backup options

## 📄 License
MIT License - See [LICENSE](LICENSE) file for details

## ⚠️ Disclaimer
The developers are not responsible for misuse of these tools. Users are solely responsible for complying with Discord's Terms of Service and applicable laws.

---

**Choose a bot, configure it, and start tracking your Discord conversations responsibly!** 🔒
---
**Remember:** With great power comes great responsibility. Use this tool ethically and legally.

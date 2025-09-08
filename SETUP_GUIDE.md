# OwO Discord Bot Setup Guide

## 🚀 Quick Start

### 1. Get Your Discord User Token
1. Open Discord in your web browser (not the app)
2. Press `F12` to open Developer Tools
3. Go to the `Network` tab
4. Send any message in Discord
5. Look for a request to `messages` in the Network tab
6. Click on it and find the `Authorization` header
7. Copy the token (it starts with `MTM` or similar)

### 2. Configure the Bot

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Set Environment Variables** (if using cloud hosting):
   ```bash
   export DISCORD_TOKEN="your_token_here"
   export CHANNELS="channel_id_1,channel_id_2"
   ```

3. **Run the Bot**:
   ```bash
   python enhanced_bot.py
   ```

### Docker Deployment
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "enhanced_bot.py"]
```

## 🌐 Web Dashboard

The bot includes a beautiful web dashboard accessible at:
- **Local**: http://127.0.0.1:5000
- **Network**: http://192.168.0.192:5000 (accessible from other devices)

### Dashboard Features
- ✅ Real-time bot status monitoring
- ✅ Live statistics and activity tracking
- ✅ Bot control (start/stop/configure)
- ✅ Log viewing and export
- ✅ Multi-channel management
- ✅ Beautiful modern UI with dark theme

## ⚙️ Configuration Options

### Basic Settings
- `user_token`: Your Discord user token
- `channels`: Array of channel objects with ID and name
- `channel_rotation`: How to rotate between channels (`round_robin`, `random`, `load_balance`)

### Farming Features
- `use_hunt`: Enable/disable hunt command
- `use_battle`: Enable/disable battle command
- `use_pray`: Enable/disable pray command
- `use_curse`: Enable/disable curse command
- `use_coinflip`: Enable/disable coinflip gambling
- `use_slots`: Enable/disable slots gambling

### Timing Settings
- `hunt_interval`: [min, max] seconds between hunt commands
- `battle_interval`: [min, max] seconds between battle commands
- `pray_interval`: [min, max] seconds between pray commands
- `curse_interval`: [min, max] seconds between curse commands

### Anti-Ban Protection
- `random_delay`: [min, max] additional random delay
- `captcha_keywords`: Words that trigger captcha detection
- `channel_delay`: [min, max] seconds between channel switches

## 🛡️ Safety Features

### 100% Anti-Ban Protection
- ✅ Human-like typing simulation
- ✅ Realistic timing patterns
- ✅ Smart break system
- ✅ Presence simulation
- ✅ Message variations
- ✅ Captcha detection
- ✅ Multi-channel distribution

### Multi-Channel Support
- ✅ Farm across multiple Discord servers
- ✅ Intelligent load balancing
- ✅ Channel rotation strategies
- ✅ Smart delay management

## 🎮 Supported Commands

The bot automatically executes these OwO commands:
- `owo hunt` - Hunt for animals
- `owo battle` - Battle other users
- `owo pray` - Pray for luck
- `owo curse` - Curse other users
- `owo coinflip` - Gambling with coinflip
- `owo slots` - Gambling with slots
- `owo inv` - Check inventory
- `owo daily` - Claim daily rewards

## 📊 Web Dashboard Usage

### Starting the Bot
1. Navigate to the dashboard at http://127.0.0.1:5000
2. If not configured, you'll be redirected to setup
3. Enter your Discord token and channel IDs
4. Click "Start Bot" to begin farming

### Monitoring
- View real-time statistics
- Monitor bot logs
- Track farming progress
- Export logs for analysis

### Configuration
- Adjust timing intervals
- Enable/disable features
- Manage multiple channels
- Configure anti-ban settings

## 🔧 Troubleshooting

### Common Issues

**"Improper token has been passed"**
- Your Discord token is invalid or expired
- Get a fresh token following the steps above

**"Template syntax error"**
- This has been fixed in the latest version
- Restart the bot if you see this error

**Bot not responding**
- Check if you're in the correct channels
- Verify the bot has permission to send messages
- Check the logs for captcha detection

### Getting Help
- Check the console logs for detailed error messages
- Use the web dashboard to monitor bot status
- Ensure your Discord account isn't rate-limited

## ⚠️ Important Notes

1. **Use at your own risk** - This is a selfbot which violates Discord ToS
2. **Keep your token secure** - Never share your Discord token
3. **Monitor regularly** - Check for captchas and rate limits
4. **Use reasonable intervals** - Don't set timings too aggressive
5. **Respect Discord** - Don't abuse the platform

## 🎯 Best Practices

- Start with longer intervals and gradually decrease
- Use multiple channels to distribute load
- Monitor the dashboard regularly
- Keep the bot updated
- Use the anti-ban features
- Don't run 24/7 without breaks

---

**Enjoy farming with your OwO Discord Bot! 🎉**

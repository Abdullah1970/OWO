# OwO Discord Farm Bot

A Discord bot that automates OwO bot interactions for farming currency and items.

## Features

- **Multi-Channel Support**: Farm across multiple channels and servers simultaneously
- **Automated Commands**: Hunt, Battle, Pray, and Curse with smart distribution
- **Advanced Anti-Detection**: 100% anti-ban protection with human simulation
- **Captcha Detection**: Automatically stops when captcha is detected
- **Smart Channel Rotation**: Round-robin, random, or load-balanced distribution
- **Statistics Tracking**: Monitor your farming progress across all channels
- **Configurable Settings**: Customize intervals, channels, and behavior

## Setup

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Create Bot Token File**:
   Create a `token.txt` file and paste your Discord bot token inside.

3. **Configure Settings**:
   Edit `config.json` to set your farming channels and preferences:
   ```json
   {
     "channels": [
       {
         "id": 123456789012345678,
         "name": "Main Channel",
         "server_name": "Server 1",
         "priority": 1
       },
       {
         "id": 987654321098765432,
         "name": "Alt Channel",
         "server_name": "Server 2", 
         "priority": 2
       }
     ],
     "multi_channel": {
       "enabled": true,
       "rotation_mode": "round_robin",
       "command_distribution": "spread",
       "channel_delay": [2, 8]
     }
   }
   ```

## Usage

1. **Start the Bot**:
   ```bash
   python owo_farm_bot.py
   ```

2. **Bot Commands**:
   - `!start` - Start farming
   - `!stop` - Stop farming
   - `!stats` - View statistics
   - `!config` - View current configuration

## Multi-Channel Setup

### Getting Channel IDs
1. Enable Developer Mode in Discord (User Settings > Advanced > Developer Mode)
2. Right-click on each farming channel
3. Select "Copy ID"
4. Add to `channels` array in `config.json`

### Channel Configuration Options
- **Simple Format**: `"channels": [123456789, 987654321]`
- **Advanced Format**: 
  ```json
  "channels": [
    {
      "id": 123456789012345678,
      "name": "Main Channel",
      "server_name": "Server 1",
      "priority": 1
    }
  ]
  ```

### Multi-Channel Modes
- **Rotation Modes**:
  - `round_robin`: Cycles through channels in order
  - `random`: Randomly selects channels
  - `load_balance`: Uses least recently active channel

- **Distribution Modes**:
  - `spread`: One command per channel (recommended)
  - `duplicate`: Send to multiple channels simultaneously
  - `focus`: Focus on one channel for a period

## Safety Features

- **Captcha Detection**: Automatically stops when OwO bot sends captcha
- **Random Delays**: Adds 1-3 second random delays between commands
- **Human-like Intervals**: Randomized timing for each command type
- **Logging**: Detailed logs of all activities

## Important Notes

⚠️ **Use at your own risk!** This bot automates Discord interactions which may violate Discord's Terms of Service.

⚠️ **Always solve captchas manually** when detected by the bot.

⚠️ **Monitor the bot regularly** to ensure it's working properly.

⚠️ **Multi-channel farming** spreads load but may increase visibility - use responsibly.

⚠️ **Don't farm in the same channels** as other bots to avoid conflicts.

## Configuration Options

### Basic Settings
| Setting | Description | Default |
|---------|-------------|---------|
| `channels` | Array of channel IDs or objects | `[]` |
| `hunt_interval` | Seconds between hunt commands | `[15, 25]` |
| `battle_interval` | Seconds between battle commands | `[15, 25]` |
| `pray_interval` | Seconds between pray commands | `[300, 360]` |
| `curse_interval` | Seconds between curse commands | `[300, 360]` |

### Multi-Channel Settings
| Setting | Description | Default |
|---------|-------------|---------|
| `multi_channel.enabled` | Enable multi-channel mode | `true` |
| `multi_channel.rotation_mode` | Channel selection method | `round_robin` |
| `multi_channel.command_distribution` | How commands are distributed | `spread` |
| `multi_channel.channel_delay` | Delay between channels (seconds) | `[2, 8]` |
| `multi_channel.max_channels_per_command` | Max channels per command | `3` |

### Anti-Detection Settings
| Setting | Description | Default |
|---------|-------------|---------|
| `anti_detection.typing_simulation` | Simulate human typing | `true` |
| `anti_detection.message_variations` | Use command variations | `true` |
| `anti_detection.random_breaks` | Take random breaks | `true` |
| `anti_detection.presence_simulation` | Change Discord status | `true` |
| `anti_detection.advanced_timing` | Human-like timing patterns | `true` |

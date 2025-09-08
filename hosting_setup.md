# 🚀 Hosting Setup Guide for Kata Dump

## Environment Variables Setup

For hosting platforms like Kata Dump, Railway, Heroku, etc., set these environment variables:

```bash
DISCORD_TOKEN=MTM5OTYzMTUwNTUxNjUyNzYzNg.GIxi4S.k-izKoj_Kovv4fzpzlFZgTF5K-vD0IL2Fz6NPk
CHANNELS=1412304902407061615,1405205020114292768,1405205020114292769
```

## Files Required

Upload these files to your hosting platform:
- `enhanced_bot.py` (main bot file)
- `requirements.txt` (dependencies)
- `config.json` (configuration - optional if using env vars)
- `emojis/` folder (emoji mappings)

## Installation Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run the bot
python enhanced_bot.py
```

## Common 403 Forbidden Fixes

If you get 403 errors on hosting but not locally:

1. **Token Format**: Ensure your token doesn't have extra spaces
2. **Environment Variables**: Use DISCORD_TOKEN instead of config.json
3. **Channel Permissions**: Verify the bot can access the channels
4. **IP Restrictions**: Some hosting IPs may be blocked by Discord

## Troubleshooting

### Token Issues
- Get a fresh token from Discord Developer Console
- Don't use browser-extracted tokens on hosting platforms
- Use environment variables instead of config.json

### Network Issues
- The bot includes SSL certificate handling for hosting
- Automatic fallback for certificate verification
- Rate limiting protection built-in

## Example Environment Setup

```bash
# Set environment variables (replace with your values)
export DISCORD_TOKEN="your_token_here"
export CHANNELS="channel1,channel2,channel3"

# Run
python enhanced_bot.py
```

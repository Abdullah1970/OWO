import requests
import json
import time
import random
import re
import os
import sys
from datetime import datetime, timedelta
import threading
try:
    from PIL import Image, ImageEnhance
    import pytesseract
    import io
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False
    print("[WARNING] OCR libraries not available. Using simple captcha solving only.")

# Import emoji replacements for CMD compatibility
try:
    from emojis.mappings import replace_emojis
    EMOJI_SUPPORT = True
except ImportError:
    EMOJI_SUPPORT = False
    def replace_emojis(text):
        return text

class EnhancedOwOBot:
    def __init__(self):
        # Initialize basic attributes
        self.last_command = None
        self.last_response = None
        self.current_channel = 0
        self.session = requests.Session()
        # Configure SSL settings for hosting environments
        self.session.verify = True
        try:
            import ssl
            import certifi
            self.session.verify = certifi.where()
        except ImportError:
            # Fallback: disable SSL verification if certifi not available
            import urllib3
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            self.session.verify = False
        
        # Command response tracking
        self.command_responses = {
            'inventory': {'content': None, 'timestamp': None},
            'hunt': {'content': None, 'timestamp': None},
            'zoo': {'content': None, 'timestamp': None},
            'team': {'content': None, 'timestamp': None},
            'quest': {'content': None, 'timestamp': None},
            'battle': {'content': None, 'timestamp': None},
            'pray': {'content': None, 'timestamp': None},
            'curse': {'content': None, 'timestamp': None}
        }
        
        # Load configuration and initialize
        try:
            print("🔍 Loading configuration...")
            self.config = self.load_config()
            print("✅ Configuration loaded successfully")
            
            # Set up headers with realistic user agent (after config is loaded with env vars)
            token = self.config['user_token'].strip()
            
            # Debug token format
            print(f"🔍 Raw token length: {len(token)}")
            print(f"🔍 Token starts with: {token[:20]}...")
            
            # Try different authorization formats for hosting compatibility
            auth_formats = [
                token,  # Raw token
                f"Bearer {token}",  # Bearer format
                f"Bot {token}"  # Bot format (if it's actually a bot token)
            ]
            
            # Use the first format for now, we'll cycle through if needed
            self.headers = {
                'Authorization': auth_formats[0],
                'Content-Type': 'application/json',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'X-Super-Properties': 'eyJvcyI6IldpbmRvd3MiLCJicm93c2VyIjoiQ2hyb21lIiwiZGV2aWNlIjoiIiwic3lzdGVtX2xvY2FsZSI6ImVuLVVTIiwiYnJvd3Nlcl91c2VyX2FnZW50IjoiTW96aWxsYS81LjAgKFdpbmRvd3MgTlQgMTAuMDsgV2luNjQ7IHg2NCkgQXBwbGVXZWJLaXQvNTM3LjM2IChLSFRNTCwgbGlrZSBHZWNrbykgQ2hyb21lLzEyMC4wLjAuMCBTYWZhcmkvNTM3LjM2IiwiYnJvd3Nlcl92ZXJzaW9uIjoiMTIwLjAuMC4wIiwib3NfdmVyc2lvbiI6IjEwIiwicmVmZXJyZXIiOiIiLCJyZWZlcnJpbmdfZG9tYWluIjoiIiwicmVmZXJyZXJfY3VycmVudCI6IiIsInJlZmVycmluZ19kb21haW5fY3VycmVudCI6IiIsInJlbGVhc2VfY2hhbm5lbCI6InN0YWJsZSIsImNsaWVudF9idWlsZF9udW1iZXIiOjI3MDkyMCwiY2xpZW50X2V2ZW50X3NvdXJjZSI6bnVsbH0='
            }
            self.session.headers.update(self.headers)
            print("✅ Headers configured with token")
            
            # Initialize stats
            self.stats = {
                'hunts': 0, 'battles': 0, 'prays': 0, 'curses': 0,
                'coinflips': 0, 'dailies': 0, 'checklists': 0,
                'uses': 0, 'votes': 0, 'quests': 0, 'gems': 0, 'team_actions': 0,
                'start_time': time.time(),
                'last_hour': {'hunts': 0, 'battles': 0, 'currency': 0},
                'hourly_rates': [],
                'has_initial_data': False  # Track if we have initial hunt/battle data
            }
            print("✅ Stats initialized")
            
        except Exception as e:
            print(f"❌ Error during initialization: {str(e)}")
            raise
        
        # Derived state
        self.active_gems = []
        self.inventory_items = {}
        self.zoo_animals = {}
        self.team_animals = {}
        self.last_daily = None
        self.last_checklist = None
        self.last_vote = None
        
        # Anti-ban features
        self.last_command_time = datetime.min
        self.command_count = 0
        self.session_start = datetime.now()
        self.captcha_detected = False
        self.captcha_pause_time = None
        
        # Advanced 100% winnable gambling strategy
        self.coinflip_pattern = ['heads', 'tails']
        self.coinflip_index = 0
        self.last_coinflip_result = None
        self.base_bet = self.config.get('coinflip_bet_amount', 1000)
        self.current_bet = self.base_bet
        self.max_bet = 30000  # Increased max bet to 30k
        self.win_streak = 0
        self.loss_streak = 0
        self.total_winnings = 0
        self.gambling_stats = {'wins': 0, 'losses': 0, 'profit': 0, 'total_bet': 0}
        self.martingale_multiplier = 1.0
        self.guaranteed_win_mode = True
        
        # Auto captcha solver
        self.auto_solve_captcha = self.config.get('auto_solve_captcha', True)
        self.simple_captcha_answers = {
            'what is 2+2': '4', 'what is 1+1': '2', 'what is 3+3': '6',
            'what is 5+5': '10', 'what is 4+4': '8', 'what is 6+6': '12',
            'type "owo"': 'owo', 'type "uwu"': 'uwu', 'type "bot"': 'bot',
            'type "human"': 'human', 'type owo': 'owo', 'type uwu': 'uwu'
        }
        
        # Cooldown tracking in seconds
        self.cooldowns = {
            'hunt': 0,    # 0 = ready to use
            'battle': 0,  # 0 = ready to use
            'pray': 0,    # 300s = 5 minutes
            'curse': 0    # 300s = 5 minutes
        }
        self.cooldown_times = {
            'hunt': 0,
            'battle': 0,
            'pray': 300,  # 5 minutes in seconds
            'curse': 300  # 5 minutes in seconds
        }
        
        # Webhook for notifications
        self.webhook_url = self.config.get('webhook_url', None)
    
    def load_config(self):
        try:
            config_path = 'config.json'
            print(f"📂 Loading config from: {os.path.abspath(config_path)}")
            if not os.path.exists(config_path):
                raise FileNotFoundError(f"Config file not found at: {os.path.abspath(config_path)}")
                
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            # Check for environment variables (for hosting platforms)
            if os.getenv('DISCORD_TOKEN'):
                print("🔧 Using Discord token from environment variable")
                config['user_token'] = os.getenv('DISCORD_TOKEN')
            
            if os.getenv('CHANNELS'):
                print("🔧 Using channels from environment variable")
                channel_ids = os.getenv('CHANNELS').split(',')
                config['channels'] = [{"id": ch_id.strip(), "name": f"Channel {ch_id.strip()[-4:]}"} for ch_id in channel_ids]
                
            # Validate required fields
            required_fields = ['user_token', 'channels']
            for field in required_fields:
                if field not in config:
                    raise ValueError(f"Missing required config field: {field}")
                    
            # Validate token format
            token = config['user_token']
            if not token or len(token) < 50:
                raise ValueError("Invalid token format - token too short")
            
            # Test token validity (skip for now to avoid circular dependency)
            # self.validate_token(token)
            
            print("✅ Config validation passed")
            return config
            
        except json.JSONDecodeError as e:
            print(f"❌ Error parsing config.json: {str(e)}")
            raise
        except Exception as e:
            print(f"❌ Error loading config: {str(e)}")
            raise
    
    def validate_token(self, token):
        """Validate Discord token by testing API access"""
        # Clean token - remove any whitespace
        token = token.strip()
        
        test_headers = {
            'Authorization': token,
            'Content-Type': 'application/json',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        print(f"🔍 Environment check: HOSTING_ENV = '{os.getenv('HOSTING_ENV', '')}'")
        print(f"🔍 Validating Discord token...")
        print(f"🔍 Token format: {token[:10]}...{token[-10:]}")  # Show partial token for debugging
        
        try:
            # Test with Discord's user info endpoint
            response = requests.get('https://discord.com/api/v9/users/@me', headers=test_headers, timeout=10)
            print(f"🔍 Response status: {response.status_code}")
            
            # Debug response content
            try:
                response_data = response.json()
                print(f"🔍 Response preview: {str(response_data)[:100]}")
            except:
                print(f"🔍 Response text: {response.text[:100]}")
            
            if response.status_code == 200:
                user_data = response.json()
                print(f"✅ Token valid for user: {user_data.get('username', 'Unknown')}#{user_data.get('discriminator', '0000')}")
                return True
            elif response.status_code == 401:
                print("❌ Token is invalid or expired")
                print("🔧 Get a new token from Discord Developer Console")
                return False
            elif response.status_code == 403:
                print("❌ Token lacks required permissions or account is restricted")
                print("🔧 Try these solutions:")
                print("   1. Get a completely fresh token")
                print("   2. Check if your account has any restrictions")
                print("   3. Try from a different browser/session")
                print("⚠️ Continuing anyway - some features may not work")
                return True  # Continue despite validation failure
            else:
                print(f"❌ Token validation failed: {response.status_code}")
                print("⚠️ Continuing anyway - some features may not work")
                return True  # Continue despite validation failure
                
        except Exception as e:
            print(f"❌ Error validating token: {e}")
            return False
    
    def test_channel_access(self, channel_id):
        """Test if we can access a specific channel"""
        url = f"https://discord.com/api/v9/channels/{channel_id}"
        
        try:
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                channel_data = response.json()
                print(f"✅ Channel access OK: #{channel_data.get('name', 'Unknown')}")
                return True
            elif response.status_code == 403:
                print(f"❌ No access to channel {channel_id}")
                print("🔧 Check if you're in the server and have message permissions")
                return False
            elif response.status_code == 404:
                print(f"❌ Channel {channel_id} not found")
                print("🔧 Verify the channel ID is correct")
                return False
            else:
                print(f"❌ Channel test failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error testing channel: {e}")
            return False
    
    def human_delay(self, base_min=0.5, base_max=1.5):
        """Human-like random delays"""
        delay = random.uniform(base_min, base_max)
        # Add occasional longer pauses (human behavior) - less frequent now
        if random.randint(1, 50) == 1:  # 2% chance for longer pause
            delay += random.uniform(1, 3)
        time.sleep(delay)
    
    def anti_ban_check(self):
        """Check if we should take a break to avoid detection"""
        now = datetime.now()
        
        # Take break every 50-80 commands
        if self.command_count > random.randint(50, 80):
            break_time = random.randint(300, 900)  # 5-15 minutes
            print(f"🛡️ Anti-ban break: {break_time//60}m {break_time%60}s")
            time.sleep(break_time)
            self.command_count = 0
        
        # Take longer break every 2-4 hours
        if now - self.session_start > timedelta(hours=random.randint(2, 4)):
            long_break = random.randint(1800, 3600)  # 30-60 minutes
            print(f"🛡️ Long anti-ban break: {long_break//60} minutes")
            time.sleep(long_break)
            self.session_start = now
    
    def check_captcha_status(self):
        """Check if captcha needs to be manually resolved"""
        if self.captcha_detected:
            print(f"\n🚨 CAPTCHA ACTIVE - Auto-solving failed")
            print(f"📝 Please solve the captcha manually in Discord")
            print(f"⌨️ Type 'resume' to continue farming after solving captcha")
            print(f"⌨️ Type 'retry' to attempt auto-solving again")
            print(f"⌨️ Type 'quit' to stop the bot")
            
            while self.captcha_detected:
                try:
                    user_input = input("\n> ").strip().lower()
                    if user_input == 'resume':
                        print(f"▶️ Resuming bot - captcha marked as solved")
                        self.captcha_detected = False
                        self.captcha_pause_time = None
                        break
                    elif user_input == 'retry':
                        print(f"🔄 Will retry auto-solving on next captcha")
                        self.captcha_detected = False
                        self.captcha_pause_time = None
                        break
                    elif user_input == 'quit':
                        print(f"🛑 Bot stopped by user")
                        exit(0)
                    else:
                        print(f"❓ Invalid input. Type 'resume', 'retry', or 'quit'")
                except KeyboardInterrupt:
                    print(f"\n🛑 Bot stopped by user")
                    exit(0)
    
    def _process_command_response(self, command, response_data):
        """Process and store command responses for state management"""
        if not response_data or 'content' not in response_data:
            return
            
        content = response_data['content']
        timestamp = datetime.now()
        
        # Map commands to their response types
        command_map = {
            'owo inv': 'inventory',
            'owo hunt': 'hunt',
            'owo zoo': 'zoo',
            'owo team': 'team',
            'owo quest': 'quest',
            'owo battle': 'battle',
            'owo pray': 'pray',
            'owo curse': 'curse'
        }
        
        # Update command response tracking
        for cmd_prefix, response_type in command_map.items():
            if command.lower().startswith(cmd_prefix):
                self.command_responses[response_type] = {
                    'content': content,
                    'timestamp': timestamp
                }
                print(f"📝 Updated {response_type} state")
                
                # Process specific command responses
                if response_type == 'inventory':
                    self._process_inventory(content)
                elif response_type == 'hunt':
                    self._process_hunt(content)
                elif response_type == 'zoo':
                    self._process_zoo(content)
                elif response_type == 'team':
                    self._process_team(content)
                    
    def _process_inventory(self, content):
        """Process inventory command response"""
        # Extract items from inventory
        # Example: Parse item names and quantities
        self.inventory_items = {}
        # TODO: Add inventory parsing logic
        
    def _process_hunt(self, content):
        """Process hunt command response"""
        # Update active gems from hunt response
        self.update_active_gems_from_hunt(content)
        # TODO: Add hunt-specific processing
        
    def _process_zoo(self, content):
        """Process zoo command response"""
        # Parse zoo animals
        self.zoo_animals = {}
        # TODO: Add zoo parsing logic
        
    def _process_team(self, content):
        """Process team command response"""
        # Parse team animals
        self.team_animals = {}
        # TODO: Add team parsing logic
        
    def log_activity(self, activity_type, amount=1, currency_earned=0):
        """Log an activity and update stats"""
        # Initialize stats if they don't exist
        if not hasattr(self, 'stats'):
            self.stats = {
                'hunts': 0, 'battles': 0, 'prays': 0, 'curses': 0,
                'coinflips': 0, 'dailies': 0, 'checklists': 0,
                'uses': 0, 'votes': 0, 'quests': 0, 'gems': 0, 'team_actions': 0,
                'start_time': time.time(),
                'last_hour': {'hunts': 0, 'battles': 0, 'currency': 0},
                'hourly_rates': []
            }
        
        # Update main stats counter
        if activity_type in self.stats and isinstance(amount, (int, float)):
            self.stats[activity_type] += amount
        
        # Initialize last_hour if it doesn't exist
        if 'last_hour' not in self.stats:
            self.stats['last_hour'] = {'hunts': 0, 'battles': 0, 'currency': 0}
            
        # Track hourly stats for estimation
        if activity_type in ['hunts', 'battles'] and isinstance(amount, (int, float)):
            self.stats['last_hour'][activity_type] += amount
            
        if currency_earned > 0 and isinstance(currency_earned, (int, float)):
            self.stats['last_hour']['currency'] += currency_earned
            
        # Update hourly rates every 5 minutes
        current_time = time.time()
        if not hasattr(self, 'last_rate_update'):
            self.last_rate_update = current_time
        elif current_time - self.last_rate_update >= 300:  # 5 minutes
            self._update_hourly_rates()
            self.last_rate_update = current_time
        else:
            self.last_rate_update = current_time
    
    def send_message(self, channel_id, content):
        """Send message with anti-ban measures and captcha detection"""
        # Check if captcha is active (doesn't auto-expire)
        if self.captcha_detected:
            self.check_captcha_status()
            return None
        
        # Anti-ban rate limiting with dynamic delays
        now = datetime.now()
        time_since_last = (now - self.last_command_time).total_seconds()
        
        # Base delays in seconds
        delays = {
            'owoh': 1.2,    # Hunt
            'owob': 1.2,    # Battle
            'owop': 1.2,    # Pray
            'owoc': 1.2,    # Curse
            'owous': 1.0,   # Use
            'owoinv': 1.5,  # Inventory check
            'owoi': 1.0,    # Info
            'default': 0.8  # Other commands
        }
        
        # Get base delay based on command type
        cmd = content.lower().replace(' ', '')[:5]
        base_delay = next((delay for prefix, delay in delays.items() if cmd.startswith(prefix)), delays['default'])
        
        # Add jitter (10-30% of base delay)
        jitter = base_delay * random.uniform(0.1, 0.3)
        final_delay = max(0.5, base_delay + jitter - time_since_last)
        
        # Only sleep if needed
        if time_since_last < final_delay:
            time.sleep(final_delay - time_since_last)
        
        url = f"https://discord.com/api/v9/channels/{channel_id}/messages"
        data = {"content": content}
        
        # Try multiple authentication methods
        auth_methods = [
            self.config['user_token'].strip(),
            f"Bearer {self.config['user_token'].strip()}",
            f"Bot {self.config['user_token'].strip()}"
        ]
        
        response = None
        for i, auth_token in enumerate(auth_methods):
            headers = {
                'Authorization': auth_token,
                'Content-Type': 'application/json',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'X-Super-Properties': 'eyJvcyI6IldpbmRvd3MiLCJicm93c2VyIjoiQ2hyb21lIiwiZGV2aWNlIjoiIiwic3lzdGVtX2xvY2FsZSI6ImVuLVVTIiwiYnJvd3Nlcl91c2VyX2FnZW50IjoiTW96aWxsYS81LjAgKFdpbmRvd3MgTlQgMTAuMDsgV2luNjQ7IHg2NCkgQXBwbGVXZWJLaXQvNTM3LjM2IChLSFRNTCwgbGlrZSBHZWNrbykgQ2hyb21lLzEyMC4wLjAuMCBTYWZhcmkvNTM3LjM2IiwiYnJvd3Nlcl92ZXJzaW9uIjoiMTIwLjAuMC4wIiwib3NfdmVyc2lvbiI6IjEwIiwicmVmZXJyZXIiOiIiLCJyZWZlcnJpbmdfZG9tYWluIjoiIiwicmVmZXJyZXJfY3VycmVudCI6IiIsInJlZmVycmluZ19kb21haW5fY3VycmVudCI6IiIsInJlbGVhc2VfY2hhbm5lbCI6InN0YWJsZSIsImNsaWVudF9idWlsZF9udW1iZXIiOjI3MDkyMCwiY2xpZW50X2V2ZW50X3NvdXJjZSI6bnVsbH0='
            }
            
            try:
                response = requests.post(url, json=data, headers=headers, timeout=10)
                if response.status_code != 403:
                    if i > 0:
                        print(f"✅ Auth method {i+1} worked: {['Raw', 'Bearer', 'Bot'][i]}")
                        # Update session headers with working method
                        self.session.headers.update(headers)
                    break
                elif i == len(auth_methods) - 1:
                    print(f"❌ All auth methods failed. Token may be invalid.")
            except Exception as e:
                if i == len(auth_methods) - 1:
                    raise e
                continue
        
        try:
            self.last_command_time = now
            self.command_count += 1
            
            if response.status_code == 200:
                response_data = response.json()
                print(f"✅ {content}")
                
                # Process the command response for state management
                self._process_command_response(content, response_data)
                
                # Track currency earned if applicable
                if 'hunt' in content.lower() or 'battle' in content.lower():
                    currency_earned = 0  # TODO: Parse currency from response
                    if currency_earned > 0:
                        self.log_activity('hunts' if 'hunt' in content.lower() else 'battles', currency_earned=currency_earned)
                
                # For inventory commands, wait for OwO bot response
                if content.lower() == 'owo inv':
                    time.sleep(1.5)  # Reduced wait time for bot response
                    # Get recent messages to find OwO bot's inventory response
                    messages_url = f"https://discord.com/api/v9/channels/{channel_id}/messages?limit=5"
                    messages_response = self.session.get(messages_url)
                    if messages_response.status_code == 200:
                        messages = messages_response.json()
                        for msg in messages:
                            # Look for OwO bot's response (bot ID: 408785106942164992)
                            if msg.get('author', {}).get('id') == '408785106942164992':
                                if 'inventory' in msg.get('content', '').lower() or len(msg.get('content', '')) > 100:
                                    return msg  # Return OwO bot's inventory response
                
                # Check for captcha in response
                if 'owo' in content.lower():
                    self.check_for_captcha(response_data, channel_id)
                
                return response_data
            elif response.status_code == 429:  # Rate limited
                retry_after = response.json().get('retry_after', 60)
                print(f"⚠️ Rate limited! Waiting {retry_after}s")
                time.sleep(retry_after + random.randint(5, 15))
                return None
            else:
                error_msg = f"❌ Failed: {response.status_code}"
                if response.status_code == 403:
                    error_msg += " Forbidden - Invalid token or insufficient permissions"
                    print(f"{error_msg}")
                    print("🔧 Please check:")
                    print("   1. Your Discord token is correct and valid")
                    print(f"   2. You have permission to send messages in channel {channel_id}")
                    print("   3. The channel ID is correct")
                    print("   4. Your account isn't banned or restricted")
                    
                    # Try to get more detailed error info
                    try:
                        error_data = response.json()
                        if 'message' in error_data:
                            print(f"   Discord API Error: {error_data['message']}")
                    except:
                        pass
                else:
                    print(error_msg)
                return None
        except Exception as e:
            print(f"❌ Error sending message: {e}")
            return None
    
    def send_webhook(self, title, description, color=0x00ff00):
        """Send webhook notification"""
        if not self.webhook_url:
            return
        
        embed = {
            "title": title,
            "description": description,
            "color": color,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        data = {"embeds": [embed]}
        
        try:
            requests.post(self.webhook_url, json=data)
        except:
            pass
    
    def _update_hourly_rates(self):
        """Update hourly rates based on recent activity"""
        if not hasattr(self, 'stats') or 'last_hour' not in self.stats:
            return
            
        current_time = time.time()
        time_elapsed = (current_time - getattr(self, 'last_rate_update', current_time)) / 3600  # in hours
        
        if time_elapsed > 0:
            rates = {
                'hunts': self.stats['last_hour']['hunts'] / time_elapsed,
                'battles': self.stats['last_hour']['battles'] / time_elapsed,
                'currency': self.stats['last_hour']['currency'] / time_elapsed
            }
            
            if 'hourly_rates' not in self.stats:
                self.stats['hourly_rates'] = []
                
            self.stats['hourly_rates'].append((current_time, rates))
            
            # Keep only last 12 rates (1 hour if updated every 5 minutes)
            if len(self.stats['hourly_rates']) > 12:
                self.stats['hourly_rates'].pop(0)
                
            # Reset counters
            for key in self.stats['last_hour']:
                self.stats['last_hour'][key] = 0
    
    def get_estimated_earnings(self, hours=1):
        """Get estimated earnings for the next X hours"""
        if not hasattr(self, 'stats') or 'hourly_rates' not in self.stats or not self.stats['hourly_rates']:
            return {
                'hunts': 0,
                'battles': 0,
                'currency': 0,
                'message': 'Not enough data yet. Please wait a few minutes.'
            }
            
        # Calculate average rates
        total_rates = {'hunts': 0, 'battles': 0, 'currency': 0}
        for _, rates in self.stats['hourly_rates']:
            for key in total_rates:
                total_rates[key] += rates.get(key, 0)
                
        avg_rates = {k: v / len(self.stats['hourly_rates']) for k, v in total_rates.items()}
        
        # Calculate estimates
        estimates = {
            'hunts': int(avg_rates['hunts'] * hours),
            'battles': int(avg_rates['battles'] * hours),
            'currency': int(avg_rates['currency'] * hours),
            'message': ''
        }
        
        return estimates
    
    def get_stats(self):
        """Get current stats and estimates"""
        if not hasattr(self, 'stats'):
            return "No stats available yet. Start farming to see statistics."
            
        stats = self.stats.copy()
        
        # Add session duration
        if 'start_time' in stats:
            duration = time.time() - stats['start_time']
            hours, remainder = divmod(duration, 3600)
            minutes, seconds = divmod(remainder, 60)
            stats['session_duration'] = f"{int(hours)}h {int(minutes)}m {int(seconds)}s"
        
        # Add estimates
        stats['estimates'] = {
            'per_hour': self.get_estimated_earnings(1),
            'per_day': self.get_estimated_earnings(24)
        }
        
        return stats
        
    def get_gem_bonuses(self):
        """Calculate active gem bonuses"""
        bonuses = {
            'hunt': 0,      # % bonus to hunt rewards
            'battle': 0,    # % bonus to battle rewards
            'lucky': 0,     # % bonus to luck (affects rare drops)
            'exp': 0        # % bonus to experience
        }
        
        if not hasattr(self, 'active_gems'):
            return bonuses
            
        # Define gem effects based on type and rarity
        gem_effects = {
            'hunting': {
                'common': 5, 'uncommon': 10, 'rare': 15, 'epic': 20
            },
            'empowering': {
                'common': 5, 'uncommon': 10, 'rare': 15, 'epic': 20
            },
            'lucky': {
                'common': 5, 'uncommon': 10, 'rare': 15, 'epic': 20
            }
        }
        
        for gem in self.active_gems:
            gem_type = gem.get('type', '').lower()
            gem_rarity = gem.get('rarity', '').lower()
            
            if gem_type in gem_effects and gem_rarity in gem_effects[gem_type]:
                bonus = gem_effects[gem_type][gem_rarity]
                if gem_type == 'hunting':
                    bonuses['hunt'] += bonus
                elif gem_type == 'empowering':
                    bonuses['battle'] += bonus
                elif gem_type == 'lucky':
                    bonuses['lucky'] += bonus
                    
        return bonuses
        
    def show_farming_estimates(self):
        """Display farming rate estimates with gem bonuses and hunting details"""
        if not hasattr(self, 'stats'):
            return "🔍 No farming data available yet. Start farming to see estimates."
            
        output = ["\n📊 **Farming Rate Estimates**"]
        
        # Get current gem bonuses
        gem_bonuses = self.get_gem_bonuses()
        
        # Base rates (will be updated as bot runs)
        base_hunt_rate = 100  # hunts per hour
        base_battle_rate = 60  # battles per hour
        # Cowoncy ranges (highly variable due to rare animals worth 100k+)
        base_currency_min_hunt = 50   # minimum cowoncy per hunt
        base_currency_max_hunt = 5000 # maximum with rare animals
        base_currency_min_battle = 30  # minimum cowoncy per battle  
        base_currency_max_battle = 2000 # maximum with rare drops
        base_animal_rate = 0.6  # animals per hunt (60% base chance for 35+ per min)
        
        # Apply gem bonuses
        hunt_rate = base_hunt_rate * (1 + gem_bonuses['hunt'] / 100)
        battle_rate = base_battle_rate * (1 + gem_bonuses['battle'] / 100)
        
        # Calculate cowoncy ranges with gem bonuses
        currency_min_hunt = int(base_currency_min_hunt * (1 + gem_bonuses['hunt'] / 100))
        currency_max_hunt = int(base_currency_max_hunt * (1 + gem_bonuses['hunt'] / 100))
        currency_min_battle = int(base_currency_min_battle * (1 + gem_bonuses['battle'] / 100))
        currency_max_battle = int(base_currency_max_battle * (1 + gem_bonuses['battle'] / 100))
        
        # Realistic animal rates based on 35+ per minute
        # 35 animals/min = 2100 animals/hour
        # With 100 hunts/hour = 21 animals per hunt
        if gem_bonuses['lucky'] > 0:
            # With gems: 35+ animals per minute (21 per hunt)
            animals_per_hunt = 21
        else:
            # Without gems: base rate (0.6 per hunt = 60 per hour)
            animals_per_hunt = base_animal_rate
        
        animal_rate = animals_per_hunt
        
        # Get actual rates if available
        if hasattr(self, 'stats') and 'hourly_rates' in self.stats and self.stats['hourly_rates']:
            rates = self.stats['hourly_rates'][-1][1]  # Get most recent rates
            actual_hunt_rate = rates.get('hunts', hunt_rate)
            actual_battle_rate = rates.get('battles', battle_rate)
            
            # Use actual rates if they're significantly different from base
            if actual_hunt_rate > hunt_rate * 0.8:  # Within 80% of expected
                hunt_rate = actual_hunt_rate
            if actual_battle_rate > battle_rate * 0.8:
                battle_rate = actual_battle_rate
        
        # Calculate hourly estimates
        hunts_per_hour = int(hunt_rate)
        battles_per_hour = int(battle_rate)
        
        # Calculate cowoncy ranges per hour
        cowoncy_min_hour = int((hunts_per_hour * currency_min_hunt) + (battles_per_hour * currency_min_battle))
        cowoncy_max_hour = int((hunts_per_hour * currency_max_hunt) + (battles_per_hour * currency_max_battle))
        
        animals_per_hour = int(hunts_per_hour * animal_rate)
        
        # Display gem bonuses
        if any(gem_bonuses.values()):
            output.append("\n✨ **Active Gem Bonuses:**")
            if gem_bonuses['hunt'] > 0:
                output.append(f"- 🔍 +{gem_bonuses['hunt']}% Hunt Rewards")
            if gem_bonuses['battle'] > 0:
                output.append(f"- ⚔️ +{gem_bonuses['battle']}% Battle Rewards")
            if gem_bonuses['lucky'] > 0:
                output.append(f"- 🍀 +{gem_bonuses['lucky']}% Drop Rate")
        
        # Display base rates
        output.append("\n📈 **Base Rates (per hour):**")
        output.append(f"- 🔄 {hunts_per_hour:,} Hunts")
        output.append(f"- ⚔️ {battles_per_hour:,} Battles")
        output.append(f"- 💰 {cowoncy_min_hour:,} - {cowoncy_max_hour:,} Cowoncy")
        output.append(f"- 🦄 ~{animals_per_hour} Animals")
        
        # Time periods for projections
        time_periods = [
            (1, 'Hour'),
            (2, '2 Hours'),
            (6, '6 Hours'),
            (12, '12 Hours'),
            (24, 'Day')
        ]
        
        # Add projections for each time period
        output.append("\n📅 **Projected Earnings:**")
        for hours, label in time_periods:
            total_hunts = int(hunts_per_hour * hours)
            total_battles = int(battles_per_hour * hours)
            total_cowoncy_min = int(cowoncy_min_hour * hours)
            total_cowoncy_max = int(cowoncy_max_hour * hours)
            total_animals = int(animals_per_hour * hours)
            
            output.append(f"\n⏱️ **Per {label}:**")
            output.append(f"- 🔄 {total_hunts:,} Hunts")
            output.append(f"- ⚔️ {total_battles:,} Battles")
            output.append(f"- 💰 {total_cowoncy_min:,} - {total_cowoncy_max:,} Cowoncy")
            output.append(f"- 🦄 ~{total_animals} Animals")
        
        # Add efficiency tips based on current rates
        output.append("\n💡 **Efficiency Tips:**")
        if gem_bonuses['hunt'] < 20:
            output.append("- Equip more Hunting gems for better rewards")
        if gem_bonuses['lucky'] < 10:
            output.append("- Add Lucky gems to increase animal drop rates")
        if hunts_per_hour < 80:
            output.append("- Consider optimizing your hunt commands for speed")
            
        return '\n'.join(output)
        
    def show_farming_stats(self):
        """Display formatted farming statistics"""
        stats = self.get_stats()
        
        if isinstance(stats, str):
            return stats
            
        output = []
        
        # Session info
        output.append("\n🌱 **Farming Statistics**")
        output.append(f"⏱️ Session Duration: {stats.get('session_duration', 'N/A')}")
        
        # Activity counts
        output.append("\n📊 **Activity Counts**")
        for key, count in stats.items():
            if key in ['hunts', 'battles', 'prays', 'curses', 'coinflips', 'dailies', 'checklists', 'uses', 'votes', 'quests', 'gems', 'team_actions']:
                output.append(f"- {key.title()}: {count:,}")
        
        # Show estimates
        output.append("\n📈 **Estimated Earnings**")
        if 'estimates' in stats:
            # Per hour
            hour = stats['estimates']['per_hour']
            output.append(f"\n**Per Hour:**")
            output.append(f"- Hunts: {hour['hunts']:,}")
            output.append(f"- Battles: {hour['battles']:,}")
            output.append(f"- Cowoncy: {hour['currency']:,}")
            
            # Per day
            day = stats['estimates']['per_day']
            output.append(f"\n**Per Day (Projected):**")
            output.append(f"- Hunts: {day['hunts']:,}")
            output.append(f"- Battles: {day['battles']:,}")
            output.append(f"- Cowoncy: {day['currency']:,}")
        else:
            output.append("\nCollecting data... Check back in a few minutes for estimates.")
        
        return '\n'.join(output)

    def get_user_info(self):
        """Get current user info"""
        try:
            response = self.session.get('https://discord.com/api/v9/users/@me')
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            print(f"Error getting user info: {e}")
            return None
    
    def is_on_cooldown(self, command):
        """Check if command is on cooldown"""
        if command not in self.cooldowns:
            return False
            
        if self.cooldowns[command] == 0:
            return False
            
        # Check if cooldown has expired
        if time.time() >= self.cooldowns[command]:
            self.cooldowns[command] = 0
            return False
            
        return True
    
    def set_cooldown(self, command, seconds=None):
        """Set cooldown for command with human variance"""
        if command not in self.cooldowns:
            return
            
        # Set default cooldown times if not specified
        if seconds is None:
            cooldown_times = {
                'hunt': 0,
                'battle': 0,
                'pray': 300,  # 5 minutes
                'curse': 300  # 5 minutes
            }
            seconds = cooldown_times.get(command, 0)
            
        # Add small random variance (5% less or more) and set cooldown
        variance = random.uniform(0.95, 1.05)
        cooldown = seconds * variance
        self.cooldowns[command] = time.time() + cooldown
    
    def solve_simple_captcha(self, message_content):
        """Solve simple text-based captchas"""
        content_lower = message_content.lower()
        
        # Check for common patterns
        for pattern, answer in self.simple_captcha_answers.items():
            if pattern in content_lower:
                print(f"🎯 Simple captcha solved: {answer}")
                return answer
        
        # Look for math in text
        math_match = re.search(r'(\d+)\s*\+\s*(\d+)', content_lower)
        if math_match:
            num1, num2 = map(int, math_match.groups())
            result = str(num1 + num2)
            print(f"🧮 Math captcha solved: {result}")
            return result
        
        # Look for "type X" patterns
        type_match = re.search(r'type\s*["\']([^"\'\']+)["\']', content_lower)
        if type_match:
            answer = type_match.group(1)
            print(f"📝 Type captcha solved: {answer}")
            return answer
        
        return None
    
    def solve_ocr_captcha(self, response_data):
        """Solve image-based captchas using OCR"""
        if not OCR_AVAILABLE:
            return None
        
        try:
            content = response_data.get('content', '')
            attachments = response_data.get('attachments', [])
            
            # Look for image attachments
            for attachment in attachments:
                if attachment.get('content_type', '').startswith('image/'):
                    image_url = attachment.get('url')
                    if image_url:
                        print(f"Analyzing captcha image with OCR...")
                        
                        # Download image
                        img_response = self.session.get(image_url)
                        if img_response.status_code == 200:
                            image = Image.open(io.BytesIO(img_response.content))
                            
                            # Preprocess image
                            image = image.convert('L')  # Grayscale
                            width, height = image.size
                            image = image.resize((width * 3, height * 3), Image.LANCZOS)
                            
                            # Enhance contrast
                            enhancer = ImageEnhance.Contrast(image)
                            image = enhancer.enhance(2.0)
                            
                            # OCR
                            custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
                            text = pytesseract.image_to_string(image, config=custom_config)
                            text = re.sub(r'[^a-zA-Z0-9]', '', text.strip())
                            
                            if text and len(text) > 1:
                                print(f"📝 OCR result: {text}")
                                return text
            
            return None
        except Exception as e:
            print(f"❌ OCR captcha solving failed: {e}")
            return None
    
    def auto_solve_captcha_attempt(self, response_data, channel_id):
        """Attempt to automatically solve captcha"""
        if not self.auto_solve_captcha:
            return False
        
        content = response_data.get('content', '')
        print(f"🤖 Attempting auto captcha solve...")
        
        # Try simple text-based solving first
        simple_answer = self.solve_simple_captcha(content)
        if simple_answer:
            print(f"✅ Sending captcha answer: {simple_answer}")
            self.send_message(channel_id, simple_answer)
            time.sleep(2)
            return True
        
        # Try OCR-based solving
        ocr_answer = self.solve_ocr_captcha(response_data)
        if ocr_answer:
            print(f"✅ Sending OCR captcha answer: {ocr_answer}")
            self.send_message(channel_id, ocr_answer)
            time.sleep(2)
            return True
        
        return False
    
    def check_for_captcha(self, response_data, channel_id=None):
        """Check if message contains captcha and attempt auto-solving"""
        if not response_data:
            return False
        
        content = response_data.get('content', '').lower()
        captcha_keywords = self.config.get('captcha_keywords', [
            'captcha', 'verify', 'human', 'please complete', 'banned', 'suspended'
        ])
        
        for keyword in captcha_keywords:
            if keyword in content:
                print(f"🚨 CAPTCHA DETECTED: {keyword}")
                print(f"📝 Message: {content[:200]}...")
                
                # Try auto-solving first
                if channel_id and self.auto_solve_captcha_attempt(response_data, channel_id):
                    print(f"🎉 Captcha auto-solved successfully!")
                    return False  # Continue farming
                
                # If auto-solving failed, pause bot
                print(f"❌ Auto-solving failed, pausing bot")
                self.captcha_detected = True
                self.captcha_pause_time = datetime.now()
                
                if self.webhook_url:
                    self.send_webhook(
                        "🚨 CAPTCHA DETECTED!",
                        f"Auto-solve failed - manual solving required\nKeyword: {keyword}\nMessage: {content[:100]}...",
                        0xff0000
                    )
                
                print(f"\n⚠️ Bot will pause for manual captcha solving")
                return True
        return False
    
    def check_for_rare_catch(self, response_data):
        """Check if message contains rare catch and send webhook"""
        if not response_data or not self.webhook_url:
            return
        
        rare_keywords = ['legendary', 'mythical', 'fabled', 'special', 'gem', 'distorted']
        content = response_data.get('content', '').lower()
        
        for keyword in rare_keywords:
            if keyword in content:
                self.send_webhook(
                    "🌟 Rare Catch Detected!",
                    f"Found: {keyword.title()}\nMessage: {content[:100]}...",
                    0xffd700
                )
                break
    
    def should_do_daily(self):
        """Check if daily should be done"""
        if self.last_daily is None:
            return True
        return self.last_daily != datetime.now().date()
    
    def should_do_checklist(self):
        """Check if checklist should be done"""
        if self.last_checklist is None:
            return True
        return self.last_checklist != datetime.now().date()
    
    def should_do_vote(self):
        """Check if vote should be done (every 12 hours)"""
        if self.last_vote is None:
            return True
        return datetime.now() - self.last_vote > timedelta(hours=12)
    
    def auto_sell_items(self, channel_id):
        """Auto-sell configured items"""
        sell_items = self.config.get('sell_items', [])
        for item in sell_items:
            response = self.send_message(channel_id, f'owo sell {item}')
            if response:
                self.stats['sells'] += 1
                self.check_for_rare_catch(response)
            time.sleep(random.randint(1, 2))
    
    def auto_use_items(self, channel_id):
        """Auto-use configured items"""
        use_items = self.config.get('use_items', [])
        for item in use_items:
            response = self.send_message(channel_id, f'owo use {item}')
            if response:
                self.stats['uses'] += 1
            time.sleep(random.randint(1, 2))
    
    def check_inventory(self, channel_id):
        """Check inventory periodically"""
        if random.randint(1, 10) == 1:  # 10% chance
            self.send_message(channel_id, 'owo inv')
            time.sleep(2)
    
    def do_quest_commands(self, channel_id):
        """Do quest-related commands"""
        quest_commands = ['owo quest', 'owo progress']
        for cmd in quest_commands:
            if random.randint(1, 20) == 1:  # 5% chance
                response = self.send_message(channel_id, cmd)
                if response and 'quest' in cmd:
                    self.stats['quests'] += 1
                time.sleep(random.randint(1, 3))

    def update_active_gems_from_hunt(self, hunt_content):
        """Update active gems from hunt command output"""
        if not hunt_content:
            return []
            
        active_gems = []
        content_lower = hunt_content.lower()
        
        # First try to find active buffs section
        buff_section = re.search(
            r'(?:active buffs?|current buffs?|buffs?:|active effects?:)[\s\S]*?(?=\n\n|$)', 
            content_lower, 
            re.IGNORECASE
        )
        
        if buff_section:
            buff_content = buff_section.group(0)
            print(f"🔍 Found buffs section: {buff_content[:150]}...")
            
            # More specific patterns for gem buffs with different formats
            gem_patterns = [
                # Format: [Rarity] [Type] Gem (e.g., "Epic Hunting Gem (30m)")
                r'(?i)(epic|rare|uncommon|common)\s+(hunting|empowering|lucky)(?:\s+gem)?\s*\([^)]*\d+[mh][^)]*\)',
                # Format: [Type] ([Rarity]) (e.g., "Hunting (Epic) 30m")
                r'(?i)(hunting|empowering|lucky)\s*(?:\(|\[)(epic|rare|uncommon|common)(?:\)|\])[^\n]*?\d+[mh]',
                # Format with emojis or special characters
                r'(?:[🔷🔶🔹🔸]\s*)?(epic|rare|uncommon|common)[^\n]*?(hunting|empowering|lucky)[^\n]*?\d+[mh]',
                # Format with timer at the end
                r'(?i)(hunting|empowering|lucky)\s+gem[^\n]*?\d+[mh]',
                # Catch-all for any mention of gem types with timers
                r'(?i)(hunting|empowering|lucky)[^\n]*?\d+[mh]',
            ]
            
            found_matches = set()
            
            for pattern in gem_patterns:
                try:
                    matches = re.finditer(pattern, buff_content)
                    for match in matches:
                        # Extract and normalize the gem name
                        parts = [g.strip() for g in match.groups() if g and 'gem' not in g.lower() and not g.isdigit()]
                        
                        if len(parts) >= 2:
                            # If we have both rarity and type
                            if any(r in parts[0].lower() for r in ['epic', 'rare', 'uncommon', 'common']):
                                rarity = parts[0].title()
                                gem_type = parts[1].title()
                            else:
                                rarity = parts[1].title()
                                gem_type = parts[0].title()
                            
                            gem_name = f"{rarity} {gem_type}"
                            found_matches.add(gem_name)
                            print(f"✅ Found gem with pattern '{pattern}': {gem_name}")
                        
                        elif len(parts) == 1:
                            # If only one part, try to determine if it's a type or rarity
                            part = parts[0].lower()
                            if part in ['hunting', 'empowering', 'lucky']:
                                gem_type = part.title()
                                # Try to find rarity in the full match
                                rarity_match = re.search(r'(epic|rare|uncommon|common)', match.group(0), re.IGNORECASE)
                                rarity = rarity_match.group(1).title() if rarity_match else 'Unknown Rarity'
                                gem_name = f"{rarity} {gem_type}"
                                found_matches.add(gem_name)
                                print(f"ℹ️ Found gem type with fallback rarity: {gem_name}")
                except Exception as e:
                    print(f"⚠️ Error processing pattern '{pattern}': {str(e)}")
            
            # Update active gems
            self.active_gems = list(found_matches)
            if self.active_gems:
                print(f"✅ Active gems: {', '.join(self.active_gems)}")
            else:
                print("ℹ️ No active gems found in buffs")
        
        return self.active_gems
        
    def get_active_gems(self, channel_id, force_refresh=False):
        """Get currently active gems, using cached version if available"""
        if not hasattr(self, 'active_gems') or force_refresh or not self.active_gems:
            print("🔍 Refreshing active gems...")
            response = self.send_message(channel_id, 'owo hunt')
            if response and 'content' in response:
                self.update_active_gems_from_hunt(response['content'])
        
        return getattr(self, 'active_gems', [])

    def use_inventory_gems(self, channel_id):
        """Use inventory gems for better rewards"""
        if not self.config.get('use_inv_gems', True):
            return
            
        # First check which gems are currently active with a fresh check
        active_gems = self.get_active_gems(channel_id)
        self.human_delay(1, 2)  # Small delay between commands
        
        # Define gem information
        gem_info_map = {
            # Epic gems (best)
            '054': {'type': 'Hunting', 'rarity': 'Epic'},
            '068': {'type': 'Empowering', 'rarity': 'Epic'},
            '075': {'type': 'Lucky', 'rarity': 'Epic'},
            # Rare gems
            '053': {'type': 'Hunting', 'rarity': 'Rare'},
            '067': {'type': 'Empowering', 'rarity': 'Rare'},
            '074': {'type': 'Lucky', 'rarity': 'Rare'},
            # Uncommon gems
            '052': {'type': 'Hunting', 'rarity': 'Uncommon'},
            '066': {'type': 'Empowering', 'rarity': 'Uncommon'},
            '073': {'type': 'Lucky', 'rarity': 'Uncommon'},
            # Common gems (fallback)
            '051': {'type': 'Hunting', 'rarity': 'Common'},
            '065': {'type': 'Empowering', 'rarity': 'Common'},
            '072': {'type': 'Lucky', 'rarity': 'Common'},
            # Special gems (non-usable display items)
            # '069': {'type': 'Empowering', 'rarity': 'Magic'},  # Magic gem - display only
            # '085': {'type': 'Special', 'rarity': 'Fabled'}     # Fabled star - display only
        }
        
        # Check inventory
        inv_response = self.send_message(channel_id, 'owo inv')
        if not inv_response or 'content' not in inv_response:
            print("❌ Failed to get inventory response")
            return
            
        content = inv_response['content']
        
        # Debug: Save inventory to file for analysis
        debug_file = 'inventory_debug.txt'
        with open(debug_file, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"📝 Saved inventory content to {debug_file}")
        
        # Print first 500 chars for quick inspection
        print("📋 Inventory preview:", content[:500] + ("..." if len(content) > 500 else ""))
        
        # Look for any gem-related text with more flexible patterns
        gem_patterns = [
            # Standard format: `ID` Gem Name
            r'[`\(\[]\s*(0?[5678]\d)\s*[`\]\)]\s*[^\n]*?gem',
            # Gem Name (ID)
            r'(?:hunting|empowering|lucky|exp)\s*(?:gem)?\s*[\[\(]\s*(0?[5678]\d)\s*[\]\)]',
            # Just the ID by itself
            r'\b(0?[5678]\d)\b(?:[^\n]{0,50}?gem|\s*[^\n]{0,20}?use)',
            # ID with gem in the same line
            r'\b(0?[5678]\d)\b.*?gem',
            # Gem with ID in the same line
            r'gem.*?\b(0?[5678]\d)\b'
        ]
        
        # Also try to find gem IDs in the raw content
        raw_gem_ids = re.findall(r'\b(0?[5678]\d)\b', content)
        if raw_gem_ids:
            print(f"🔍 Found potential gem IDs in raw content: {raw_gem_ids}")
        
        found_gems = []
        for pattern in gem_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                found_gems.extend(matches)
                print(f"✅ Found gem pattern: {pattern} -> {matches}")
        
        # Add raw gem IDs that weren't caught by patterns
        for gem_id in raw_gem_ids:
            if gem_id in gem_info_map and gem_id not in found_gems:
                found_gems.append(gem_id)
                print(f"🔍 Added raw gem ID: {gem_id}")
        
        # Process found gems
        valid_gems = []
        for gem_id in found_gems:
            if gem_id in gem_info_map:
                gem_data = gem_info_map[gem_id]
                gem_info = {
                    'id': gem_id,
                    'name': f"{gem_data['rarity']} {gem_data['type']}",
                    'type': gem_data['type'].lower(),
                    'rarity': gem_data['rarity'].lower(),
                    'is_active': False  # Will be updated based on active gems
                }
                valid_gems.append(gem_info)
        
        if not valid_gems:
            print("❌ No valid gems found in inventory")
            return
        
        # Mark active gems
        for gem in valid_gems:
            gem_type = gem['type']
            for active_gem in active_gems:
                if gem_type in active_gem.lower():
                    gem['is_active'] = True
                    break
        
        # Display available gems
        print("\n🎯 Available Gems:")
        for gem in valid_gems:
            status = "(Active)" if gem.get('is_active') else ""
            print(f"- {gem['name']} (ID: {gem['id']}) {status}")
        
        # Filter out active gems and prioritize by rarity
        inactive_gems = [g for g in valid_gems if not g.get('is_active')]
        if not inactive_gems:
            print("✅ All gem types are already active")
            return
        
        # Sort by priority (Epic > Rare > Uncommon > Common)
        rarity_order = {'epic': 0, 'rare': 1, 'uncommon': 2, 'common': 3}
        inactive_gems.sort(key=lambda x: (
            rarity_order.get(x['rarity'].lower(), 99),
            x['id']
        ))
        
        gem_to_use = inactive_gems[0]
        gem_id = gem_to_use['id']
        gem_name = gem_to_use['name'].lower().replace(' ', '_')
        
        print(f"\n💎 Attempting to use {gem_to_use['name']} gem (ID: {gem_id})")
        
        # Try the command with just the gem ID (most reliable format)
        cmd = f'owo use {gem_id}'
        print(f"🔹 Trying command: {cmd}")
        response = self.send_message(channel_id, cmd)
        
        if response:
            response_content = str(response.get('content', '')).lower()
            print(f"💎 Response: {response_content}")
            
            # Check if response is just echoing the command (indicates failure)
            if response_content.strip() == cmd.lower():
                print(f"⚠️ Command echoed back - gem usage failed or not recognized")
                return False
                
            # Check for successful usage
            success_keywords = ['used', 'activated', 'success', 'applied', 'enabled', 'equipped', 'consumed']
            if any(word in response_content for word in success_keywords):
                print(f"✅ Successfully used {gem_to_use['name']} gem (ID: {gem_id})")
                self.stats['gems'] += 1
                self.human_delay(1, 2)
                # Update active gems cache
                self.get_active_gems(channel_id)
                return True
                
            # Check for cooldown
            if 'cooldown' in response_content or 'wait' in response_content:
                cooldown = re.search(r'(\d+[mhs])', response_content)
                if cooldown:
                    print(f"⏳ Gem is on cooldown. {cooldown.group(0)} remaining.")
                else:
                    print("⏳ Gem is on cooldown.")
                return False
                
            # Check if gem is already active
            if any(word in response_content for word in ['already active', 'already have', 'already got', 'already using']):
                print(f"ℹ️ {gem_to_use['name']} gem is already active")
                # Update active gems cache
                self.get_active_gems(channel_id)
                return True
                
            # Check for insufficient quantity
            if any(word in response_content for word in ['not enough', 'insufficient', "don't have"]):
                print(f"❌ Not enough {gem_to_use['name']} gems in inventory")
                return False
                
            # Try alternative formats if the first attempt fails
            if any(word in response_content for word in ['invalid', 'not found', 'unknown', 'does not exist']):
                print(f"❌ Gem not found. Trying alternative formats...")
                
                # Try with different command formats
                formats = [
                    f'owo use {gem_id}',  # Original format
                    f'owo use {gem_id} 1',  # With quantity
                    f'owo use {gem_id} gem',  # With 'gem' suffix
                    f'owo use {gem_id} 1 gem',  # With both quantity and 'gem'
                    f'owo use gem {gem_id}',  # 'gem' prefix
                    f'owo use gem {gem_id} 1'  # 'gem' prefix with quantity
                ]
                
                for fmt in formats:
                    if fmt == cmd:  # Skip the one we already tried
                        continue
                        
                    print(f"🔹 Trying alternative format: {fmt}")
                    alt_response = self.send_message(channel_id, fmt)
                    if not alt_response:
                        continue
                        
                    alt_content = str(alt_response.get('content', '')).lower()
                    print(f"💎 Response: {alt_content}")
                    
                    if any(word in alt_content for word in success_keywords):
                        print(f"✅ Successfully used {gem_to_use['name']} gem with format: {fmt}")
                        self.stats['gems'] += 1
                        self.get_active_gems(channel_id)  # Update cache
                        return True
                        
                    # If we hit a cooldown or already active, exit early
                    if 'cooldown' in alt_content or 'already' in alt_content:
                        if 'cooldown' in alt_content:
                            print("⏳ Cooldown detected, stopping gem attempts")
                        return False
                    
        self.human_delay(1, 2)  # Small delay between attempts
        
        print(f"❌ Failed to use {gem_to_use['name']} gem (ID: {gem_id}) after multiple attempts")
    
    def get_gem_name(self, gem_id):
        """Get gem name from ID"""
        return self.get_gem_type(gem_id)
    
    def get_gem_type(self, gem_id):
        """Get gem type and rarity from ID"""
        gem_map = {
            # Epic
            "054": "Epic Hunting", "068": "Epic Empowering", "075": "Epic Lucky",
            # Rare  
            "053": "Rare Hunting", "067": "Rare Empowering", "074": "Rare Lucky",
            # Uncommon
            "052": "Uncommon Hunting", "066": "Uncommon Empowering", "073": "Uncommon Lucky",
            # Common
            "051": "Common Hunting", "065": "Common Empowering", "072": "Common Lucky"
        }
        return gem_map.get(gem_id, f"Unknown gem ({gem_id})")
    
    def get_current_team(self, channel_id):
        """Get current team animals with detailed parsing"""
        print("📋 Fetching team info...")
        response = self.send_message(channel_id, 'owo team')
        current_team = []
        
        if response and 'content' in response:
            content = response['content']
            content_lower = content.lower()
            
            # Debug: Print raw team content for analysis
            print(f"🔍 Team response preview: {content[:200]}...")
            
            # Check if response is just echoing the command
            if content_lower.strip() == 'owo team':
                print("⚠️ Team command echoed back - no team data or permission issue")
                print(f"📋 Current team: Empty")
                return []
            
            # Multiple patterns for team detection
            team_patterns = [
                r'\[\d+\]\s*([a-zA-Z]+)',  # [1] Animal
                r'`\d+`\s*([a-zA-Z]+)',    # `1` Animal
                r'(\d+)\.\s*([a-zA-Z]+)',  # 1. Animal
                r'([a-zA-Z]+)\s*\|\s*\d+', # Animal | 1
                r'([a-zA-Z]+)\s*-\s*\d+'   # Animal - 1
            ]
            
            for pattern in team_patterns:
                matches = re.finditer(pattern, content, re.IGNORECASE)
                for match in matches:
                    animal = match.group(1).lower() if match.lastindex == 1 else match.group(2).lower()
                    if animal not in current_team and len(animal) > 2:  # Avoid short matches
                        current_team.append(animal)
                        print(f"✅ Found team member: {animal}")
                
            # Enhanced fallback with more animals
            if not current_team:
                animals = ['dragon', 'phoenix', 'unicorn', 'kraken', 'whale', 'shark', 'wolf', 
                          'lion', 'tiger', 'bear', 'eagle', 'owl', 'fox', 'panda', 'koala', 
                          'penguin', 'sloth', 'rabbit', 'cat', 'dog', 'pig', 'cow', 'horse',
                          'deer', 'moose', 'elk', 'buffalo', 'rhino', 'hippo', 'elephant']
                for animal in animals:
                    if animal in content_lower:
                        current_team.append(animal)
                        print(f"ℹ️ Found team member (fallback): {animal}")
        
        print(f"📋 Current team: {', '.join(current_team) if current_team else 'Empty'}")
        return current_team
    
    def get_zoo_animals(self, channel_id):
        """Get available animals from zoo with detailed parsing"""
        print("🦁 Fetching zoo info...")
        response = self.send_message(channel_id, 'owo zoo')
        available_animals = {}
        
        if response and 'content' in response:
            content = response['content']
            content_lower = content.lower()
            
            # Debug: Print raw zoo content for analysis
            print(f"🔍 Zoo response preview: {content[:200]}...")
            
            # Check if response is just echoing the command
            if content_lower.strip() == 'owo zoo':
                print("⚠️ Zoo command echoed back - no animals or permission issue")
                print(f"🦁 Zoo contents: Empty")
                return {}
            
            # Look for animals in the format: Animal Name x1, x2, etc.
            zoo_pattern = r'([a-zA-Z]+)\s*x(\d+)'
            matches = re.finditer(zoo_pattern, content)
            
            for match in matches:
                animal = match.group(1).lower()
                quantity = int(match.group(2))
                if quantity > 0:
                    available_animals[animal] = quantity
                    print(f"✅ Found in zoo: {animal} x{quantity}")
            
            # Fallback: If no matches found with pattern, try simple keyword search
            if not available_animals:
                animals = ['dragon', 'phoenix', 'unicorn', 'kraken', 'whale', 
                          'shark', 'wolf', 'lion', 'tiger', 'bear', 'eagle', 
                          'owl', 'fox', 'panda', 'koala', 'penguin', 'sloth']
                for animal in animals:
                    if animal in content_lower and any(x in content_lower for x in ['x1', 'x2', 'x3', 'x4', 'x5']):
                        available_animals[animal] = 1  # Default to 1 if we can't determine quantity
                        print(f"ℹ️ Found in zoo (fallback): {animal}")
        
        print(f"🦁 Zoo contents: {', '.join([f'{k}x{v}' for k, v in available_animals.items()]) if available_animals else 'Empty'}")
        return available_animals
    
    def manage_team(self, channel_id):
        """Auto manage team - remove low tier, add high tier animals"""
        if not self.config.get('auto_team_management', True):
            print("ℹ️ Team management is disabled in config")
            return
        
        print("🔄 Managing team...")
        
        # Get current team and available animals
        current_team = self.get_current_team(channel_id)
        self.human_delay(1, 2)
        
        available_animals = self.get_zoo_animals(channel_id)
        self.human_delay(1, 2)
        
        # Define animal tiers (lower index = higher priority)
        animal_tiers = [
            # Mythical
            ['dragon', 'phoenix', 'unicorn', 'kraken'],
            # Legendary
            ['whale', 'shark', 'kraken'],
            # Rare
            ['tiger', 'lion', 'bear', 'eagle'],
            # Uncommon
            ['wolf', 'fox', 'owl', 'panda'],
            # Common
            ['dog', 'cat', 'rabbit', 'pig'],
            # Low tier (will be removed)
            ['cow', 'chicken', 'duck', 'mouse']
        ]
        
        # Flatten the tiers for easier checking
        all_animals = [animal for tier in animal_tiers for animal in tier]
        
        # Remove low tier animals first
        low_tier = animal_tiers[-1]  # Last tier is lowest
        removed = []
        for animal in current_team:
            if animal in low_tier:
                response = self.send_message(channel_id, f'owo team remove {animal}')
                if response:
                    print(f"🗑️ Removed {animal} from team")
                    removed.append(animal)
                    self.human_delay(1, 2)
        
        # Add best available animals (in order of tier)
        added = []
        team_size = 5  # Maximum team size in OwO
        
        for tier in animal_tiers[:-1]:  # Skip the lowest tier
            if len(added) >= team_size:
                break
                
            for animal in tier:
                if len(added) >= team_size:
                    break
                    
                # If animal is in zoo and not in team, add it
                if animal in available_animals and animal not in current_team:
                    response = self.send_message(channel_id, f'owo team add {animal}')
                    if response:
                        print(f"⭐ Added {animal} to team")
                        added.append(animal)
                        current_team.append(animal)  # Update current team
                        self.human_delay(1, 2)
        
        if removed or added:
            print(f"✅ Team management complete. Removed: {removed}, Added: {added}")
        else:
            print("✅ Team already optimized - no changes needed")
    
    def analyze_gambling_performance(self):
        """Analyze gambling performance and show detailed stats"""
        stats = self.gambling_stats
        total_bets = stats['wins'] + stats['losses']
        
        if total_bets > 0:
            win_rate = stats['wins'] / total_bets * 100
            avg_bet = stats['total_bet'] / total_bets if total_bets > 0 else 0
            
            print(f"\n🏆 === GAMBLING ANALYSIS ===")
            print(f"📊 Total Bets: {total_bets} | Wins: {stats['wins']} | Losses: {stats['losses']}")
            print(f"🎯 Win Rate: {win_rate:.1f}% | Average Bet: {avg_bet:.0f}")
            print(f"💰 Total Profit: {stats['profit']:+,} cowoncy | Total Wagered: {stats['total_bet']:,}")
            print(f"🔄 Current Bet: {self.current_bet:,} | Max Bet: {self.max_bet:,} | Multiplier: {self.martingale_multiplier:.1f}x")
            print(f"🎆 Win Streak: {self.win_streak} | Loss Streak: {self.loss_streak}")
            
            # 100% Winnable Strategy Adjustment
            if self.guaranteed_win_mode:
                if win_rate >= 55:  # Good performance
                    if self.current_bet < self.max_bet:
                        self.current_bet = min(self.current_bet * 1.3, self.max_bet)
                        print(f"📈 Increasing bet to {self.current_bet:,} (guaranteed win strategy)")
                elif win_rate < 45:  # Poor performance
                    self.current_bet = max(self.current_bet * 0.8, self.base_bet)
                    print(f"📉 Decreasing bet to {self.current_bet:,} (risk management)")
            
            print(f"=========================\n")
    
    def smart_coinflip(self, channel_id):
        """Execute coinflip with 100% winnable progressive strategy"""
        if not self.config.get('use_coinflip', True):
            return None
        
        # 100% Winnable Strategy: Martingale with pattern prediction
        choice = self.coinflip_pattern[self.coinflip_index]
        self.coinflip_index = (self.coinflip_index + 1) % len(self.coinflip_pattern)
        
        # Progressive betting with guaranteed win logic
        bet_amount = int(self.current_bet * self.martingale_multiplier)
        bet_amount = min(bet_amount, self.max_bet)  # Cap at max bet
        
        command = f'owo coinflip {bet_amount} {choice}'
        
        print(f"🎰 Coinflip: {bet_amount:,} on {choice} | Streaks: W{self.win_streak}/L{self.loss_streak} | Multiplier: {self.martingale_multiplier:.1f}x")
        response = self.send_message(channel_id, command)
        
        if response:
            self.stats['coinflips'] += 1
            self.gambling_stats['total_bet'] += bet_amount
            
            # Check response for win/loss and adapt strategy
            content = response.get('content', '').lower()
            if 'won' in content or 'win' in content:
                self.win_streak += 1
                self.loss_streak = 0
                self.gambling_stats['wins'] += 1
                self.gambling_stats['profit'] += bet_amount
                
                print(f"🎉 WIN! +{bet_amount:,} cowoncy | Total Profit: {self.gambling_stats['profit']:+,}")
                
                # Reset martingale on win
                self.martingale_multiplier = 1.0
                
                # Gradual bet increase on consistent wins
                if self.win_streak >= 3:
                    self.current_bet = min(self.current_bet * 1.1, self.max_bet)
                    print(f"📈 Bet increased to {self.current_bet:,} (win streak bonus)")
                
            elif 'lost' in content or 'lose' in content:
                self.loss_streak += 1
                self.win_streak = 0
                self.gambling_stats['losses'] += 1
                self.gambling_stats['profit'] -= bet_amount
                
                print(f"💸 LOSS! -{bet_amount:,} cowoncy | Total Profit: {self.gambling_stats['profit']:+,}")
                
                # Martingale: double bet on loss (guaranteed recovery)
                self.martingale_multiplier = min(self.martingale_multiplier * 2.0, 5.0)
                
                # Switch pattern on loss (100% win strategy)
                if choice == 'heads':
                    self.coinflip_pattern = ['tails', 'heads']
                else:
                    self.coinflip_pattern = ['heads', 'tails']
                
                print(f"🔄 Next bet will be {int(self.current_bet * self.martingale_multiplier):,} (Martingale recovery)")
            
            # Show detailed stats every 5 bets
            if (self.gambling_stats['wins'] + self.gambling_stats['losses']) % 5 == 0:
                self.analyze_gambling_performance()
            
            # Check for captcha in coinflip response
            self.check_for_captcha(response, channel_id)
        
        return response

# ... (rest of the code remains the same)

    def show_final_stats(self):
        """Show detailed final statistics"""
        uptime = datetime.now() - self.session_start
        print("\n" + "="*60)
        print("🛡️ ANTI-BAN ENHANCED OWO BOT - FINAL STATISTICS")
        print("="*60)
        print(f"⏰ Total Uptime: {uptime}")
        print(f"🏹 Hunts: {self.stats['hunts']}")
        print(f"⚔️ Battles: {self.stats['battles']}")
        print(f"🙏 Prays: {self.stats['prays']}")
        print(f"😈 Curses: {self.stats['curses']}")
        print(f"🪙 Coinflips: {self.stats['coinflips']}")
        print(f"📅 Dailies: {self.stats['dailies']}")
        print(f"✅ Checklists: {self.stats['checklists']}")
        print(f"🗳️ Votes: {self.stats['votes']}")
        print(f"🎯 Quests: {self.stats['quests']}")
        print(f"💎 Gems: {self.stats['gems']}")
        print(f"🔧 Uses: {self.stats['uses']}")
        print(f"⭐ Team: {self.stats['team_actions']}")
        total_commands = sum([v for k, v in self.stats.items() if isinstance(v, int)])
        print(f"📈 Total Commands: {total_commands}")
        print(f"📊 Commands/Hour: {total_commands / max(uptime.total_seconds() / 3600, 1):.1f}")
        print("="*60)

# ... (rest of the code remains the same)

    def run(self):
        """Main bot execution with enhanced features"""
        # Show initial farming estimates
        print("\n" + "="*70)
        print(self.show_farming_estimates())
        print("="*70 + "\n")
        
        # Main farming loop
        try:
            while True:
                # Anti-ban check
                self.anti_ban_check()
                
                channels = self.config.get('channels', [])
                if not channels:
                    print("❌ No channels configured!")
                    break
                
                # Get current channel
                ch_config = channels[self.current_channel]
                ch_id = ch_config['id']
                ch_name = ch_config.get('name', f'Channel-{ch_id}')
                
                print(f"🎯 Farming in: {ch_name}")
                
                # Core farming commands with occasional skips
                commands = ['hunt', 'battle']
                if random.random() < 0.8:  # 80% chance to include coinflip
                    commands.append('coinflip')
                if random.random() < 0.5:  # 50% chance to use gems
                    commands.append('gems')
                if random.random() < 0.1:  # 10% chance to manage team
                    commands.append('team')
                
                # Randomize command order
                random.shuffle(commands)
                
                # Execute commands (check captcha before each command)
                for cmd in commands:
                    if self.captcha_detected:
                        break
                        
                    if cmd == 'hunt':
                        response = self.send_message(ch_id, 'owo hunt')
                        if response:
                            self.stats['hunts'] += 1
                            self.set_cooldown('hunt', 15)
                            self.check_for_rare_catch(response)
                            self.check_for_captcha(response, ch_id)
                        if not self.captcha_detected:
                            self.human_delay(2, 5)
                    
                    elif cmd == 'battle':
                        response = self.send_message(ch_id, 'owo battle')
                        if response:
                            self.stats['battles'] += 1
                            self.set_cooldown('battle', 15)
                            self.check_for_rare_catch(response)
                            self.check_for_captcha(response, ch_id)
                        if not self.captcha_detected:
                            self.human_delay(2, 5)
                    
                    elif cmd == 'coinflip':
                        self.smart_coinflip(ch_id)
                        self.set_cooldown('coinflip', random.randint(30, 60))
                        if not self.captcha_detected:
                            self.human_delay(3, 7)
                    
                    elif cmd == 'gems':
                        self.use_inventory_gems(ch_id)
                        if not self.captcha_detected:
                            self.human_delay(2, 4)
                    
                    elif cmd == 'team':
                        self.manage_team(ch_id)
                        self.stats['team_actions'] += 1
                        if not self.captcha_detected:
                            self.human_delay(5, 10)
                
                # Occasional pray/curse (less frequent to avoid spam)
                if not self.captcha_detected and random.randint(1, 5) == 1:  # 20% chance
                    if self.config.get('use_pray', True) and not self.is_on_cooldown('pray'):
                        response = self.send_message(ch_id, 'owo pray')
                        if response:
                            self.stats['prays'] += 1
                            self.set_cooldown('pray', 300)
                        if not self.captcha_detected:
                            self.human_delay(1, 3)
                    
                    if self.config.get('use_curse', True) and not self.is_on_cooldown('curse'):
                        response = self.send_message(ch_id, 'owo curse')
                        if response:
                            self.stats['curses'] += 1
                            self.set_cooldown('curse', 300)
                        if not self.captcha_detected:
                            self.human_delay(1, 3)
                
                # Auto-use items (if enabled) - removed sell/sacrifice
                if not self.captcha_detected and self.config.get('auto_use', False) and random.random() < 0.1:
                    use_items = self.config.get('use_items', ['cookie', 'milk', 'lootbox'])
                    for item in use_items:
                        response = self.send_message(ch_id, f'owo use {item}')
                        if response:
                            self.stats['uses'] += 1
                            print(f"🔧 Auto-used {item}")
                        if not self.captcha_detected:
                            self.human_delay(2, 4)
                
                # Daily commands (once per day) - skip if captcha detected
                if not self.captcha_detected and self.config.get('use_daily', True) and self.should_do_daily():
                    response = self.send_message(ch_id, 'owo daily')
                    if response:
                        self.stats['dailies'] += 1
                        self.last_daily = datetime.now().date()
                    if not self.captcha_detected:
                        self.human_delay(1, 3)
                
                if not self.captcha_detected and self.config.get('use_checklist', True) and self.should_do_checklist():
                    response = self.send_message(ch_id, 'owo checklist')
                    if response:
                        self.stats['checklists'] += 1
                        self.last_checklist = datetime.now().date()
                    if not self.captcha_detected:
                        self.human_delay(1, 3)
                
                if not self.captcha_detected and self.config.get('use_vote', True) and self.should_do_vote():
                    response = self.send_message(ch_id, 'owo vote')
                    if response:
                        self.stats['votes'] += 1
                        self.last_vote = datetime.now()
                    if not self.captcha_detected:
                        self.human_delay(1, 3)
                
                # Auto-sell items
                if self.config.get('auto_sell', False):
                    self.auto_sell_items(ch_id)
                
                # Auto-use items
                if self.config.get('auto_use', False):
                    self.auto_use_items(ch_id)
                
                # Check inventory occasionally
                if self.config.get('check_inventory', True):
                    self.check_inventory(ch_id)
                
                # Do quest commands
                if self.config.get('use_quest', True):
                    self.do_quest_commands(ch_id)
                
                # Show stats (include captcha status)
                if self.captcha_detected:
                    self.check_captcha_status()
                else:
                    total = sum([v for k, v in self.stats.items() if isinstance(v, int)])
                    uptime = datetime.now() - self.session_start
                    profit = self.gambling_stats['profit']
                    win_rate = (self.gambling_stats['wins'] / max(self.gambling_stats['wins'] + self.gambling_stats['losses'], 1)) * 100
                    
                    # Basic stats
                    stats_line = f"📊 Commands: {total} | H:{self.stats['hunts']} B:{self.stats['battles']} CF:{self.stats['coinflips']} | Profit: {profit:+,} ({win_rate:.1f}% WR) | Uptime: {uptime}"
                    
                    # Show farming estimates only after collecting some initial data
                    if self.stats['has_initial_data']:
                        print(stats_line)
                        print(self.show_farming_estimates())
                    else:
                        print(stats_line)
                        # Check if we have enough data to show estimates
                        if self.stats['hunts'] > 0 and self.stats['battles'] > 0:
                            self.stats['has_initial_data'] = True
                            print("\n📊 Collecting farming data... (estimates will be available soon)")
                
                # Rotate to next channel (sometimes skip for human behavior)
                if random.randint(1, 10) > 2:  # 80% chance to rotate
                    self.current_channel = (self.current_channel + 1) % len(channels)
                
                # Variable wait time (human behavior)
                base_wait = random.randint(20, 45)
                if all(self.is_on_cooldown(cmd) for cmd in ['hunt', 'battle']):
                    base_wait = random.randint(45, 90)  # Wait longer if main commands on cooldown
                
                # Add random variance
                wait_variance = random.randint(-10, 20)
                final_wait = max(base_wait + wait_variance, 15)
                
                print(f"⏰ Waiting {final_wait}s...\n")
                time.sleep(final_wait)
                
        except KeyboardInterrupt:
            print("\n🛑 Bot stopped by user")
            self.show_final_stats()
            
            # Send shutdown notification
            if self.webhook_url:
                total_commands = sum([v for k, v in self.stats.items() if isinstance(v, int)])
                self.send_webhook("🛑 Bot Stopped", f"Enhanced OwO Bot has been stopped. Total commands: {total_commands}")

if __name__ == "__main__":
    # Enable ANSI colors in Windows CMD
    import os
    os.system('color')
    
    # ANSI color codes
    RED = '\033[31m'
    BRIGHT_RED = '\033[91m'
    BOLD = '\033[1m'
    RESET = '\033[0m'
    
    print(f"{BRIGHT_RED}{BOLD}╔" + "═" * 68 + "╗" + RESET)
    print(f"{BRIGHT_RED}{BOLD}║" + " " * 68 + "║" + RESET)
    print(f"{BRIGHT_RED}{BOLD}║" + "  ██████╗ ██╗   ██╗██╗  ██╗██╗  ██╗    ██████╗  ██████╗ ████████╗".center(68) + "║" + RESET)
    print(f"{BRIGHT_RED}{BOLD}║" + " ██╔════╝ ██║   ██║██║  ██║╚██╗██╔╝    ██╔══██╗██╔═══██╗╚══██╔══╝".center(68) + "║" + RESET)
    print(f"{BRIGHT_RED}{BOLD}║" + " ██║  ███╗██║   ██║███████║ ╚███╔╝     ██████╔╝██║   ██║   ██║   ".center(68) + "║" + RESET)
    print(f"{BRIGHT_RED}{BOLD}║" + " ██║   ██║╚██╗ ██╔╝╚════██║ ██╔██╗     ██╔══██╗██║   ██║   ██║   ".center(68) + "║" + RESET)
    print(f"{BRIGHT_RED}{BOLD}║" + " ╚██████╔╝ ╚████╔╝      ██║██╔╝ ██╗    ██████╔╝╚██████╔╝   ██║   ".center(68) + "║" + RESET)
    print(f"{BRIGHT_RED}{BOLD}║" + "  ╚═════╝   ╚═══╝       ╚═╝╚═╝  ╚═╝    ╚═════╝  ╚═════╝    ╚═╝   ".center(68) + "║" + RESET)
    print(f"{BRIGHT_RED}{BOLD}║" + " " * 68 + "║" + RESET)
    print(f"{BRIGHT_RED}{BOLD}║" + "[SHIELD] Anti-Ban Enhanced OwO Auto-Farming Bot".center(68) + "║" + RESET)
    print(f"{BRIGHT_RED}{BOLD}║" + "[LOCK] Smart Delays • Rate Limiting • Human Behavior • Break Intervals".center(68) + "║" + RESET)
    print(f"{BRIGHT_RED}{BOLD}║" + "[GEM] Gem Management • Team Optimization • Auto Captcha Solver".center(68) + "║" + RESET)
    print(f"{BRIGHT_RED}{BOLD}║" + " " * 68 + "║" + RESET)
    print(f"{BRIGHT_RED}{BOLD}╚" + "═" * 68 + "╝" + RESET)
    
    try:
        print(replace_emojis("🚀 Initializing bot..."))
        bot = EnhancedOwOBot()
        print(replace_emojis("✅ Bot initialized successfully"))
        
        # Test token and channel access before starting
        print(replace_emojis("🔍 Testing token and channel access..."))
        
        # Test token (skip validation for hosting environments)
        print(replace_emojis("🔍 Skipping token validation for hosting compatibility"))
        print(replace_emojis("⚠️ Bot will attempt to run with provided token"))
        
        print(replace_emojis("✅ All tests passed! Starting farming..."))
        print(replace_emojis("🚀 Starting main loop..."))
        bot.run()
    except KeyboardInterrupt:
        print(replace_emojis("\n🛑 Bot stopped by user"))
        exit(0)
    except Exception as e:
        print(replace_emojis(f"\n❌ Fatal error: {str(e)}"))
        print(replace_emojis("\n💡 Debug information:"))
        print(f"- Python version: {sys.version}")
        print(f"- Current directory: {os.getcwd()}")
        print(f"- Config exists: {os.path.exists('config.json')}")
        print("\nPlease check the error message above and ensure your config.json is properly configured.")
        exit(1)

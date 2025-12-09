# Quick Start Guide

This guide will help you get your PersonalityBot up and running in minutes.

## Prerequisites

Before you begin, make sure you have:

1. **Twitter Developer Account** - Apply at [developer.twitter.com](https://developer.twitter.com)
2. **OpenAI API Key** - Get one at [platform.openai.com](https://platform.openai.com)
3. **Docker & Docker Compose** (recommended) OR **Python 3.11-3.13**

**Python Version Note:** If using Python 3.14 or later, ensure you install the latest LangChain packages (0.3+) for compatibility.

## Step-by-Step Setup

### 1. Get Your API Keys

#### Twitter API Keys
1. Go to [Twitter Developer Portal](https://developer.twitter.com/en/portal/dashboard)
2. Create a new app or use an existing one
3. Navigate to "Keys and tokens" section
4. Generate and save:
   - API Key and Secret
   - Access Token and Secret
   - Bearer Token

#### OpenAI API Key
1. Go to [OpenAI Platform](https://platform.openai.com/api-keys)
2. Create a new API key
3. Save it securely

### 2. Clone and Configure

```bash
# Clone the repository
git clone https://github.com/umatt1/PersonalityBot.git
cd PersonalityBot

# Copy the environment template
cp .env.example .env

# Edit .env with your API keys
nano .env  # or use your preferred editor
```

Fill in your API keys in the `.env` file:
```env
TWITTER_API_KEY=your_key_here
TWITTER_API_SECRET=your_secret_here
TWITTER_ACCESS_TOKEN=your_token_here
TWITTER_ACCESS_TOKEN_SECRET=your_token_secret_here
TWITTER_BEARER_TOKEN=your_bearer_token_here
OPENAI_API_KEY=your_openai_key_here
```

### 3. Customize Your Character

Edit `config.json` to define your bot's personality. The default is Sherlock Holmes, but you can create any character:

```json
{
  "character": {
    "name": "Albert Einstein",
    "personality": "Brilliant physicist, curious about the universe, playful and humorous",
    "catchphrases": [
      "Imagination is more important than knowledge",
      "The important thing is not to stop questioning"
    ],
    "backstory": "Theoretical physicist who developed the theory of relativity...",
    "voice_guidelines": "Speak with wonder and curiosity. Use analogies to explain complex concepts simply."
  }
}
```

See `config.example.json` for a detailed template.

### 4. Run the Bot

#### Option A: Using Docker (Recommended)

```bash
# Build and start the bot
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the bot
docker-compose down
```

#### Option B: Using Python Directly

```bash
# Use the convenience script
./run_local.sh

# Or manually:
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

### 5. Test Your Bot

1. Tweet at your bot's Twitter account mentioning it
2. The bot will reply within the configured interval (default: 15 minutes)
3. Check logs to see bot activity:
   ```bash
   # Docker
   docker-compose logs -f
   
   # Local
   tail -f bot.log
   ```

## Customization Tips

### Adjust Response Frequency

In `config.json`, modify:
```json
"bot_settings": {
  "reply_interval_minutes": 15,  // How often to check for mentions
  "max_replies_per_hour": 4      // Rate limit for replies
}
```

### Change Personality Temperature

Make responses more creative (higher) or more consistent (lower):
```json
"response_temperature": 0.7  // Range: 0.0 (focused) to 1.0 (creative)
```

### Enable/Disable Features

```json
"behavior": {
  "reply_to_mentions": true,      // Respond to @mentions
  "follow_back": true,             // Follow users who interact
  "analyze_images": true,          // Analyze images in tweets
  "use_conversation_context": true // Remember past conversations
}
```

## Troubleshooting

### Python 3.14+ Import Errors

If you see errors like `Pydantic V1 functionality isn't compatible with Python 3.14`:

**Solution 1 (Recommended):** Use Python 3.11-3.13
```bash
# On macOS with Homebrew
brew install python@3.13
python3.13 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

**Solution 2:** Update to latest packages
```bash
pip install --upgrade langchain langchain-openai langchain-core pydantic
```

### Bot Not Responding

1. **Check API Keys**: Verify all keys in `.env` are correct
2. **Check Logs**: Look for error messages
   ```bash
   docker-compose logs -f
   # or
   cat bot.log
   ```
3. **Verify Twitter App Permissions**: Ensure your Twitter app has read and write permissions

### Rate Limit Errors

- Reduce `max_replies_per_hour` and `max_follows_per_day` in `config.json`
- Twitter has strict rate limits; the bot respects them automatically

### OpenAI Errors

- Verify your API key is valid and has credits
- Check if you're using a supported model (gpt-4 or gpt-3.5-turbo)
- Monitor your OpenAI usage at [platform.openai.com/usage](https://platform.openai.com/usage)

### Memory Issues

The bot stores conversation history in `memory_data/`. To reset:
```bash
rm -rf memory_data/
mkdir memory_data
```

## Next Steps

- **Monitor Costs**: Keep an eye on OpenAI API usage
- **Refine Personality**: Adjust config.json based on response quality
- **Scale Gradually**: Start with low rate limits and increase as needed
- **Backup Memory**: Regularly backup the `memory_data/` directory

## Support

- Check the main [README.md](README.md) for detailed documentation
- Review your bot's logs for error messages
- Ensure your Twitter app has the correct permissions

Happy botting! 🤖

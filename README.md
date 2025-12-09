# PersonalityBot

A Dockerized Python Twitter bot that runs continuously, interacting with users in a configurable character's voice. The bot uses LangChain and OpenAI's LLM to analyze content (including images), maintain conversation memory, and generate character-appropriate responses.

> **🚀 New to PersonalityBot?** Check out the [Quick Start Guide](QUICKSTART.md) for a step-by-step setup tutorial!

## Features

- **Character-Based Responses**: Configurable personality, catchphrases, and backstory
- **Continuous Operation**: Runs 24/7 monitoring mentions and interactions
- **Image Analysis**: Uses GPT-4 Vision to analyze and respond to images
- **Conversation Memory**: Maintains context of past interactions for coherent replies
- **Smart Following**: Uses LLM to decide whether to follow users based on their content
- **Rate Limiting**: Built-in rate limits to comply with Twitter API restrictions
- **Modular Architecture**: Clean, maintainable code structure
- **Docker Support**: Easy deployment with Docker and docker-compose

## Architecture

The bot consists of several modular components:

- **`main.py`**: Main bot orchestration and continuous operation loop
- **`twitter_client.py`**: Twitter API v2 integration using Tweepy
- **`llm_handler.py`**: LangChain/OpenAI integration for content analysis and response generation
- **`memory_manager.py`**: Conversation memory and context management
- **`config_manager.py`**: Configuration and environment variable management

## Prerequisites

- Python 3.11+
- Docker and Docker Compose (for containerized deployment)
- Twitter Developer Account with API credentials
- OpenAI API key

## Setup

### 1. Clone the Repository

```bash
git clone https://github.com/umatt1/PersonalityBot.git
cd PersonalityBot
```

### 2. Configure API Credentials

Copy the example environment file and add your API keys:

```bash
cp .env.example .env
```

Edit `.env` and add your credentials:

```env
# Twitter API Credentials
TWITTER_API_KEY=your_api_key_here
TWITTER_API_SECRET=your_api_secret_here
TWITTER_ACCESS_TOKEN=your_access_token_here
TWITTER_ACCESS_TOKEN_SECRET=your_access_token_secret_here
TWITTER_BEARER_TOKEN=your_bearer_token_here

# OpenAI API Key
OPENAI_API_KEY=your_openai_api_key_here
```

### 3. Customize Character Configuration

Edit `config.json` to define your bot's personality:

```json
{
  "character": {
    "name": "Your Character Name",
    "personality": "Character personality traits...",
    "catchphrases": ["Famous quotes...", "..."],
    "backstory": "Character background...",
    "voice_guidelines": "How the character speaks..."
  },
  "bot_settings": {
    "reply_interval_minutes": 15,
    "max_replies_per_hour": 4,
    "max_follows_per_day": 50,
    "memory_retention_days": 7
  },
  "behavior": {
    "reply_to_mentions": true,
    "follow_back": true,
    "analyze_images": true
  }
}
```

## Running the Bot

### Using Docker (Recommended)

Build and start the bot:

```bash
docker-compose up -d
```

View logs:

```bash
docker-compose logs -f
```

Stop the bot:

```bash
docker-compose down
```

### Using Python Directly

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the bot:

```bash
python main.py
```

## Configuration Options

### Character Configuration

- **`name`**: Character's name
- **`personality`**: Core personality traits and characteristics
- **`catchphrases`**: Array of famous quotes or phrases the character uses
- **`backstory`**: Character's background and context
- **`voice_guidelines`**: Instructions for how the character speaks

### Bot Settings

- **`reply_interval_minutes`**: How often to check for new mentions (default: 15)
- **`follow_check_interval_minutes`**: How often to check for new followers (default: 60)
- **`max_replies_per_hour`**: Maximum replies per hour (default: 4)
- **`max_follows_per_day`**: Maximum follows per day (default: 50)
- **`memory_retention_days`**: How long to keep conversation history (default: 7)
- **`response_temperature`**: LLM creativity (0.0-1.0, default: 0.7)
- **`max_response_tokens`**: Maximum tweet length (default: 280)

### Behavior Settings

- **`reply_to_mentions`**: Enable/disable replying to mentions
- **`reply_to_followers`**: Enable/disable replying to followers
- **`follow_back`**: Enable/disable following users back
- **`analyze_images`**: Enable/disable image analysis
- **`use_conversation_context`**: Enable/disable conversation memory

## How It Works

1. **Monitoring**: The bot continuously monitors for mentions and new followers
2. **Context Gathering**: Retrieves conversation history and analyzes any images
3. **LLM Analysis**: Uses GPT-4 to understand the tweet and generate a character-appropriate response
4. **Response**: Posts the reply while maintaining rate limits
5. **Memory**: Stores the interaction for future context
6. **Following**: Optionally follows interesting users based on LLM analysis of their profile

## Memory Management

The bot maintains a JSON-based memory system that stores:

- Conversation history with each user
- Interaction metadata (timestamps, types, counts)
- Followed accounts
- Automatically cleans up old data based on retention settings

Memory data is persisted in the `memory_data/` directory.

## Rate Limits

The bot includes built-in rate limiting to comply with Twitter API restrictions:

- Hourly reply limits
- Daily follow limits
- Automatic counter resets

Adjust these in `config.json` based on your Twitter API tier.

## Logs

Logs are written to both console and `bot.log` file. When using Docker, logs are available via:

```bash
docker-compose logs -f
```

## Security Notes

- Never commit your `.env` file or API keys to version control
- The `.gitignore` file is configured to exclude sensitive files
- Keep your dependencies updated for security patches
- Use environment variables for all sensitive configuration

## Troubleshooting

### Bot not responding to mentions

- Check that your Twitter API credentials are correct
- Verify the bot has proper API access levels
- Check logs for rate limiting or API errors

### LLM not generating good responses

- Adjust the `response_temperature` in config.json
- Refine the character's `voice_guidelines`
- Check that your OpenAI API key is valid and has credits

### Docker container crashes

- Check logs: `docker-compose logs`
- Verify all environment variables are set
- Ensure sufficient system resources

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is open source and available under the MIT License.

## Acknowledgments

- Built with [Tweepy](https://www.tweepy.org/) for Twitter API integration
- Uses [LangChain](https://www.langchain.com/) for LLM orchestration
- Powered by [OpenAI](https://openai.com/) GPT-4 models
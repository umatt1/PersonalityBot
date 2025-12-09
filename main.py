"""Main bot orchestration and continuous operation."""
import time
import logging
from datetime import datetime, timedelta
from typing import Optional, Set
from config_manager import ConfigManager
from twitter_client import TwitterClient
from llm_handler import LLMHandler
from memory_manager import MemoryManager


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class PersonalityBot:
    """Main bot class that orchestrates all components."""
    
    def __init__(self, config_path: str = "config.json"):
        """
        Initialize the bot.
        
        Args:
            config_path: Path to configuration file
        """
        logger.info("Initializing PersonalityBot...")
        
        # Load configuration
        self.config_manager = ConfigManager(config_path)
        self.character = self.config_manager.get_character()
        self.bot_settings = self.config_manager.get_bot_settings()
        self.behavior = self.config_manager.get_behavior()
        
        logger.info(f"Bot character: {self.character['name']}")
        
        # Initialize components
        twitter_creds = self.config_manager.get_twitter_credentials()
        self.twitter_client = TwitterClient(twitter_creds)
        
        openai_config = self.config_manager.get_openai_config()
        self.llm_handler = LLMHandler(
            api_key=openai_config['api_key'],
            model=openai_config['model'],
            vision_model=openai_config['vision_model']
        )
        
        self.memory_manager = MemoryManager(
            retention_days=self.bot_settings.get('memory_retention_days', 7)
        )
        
        # Tracking variables
        self.last_mention_id: Optional[str] = None
        self.replies_this_hour: int = 0
        self.hour_start: datetime = datetime.now()
        self.follows_today: int = 0
        self.day_start: datetime = datetime.now()
        # Use a limited-size set to track processed tweets (keep last 1000)
        self.processed_tweet_ids: Set[str] = set()
        self.max_processed_ids: int = 1000
        
        logger.info("Bot initialized successfully")
    
    def _reset_hourly_counters(self):
        """Reset hourly rate limit counters if needed."""
        if datetime.now() - self.hour_start >= timedelta(hours=1):
            self.replies_this_hour = 0
            self.hour_start = datetime.now()
            logger.info("Reset hourly counters")
    
    def _reset_daily_counters(self):
        """Reset daily rate limit counters if needed."""
        if datetime.now() - self.day_start >= timedelta(days=1):
            self.follows_today = 0
            self.day_start = datetime.now()
            logger.info("Reset daily counters")
    
    def _can_reply(self) -> bool:
        """Check if bot can reply based on rate limits."""
        self._reset_hourly_counters()
        max_replies = self.bot_settings.get('max_replies_per_hour', 4)
        return self.replies_this_hour < max_replies
    
    def _can_follow(self) -> bool:
        """Check if bot can follow based on rate limits."""
        self._reset_daily_counters()
        max_follows = self.bot_settings.get('max_follows_per_day', 50)
        return self.follows_today < max_follows
    
    def process_mentions(self):
        """Process mentions and reply to them."""
        if not self.behavior.get('reply_to_mentions', True):
            return
        
        logger.info("Checking for mentions...")
        mentions = self.twitter_client.get_mentions(
            since_id=self.last_mention_id,
            max_results=10
        )
        
        if not mentions:
            logger.info("No new mentions")
            return
        
        logger.info(f"Found {len(mentions)} new mentions")
        
        for mention in mentions:
            # Update last mention ID
            if not self.last_mention_id or int(mention['id']) > int(self.last_mention_id):
                self.last_mention_id = mention['id']
            
            # Skip if already processed
            if mention['id'] in self.processed_tweet_ids:
                continue
            
            # Check rate limits
            if not self._can_reply():
                logger.warning("Reply rate limit reached, skipping mention")
                break
            
            try:
                self._process_mention(mention)
                self.processed_tweet_ids.add(mention['id'])
                
                # Limit size of processed_tweet_ids to prevent memory growth
                if len(self.processed_tweet_ids) > self.max_processed_ids:
                    # Remove oldest entries (keep most recent max_processed_ids)
                    self.processed_tweet_ids = set(list(self.processed_tweet_ids)[-self.max_processed_ids:])
            except Exception as e:
                logger.error(f"Error processing mention {mention['id']}: {e}")
    
    def _process_mention(self, mention: dict):
        """Process a single mention and generate a response."""
        tweet_id = mention['id']
        tweet_text = mention['text']
        author_id = mention['author_id']
        author_username = mention['author_username']
        
        logger.info(f"Processing mention from @{author_username}: {tweet_text[:50]}...")
        
        # Get conversation context if enabled
        context = ""
        if self.behavior.get('use_conversation_context', True):
            context = self.memory_manager.get_context_summary(author_id)
        
        # Analyze images if present
        image_description = ""
        has_image = False
        if self.behavior.get('analyze_images', True) and mention.get('media'):
            for media in mention['media']:
                if media.get('url'):
                    logger.info("Analyzing image...")
                    image_description = self.llm_handler.analyze_image(media['url'])
                    has_image = True
                    logger.info(f"Image description: {image_description[:100]}...")
                    break
        
        # Generate response
        logger.info("Generating response...")
        response = self.llm_handler.generate_response(
            character=self.character,
            tweet_text=tweet_text,
            context=context,
            image_description=image_description
        )
        
        # Post reply
        logger.info(f"Replying: {response}")
        reply_id = self.twitter_client.reply_to_tweet(tweet_id, response)
        
        if reply_id:
            # Update memory
            self.memory_manager.add_conversation(
                user_id=author_id,
                username=author_username,
                tweet_id=tweet_id,
                tweet_text=tweet_text,
                response=response,
                has_image=has_image
            )
            
            self.memory_manager.update_interaction(
                user_id=author_id,
                username=author_username,
                interaction_type='reply'
            )
            
            self.replies_this_hour += 1
            logger.info("Reply posted successfully")
            
            # Follow back if enabled
            if self.behavior.get('follow_back', True):
                self._consider_following(author_id, author_username)
    
    def _consider_following(self, user_id: str, username: str):
        """Consider following a user based on their profile."""
        # Skip if already followed
        if self.memory_manager.is_followed(user_id):
            return
        
        # Check rate limits
        if not self._can_follow():
            logger.info("Follow rate limit reached")
            return
        
        try:
            # Get user info
            user_info = self.twitter_client.get_user_info(user_id)
            if not user_info:
                return
            
            # Get recent tweets
            recent_tweets = self.twitter_client.get_user_tweets(user_id, max_results=3)
            tweets_text = "\n".join([t['text'] for t in recent_tweets])
            
            # Decide whether to follow
            should_follow = self.llm_handler.generate_follow_decision(
                character=self.character,
                user_bio=user_info.get('description', ''),
                recent_tweets=tweets_text
            )
            
            if should_follow:
                if self.twitter_client.follow_user(user_id):
                    self.memory_manager.add_followed_account(user_id, username)
                    self.follows_today += 1
                    logger.info(f"Followed @{username}")
            else:
                logger.info(f"Decided not to follow @{username}")
                
        except Exception as e:
            logger.error(f"Error considering follow for {username}: {e}")
    
    def check_followers(self):
        """Check new followers and potentially follow them back."""
        if not self.behavior.get('follow_back', True):
            return
        
        logger.info("Checking followers...")
        
        try:
            followers = self.twitter_client.get_followers(max_results=10)
            
            for follower in followers:
                user_id = follower['id']
                username = follower['username']
                
                # Skip if already followed
                if self.memory_manager.is_followed(user_id):
                    continue
                
                # Consider following back
                self._consider_following(user_id, username)
                
        except Exception as e:
            logger.error(f"Error checking followers: {e}")
    
    def run(self):
        """Main bot loop that runs continuously."""
        logger.info(f"Starting bot as {self.character['name']}...")
        logger.info("Press Ctrl+C to stop")
        
        reply_interval = self.bot_settings.get('reply_interval_minutes', 15) * 60
        follow_check_interval = self.bot_settings.get('follow_check_interval_minutes', 60) * 60
        
        last_reply_check = 0
        last_follow_check = 0
        
        try:
            while True:
                current_time = time.time()
                
                # Check mentions and reply
                if current_time - last_reply_check >= reply_interval:
                    try:
                        self.process_mentions()
                    except Exception as e:
                        logger.error(f"Error in process_mentions: {e}")
                    last_reply_check = current_time
                
                # Check followers
                if current_time - last_follow_check >= follow_check_interval:
                    try:
                        self.check_followers()
                    except Exception as e:
                        logger.error(f"Error in check_followers: {e}")
                    last_follow_check = current_time
                
                # Sleep for a bit before next iteration
                time.sleep(60)  # Check every minute
                
        except KeyboardInterrupt:
            logger.info("Bot stopped by user")
        except Exception as e:
            logger.error(f"Fatal error in bot loop: {e}")
            raise


def main():
    """Entry point for the bot."""
    try:
        bot = PersonalityBot()
        bot.run()
    except Exception as e:
        logger.error(f"Failed to start bot: {e}")
        raise


if __name__ == "__main__":
    main()

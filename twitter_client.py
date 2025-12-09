"""Twitter API client for interacting with Twitter."""
import tweepy
from typing import List, Dict, Any, Optional
import time


class TwitterClient:
    """Manages Twitter API interactions."""
    
    def __init__(self, credentials: Dict[str, str]):
        """
        Initialize the Twitter client.
        
        Args:
            credentials: Dictionary containing Twitter API credentials
        """
        self.credentials = credentials
        
        # Initialize Tweepy client for API v2
        self.client = tweepy.Client(
            bearer_token=credentials.get('bearer_token'),
            consumer_key=credentials['api_key'],
            consumer_secret=credentials['api_secret'],
            access_token=credentials['access_token'],
            access_token_secret=credentials['access_token_secret'],
            wait_on_rate_limit=True
        )
        
        # Initialize API v1.1 for additional functionality
        auth = tweepy.OAuth1UserHandler(
            credentials['api_key'],
            credentials['api_secret'],
            credentials['access_token'],
            credentials['access_token_secret']
        )
        self.api = tweepy.API(auth, wait_on_rate_limit=True)
        
        # Get authenticated user info
        self.me = self.client.get_me(user_fields=['username']).data
        print(f"Authenticated as: @{self.me.username}")
    
    def get_mentions(self, since_id: Optional[str] = None, max_results: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent mentions of the bot.
        
        Args:
            since_id: Only return tweets after this ID
            max_results: Maximum number of tweets to return
            
        Returns:
            List of mention dictionaries
        """
        try:
            kwargs = {
                'max_results': max_results,
                'tweet_fields': ['created_at', 'author_id', 'conversation_id'],
                'expansions': ['author_id', 'attachments.media_keys'],
                'media_fields': ['url', 'preview_image_url'],
                'user_fields': ['username']
            }
            
            if since_id:
                kwargs['since_id'] = since_id
            
            response = self.client.get_users_mentions(
                id=self.me.id,
                **kwargs
            )
            
            if not response.data:
                return []
            
            # Process mentions
            mentions = []
            users = {user.id: user for user in (response.includes.get('users', []) or [])}
            media = {m.media_key: m for m in (response.includes.get('media', []) or [])}
            
            for tweet in response.data:
                author = users.get(tweet.author_id)
                
                mention_data = {
                    'id': tweet.id,
                    'text': tweet.text,
                    'author_id': tweet.author_id,
                    'author_username': author.username if author else 'unknown',
                    'created_at': tweet.created_at,
                    'conversation_id': tweet.conversation_id,
                    'media': []
                }
                
                # Add media if present
                if hasattr(tweet, 'attachments') and tweet.attachments:
                    media_keys = tweet.attachments.get('media_keys', [])
                    for key in media_keys:
                        if key in media:
                            media_obj = media[key]
                            mention_data['media'].append({
                                'url': getattr(media_obj, 'url', None),
                                'preview_url': getattr(media_obj, 'preview_image_url', None)
                            })
                
                mentions.append(mention_data)
            
            return mentions
            
        except Exception as e:
            print(f"Error getting mentions: {e}")
            return []
    
    def reply_to_tweet(self, tweet_id: str, text: str) -> Optional[str]:
        """
        Reply to a tweet.
        
        Args:
            tweet_id: ID of the tweet to reply to
            text: Reply text
            
        Returns:
            ID of the reply tweet, or None if failed
        """
        try:
            response = self.client.create_tweet(
                text=text,
                in_reply_to_tweet_id=tweet_id
            )
            print(f"Replied to tweet {tweet_id}")
            return response.data['id']
        except Exception as e:
            print(f"Error replying to tweet: {e}")
            return None
    
    def follow_user(self, user_id: str) -> bool:
        """
        Follow a user.
        
        Args:
            user_id: Twitter user ID to follow
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.client.follow_user(user_id)
            print(f"Followed user {user_id}")
            return True
        except Exception as e:
            print(f"Error following user: {e}")
            return False
    
    def get_user_info(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get user information.
        
        Args:
            user_id: Twitter user ID
            
        Returns:
            User information dictionary or None
        """
        try:
            response = self.client.get_user(
                id=user_id,
                user_fields=['description', 'public_metrics']
            )
            
            if response.data:
                user = response.data
                return {
                    'id': user.id,
                    'username': user.username,
                    'name': user.name,
                    'description': getattr(user, 'description', ''),
                    'followers_count': user.public_metrics.get('followers_count', 0) if hasattr(user, 'public_metrics') else 0
                }
            return None
        except Exception as e:
            print(f"Error getting user info: {e}")
            return None
    
    def get_user_tweets(self, user_id: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """
        Get recent tweets from a user.
        
        Args:
            user_id: Twitter user ID
            max_results: Maximum number of tweets to return
            
        Returns:
            List of tweet dictionaries
        """
        try:
            response = self.client.get_users_tweets(
                id=user_id,
                max_results=max_results,
                tweet_fields=['created_at', 'public_metrics']
            )
            
            if not response.data:
                return []
            
            tweets = []
            for tweet in response.data:
                tweets.append({
                    'id': tweet.id,
                    'text': tweet.text,
                    'created_at': tweet.created_at
                })
            
            return tweets
        except Exception as e:
            print(f"Error getting user tweets: {e}")
            return []
    
    def get_followers(self, max_results: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent followers.
        
        Args:
            max_results: Maximum number of followers to return
            
        Returns:
            List of follower dictionaries
        """
        try:
            response = self.client.get_users_followers(
                id=self.me.id,
                max_results=max_results,
                user_fields=['username', 'description']
            )
            
            if not response.data:
                return []
            
            followers = []
            for user in response.data:
                followers.append({
                    'id': user.id,
                    'username': user.username,
                    'name': user.name,
                    'description': getattr(user, 'description', '')
                })
            
            return followers
        except Exception as e:
            print(f"Error getting followers: {e}")
            return []
    
    def search_recent_tweets(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """
        Search for recent tweets.
        
        Args:
            query: Search query
            max_results: Maximum number of tweets to return
            
        Returns:
            List of tweet dictionaries
        """
        try:
            response = self.client.search_recent_tweets(
                query=query,
                max_results=max_results,
                tweet_fields=['created_at', 'author_id'],
                expansions=['author_id'],
                user_fields=['username']
            )
            
            if not response.data:
                return []
            
            users = {user.id: user for user in (response.includes.get('users', []) or [])}
            
            tweets = []
            for tweet in response.data:
                author = users.get(tweet.author_id)
                tweets.append({
                    'id': tweet.id,
                    'text': tweet.text,
                    'author_id': tweet.author_id,
                    'author_username': author.username if author else 'unknown',
                    'created_at': tweet.created_at
                })
            
            return tweets
        except Exception as e:
            print(f"Error searching tweets: {e}")
            return []

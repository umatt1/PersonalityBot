"""Memory management for maintaining conversation context."""
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional


class MemoryManager:
    """Manages conversation memory and context for the bot."""
    
    def __init__(self, memory_file: str = "memory_data/conversations.json", retention_days: int = 7):
        """
        Initialize the memory manager.
        
        Args:
            memory_file: Path to the memory storage file
            retention_days: Number of days to retain memory
        """
        self.memory_file = memory_file
        self.retention_days = retention_days
        self.memory = self._load_memory()
        self._cleanup_old_memories()
    
    def _load_memory(self) -> Dict[str, Any]:
        """Load memory from file or create new memory structure."""
        os.makedirs(os.path.dirname(self.memory_file), exist_ok=True)
        
        try:
            with open(self.memory_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {
                'conversations': {},
                'interactions': {},
                'followed_accounts': []
            }
    
    def _save_memory(self):
        """Save memory to file."""
        os.makedirs(os.path.dirname(self.memory_file), exist_ok=True)
        with open(self.memory_file, 'w') as f:
            json.dump(self.memory, f, indent=2)
    
    def _cleanup_old_memories(self):
        """Remove memories older than retention period."""
        cutoff_date = datetime.now() - timedelta(days=self.retention_days)
        cutoff_str = cutoff_date.isoformat()
        
        # Clean up old conversations
        conversations = self.memory.get('conversations', {})
        for user_id in list(conversations.keys()):
            user_convs = conversations[user_id]
            conversations[user_id] = [
                conv for conv in user_convs
                if conv.get('timestamp', '') > cutoff_str
            ]
            if not conversations[user_id]:
                del conversations[user_id]
        
        # Clean up old interactions
        interactions = self.memory.get('interactions', {})
        for user_id in list(interactions.keys()):
            if interactions[user_id].get('last_interaction', '') < cutoff_str:
                del interactions[user_id]
        
        self._save_memory()
    
    def add_conversation(self, user_id: str, username: str, tweet_id: str, 
                        tweet_text: str, response: str, has_image: bool = False):
        """
        Add a conversation to memory.
        
        Args:
            user_id: Twitter user ID
            username: Twitter username
            tweet_id: Tweet ID
            tweet_text: Original tweet text
            response: Bot's response
            has_image: Whether the tweet contained an image
        """
        if 'conversations' not in self.memory:
            self.memory['conversations'] = {}
        
        if user_id not in self.memory['conversations']:
            self.memory['conversations'][user_id] = []
        
        conversation = {
            'timestamp': datetime.now().isoformat(),
            'username': username,
            'tweet_id': tweet_id,
            'tweet_text': tweet_text,
            'response': response,
            'has_image': has_image
        }
        
        self.memory['conversations'][user_id].append(conversation)
        
        # Keep only recent conversations per user (last 10)
        self.memory['conversations'][user_id] = self.memory['conversations'][user_id][-10:]
        
        self._save_memory()
    
    def get_conversation_history(self, user_id: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Get conversation history with a user.
        
        Args:
            user_id: Twitter user ID
            limit: Maximum number of conversations to return
            
        Returns:
            List of conversation dictionaries
        """
        conversations = self.memory.get('conversations', {}).get(user_id, [])
        return conversations[-limit:]
    
    def update_interaction(self, user_id: str, username: str, interaction_type: str):
        """
        Update interaction metadata for a user.
        
        Args:
            user_id: Twitter user ID
            username: Twitter username
            interaction_type: Type of interaction (reply, follow, etc.)
        """
        if 'interactions' not in self.memory:
            self.memory['interactions'] = {}
        
        if user_id not in self.memory['interactions']:
            self.memory['interactions'][user_id] = {
                'username': username,
                'first_interaction': datetime.now().isoformat(),
                'interaction_count': 0,
                'interaction_types': []
            }
        
        self.memory['interactions'][user_id]['last_interaction'] = datetime.now().isoformat()
        self.memory['interactions'][user_id]['interaction_count'] += 1
        self.memory['interactions'][user_id]['interaction_types'].append({
            'type': interaction_type,
            'timestamp': datetime.now().isoformat()
        })
        
        # Keep only recent interaction types (last 20)
        self.memory['interactions'][user_id]['interaction_types'] = \
            self.memory['interactions'][user_id]['interaction_types'][-20:]
        
        self._save_memory()
    
    def add_followed_account(self, user_id: str, username: str):
        """
        Add a followed account to memory.
        
        Args:
            user_id: Twitter user ID
            username: Twitter username
        """
        if 'followed_accounts' not in self.memory:
            self.memory['followed_accounts'] = []
        
        if user_id not in [acc['user_id'] for acc in self.memory['followed_accounts']]:
            self.memory['followed_accounts'].append({
                'user_id': user_id,
                'username': username,
                'followed_at': datetime.now().isoformat()
            })
            self._save_memory()
    
    def is_followed(self, user_id: str) -> bool:
        """
        Check if an account is already followed.
        
        Args:
            user_id: Twitter user ID
            
        Returns:
            True if account is followed, False otherwise
        """
        return user_id in [acc['user_id'] for acc in self.memory.get('followed_accounts', [])]
    
    def get_context_summary(self, user_id: str) -> str:
        """
        Get a summary of past interactions with a user for context.
        
        Args:
            user_id: Twitter user ID
            
        Returns:
            A formatted summary string
        """
        conversations = self.get_conversation_history(user_id, limit=3)
        interaction_data = self.memory.get('interactions', {}).get(user_id, {})
        
        if not conversations and not interaction_data:
            return "First time interacting with this user."
        
        summary_parts = []
        
        if interaction_data:
            count = interaction_data.get('interaction_count', 0)
            summary_parts.append(f"Previous interactions: {count}")
        
        if conversations:
            summary_parts.append("Recent conversation context:")
            for conv in conversations:
                summary_parts.append(f"- User: {conv['tweet_text'][:100]}")
                summary_parts.append(f"  Response: {conv['response'][:100]}")
        
        return "\n".join(summary_parts)

"""LLM integration using LangChain for content analysis and response generation."""
import base64
import io
from typing import Dict, Any, Optional
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import HumanMessage, SystemMessage
from PIL import Image
import requests


class LLMHandler:
    """Handles LLM operations for analyzing content and generating responses."""
    
    def __init__(self, api_key: str, model: str = "gpt-4", vision_model: str = "gpt-4-vision-preview"):
        """
        Initialize the LLM handler.
        
        Args:
            api_key: OpenAI API key
            model: Model to use for text generation
            vision_model: Model to use for image analysis
        """
        self.api_key = api_key
        self.model = model
        self.vision_model = vision_model
        self.llm = ChatOpenAI(api_key=api_key, model=model, temperature=0.7)
        self.vision_llm = ChatOpenAI(api_key=api_key, model=vision_model, temperature=0.7)
    
    def generate_response(self, character: Dict[str, Any], tweet_text: str, 
                         context: str = "", image_description: str = "") -> str:
        """
        Generate a character-appropriate response to a tweet.
        
        Args:
            character: Character configuration dictionary
            tweet_text: The tweet to respond to
            context: Previous conversation context
            image_description: Description of any image in the tweet
            
        Returns:
            Generated response text
        """
        # Build the system prompt with character details
        system_prompt = f"""You are {character['name']}. 

Personality: {character['personality']}

Backstory: {character['backstory']}

Voice Guidelines: {character.get('voice_guidelines', 'Speak naturally in character.')}

Catchphrases you might use: {', '.join(character.get('catchphrases', []))}

Your task is to respond to tweets in character. Keep responses under 280 characters. 
Be engaging, stay in character, and reference your background when appropriate."""
        
        # Build the user prompt
        user_parts = []
        
        if context:
            user_parts.append(f"Previous conversation context:\n{context}\n")
        
        if image_description:
            user_parts.append(f"The tweet includes an image showing: {image_description}\n")
        
        user_parts.append(f"Tweet to respond to: {tweet_text}\n")
        user_parts.append("Generate a response in character:")
        
        user_prompt = "\n".join(user_parts)
        
        # Create messages
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]
        
        # Generate response
        response = self.llm.invoke(messages)
        
        # Ensure response is under 280 characters
        response_text = response.content.strip()
        if len(response_text) > 280:
            response_text = response_text[:277] + "..."
        
        return response_text
    
    def analyze_image(self, image_url: str) -> str:
        """
        Analyze an image from a tweet.
        
        Args:
            image_url: URL of the image to analyze
            
        Returns:
            Description of the image content
        """
        try:
            # Download the image
            response = requests.get(image_url, timeout=10)
            response.raise_for_status()
            
            # Convert to base64
            image = Image.open(io.BytesIO(response.content))
            
            # Resize if too large
            max_size = (1024, 1024)
            image.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            # Convert to base64
            buffered = io.BytesIO()
            image.save(buffered, format="JPEG")
            img_base64 = base64.b64encode(buffered.getvalue()).decode()
            
            # Create message with image
            messages = [
                HumanMessage(
                    content=[
                        {
                            "type": "text",
                            "text": "Describe this image in detail. Focus on key elements, emotions, and context that would be relevant for crafting a response."
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{img_base64}"
                            }
                        }
                    ]
                )
            ]
            
            # Get image description
            response = self.vision_llm.invoke(messages)
            return response.content.strip()
            
        except Exception as e:
            print(f"Error analyzing image: {e}")
            return "Unable to analyze image"
    
    def should_respond(self, character: Dict[str, Any], tweet_text: str, 
                       image_description: str = "") -> bool:
        """
        Determine if the bot should respond to a tweet based on relevance.
        
        Args:
            character: Character configuration
            tweet_text: The tweet text
            image_description: Description of any image
            
        Returns:
            True if bot should respond, False otherwise
        """
        prompt = f"""You are {character['name']}. 

Based on your character and interests, should you respond to this tweet?

Tweet: {tweet_text}
{f"Image content: {image_description}" if image_description else ""}

Respond with only "YES" or "NO" and a brief reason."""
        
        messages = [
            HumanMessage(content=prompt)
        ]
        
        response = self.llm.invoke(messages)
        response_text = response.content.strip().upper()
        
        # Check if response starts with YES
        return response_text.startswith("YES")
    
    def generate_follow_decision(self, character: Dict[str, Any], 
                                user_bio: str, recent_tweets: str) -> bool:
        """
        Decide whether to follow a user based on their profile and content.
        
        Args:
            character: Character configuration
            user_bio: User's bio/description
            recent_tweets: Sample of user's recent tweets
            
        Returns:
            True if should follow, False otherwise
        """
        prompt = f"""You are {character['name']}. 

Based on your character and interests, would you find this Twitter user interesting to follow?

User Bio: {user_bio}

Recent tweets:
{recent_tweets}

Respond with only "YES" or "NO"."""
        
        messages = [
            HumanMessage(content=prompt)
        ]
        
        response = self.llm.invoke(messages)
        response_text = response.content.strip().upper()
        
        return response_text.startswith("YES")

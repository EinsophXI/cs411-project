import logging
import os
import requests
import datetime
from datetime import datetime, timezone

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def get_article(keyword: str) -> str:
    """
    Fetches an article related to the given keyword from the NewsAPI.
    
    Args:
        keyword (str): The keyword to search for articles.
        
    Returns:
        str: The title and description of the first article found.
    
    Raises:
        RuntimeError: If the request to the API fails.
    """
    api_key = os.getenv("NEWS_API_KEY", "e616acff8a674cfc8ba4648026e85f1d")  # Load API key from environment variables
    url = f"https://newsapi.org/v2/everything?q={keyword}&pageSize=1&apiKey={api_key}"

    try:
        logger.info("Fetching article from %s", url)
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        
        data = response.json()
        
        if 'articles' in data and data['articles']:
            article = data['articles'][0]
            name = article.get('name', 'No Name')
            author = article.get('author', 'No Author')
            title = article.get('title', 'No Title')
            description = article.get('description', 'No Description')
            articleurl = article.get('url', 'No URL')
            published_at = article.get('publishedAt', 'No Date')
            content = article.get('content', 'No Content')
            
            # Parse the publication date into a datetime object
            if published_at != 'No Date':
                try:
                    published_datetime = datetime.strptime(published_at, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
                    published_at = published_datetime.strftime("%Y-%m-%d %H:%M:%S %Z")
                except ValueError as e:
                    logger.error("Error parsing publication date: %s", e)
                    published_at = "Invalid Date Format"
            
            logger.info("Received article: %s", article)
            return f"Name: {name}\nAuthor: {author}\nTitle: {title}\nDescription: {description}\nURL: {articleurl}\nPublished At: {published_at}\nContent: {content}"
        else:
            logger.warning("No articles found for keyword: %s", keyword)
            return "No articles found."

    except requests.exceptions.Timeout:
        logger.error("Request to newsapi.org timed out.")
        raise RuntimeError("Request to newsapi.org timed out.")
    except requests.exceptions.RequestException as e:
        logger.error("Request to newsapi.org failed: %s", e)
        raise RuntimeError(f"Request to newsapi.org failed: {e}")
    except ValueError as e:
        logger.error("Invalid response received: %s", e)
        raise RuntimeError(f"Invalid response received: {e}")

if __name__ == "__main__":
    keyword = "tesla"
    try:
        print(get_article(keyword))
    except RuntimeError as e:
        logger.error("Error fetching article: %s", e)
import logging
import requests

# from music_collection.utils.logger import configure_logger

logger = logging.getLogger(__name__)
# configure_logger(logger)




def get_article(keyword: str) -> str:
    """
    Fetches a random int between 1 and the number of songs in the catalog from random.org.

    Returns:
        int: The random number fetched from random.org.

    Raises:
        RuntimeError: If the request to random.org fails or returns an invalid response.
        ValueError: If the response from random.org is not a valid float.
    """
    url = f"https://newsapi.org/v2/everything?q={keyword}&pagesize=1&apiKey=e616acff8a674cfc8ba4648026e85f1d"

    try:
        # Log the request to random.org
        logger.info("Fetching article from %s", url)

        response = requests.get(url, timeout=5)

        # Check if the request was successful
        response.raise_for_status()

        article = response.text.strip()

        # try:
        #     random_number = int(random_number_str)
        # except ValueError:
        #     raise ValueError("Invalid response from random.org: %s" % random_number_str)

        print("Received article: %.3f", article)
        return article

    except requests.exceptions.Timeout:
        logger.error("Request to newsapi.org timed out.")
        raise RuntimeError("Request to newsapi.org timed out.")

    except requests.exceptions.RequestException as e:
        logger.error("Request to newsapi.org failed: %s", e)
        raise RuntimeError("Request to newsapi.org failed: %s" % e)

get_article("tesla")

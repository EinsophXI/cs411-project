import logging
import requests

from meal_max.utils.logger import configure_logger

logger = logging.getLogger(__name__)
configure_logger(logger)


def get_random() -> str:
    url = "https://newsapi.org/v2/everything?q=tesla&from=2024-11-06&sortBy=publishedAt&apiKey=e616acff8a674cfc8ba4648026e85f1d"

    try:
        # Log the request to random.org
        logger.info("Fetching random number from %s", url)

        response = requests.get(url, timeout=5)

        # Check if the request was successful
        response.raise_for_status()

        random_number_str = response.text.strip()

        try:
            random_number = float(random_number_str)
        except ValueError:
            raise ValueError("Invalid response from random.org: %s" % random_number_str)

        logger.info("Received random number: %.3f", random_number)
        return random_number

    except requests.exceptions.Timeout:
        logger.error("Request to random.org timed out.")
        raise RuntimeError("Request to random.org timed out.")

    except requests.exceptions.RequestException as e:
        logger.error("Request to random.org failed: %s", e)
        raise RuntimeError("Request to random.org failed: %s" % e)
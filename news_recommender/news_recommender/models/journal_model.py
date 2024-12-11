import logging
from typing import List
from news_recommender.models.article_model import Article, update_read_count
from news_recommender.utils.logger import configure_logger

logger = logging.getLogger(__name__)
configure_logger(logger)


class JournalModel:
    """
    A class to manage a journal of articles.
  
    Attributes:
        # current_article_number (int): The current article number being readed.
        # journal (List[Article]): The list of articles in the journal.
        
        current_article_number (int): The current article being viewed.
        journal (List[Article]): The list of articles in the journal.

    """

    def __init__(self):
        """
        Initializes the JournalModel with an empty journal and the current article set to 1.
        """
        self.current_article_number = 1
        self.journal: List[Article] = []

    ##################################################
    # Article Management Functions
    ##################################################

    def add_article_to_journal(self, article: Article) -> None:
        """
        Adds an article to the journal.

        Args:
            article (Article): the article to add to the journal.

        Raises:
            TypeError: If the article is not a valid article instance.
            ValueError: If an article with the same 'id' already exists.
        """
        logger.info("Adding new article to journal")
        if not isinstance(article, Article):
            logger.error("Article is not a valid article")
            raise TypeError("Article is not a valid article")

        article_id = self.validate_article_id(article.id, check_in_journal=False)
        if article_id in [article_in_journal.id for article_in_journal in self.journal]:
            logger.error("article with ID %d already exists in the journal", article.id)
            raise ValueError(f"Article with ID {article.id} already exists in the journal")

        self.journal.append(article)

    def remove_article_by_article_id(self, article_id: int) -> None:
        """
        Removes an article from the journal by its article ID.

        Args:
            article_id (int): The ID of the article to remove from the journal.

        Raises:
            ValueError: If the journal is empty or the article ID is invalid.
        """
        logger.info("Removing article with id %d from journal", article_id)
        self.check_if_empty()
        article_id = self.validate_article_id(article_id)
        self.journal = [article_in_journal for article_in_journal in self.journal if article_in_journal.id != article_id]
        logger.info("Article with id %d has been removed", article_id)

    def remove_article_by_article_number(self, article_number: int) -> None:
        """
        Removes an article from the journal by its article number (1-indexed).

        Args:
            article_number (int): The article number of the article to remove.

        Raises:
            ValueError: If the journal is empty or the article number is invalid.
        """
        logger.info("Removing article at article number %d from journal", article_number)
        self.check_if_empty()
        article_number = self.validate_article_number(article_number)
        journal_index = article_number - 1
        logger.info("Removing article: %s", self.journal[journal_index].title)
        del self.journal[journal_index]

    def clear_journal(self) -> None:
        """
        Clears all articles from the journal. If the journal is already empty, logs a warning.
        """
        logger.info("Clearing journal")
        if self.get_journal_length() == 0:
            logger.warning("Clearing an empty journal")
        self.journal.clear()

    ##################################################
    # Journal Retrieval Functions
    ##################################################

    def get_all_articles(self) -> List[Article]:
        """
        Returns a list of all articles in the journal.
        """
        self.check_if_empty()
        logger.info("Getting all articles in the journal")
        return self.journal

    def get_article_by_article_id(self, article_id: int) -> Article:
        """
        Retrieves an article from the journal by its article ID.

        Args:
            article_id (int): The ID of the article to retrieve.

        Raises:
            ValueError: If the journal is empty or the article is not found.
        """
        self.check_if_empty()
        article_id = self.validate_article_id(article_id)
        logger.info("Getting article with id %d from journal", article_id)
        return next((article for article in self.journal if article.id == article_id), None)

    def get_article_by_article_number(self, article_number: int) -> Article:
        """
        Retrieves an article from the journal by its article number (1-indexed).

        Args:
            article_number (int): The article number of the article to retrieve.

        Raises:
            ValueError: If the journal is empty or the article number is invalid.
        """
        self.check_if_empty()
        article_number = self.validate_article_number(article_number)
        journal_index = article_number - 1
        logger.info("Getting article at article number %d from journal", article_number)
        return self.journal[journal_index]

    def get_current_article(self) -> Article:
        """
        Returns the current article being readed.
        """
        self.check_if_empty()
        return self.get_article_by_article_number(self.current_article_number)

    def get_journal_length(self) -> int:
        """
        Returns the number of articles in the journal.
        """
        return len(self.journal)

    ##################################################
    # Journal Movement Functions
    ##################################################

    def go_to_article_number(self, article_number: int) -> None:
        """
        Sets the current article number to the specified article number.

        Args:
            article_number (int): The article number to set as the current article.
        """
        self.check_if_empty()
        article_number = self.validate_article_number(article_number)
        logger.info("Setting current article number to %d", article_number)
        self.current_article_number = article_number

    def move_article_to_beginning(self, article_id: int) -> None:
        """
        Moves an article to the beginning of the journal.

        Args:
            article_id (int): The ID of the article to move to the beginning.
        """
        logger.info("Moving article with ID %d to the beginning of the journal", article_id)
        self.check_if_empty()
        article_id = self.validate_article_id(article_id)
        article = self.get_article_by_article_id(article_id)
        self.journal.remove(article)
        self.journal.insert(0, article)
        logger.info("Article with ID %d has been moved to the beginning", article_id)

    def move_article_to_end(self, article_id: int) -> None:
        """
        Moves an article to the end of the journal.

        Args:
            article_id (int): The ID of the article to move to the end.
        """
        logger.info("Moving article with ID %d to the end of the journal", article_id)
        self.check_if_empty()
        article_id = self.validate_article_id(article_id)
        article = self.get_article_by_article_id(article_id)
        self.journal.remove(article)
        self.journal.append(article)
        logger.info("Article with ID %d has been moved to the end", article_id)

    def move_article_to_article_number(self, article_id: int, article_number: int) -> None:
        """
        Moves an article to a specific article number in the journal.

        Args:
            article_id (int): The ID of the article to move.
            article_number (int): The article number to move the article to (1-indexed).
        """
        logger.info("Moving article with ID %d to article number %d", article_id, article_number)
        self.check_if_empty()
        article_id = self.validate_article_id(article_id)
        article_number = self.validate_article_number(article_number)
        journal_index = article_number - 1
        article = self.get_article_by_article_id(article_id)
        self.journal.remove(article)
        self.journal.insert(journal_index, article)
        logger.info("Article with ID %d has been moved to article number %d", article_id, article_number)

    def swap_articles_in_journal(self, article1_id: int, article2_id: int) -> None:
        """
        Swaps the positions of two articles in the journal.

        Args:
            article1_id (int): The ID of the first article to swap.
            article2_id (int): The ID of the second article to swap.

        Raises:
            ValueError: If you attempt to swap an article with itself.
        """
        logger.info("Swapping articles with IDs %d and %d", article1_id, article2_id)
        self.check_if_empty()
        article1_id = self.validate_article_id(article1_id)
        article2_id = self.validate_article_id(article2_id)

        if article1_id == article2_id:
            logger.error("Cannot swap an article with itself, both article IDs are the same: %d", article1_id)
            raise ValueError(f"Cannot swap an article with itself, both article IDs are the same: {article1_id}")

        article1 = self.get_article_by_article_id(article1_id)
        article2 = self.get_article_by_article_id(article2_id)
        index1 = self.journal.index(article1)
        index2 = self.journal.index(article2)
        self.journal[index1], self.journal[index2] = self.journal[index2], self.journal[index1]
        logger.info("Swapped articles with IDs %d and %d", article1_id, article2_id)

    ##################################################
    # Journal Readback Functions
    ##################################################

    def read_current_article(self) -> None:
        """
        Reads the current article.

        Side-effects:
            Updates the current article number.
            Updates the read count for the article.
        """
        self.check_if_empty()
        current_article = self.get_article_by_article_number(self.current_article_number)
        logger.info("Reading article: %s (ID: %d) at article number: %d", current_article.title, current_article.id, self.current_article_number)
        update_read_count(current_article.id)
        logger.info("Updated read count for article: %s (ID: %d)", current_article.title, current_article.id)
        previous_article_number = self.current_article_number
        self.current_article_number = (self.current_article_number % self.get_journal_length()) + 1
        logger.info("Article number updated from %d to %d", previous_article_number, self.current_article_number)

    def read_entire_journal(self) -> None:
        """
        Reads the entire journal.

        Side-effects:
            Resets the current article number to 1.
            Updates the read count for each article.
        """
        self.check_if_empty()
        logger.info("Starting to read the entire journal.")
        self.current_article_number = 1
        logger.info("Reset current article number to 1.")
        for _ in range(self.get_journal_length()):
            logger.info("Reading article number: %d", self.current_article_number)
            self.read_current_article()
        logger.info("Finished reading the entire journal. Current article number reset to 1.")

    def read_rest_of_journal(self) -> None:
        """
        Reads the rest of the journal from the current article.

        Side-effects:
            Updates the current article number back to 1.
            Updates the read count for each article in the rest of the journal.
        """
        self.check_if_empty()
        logger.info("Starting to read the rest of the journal from article number: %d", self.current_article_number)
        for _ in range(self.get_journal_length() - self.current_article_number + 1):
            logger.info("Reading article number: %d", self.current_article_number)
            self.read_current_article()
        logger.info("Finished reading the rest of the journal. Current article number reset to 1.")

    def rewind_journal(self) -> None:
        """
        Rewinds the journal to the beginning.
        """
        self.check_if_empty()
        logger.info("Rewinding journal to the beginning.")
        self.current_article_number = 1

    ##################################################
    # Utility Functions
    ##################################################

    def validate_article_id(self, article_id: int, check_in_journal: bool = True) -> int:
        """
        Validates the given article ID, ensuring it is a non-negative integer.

        Args:
            article_id (int): The article ID to validate.
            check_in_journal (bool, optional): If True, checks if the article ID exists in the journal.
                                                If False, skips the check. Defaults to True.

        Raises:
            ValueError: If the article ID is not a valid non-negative integer.
        """
        try:
            article_id = int(article_id)
            if article_id < 0:
                logger.error("Invalid article id %d", article_id)
                raise ValueError(f"Invalid article id: {article_id}")
        except ValueError:
            logger.error("Invalid article id %s", article_id)
            raise ValueError(f"Invalid article id: {article_id}")

        if check_in_journal:
            if article_id not in [article_in_journal.id for article_in_journal in self.journal]:
                logger.error("Article with id %d not found in journal", article_id)
                raise ValueError(f"Article with id {article_id} not found in journal")

        return article_id

    def validate_article_number(self, article_number: int) -> int:
        """
        Validates the given article number, ensuring it is a non-negative integer within the journal's range.

        Args:
            article_number (int): The article number to validate.

        Raises:
            ValueError: If the article number is not a valid non-negative integer or is out of range.
        """
        try:
            article_number = int(article_number)
            if article_number < 1 or article_number > self.get_journal_length():
                logger.error("Invalid article number %d", article_number)
                raise ValueError(f"Invalid article number: {article_number}")
        except ValueError:
            logger.error("Invalid article number %s", article_number)
            raise ValueError(f"Invalid article number: {article_number}")

        return article_number

    def check_if_empty(self) -> None:
        """
        Checks if the journal is empty, logs an error, and raises a ValueError if it is.

        Raises:
            ValueError: If the journal is empty.
        """
        if not self.journal:
            logger.error("Journal is empty")
            raise ValueError("Journal is empty")
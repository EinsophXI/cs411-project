#!/bin/bash

# Define the base URL for the Flask API
BASE_URL="http://localhost:5003/project"

# Flag to control whether to echo JSON output
ECHO_JSON=false

# Parse command-line arguments
while [ "$#" -gt 0 ]; do
  case $1 in
    --echo-json) ECHO_JSON=true ;;
    *) echo "Unknown parameter passed: $1"; exit 1 ;;
  esac
  shift
done


###############################################
#
# Health checks
#
###############################################

# Function to check the health of the service
check_health() {
  echo "Checking health status..."
  curl -s -X GET "$BASE_URL/health" | grep -q '"status": "healthy"'
  if [ $? -eq 0 ]; then
    echo "Service is healthy."
  else
    echo "Health check failed."
    exit 1
  fi
}

# Function to check the database connection
check_db() {
  echo "Checking database connection..."
  curl -s -X GET "$BASE_URL/db-check" | grep -q '"database_status": "healthy"'
  if [ $? -eq 0 ]; then
    echo "Database connection is healthy."
  else
    echo "Database check failed."
    exit 1
  fi
}


##########################################################
#
# Article Management
#
##########################################################

clear_catalog() {
  echo "Clearing the journal..."
  curl -s -X DELETE "$BASE_URL/clear-catalog" | grep -q '"status": "success"'
}

create_article() {
  id=$1
  name=$2
  author=$3
  title=$4
  url=$5
  content=$6
  publishedAt=$7

  echo "Adding article ($author - $title, $publishedAt) to the journal..."
  curl -s -X POST "$BASE_URL/create-article" -H "Content-Type: application/json" \
    -d "{\"id\":\"$id\", \"name\":\"$name\", \"author\":$author, \"title\":\"$title\", \"url\":\"$url\", \"content\":\"$content\", \"publishedAt\":$publishedAt}" | grep -q '"status": "success"'

  if [ $? -eq 0 ]; then
    echo "Article added successfully."
  else
    echo "Failed to add article."
    exit 1
  fi
}

delete_article_by_id() {
  article_id=$1

  echo "Deleting article by ID ($article_id)..."
  response=$(curl -s -X DELETE "$BASE_URL/delete-article/$article_id")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Article deleted successfully by ID ($article_id)."
  else
    echo "Failed to delete article by ID ($article_id)."
    exit 1
  fi
}

get_article_by_id() {
  article_id=$1

  echo "Getting article by ID ($article_id)..."
  response=$(curl -s -X GET "$BASE_URL/get-article-by-id/$article_id")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Article retrieved successfully by ID ($article_id)."
    if [ "$ECHO_JSON" = true ]; then
      echo "Article JSON (ID $article_id):"
      echo "$response" | jq .
    fi
  else
    echo "Failed to get article by ID ($article_id)."
    exit 1
  fi
}


############################################################
#
# Journal Management
#
############################################################

add_article_to_journal() {
  id=$1
  name=$2
  author=$3
  title=$4
  url=$5
  content=$6
  publishedAt=$7

  echo "Adding article to journal: $author - $title ($publishAt)..."
  response=$(curl -s -X POST "$BASE_URL/add-article-to-journal" \
    -H "Content-Type: application/json" \
    -d "{\"id\":\"$id\", \"name\":\"$name\", \"author\":$author, \"title\":\"$title\", \"url\":\"$url\", \"content\":\"$content\", \"publishedAt\":$publishedAt}" | grep -q '"status": "success"'

  if echo "$response" | grep -q '"status": "success"'; then
    echo "Article added to journal successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Article JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to add article to journal."
    exit 1
  fi
}

remove_article_from_journal() {
  id=$1
  name=$2
  author=$3
  title=$4
  url=$5
  content=$6
  publishedAt=$7

  echo "Removing article from journal: $author - $title ($publishAt)..."
  response=$(curl -s -X DELETE "$BASE_URL/remove-article-from-journal" \
    -H "Content-Type: application/json" \
    -d "{\"id\":\"$id\", \"name\":\"$name\", \"author\":$author, \"title\":\"$title\", \"url\":\"$url\", \"content\":\"$content\", \"publishedAt\":$publishedAt}" | grep -q '"status": "success"'

  if echo "$response" | grep -q '"status": "success"'; then
    echo "Article removed from journal successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Article JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to remove article from journal."
    exit 1
  fi
}

remove_article_by_article_number() {
  article_number=$1

  echo "Removing article by article number: $article_number..."
  response=$(curl -s -X DELETE "$BASE_URL/remove-article-from-journal-by-article-number/$article_number")

  if echo "$response" | grep -q '"status":'; then
    echo "Article removed from journal by article number ($article_number) successfully."
  else
    echo "Failed to remove article from journal by article number."
    exit 1
  fi
}

clear_journal() {
  echo "Clearing journal..."
  response=$(curl -s -X POST "$BASE_URL/clear-journal")

  if echo "$response" | grep -q '"status": "success"'; then
    echo "Journal cleared successfully."
  else
    echo "Failed to clear journal."
    exit 1
  fi
}


############################################################
#
# Read Journal
#
############################################################

read_current_article() {
  echo "Reading current article..."
  response=$(curl -s -X POST "$BASE_URL/read-current-article")

  if echo "$response" | grep -q '"status": "success"'; then
    echo "Current article is now reading."
  else
    echo "Failed to read current article."
    exit 1
  fi
}

get_article_from_journal_by_article_number() {
  article_number=$1
  echo "Retrieving article by article number ($article_number)..."
  response=$(curl -s -X GET "$BASE_URL/get-article-from-journal-by-article-number/$article_number")

  if echo "$response" | grep -q '"status": "success"'; then
    echo "Article retrieved successfully by article number."
    if [ "$ECHO_JSON" = true ]; then
      echo "Article JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to retrieve article by article number."
    exit 1
  fi
}

get_current_article() {
  echo "Retrieving current article..."
  response=$(curl -s -X GET "$BASE_URL/get-current-article")

  if echo "$response" | grep -q '"status": "success"'; then
    echo "Current article retrieved successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Current Article JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to retrieve current article."
    exit 1
  fi
}

read_entire_journal() {
  echo "Reading entire journal..."
  curl -s -X POST "$BASE_URL/read-entire-journal" | grep -q '"status": "success"'
  if [ $? -eq 0 ]; then
    echo "Entire journal readed successfully."
  else
    echo "Failed to read entire journal."
    exit 1
  fi
}

############################################################
#
# Arrange Journal
#
############################################################

swap_articles_in_journal() {
  article_number1=$1
  article_number2=$2

  echo "Swapping articles at article numbers ($article_number1) and ($article_number2)..."
  response=$(curl -s -X POST "$BASE_URL/swap-articles-in-journal" \
    -H "Content-Type: application/json" \
    -d "{\"article_number_1\": $article_number1, \"article_number_2\": $article_number2}")

  if echo "$response" | grep -q '"status": "success"'; then
    echo "Articles swapped successfully between article numbers ($article_number1) and ($article_number2)."
  else
    echo "Failed to swap articles."
    exit 1
  fi
}

# Health checks
check_health
check_db

# Clear the catalog
clear_catalog

# Create articles
create_article "The Beatles" "Hey Jude" 1968 "Rock" 180
create_article "The Rolling Stones" "Paint It Black" 1966 "Rock" 180
create_article "The Beatles" "Let It Be" 1970 "Rock" 180
create_article "Queen" "Bohemian Rhapsody" 1975 "Rock" 180
create_article "Led Zeppelin" "Stairway to Heaven" 1971 "Rock" 180

delete_article_by_id 1
get_all_articles

get_article_by_id 2
get_article_by_compound_key "The Beatles" "Let It Be" 1970
get_random_article

clear_journal

add_article_to_journal "The Rolling Stones" "Paint It Black" 1966
add_article_to_journal "Queen" "Bohemian Rhapsody" 1975
add_article_to_journal "Led Zeppelin" "Stairway to Heaven" 1971
add_article_to_journal "The Beatles" "Let It Be" 1970

remove_article_from_journal "The Beatles" "Let It Be" 1970
remove_article_by_article_number 2

get_all_articles_from_journal

add_article_to_journal "Queen" "Bohemian Rhapsody" 1975
add_article_to_journal "The Beatles" "Let It Be" 1970

move_article_to_beginning "The Beatles" "Let It Be" 1970
move_article_to_end "Queen" "Bohemian Rhapsody" 1975
move_article_to_article_number "Led Zeppelin" "Stairway to Heaven" 1971 2
swap_articles_in_journal 1 2

get_all_articles_from_journal
get_article_from_journal_by_article_number 1

get_journal_length_duration

read_current_article
rewind_journal

read_entire_journal
read_current_article
read_rest_of_journal

get_article_leaderboard

echo "All tests passed successfully!"

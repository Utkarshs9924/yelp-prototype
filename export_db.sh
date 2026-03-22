#!/bin/bash
cd /Users/akash/dev/DATA236/Lab/yelp-teammate
echo "Exporting yelp_db database to mock_data.sql..."

# Note: Using root without password if DB_PASSWORD is empty like in the .env, 
# otherwise prompt the user or load from .env
if [ -f "backend/.env" ]; then
    export $(grep -v '^#' backend/.env | xargs)
fi

DB_USER=${DB_USER:-root}
DB_PASSWORD=${DB_PASSWORD:-Akash#123}
DB_NAME=${DB_NAME:-yelp_db}

# Create the file with the database creation commands first
echo "CREATE DATABASE IF NOT EXISTS yelp_db;" > mock_data.sql
echo "USE yelp_db;" >> mock_data.sql
echo "" >> mock_data.sql

# Append the mysqldump output
mysqldump --set-gtid-purged=OFF -u "$DB_USER" -p"$DB_PASSWORD" "$DB_NAME" >> mock_data.sql

if [ $? -eq 0 ]; then
    echo "✅ Database exported successfully to mock_data.sql!"
    echo "You can now commit this file to GitHub for your teammates."
else
    echo "❌ Failed to export database. Please check your MySQL credentials."
fi

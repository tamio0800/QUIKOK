#!/bin/sh

mysql -u root --password="0800" < test_folder/to_create_users_and_lessons.sql
echo "SQL script has been executed successfully!"

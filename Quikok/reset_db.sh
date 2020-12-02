#!/bin/bash
# mysql -u root --password="0800" -e "drop database quikok_db;create database quikok_db DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;" 
# && mysql -u root --password="0800" < test_folder/to_create_users_and_lessons.sql && echo "SQL script has been executed successfully!"
find account/migrations/* | grep -v __init__.py | xargs rm -rf
find account_finance/migrations/* | grep -v __init__.py | xargs rm -rf
find chatroom/migrations/* | grep -v __init__.py | xargs rm -rf
find lesson/migrations/* | grep -v __init__.py | xargs rm -rf

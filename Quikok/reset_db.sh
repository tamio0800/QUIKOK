!/bin/sh
mysql -u root --password="0800" -e "drop database quikok_db;create database quikok_db DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;"
sudo rm -rf account/migrations/* chatroom/migrations/* lesson/migrations/* && touch account/migrations/__init__.py chatroom/migrations/__init__.py lesson/migrations/__init__.py && python3 manage.py makemigrations && python3 manage.py migrate && mysql -u root --password="0800" < test_folder/to_create_users_and_lessons.sql && echo "SQL script has been executed successfully!"

# NexusBoard-Module1-4
Providing project management tools of creating login registration system, followed by Project board creation, and list and card CRUD operations, followed by draggable cards with updates in database and board sharing for real time applications

# Instruction for Working with the Project
1. Install the required python packages using

   pip install -r requirements.txt

2. Check the packages are installed in your local or global virtual environment

   py -m venv <virtual environment name>       ------- to create your local virtual environment

   <virtual environment name>\Scripts\activate ------- to activate your local virtual environment

3. Create the database in your postgresql CLI PgAdmin4 and update it in .env file

DATABASE_URL='postgresql://<your_db_username>:your_db_password@localhost/<database_name>'
(Replace the DATABASE_URL with your actual PostgreSQL credentials).

4. Run the program in cmd

   python run.py        ----------- to run where run.py directory is opened

5. Or Run and Debug in your CLI

# Instruction for Testing the project using pytest

1. Install pytest and pytest-flask in your pip environment.

2. In your CLI or cmd, enter pytest

3. Check the execution of the test cases.



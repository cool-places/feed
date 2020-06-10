To set up a virtual environment, first navigate to root directory and
run

    python3 -m venv .

To activate the virtual environment, run

    source bin/activate

To deactivate the virtual environment, run

    deactivate

When you run `pip install -r requirements.txt`, it will most likely
fail to install `pyodbc` the first time. You must first do

    sudo apt-get install unixodbc-dev

and (maybe) install `g++` too:

    sudo apt install g++

Finally, install `python-dev`.

    sudo apt install python-dev

You will also have to install the Microsoft ODBC driver for SQL server.
Follow the instructions here[https://docs.microsoft.com/en-us/sql/connect/odbc/linux-mac/installing-the-microsoft-odbc-driver-for-sql-server?view=sql-server-ver15#ubuntu17].

To run, first do

    export FLASK_APP=feed.py

Then

    flask run
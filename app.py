from flask_app import Flask, render_template
import pyodbc
import os
from dotenv import load_dotenv

app = Flask(__name__)

# Connectrion details for SQL server
load_dotenv()
server = os.getenv('SERVER')
database = os.getenv('DATABASE')
username = os.getenv('DB_USERNAME')
password = os.getenv('PASSWORD')
driver = os.getenv('DRIVER')

# Database connection
conn = pyodbc.connect('DRIVER=' + driver + ';SERVER=' + server + ';PORT=1433;DATABASE=' + database + ';UID=' + username + ';PWD=' + password)
cursor = conn.cursor()

@app.route('/')
def index():
    cursor.execute("SELECT year, SUM(CASE WHEN gender_code = 1 THEN total_population ELSE 0 END) AS male_population, "
                   "SUM(CASE WHEN gender_code = 2 THEN total_population ELSE 0 END) AS female_population "
                   "FROM dbo.population_data "
                   "GROUP BY year "
                   "ORDER BY year")
    data = cursor.fetchall()

    years = [row[0] for row in data]
    male_population = [row[1] for row in data]
    female_population = [row[2] for row in data]

    return render_template('index.html', years=years, male_population=male_population, female_population=female_population, zip=zip)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

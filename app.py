from flask import Flask, render_template, send_file
import pyodbc
import os
from dotenv import load_dotenv
import matplotlib.pyplot as plt
import io
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas

app = Flask(__name__)

# Load environment variables
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
    # Query data
    cursor.execute("SELECT year, SUM(CASE WHEN gender_code = 1 THEN total_population ELSE 0 END) AS male_population, "
                   "SUM(CASE WHEN gender_code = 2 THEN total_population ELSE 0 END) AS female_population "
                   "FROM dbo.population_data "
                   "GROUP BY year "
                   "ORDER BY year")
    data = cursor.fetchall()

    years = [row[0] for row in data]
    male_population = [row[1] for row in data]
    female_population = [row[2] for row in data]

    return render_template('index.html', years=years, male_population=male_population, female_population=female_population)

@app.route('/plot.png')
def plot_png():
    # Generate plot
    cursor.execute("SELECT year, SUM(CASE WHEN gender_code = 1 THEN total_population ELSE 0 END) AS male_population, "
                   "SUM(CASE WHEN gender_code = 2 THEN total_population ELSE 0 END) AS female_population "
                   "FROM dbo.population_data "
                   "GROUP BY year "
                   "ORDER BY year")
    data = cursor.fetchall()

    years = [row[0] for row in data]
    male_population = [row[1] for row in data]
    female_population = [row[2] for row in data]

    # Create figure and axis
    fig, ax = plt.subplots()

    # Plot the data
    ax.plot(years, male_population, label='Male Population', color='blue')
    ax.plot(years, female_population, label='Female Population', color='red')

    # Add labels and legend
    ax.set_xlabel('Year')
    ax.set_ylabel('Population')
    ax.legend()

    # Create an in-memory buffer to save the plot
    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)

    # Return image as response
    output.seek(0)
    return send_file(output, mimetype='image/png')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

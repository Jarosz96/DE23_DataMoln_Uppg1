from flask import Flask, render_template
import pyodbc
import plotly.express as px
import plotly.io as pio
import os

app = Flask(__name__)

# Database connection setup
def get_db_connection():
    server = os.getenv('DB_SERVER')
    database = os.getenv('DB_DATABASE')
    username = os.getenv('DB_USERNAME')
    password = os.getenv('DB_PASSWORD')
    driver = '{ODBC Driver 17 for SQL Server}'
    conn = pyodbc.connect(f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}')
    return conn

@app.route('/')
def index():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = '''
    SELECT year, SUM(CASE WHEN gender_code = 1 THEN total_population ELSE 0 END) AS male_population,
           SUM(CASE WHEN gender_code = 2 THEN total_population ELSE 0 END) AS female_population
    FROM dbo.population_data
    GROUP BY year
    ORDER BY year
    '''
    
    cursor.execute(query)
    data = cursor.fetchall()
    conn.close()

    # Prepare data for the graph
    years = [row[0] for row in data]
    male_population = [row[1] for row in data]
    female_population = [row[2] for row in data]

    # Create Plotly figure
    fig = px.line(x=years, y=[male_population, female_population], labels={'x': 'Year', 'y': 'Population'},
                  title="Population by Gender Over Time", 
                  color_discrete_map={"Male Population": 'blue', "Female Population": 'red'})
    
    fig.update_layout(xaxis_title='Year', yaxis_title='Population')

    # Render the graph as an HTML component
    graph_html = pio.to_html(fig, full_html=False)
    
    return render_template('index.html', graph_html=graph_html)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

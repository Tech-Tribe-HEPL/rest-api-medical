# More info about libs available in requirements.txt
# Pressing F5 will run the app and open the browser with the swagger UI

from apiflask import APIFlask
import psycopg
import os

app = APIFlask(__name__, title='Medical API', version='1.0')

@app.get('/medical')
def index():
    conn.cursor().execute("""
                        SELECT medicaltreatement.MedicalTreatmentUniqueId,medicaltreatment.Description,doctor.name
                        FROM medicaltreatment 
                        JOIN doctor ON medicaltreatment.LeadDoctor = doctor.InamiNumber
                        """)
    content = conn.cursor().fetchall()
    flask.jsonify(content)
    return flask.jsonify(content)

@app.post('/medical')
def post_medical():
    conn.cursor().execute("""
                        INSERT INTO medicaltreatment (MedicalTreatmentUniqueId, Description, Citizen, LeadDoctor)
                        VALUES ('1','test','1234567890','1234567890');
                        """)
    conn.commit()
    return '201 - Medical treatment created'

@app.get('/medical/<int:id>')
def get_medical(id):
    conn.cursor().execute("""
                        SELECT * FROM medicaltreatment 
                        WHERE Citizen = '1234567890';
                        """)
    #get the content from cursor in json format
    content = conn.cursor().fetchall()
    #parse the content into 
    return flask.jsonify(content)

if __name__ == '__main__':
    # Extract from envionnement variable information to connect to the database
    pg_user = os.getenv('POSTGRES_USER', 'postgres')
    pg_password = os.getenv('POSTGRES_PASSWORD', 'postgres')
    pg_host = os.getenv('POSTGRES_HOST', 'localhost')
    pg_port = os.getenv('POSTGRES_PORT', '5432')
    pg_db = os.getenv('POSTGRES_DB', 'test')
    #Display a Warning if the default values are used
    if pg_user == 'postgres' or pg_password == 'postgres' or pg_host == 'localhost' or pg_port == '5432' or pg_db == 'test':
        print('Warning: Using default values for database connection')
    # Connect to the database
    with psycopg.connect("dbname=test user=postgres") as conn:
        app.run(conn)
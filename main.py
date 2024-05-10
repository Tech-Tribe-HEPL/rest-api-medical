# More info about libs available in requirements.txt
# Pressing F5 will run the app and open the browser with the swagger UI

from apiflask import APIFlask
from flask_cors import CORS
import flask
import psycopg
import os

def get_db_connection():
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
    with psycopg.connect() as conn:
        return conn

def create_app(config_filename):
    app = APIFlask(__name__, title='Medical API', version='1.0')
    CORS(app)
    @app.get('/medical')
    def index():
        conn = get_db_connection
        # TODO: Check if this method is vulnerable to SQL Injection
        user_uuid = "1234567890" # TODO: Extract from JWT token
        
        # Obtain get_db_connection
        conn = get_db_connection
        conn.cursor().execute("""
                                SELECT * FROM medicaltreatment 
                                WHERE citizen = '%s';
                                """, (user_uuid))
        content = conn.cursor().fetchall()
        conn.close()
        
        flask.jsonify(content)
        return flask.jsonify(content)

    @app.post('/medical')
    def post_medical():
        conn = get_db_connection
        conn.cursor().execute("""
                                INSERT INTO medicaltreatment (MedicalTreatmentUniqueId, Description, Citizen, LeadDoctor)
                                VALUES ('1','test','1234567890','1234567890');
                                """)
        conn.commit()
        conn.close()
        return '201 - Medical treatment created'

    @app.get('/medical/<int:id>')
    def get_medical(id):
        #get the content from the database /!\ SQL Injection
        id = flask.request.args.get('id')
        # Obtain get_db_connection
        conn = get_db_connection
        
        conn.cursor().execute("""
                                SELECT * FROM medicaltreatment
                                WHERE id = %s AND citizen = '%s';
                                """, (id, user_uuid))
        #get the content from cursor in json format
        content = conn.cursor().fetchall()
        conn.close()
        #parse the content into
        return flask.jsonify(content)

    @app.errorhandler(404)
    def not_found(error):
        # This function will handle 404 errors
        # display the full path in the response 
        return flask.jsonify(flask.request.full_path)
    return app


app = create_app(__name__)

if __name__ == "__main__":
    app.run(debug=True)
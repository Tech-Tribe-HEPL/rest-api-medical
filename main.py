# More info about libs available in requirements.txt
# Pressing F5 will run the app and open the browser with the swagger UI

from apiflask import APIFlask
from flask_cors import CORS
import flask
import psycopg
import os
import logging

class DatabaseConnection:
    # Singleton pattern
    # A timer to deconnect the database after a certain time could be added
    _instance = None

    def __new__(cls,app):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.connect(app)
        return cls._instance

    def connect(self,app):
        # Extract from environment variable information to connect to the database
        pg_user = os.getenv('POSTGRES_USER', 'postgres')
        pg_password = os.getenv('POSTGRES_PASSWORD', 'postgres')
        pg_host = os.getenv('POSTGRES_HOST', 'localhost')
        pg_port = os.getenv('POSTGRES_PORT', '5432')
        pg_db = os.getenv('POSTGRES_DB', 'test')
        # Display a Warning if the default values are used
        if pg_user == 'postgres' and pg_password == 'postgres' and pg_host == 'localhost' and pg_port == '5432' and pg_db == 'test':
             app.logger.info('Warning: Using default values for database connection')
            
        # Connect to the database
        app.logger.info(f'Connecting to database {pg_db} on {pg_host}:{pg_port} as {pg_user}')
        #Based on key values present there  https://www.postgresql.org/docs/current/libpq-connect.html#LIBPQ-CONNSTRING-KEYWORD-VALUE
        self.conn = psycopg.connect(
            user=pg_user,
            password=pg_password,
            host=pg_host,
            port=pg_port,
            dbname=pg_db
        )
        
    def get_connection(self):
        return self.conn


def create_app():
    
    app = APIFlask(__name__, title='Medical API', version='1.0')
    CORS(app)
    db = DatabaseConnection(app)
    app.logger.setLevel(logging.DEBUG) 
    app.logger.info("Init the application.")
    @app.get('/')
    def index():
        conn = db.get_connection()
        # TODO: Check if this method is vulnerable to SQL Injection
        user_uuid = "123456789012" # TODO: Extract from JWT token
        cur = conn.cursor()
        cur.execute("""
                                SELECT * FROM medicaltreatment 
                                WHERE citizen = (%s);
                                """, (user_uuid,))
        content = cur.fetchall()
        conn.close()
        
        flask.jsonify(content)
        return flask.jsonify(content)

    @app.post('/')
    def post_medical():
        conn = db.get_connection()
        conn.cursor().execute("""
                                INSERT INTO medicaltreatment (MedicalTreatmentUniqueId, Description, Citizen, LeadDoctor)
                                VALUES ('1','test','1234567890','1234567890');
                                """)
        conn.commit()
        conn.close()
        return '201 - Medical treatment created'

    @app.get('/<int:id>')
    def get_medical(id):
        #get the content from the database /!\ SQL Injection
        id = flask.request.args.get('id')
        #Obtain get_connection
        conn = db.get_connection()

        conn.cursor().execute("""
                                SELECT * FROM medicaltreatment
                                WHERE id = %s AND citizen = '%s';
                                """, (id, user_uuid))
        #get the content from cursor in json format
        content = conn.cursor().fetchall()
        conn.close()
        #parse the content into
        return flask.jsonify(content)

    return app

app = create_app() 

if __name__ == "__main__":
    from gunicorn.main import run  # Assuming Gunicorn is installed
    run(app, "0.0.0.0:5000", workers=4)  # Run Gunicorn with the app instance
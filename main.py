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
            WHERE citizen = %s;
        """, (user_uuid,))
        rows = cur.fetchall()
        column_names = [desc[0] for desc in cur.description]
        
        # Construct a list of dictionaries
        content = []
        for row in rows:
            content.append(dict(zip(column_names, row)))
        
        return flask.jsonify(content)

    #TODO This route should be secured more deeply with a JWT token -> To be seen in the api gateway
    #TODO add a check if the doctor exist and return error accordingly
    @app.post('/')
    def post_medical():
        conn = db.get_connection()
        conn.cursor().execute("""
                                INSERT INTO medicaltreatment (Description, Citizen, LeadDoctor,startdate)
                                VALUES ('%s','%s','%s','%s','%s');
                                """, (flask.request.json['Description'], flask.request.json['Citizen'], flask.request.json['LeadDoctor'],flask.request.json['startdate']))
        conn.commit()
        conn.close()
        return '201 - Medical treatment created'

    #This is a full access of a folder: it should be logged in the system
    @app.get('/<int:id>')
    def get_medical(id):
        #get the content from the database /!\ SQL Injection
        id = flask.request.args.get('id')
        #extracted from the JWT token by kong
        user_uuid = "123456789012"
        #Obtain get_connection
        conn = db.get_connection()
        curr = conn.cursor()
        curr.execute("""
                                SELECT * FROM medicaltreatment
                                WHERE id = %s AND citizen = '%s';
                                """, (id, user_uuid))
        #get the content from cursor in json format
        rows = cur.fetchall()
        column_names = [desc[0] for desc in cur.description]
        
        # Construct a list of dictionaries
        content = []
        for row in rows:
            content.append(dict(zip(column_names, row)))
        
        #Log in the db the access using an insert
        conn.cursor().execute("""
                                INSERT INTO accesslog (MedicalTreatmentUniqueId, Citizen, AccessDate)
                                VALUES ('%s','%s',CURRENT_TIMESTAMP);
                                """,(id, user_uuid))
        #The postgresql instance generate the timestamp
        conn.commit()
        return flask.jsonify(content)

    return app

app = create_app() 

if __name__ == "__main__":
    from gunicorn.main import run  # Assuming Gunicorn is installed
    run(app, "0.0.0.0:5000", workers=4)  # Run Gunicorn with the app instance
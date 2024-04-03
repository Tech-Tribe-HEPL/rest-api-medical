# More info about libs available in requirements.txt
# Pressing F5 will run the app and open the browser with the swagger UI

from apiflask import APIFlask


app = APIFlask(__name__, title='Wonderful API', version='1.0')


@app.get('/')
def index():
    return {'message': 'hello'}


if __name__ == '__main__':
    app.run()
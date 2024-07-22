from Model_Handler import Model_handler
from flask import Flask, request
from flask_cors import CORS


app = Flask(__name__)
CORS(app)
model = Model_handler()

@app.route('/')
def hello_world():
   return 'Hello World'

@app.route('/generateMove', methods = ["POST"])
def generate_move() :
   data = request.get_json()
   return model.predict(data['state'], data['turn'])

if __name__ == '__main__':
   app.run(debug=True)
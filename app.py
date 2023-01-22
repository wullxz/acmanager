from flask import Flask, jsonify
from flask_cors import CORS
from AcAutomation import AcConfig, AcServer


# configuration
DEBUG = True

# instantiate the app
app = Flask(__name__)
app.config.from_object(__name__)

# enable CORS
CORS(app, resources={r'/*': {'origins': '*'}})

@app.route('/api/server', methods=['GET'])
def get_server():
  return jsonify({ "servers": AcServer.get_server_list()})

if __name__ == '__main__':
  app.run(host='0.0.0.0', port=5000)
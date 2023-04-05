from flask import Flask, jsonify, request
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
def get_servers():
    return jsonify({ "servers": AcServer.get_server_list()})
    
@app.route('/api/server/', defaults={'srv_number': None}, methods=['GET', 'POST'])
@app.route('/api/server/<srv_number>', methods=['GET', 'POST'])
def get_server(srv_number):
  if request.method == 'GET' and srv_number is not None:
    return jsonify(AcServer.get_server(srv_number))

  if request.method == 'GET':
    return ('', 204)

  # Create new Server
  srv_data = request.get_json()
  if srv_number is None:
    srv_number = AcServer.get_free_srvnum()
  acsrv = AcServer(srv_number)
  (ret, exception) = acsrv.create_config(srv_data)
  if ret:
    return ('', 200)
  else:
    return (str(exception), 406)

@app.route('/api/tracks', methods=['GET'])
def get_available_tracks():
  return jsonify(AcConfig.get_available_tracks())

@app.route('/api/cars', methods=['GET'])
def get_available_cars():
  return jsonify(AcConfig.get_available_cars())

if __name__ == '__main__':
  app.run(host='localhost', port=5000)
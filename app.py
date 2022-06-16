import json, os, urllib3, threading, time
from flask import Flask, jsonify, request, render_template
# from tasks import uwsgi_task
import cmd

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

BASE_URL = "https://owner-api.teslamotors.com/api/1/vehicles/"

global TOKEN, VEHICLE_ID, INPUT_CMD, PARAMETER_1, PARAMETER_2, INITIAL_VEHICLE_STATE


#post /store data: {name :}
@app.route('/tesla' , methods=['POST'])
def create_store():
  request_data = request.get_json()

  TOKEN = request_data['TOKEN']
  VEHICLE_ID = request_data['VEHICLE_ID']
  INPUT_CMD = request_data['INPUT_CMD']
  PARAMETER_1 = request_data['PARAMETER_1']
  PARAMETER_2 = request_data['PARAMETER_2']

  INITIAL_VEHICLE_STATE = cmd.GetVehicleState(BASE_URL, VEHICLE_ID, TOKEN)

  if INPUT_CMD == "test_command":
    INITIAL_VEHICLE_STATE = "testing"


  if INITIAL_VEHICLE_STATE is not None:

    RETURN_DATA = {
      "statusCode": 200,
      "BASE_URL": BASE_URL,
      "VEHICLE_ID": VEHICLE_ID,
      "INPUT_CMD": INPUT_CMD,
      "PARAMETER_1": PARAMETER_1,
      "PARAMETER_2": PARAMETER_2,
      "INITIAL_VEHICLE_STATE": INITIAL_VEHICLE_STATE
      } 
  else:

    RETURN_DATA = {
      "statusCode": 400,
      "BASE_URL": BASE_URL,
      "VEHICLE_ID": VEHICLE_ID,
      "INPUT_CMD": INPUT_CMD,
      "PARAMETER_1": PARAMETER_1,
      "PARAMETER_2": PARAMETER_2,
      "INITIAL_VEHICLE_STATE": INITIAL_VEHICLE_STATE
      }
    return jsonify(RETURN_DATA)  

  t = threading.Thread(target = backend_processing, args=(INITIAL_VEHICLE_STATE, BASE_URL, VEHICLE_ID, INPUT_CMD, PARAMETER_1, PARAMETER_2, TOKEN))
  t.daemon = True 
  t.start()
  return jsonify(RETURN_DATA)

def backend_processing(INITIAL_VEHICLE_STATE, BASE_URL, VEHICLE_ID, INPUT_CMD, PARAMETER_1, PARAMETER_2, TOKEN):
    # Capture the INITIAL_VEHICLE_STATE to verify that the vehicle is awake
    if INITIAL_VEHICLE_STATE == "online" or INITIAL_VEHICLE_STATE == "testing":
      print("Sending the " + INPUT_CMD)
      cmd.RunCommand(BASE_URL, VEHICLE_ID, INPUT_CMD, PARAMETER_1, PARAMETER_2, TOKEN)
    else:
      print("Vehicle ID # " + VEHICLE_ID + " is currently " + INITIAL_VEHICLE_STATE)

      print("Sending the wake_up command to vehicle ID #" + VEHICLE_ID)
      cmd.WakeVehicle(BASE_URL, VEHICLE_ID, TOKEN)

      print("Sending the " + INPUT_CMD + " command to vehicle ID #" + VEHICLE_ID)
      cmd.RunCommand(BASE_URL, VEHICLE_ID, INPUT_CMD, PARAMETER_1, PARAMETER_2, TOKEN)


app.run(host="0.0.0.0", port=5000, threaded=True)

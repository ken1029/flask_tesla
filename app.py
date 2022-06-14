import json,os,urllib3
from flask import Flask,jsonify,request,render_template

app = Flask(__name__)

#stores = [{
#    'name': 'My Store',
#    'items': [{'name':'my item', 'price': 15.99 }]
#}]

BASE_URL = "https://owner-api.teslamotors.com/api/1/vehicles/"

#post /store data: {name :}
@app.route('/tesla' , methods=['POST'])
def create_store():
  request_data = request.get_json()

  global TOKEN, VEHICLE_ID, INPUT_CMD, PARAMETER_1, PARAMETER_2, INITIAL_VEHICLE_STATE
  TOKEN = request_data['TOKEN']
  VEHICLE_ID = request_data['VEHICLE_ID']
  INPUT_CMD = request_data['INPUT_CMD']
  PARAMETER_1 = request_data['PARAMETER_1']
  PARAMETER_2 = request_data['PARAMETER_2']

  INITIAL_VEHICLE_STATE = GetVehicleState(BASE_URL, VEHICLE_ID)

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

  # Capture the INITIAL_VEHICLE_STATE to verify that the vehicle is awake
  print(INITIAL_VEHICLE_STATE)
  if INITIAL_VEHICLE_STATE == "online" or INITIAL_VEHICLE_STATE == "testing":
    if INPUT_CMD == "start_hvac":
      StartClimateControl(BASE_URL, VEHICLE_ID)
    print("Sending the " + INPUT_CMD)
  else:
    print("Vehicle ID # " + VEHICLE_ID)

  return jsonify(RETURN_DATA)

#################def############################
def GetVehicleState(BASE_URL, VEHICLE_ID):
    # Variables
    HEADERS = {
      'Authorization': "Bearer "+TOKEN,
      'Content-Type': 'application/json',
      'User-Agent': 'None'
    }
    URL = BASE_URL + VEHICLE_ID
    HTTP = urllib3.PoolManager()
    HTTP_REQUEST = HTTP.request(
      'GET',
      URL,
      headers=HEADERS
    )
    HTTP_REQUEST_STATUS_CODE = HTTP_REQUEST.status
#    print(HTTP_REQUEST_STATUS_CODE)

    if HTTP_REQUEST_STATUS_CODE == 200:
      VEHICLE_DATA = json.loads(HTTP_REQUEST.data.decode('utf-8'))
      VEHICLE_STATE = VEHICLE_DATA["response"]["state"]

      return(VEHICLE_STATE)

def WakeVehicle(BASE_URL, VEHICLE_ID):
  # Variables
  HEADERS = {
    'Authorization': "Bearer " + TOKEN,
    'Content-Type': 'application/json',
    'User-Agent': 'None'
  }
  URL = BASE_URL + VEHICLE_ID + "/wake_up"
  HTTP = urllib3.PoolManager()
  HTTP_REQUEST = HTTP.request(
    'POST',
    URL,
    headers=HEADERS
  )
  HTTP_REQUEST_STATUS_CODE = HTTP_REQUEST.status
  
  # Only for debug
  # HTTP_REQUEST = URL + HEADERS
  # HTTP_REQUEST_STATUS_CODE = 200

  if HTTP_REQUEST_STATUS_CODE == 200:
    # Waiting for the vehicle to wake up before returning
    while GetVehicleState(BASE_URL, VEHICLE_ID) != "online":
      # Variables
      COUNTER = 0

      if COUNTER > 20:
        print("ERROR: Exiting as the vehicle is not waking up...")
        exit(1)
      else:
        # Sleep for 1 second and increment COUNTER
        time.sleep(1)
        COUNTER = COUNTER + 1
  else:
    print("ERROR: The vehicle failed to receive the wake up command")

# Function that activates the vehicle's Climate Control system
def StartClimateControl(BASE_URL, VEHICLE_ID):
  # Variables
  HEADERS = {
    'Authorization': "Bearer " + TOKEN,
    'User-Agent': 'None'
  }
  URL = BASE_URL + VEHICLE_ID + "/command/auto_conditioning_start"
  HTTP = urllib3.PoolManager()
  HTTP_REQUEST = HTTP.request(
    'POST',
    URL,
    headers=HEADERS
  )
  HTTP_REQUEST_STATUS_CODE = HTTP_REQUEST.status

  if HTTP_REQUEST_STATUS_CODE == 200:
    print("The vehicle's Climate Control system has been activated")
  else:
    print("ERROR: The vehicle failed to receive the start Climate Control system command")

app.run(host="0.0.0.0", port=5000)

from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from flask import *
from sklearn import linear_model
import pandas

hostname = "192.168.43.190" # this is the hostname in pg 192.168.0.107 this is the ip address when connected to phone 192.168.43.190
app = Flask(__name__)

parameters_temperature, parameters_soil_moisture, parameters_humidity = None, None, None

temp, moist, hum = 0, 0, 0
condition, accuracy  =  "Normal", 0
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/manual_model_test")
def manual_model_test():
    return render_template("manual_request.html")

@app.route("/result")
def result():
    global condition, accuracy, temp, moist, hum
    return render_template("result.html", condition = condition, accuracy = accuracy, temp = temp, moist = moist, hum = hum)

@app.route("/analyse_manual_data", methods = ['GET'])
def analyse_manual_data():
    temperature = request.args.get('temperature')
    soil_moisture = request.args.get('soil_moisture')
    humidity = request.args.get("humidity")
    value = True
    status = "Normal"
    df = pandas.read_csv("dataset1.csv")
    features = df[['Temperature', 'Humidity','Soil moisture']]
    result = df['status']
    if temperature is None and humidity is None and soil_moisture is None:
        return render_template("DataNotFound.html")

    regr = linear_model.LinearRegression()
    regr.fit(features, result)

    predict = regr.predict([[temperature, humidity, soil_moisture]])
    if predict>1:
        value=False
    else:
        value=True
        
    print(value)

    if value==True:
        status = "Normal"
        print("normal")
    else:
        status = "Drought"
        print("Drought")
    
    r2_score = regr.score(features,result)

    print("the accuracy of Linear Regression is =",r2_score*100,'%')

    global accuracy, condition, temp, moist, hum
    condition = status
    accuracy = r2_score*100
    temp = temperature
    moist = soil_moisture
    hum = humidity
    return redirect(url_for('result'))



@app.route('/input_pipe', methods = ['GET'])
def input_pipe():
    global parameters_temperature, parameters_soil_moisture, parameters_humidity
    parameters_temperature = request.args.get('temperature')
    parameters_soil_moisture = request.args.get('soil_moisture')
    parameters_humidity = request.args.get("humidity")
    print(parameters_humidity)
    print(parameters_soil_moisture)
    print(parameters_temperature)
    return "SUCCESS"

@app.route("/access_ml_result")
def access_ml_result():
    global temp, moist, hum
    value = True
    status = "Normal"
    df = pandas.read_csv("dataset1.csv")
    features = df[['Temperature', 'Humidity','Soil moisture']]
    result = df['status']
    global parameters_temperature, parameters_soil_moisture, parameters_humidity, temp, moist, hum
    if parameters_humidity is None and parameters_soil_moisture is None and parameters_temperature is None:
        return render_template("DataNotFound.html")
    regr = linear_model.LinearRegression()
    regr.fit(features, result)
    temperature = parameters_temperature
    temp = temperature
    humidity = parameters_humidity
    hum = humidity
    soil_moisture = parameters_soil_moisture
    moist = soil_moisture
    predict = regr.predict([[temperature, humidity, soil_moisture]])
    if predict>1:
        value=False
    else:
        value=True
        
    print(value)

    if value==True:
        status = "Normal"
        print("normal")
    else:
        status = "Drought"
        print("Drought")

    r2_score = regr.score(features,result)

    print("the accuracy of Linear Regression is =",r2_score*100,'%')

    global accuracy, condition
    condition = status
    accuracy = r2_score*100
    
    return redirect(url_for('result'))

if __name__ == '__main__':
    #app.run(debug=True) # This is for developement only

    """The below three lines are for production only"""
    http_server = HTTPServer(WSGIContainer(app))
    #http_server.listen(int(5000),address="192.168.43.190")
    #http_server.listen(int(5000),address="192.168.0.107")
    http_server.listen(int(5000),address=hostname)
    IOLoop.instance().start()
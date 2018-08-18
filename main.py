import argparse
import os
import json
import requests
from time import sleep
from influxdb import InfluxDBClient

def request(url):
    headers = {'Content-Type': 'application/json'}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return json.loads(response.content.decode('utf-8'))
    else:
        print("Error getting weather: {0}".format(response.status_code))
        return None

def weather(city, state, interval, db_host, db_port, db_name):

    db_client = InfluxDBClient(host=db_host, port=db_port, database=db_name)
    db_client.create_database(db_name)


    print("Getting weather in {0}, {1} and sending to {2}:{3} every {4} seconds".format(city, state, db_host, db_port, interval))
    url = "https://query.yahooapis.com/v1/public/yql?q=select%20item.condition%2C%20atmosphere%20from%20weather.forecast%20where%20woeid%20in%20(select%20woeid%20from%20geo.places(1)%20where%20text%3D%22{0}%2C%20{1}%22)&format=json&env=store%3A%2F%2Fdatatables.org%2Falltableswithkeys".format(city, state)

    ok = True
    while(ok):
        response = request(url)
        if response is not None:
            channel = response['query']['results']['channel']
            atmosphere = channel['atmosphere']
            temp = channel['item']['condition']['temp']
            pressure = atmosphere['pressure']
            humidity = atmosphere['humidity']
            rising = atmosphere['rising']
            metrics = [
                {
                    'measurement': 'weather',
                    'tags': {
                        'city': city,
                        'state': state
                    },
                    'fields': {
                        'temp': temp,
                        'humidity': humidity,
                        'pressure': pressure,
                        'rising': rising
                    }
                }
            ]
            db_client.write_points(metrics)
            #print("temp:{0} pressure:{1} humidity:{2} rising:{3}".format(temp, pressure, humidity, rising))
        sleep(interval)


def parse_args():
    parser = argparse.ArgumentParser(description='Weather Reporter')
    parser.add_argument('--city', default=os.environ.get('CITY', 'Newark'))
    parser.add_argument('--state', default=os.environ.get('STATE', 'DE'))
    parser.add_argument('--interval', type=int, default=int(os.environ.get('INTERVAL', 1800)))
    parser.add_argument('--host', default=os.environ.get('HOST', '192.168.1.4'))
    parser.add_argument('--port', default=os.environ.get('PORT', '8086'))
    parser.add_argument('--db', default=os.environ.get('DB_NAME', 'stats'))

    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    weather(city=args.city, state=args.state, interval=args.interval, db_host=args.host, db_port=args.port, db_name=args.db)

import json
from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash
from yaml import load, dump
from contextlib import closing
from soda import SodaQuery

try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

app = Flask(__name__)
app.config.from_pyfile('config.cfg')

@app.route("/")
def map():
    return render_template("map.html", api_key=app.config['GOOGLE_API_KEY'])

@app.route("/foodtrucks", methods=['GET'])
def trucks():
	if request.method == 'GET':
		query = SodaQuery('http://data.sfgov.org/resource/rqzj-sfat.json') \
					.select('objectid', 'applicant', 'fooditems', 'latitude', 'longitude', 'location', 'address') \
					.where(facilitytype = 'Truck', approved__null = False, latitude__null = False, longitude__null = False, address__null = False)

		# Unfortunately, it looks like the within_box api on the data.sfgov.org site doesn't work, at least for this dataset
		# Uncomment this when it does work, and refactor the JS to not expect a full list of trucks as it does now
		#location_box = request.args.get('location_box', None)
		#if location_box:
		#	query = query.where(location__within_box=location_box.split(','))


		data = query.execute()

		response = []
		for truck in data:
			response.append({
				'id': truck['objectid'],
				'name': truck['applicant'],
				'type': truck['fooditems'],
				'lat': truck['latitude'],
				'lng': truck['longitude'],
				'address': truck['address']
			})

		return json.dumps(response), 200, {'Content-Type' : 'application/json'}

if __name__ == '__main__':
	app.run()
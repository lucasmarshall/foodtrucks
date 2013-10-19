import json
from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash
from yaml import load, dump
from contextlib import closing
from soda import SodaQuery

app = Flask(__name__)
app.config.from_pyfile('config.cfg')

@app.route("/")
def mapview():
    return render_template("map.html", api_key=app.config['GOOGLE_API_KEY'])

@app.route("/foodtrucks", methods=['GET'])
def trucks():
	if request.method == 'GET':
		query = SodaQuery('http://data.sfgov.org/resource/rqzj-sfat.json') \
				.select('objectid', 'applicant', 'fooditems', 'latitude', 'longitude', 'location', 'address') \
				.where( # get only food trucks, and filter out incomplete records
					facilitytype = 'Truck',
					approved__null = False,
					latitude__null = False,
					longitude__null = False,
					address__null = False
				)

		# @todo
		# Unfortunately, it looks like the within_box api on the data.sfgov.org site doesn't work, at least for this dataset
		# Uncomment this when it does work, and refactor the JS to not expect a full list of trucks as it does now
		# You'll also want to revisit caching stragegies as the query-based one implemented in the soda library won't cut it.
		#location_box = request.args.get('location_box', None)
		#if location_box:
		#	query = query.where(location__within_box=location_box.split(','))

		data     = query.execute()
		response = map(__doResponseMapping, data);

		return json.dumps(response), 200, {'Content-Type' : 'application/json'}

def __doResponseMapping(item):
	return {
		'id': item['objectid'],
		'name': item['applicant'],
		'type': item['fooditems'],
		'lat': item['latitude'],
		'lng': item['longitude'],
		'address': item['address'],
		'streetviewurl': 'http://maps.googleapis.com/maps/api/streetview?size=386x120&location=%s,%s&pitch=-8&sensor=true&key=%s' % (item['latitude'], item['longitude'], app.config['GOOGLE_API_KEY'])
	}

if __name__ == '__main__':
	app.run()
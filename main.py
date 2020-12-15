import csv, google_api_key, urllib.request, urllib.error, urllib.parse, json, random
from flask import Flask, render_template, request


def pretty(obj):
    return json.dumps(obj, sort_keys=True, indent=2)


def safeGet(url):
    try:
        return urllib.request.urlopen(url)
    except urllib.error.HTTPError as e:
        if hasattr(e, 'reason'):
            print('The server could not fulfill the request')
            print("Error reason: " + e.reason)


app = Flask(__name__)


# creates the homepage
@app.route("/")
def home():
    return render_template('index.html', prompt = None)


# gathers data from the csv file
def gatherSeaData():
    with open('Seattle_Data.csv', mode = 'r', encoding = 'utf-8') as file:
        csvfile = csv.DictReader(file)
        list1 = []
        for rows in csvfile:
            dict1 = {}
            dict1['long'] = rows['\ufeffLong']
            dict1['lat'] = rows['Lat']
            dict1['bname'] = rows['business_name']
            dict1['address'] = rows['address_help_your_customer_find']
            dict1['website'] = rows['business_website']
            dict1['phonenum'] = rows['phone_number_to_place_an_order']
            list1.append(dict1)
    return list1

# creates the second page of the web-app with suggestions
@app.route("/suggest")
def add():
        name = request.args.get('username')
        numid = request.args.get('numid')
        data = gatherSeaData()
        if name and numid:
            rand1 = random.randrange(1,2850)
            listdata = []
            for output in data[rand1:rand1 + int(numid)]:
                searchdata = get_Places(output['bname'])

                # grabs the data from the csv file
                dict2 = {}
                dict2['lat'] = output['lat']
                dict2['long'] = output['long']
                dict2['bname'] = output['bname']
                if output['website'] != '':
                    dict2['website'] = output['website']
                dict2['phonenum'] = output['phonenum']
                dict2['address'] = output['address']

                # grabs the data from the google places api
                if 'rating' in searchdata['candidates'][0].keys():
                    dict2['rating'] = searchdata['candidates'][0]['rating']
                if 'opening_hours' in searchdata['candidates'][0].keys():
                    dict2['open'] = searchdata['candidates'][0]['opening_hours']['open_now']
                if 'price_level' in searchdata['candidates'][0].keys():
                    dict2['pricelevel'] = searchdata['candidates'][0]['price_level']
                listdata.append(dict2)
            return render_template('search.html', alldata = listdata, name = name)
        else:
            return render_template('index.html', prompt = 0)


# creates the google places api url
def get_Places(bname = ''):
    params = {}
    params['key'] = google_api_key.key
    params['input'] = bname
    params['inputtype'] = 'textquery'
    params['fields'] = 'rating,opening_hours,price_level'
    url = "https://maps.googleapis.com/maps/api/place/findplacefromtext/json" + "?" + urllib.parse.urlencode(params)
    better = safeGet(urllib.request.Request(url)).read()
    return json.loads(better)


if __name__ == '__main__':
    app.run(host = "localhost", port = 8080, debug = True)
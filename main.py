from flask import Flask, jsonify, request, render_template, redirect, url_for
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

addressId = 1
addresses = [{"id": 1,
              "name": "Joshua Small",
              "address": "1060 N Downing St",
              "city": "Denver",
              "state": "CO",
              "zip": "80218"}]

@app.route("/")
def index():
    return render_template("main.html", addresses=addresses)

@app.route("/addresses")
def getAll():
    return jsonify({"addresses": addresses})

@app.route("/addresses", methods=["POST"])
def post():
    uspsId = "524FREEL4722"
    name = request.values["name"]
    address = request.values["address"]
    city = request.values["city"]
    state = request.values["state"]
    formZip = request.values["zip"]

    if city == "" and formZip == "" or state == "" and formZip == "":
        print("Must provide zip code or city and state")
        return redirect(url_for('index'))
    elif formZip == "":
        formZip = lookupZip(uspsId, address, city, state)
    elif city == "" or state == "":
        cityState = lookupCityState(uspsId, formZip)
        city = cityState[0]
        state = cityState[1]


    global addressId
    addressId += 1

    address = {
        "id": addressId,
        "name": name,
        "address": address,
        "city": city,
        "state": state,
        "zip": formZip
    }

    addresses.append(address)
    return redirect(url_for('index'))

@app.route("/delete/<int:_id>", methods=["POST"])
def delete(_id):
    address = [address for address in addresses if address["id"] == _id]
    addresses.remove(address[0])
    return redirect(url_for('index'))

def lookupZip(uspsId, address, city, state):
    url = "http://production.shippingapis.com/ShippingAPI.dll?API=ZipCodeLookup&XML="
    xml = """<ZipCodeLookupRequest USERID="{uspsId}">
                <Address ID="0">
                    <Address1></Address1>
                    <Address2>{address}</Address2>
                    <City>{city}</City>
                    <State>{state}</State>
                </Address>
            </ZipCodeLookupRequest>""".format(uspsId=uspsId,
                                              address=address,
                                              city=city,
                                              state=state)
    res = requests.get(url + xml)
    soup = BeautifulSoup(res.text, "html.parser")
    zipCode = soup.find('zip5').text
    return zipCode

def lookupCityState(uspsId, formZip):
    url = "http://production.shippingapis.com/ShippingApi.dll?API=CityStateLookup&XML="
    xml = """<CityStateLookupRequest USERID="{uspsId}">
                <ZipCode ID="0">
                    <Zip5>{formZip}</Zip5>
                </ZipCode>
            </CityStateLookupRequest>""".format(uspsId=uspsId, formZip=formZip)
    res = requests.get(url + xml)
    soup = BeautifulSoup(res.text, "html.parser")
    city = soup.find('city').text
    state = soup.find('state').text
    return [city, state]

if __name__ == "__main__":
    app.run()

import httplib2
import json

def getLocation(inputString):
    google_api_key = "AIzaSyDNHuQCoY2ZVjseYEriafya25hCOJ4Jd7c"
    locationString = inputString.replace(" ","+")
    url = ('https://maps.googleapis.com/maps/api/geocode/json?address=%s&key=%s'% (locationString, google_api_key))
    h = httplib2.Http()
    response, content = h.request(url, 'GET')
    result = json.loads(content)
    lat = result['results'][0]['geometry']['location']['lat']
    lng = result['results'][0]['geometry']['location']['lng']
    return (lat,lng)

def findRestaurant(mealType, location):
    foursquare_client_id = "WDFNQIYXIIKFH4B24H4DHMZORHMMB0CHTH0PLN1RHIKMEZPL"
    foursquare_client_secret = "FSFMFNZ3H55KWFBH4MG5EZEXYKEWCF2BDGYH05FANNHLJTJP"
    ll = getLocation(location)
    print(ll)
    lat = ll[0]
    lng = ll[1]
    print(lat)
    print(lng)
    
    location_url = ('https://api.foursquare.com/v2/venues/search?v=20170101&client_id=%s&client_secret=%s&ll=%s,+%s&explore?section=food&query=%s&venuePhoto=1') % (foursquare_client_id, foursquare_client_secret, lat, lng, mealType)

    h = httplib2.Http()
    response, content = h.request(location_url, 'GET')
    result = json.loads(content)
    restaurantObj = result['response']['venues'][0]
    restaurantID = restaurantObj['id']
    restaurantName = restaurantObj['name']
    restaurantAddr = restaurantObj['location']['address']
    restaurantIconObj = restaurantObj['categories'][0]['icon']
    restaurantImgString = restaurantIconObj['prefix']+"100x100"+restaurantIconObj['suffix']

    return { restaurantID, restaurantName, restaurantAddr, restaurantImgString}

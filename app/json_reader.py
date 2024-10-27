import json, sys

with open(sys.argv[1], 'r') as file:
    data = json.load(file)

    for user in data:
        id = user["id"]
        startpoint = user["startpoint"]
        endpoint = user["endpoint"]
        wagon_type = user["wagon_type"]
        ticket_count = user["ticket_count"]
        seat_preference = user["seat_preference"]
        departure_dates = user["departure_dates"]
        
        
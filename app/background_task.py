from app.config import settings, celery_client, client
import json, sys


@celery_client.task
async def check_new_orders(file_name):
    
    response = await client.post(
        url=f'{settings.API_ADDRESS}/api/auth/register',
        json={
            'fio': "Tenegin club",
            'email': "tene@mail.ru",
            'password': "123",
            'team': "Wins"
        }
    )
    token = response.json()["token"]
    

    with open(file_name, 'r') as file:
        data = json.load(file)
        for user in data:
            id = user["id"]
            startpoint = user["startpoint"]
            endpoint = user["endpoint"]
            wagon_type = user["wagon_type"]
            ticket_count = user["ticket_count"]
            seat_preference = user["seat_preference"]
            departure_dates = user["departure_dates"]
            
            
            trains = await client.get("http://84.252.135.231/api/info/train" + f"?start_point={startpoint}&end_point={endpoint}")
            for i in range(len(trains)):
                for y in i:
                    pass
            
        
        
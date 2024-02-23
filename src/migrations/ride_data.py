import random
from datetime import datetime, timedelta
import json


def generate_coordinates():
    """Generate random coordinates (latitude, longitude)."""
    lat = random.uniform(-90, 90)
    lon = random.uniform(-180, 180)
    return [lat, lon]


def random_date(start, l):
    """Generate a random datetime within `l` days of `start`."""
    current = datetime.strptime(start, "%Y-%m-%dT%H:%M:%S")
    delta = timedelta(days=random.randint(0, l))
    return (current + delta).strftime("%Y-%m-%dT%H:%M:%S")


def generate_car():
    makes = ["Tesla", "Toyota", "Ford", "BMW", "Volkswagen"]
    models = {"Tesla": ["Model 3", "Model S"],
              "Toyota": ["Corolla", "Camry"],
              "Ford": ["Fiesta", "Focus"],
              "BMW": ["3 Series", "5 Series"],
              "Volkswagen": ["Golf", "Polo"]}
    colors = ["Red", "Blue", "Green", "Black", "White"]
    make = random.choice(makes)
    model = random.choice(models[make])
    return {
        "make": make,
        "model": model,
        "year": random.randint(2015, 2023),
        "color": random.choice(colors),
        "plateNumber": "EV" + str(random.randint(1000, 9999))
    }


def generate_data_template(start_date, total_records=50):
    data_list = []
    for _ in range(total_records):
        car_data = generate_car()
        startPoint = generate_coordinates()
        endPoint = generate_coordinates()
        midPoint = generate_coordinates()
        data_list.append({
            "driverUserId": "driver" + str(random.randint(10000, 99999)),
            "startPoint": {"name": "City Center", "coordinates": startPoint},
            "endPoint": {"name": "Downtown", "coordinates": endPoint},
            "stopPoints": [{"name": "Midway Point", "coordinates": midPoint}],
            "capacity": {"total": 4, "occupied": random.randint(1, 4)},
            "car": car_data,
            "bookings": [],  # This could be populated similarly with user data and booking details
            "status": random.choice(["IN_PROGRESS", "COMPLETED", "CANCELLED"]),
            # assuming a 30-day span for ride dates
            "date": random_date(start_date, 30),
            "priceSeat": random.uniform(15.0, 30.0)
        })
    return data_list


# Generate data
start_date = "2023-05-01T14:00:00"
generated_data = generate_data_template(start_date, 50)

# Optionally, save to a file
with open("./generated_rides.json", "w") as file:
    json.dump(generated_data, file, indent=4)

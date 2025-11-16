# CarCool - The fun way of ride sharing 🚘

This repository contains the backend codebase for CarCool - a ride-sharing application built using Python, FastAPI, MongoDB, and Google Maps API.

## Features

- **User Authentication**: Secure user authentication system implemented.
- **Ride Management**: CRUD operations for managing rides.
- **Location Services**: Integration with Google Maps API for location-based services.
- **Notifications**: Real-time notifications for ride updates and statuses.
- **Machine Learning**: Users are matched based on their similarity closeness

## Tech Stack

- **Python**: Backend logic implemented using Python programming language.
- **FastAPI**: Utilized FastAPI framework for building robust APIs with ease.
- **MongoDB**: NoSQL database for storing application data.
- **Google Maps API**: Integration for location-based services and routing.
- **Hosting**: Virginia Tech's CS Cloud cluster

## Setup

1. Clone the repository:
    - git clone "repository-url"

2. Install dependencies:
    - pip install poetry
    - poetry install


4. Configure environment variables:

   - **MONGO_URI**: MongoDB connection string.
   - **GOOGLE_MAPS_API_KEY**: Google Maps API key.
   - **ENVIRONMENT**: local/prod

5. Run the application:
    - poetry run uvicorn src.app.main:app --reload
  

## Contributors

- Aseem Khandelwal
- Shankar Srinidhi
- Ashish Aggarwal
- Samar Kansal


<img src="./carcool.png" alt="CarcCool - Ride Sharing App Logo" width="200" height="200">






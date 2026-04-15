# profile-intelligence-API

Profile Intelligence API

Overview:
This is a simple REST API that creates and stores a person's name, gender, age and nationality based on the data from genderize.io, agify.io and nationalize.io APIs using their name.

It returns probability, sample size, gender, age group, country id and country probability, and handles invalid inputs and specific edge cases.

Tech Stack:
Python and Django 
https://api.genderized.io - external API
https://api.agify.io - external API
https://api.nationalize.io - external API

Endpoints:
1. POST /api/profiles

Example Request:
POST /api/profiles
body request: {
    "name": "john"
}

Successful Response:
{
    "status": "success",
    "message": "Profile created successfully",
    "data": {
        "id": "019d926d-3915-79fb-a8d8-73b79370f601",
        "name": "john",
        "gender": "male",
        "gender_probability": 1.0,
        "sample_size": 2692560,
        "age": 75,
        "age_group": "senior",
        "country_id": "NG",
        "country_probability": 0.07613817567167579,
        "created_at": "2026-04-15T15:40:22.509328Z"
    }
}

2. GET /api/profiles/<id>

Example Request:
GET /api/profiles/019d926d-3915-79fb-a8d8-73b79370f601

Successful Response:
{
    "status": "success",
    "message": "Profile Data",
    "data": {
        "id": "019d926d-3915-79fb-a8d8-73b79370f601",
        "name": "john",
        "gender": "male",
        "gender_probability": 1.0,
        "sample_size": 2692560,
        "age": 75,
        "age_group": "senior",
        "country_id": "NG",
        "country_probability": 0.07613817567167579,
        "created_at": "2026-04-15T15:40:22.509328Z"
    }
}

3. GET /api/profiles

Example Requests:
GET /api/profiles

Successful Response:
{
    "status": "success",
    "count": 3,
    "data": [
        {
            "id": "id-1",
            "name": "asun",
            "gender": "female",
            "age": 63,
            "age_group": "senior",
            "country_id": "MY"
        },
        {
            "id": "id-2",
            "name": "john",
            "gender": "male",
            "age": 75,
            "age_group": "senior",
            "country_id": "NG"
        },
        {
            "id": "id-3",
            "name": "ella",
            "gender": "female",
            "age": 53,
            "age_group": "adult",
            "country_id": "CM"
        }
    ]
}

GET /api/profiles?gender=male&country_id=NG

    "status": "success",
    "count": 1,
    "data": [
        {
            "id": "id-1",
            "name": "john",
            "gender": "male",
            "age": 75,
            "age_group": "senior",
            "country_id": "NG"
        }
    ]

4. DELETE /api/profiles/<id>

Example Request:
DELETE /api/profiles/0a3f8eb3-49a0-483f-b3b9-fea97739af80

Run Locally
1. Clone repository: git clone https://github.com/tolua-d/profile-intelligence-API.git
2. Install dependecies: pip install -r requirements.txt
3. Set necessary environment variables:  SECRET_KEY
4. Run the server: python manage.py runserver

Author
Tolu Agbaje-Daniels
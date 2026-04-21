# profile-intelligence-API

Queryable Intelligence Engine

Overview:
This is a simple REST API that creates and stores a person's name, gender, age 
and nationality based on the data from genderize.io, agify.io and nationalize.io APIs using their name.
It takes in some query parameters such as age_group, sort_by and min_age.

It returns a paginated response with probability, gender, age group, 
country id and country probability, and handles invalid inputs and specific edge cases.


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
    "name": "Thabo Ndebele"
}

Successful Response:
{
    "id": "019db06d-b517-70dd-8746-8c1e039a8dc0",
    "name": "Thabo Ndebele",
    "gender": "male",
    "gender_probability": 0.66,
    "age": 18,
    "age_group": "teenager",
    "country_id": "AO",
    "country_name": "Angola",
    "country_probability": 0.68,
    "created_at": "2026-04-21T14:24:32.183559Z"
}

2. GET /api/profiles/{id}

Example Request:
GET /api/profiles/019db06d-b517-70dd-8746-8c1e039a8dc0

Successful Response:
{
"status": "success",
"data": {
    "id": "019db06d-b517-70dd-8746-8c1e039a8dc0",
    "name": "Thabo Ndebele",
    "gender": "male",
    "gender_probability": 0.66,
    "age": 18,
    "age_group": "teenager",
    "country_id": "AO",
    "country_name": "Angola",
    "country_probability": 0.68,
    "created_at": "2026-04-21T14:24:32.183559Z"
    }
}

3. GET /api/profiles

Example Requests:
GET /api/profiles

Successful Response:
{
    "status": "success",
    "page": 1,
    "limit": 10,
    "total": 2,
    "data": [
        {
            "id": "019db06d-b3b9-719e-a8f3-3b8d66086c48",
            "name": "Bongani Khumalo",
            "gender": "male",
            "gender_probability": 0.91,
            "age": 14,
            "age_group": "teenager",
            "country_id": "AO",
            "country_name": "Angola",
            "country_probability": 0.11,
            "created_at": "2026-04-21T14:24:32.147440Z"
        },
        {
            "id": "019db06d-b242-7019-982f-62fe121d9ce8",
            "name": "Nompumelelo Sibanda",
            "gender": "female",
            "gender_probability": 0.98,
            "age": 16,
            "age_group": "teenager",
            "country_id": "AO",
            "country_name": "Angola",
            "country_probability": 0.84,
            "created_at": "2026-04-21T14:24:32.129889Z"
        }
    ]
}

GET /api/profiles?gender=male&country_id=NG
{
    "status": "success",
    "page": 1,
    "limit": 10,
    "total": 1,
    "data": [
        {
            "id": "019db06d-b3b9-719e-a8f3-3b8d66086c48",
            "name": "Bongani Khumalo",
            "gender": "male",
            "gender_probability": 0.91,
            "age": 14,
            "age_group": "teenager",
            "country_id": "NG",
            "country_name": "nigeria",
            "country_probability": 0.11,
            "created_at": "2026-04-21T14:24:32.147440Z"
        }
    ]
}

4. GET /api/profiles/search?q=male and female  teenagers from south africa
This endpoint takes in a query parameter q in the natural langauge sequence.

Successful Response:
{
    "status": "success",
    "page": 1,
    "limit": 10,
    "total": 3,
    "data": [
        {
            "id": "019db06d-b4d7-7a60-893a-3d5baa93224d",
            "name": "Tebogo Dube",
            "gender": "male",
            "gender_probability": 0.79,
            "age": 17,
            "age_group": "teenager",
            "country_id": "ZA",
            "country_name": "South Africa",
            "country_probability": 0.89,
            "created_at": "2026-04-21T14:24:32.179580Z"
        },
        {
            "id": "019db06d-b4aa-76a4-9bcf-840b96b836d4",
            "name": "Tendai Masondo",
            "gender": "male",
            "gender_probability": 0.7,
            "age": 18,
            "age_group": "teenager",
            "country_id": "ZA",
            "country_name": "South Africa",
            "country_probability": 0.59,
            "created_at": "2026-04-21T14:24:32.178442Z"
        },
        {
            "id": "019db06d-adbd-7944-81b6-fedbbe9f128e",
            "name": "Nokwanda Sibanda",
            "gender": "female",
            "gender_probability": 0.71,
            "age": 19,
            "age_group": "teenager",
            "country_id": "ZA",
            "country_name": "South Africa",
            "country_probability": 0.5,
            "created_at": "2026-04-21T14:24:32.076810Z"
        }
    ]
}

5. DELETE /api/profiles/<id>

Example Request:
DELETE /api/profiles/019db06d-b3b9-719e-a8f3-3b8d66086c48

Run Locally
1. Clone repository: git clone https://github.com/tolua-d/profile-intelligence-API.git
2. Install dependecies: pip install -r requirements.txt
3. Set necessary environment variables:  SECRET_KEY, DATABASE_URL
4. Run the server: python manage.py runserver

Author
Tolu Agbaje-Daniels
# *Too good to go stock reading*

A django web application to synchronise food stock items data within a shop stock through a REST
API.

## Testing the internet deployed version

*too good to go stock reading* is deployed on https://toogoodtogo-r3qg.onrender.com/. The following
examples will use this domain. Read the below section to deploy it locally.

## Deploy locally

*too good to go stock reading* comes with a `docker-compose.yaml` file. Run `docker-compose up` and
it will launch a postgres database and a django web server, and a one-off container will run the
migrations against the database. You will still need to create a superuser to access the admin
interface. You can do so with the following command: `docker compose exec frontend python manage.py
createsuperuser`. The email is not needed. Then it's standard django admin interface. You can access
it at `http://localhost:8000/admin/`.

## Develop locally

Well it's a standard django project, I should not even be writing this section. But OK, put that gun
down, I will give you some hints.

```bash
# install dependencies (if you don't have poetry you live in the middle-age)
poetry install
# fire a postgres database via docker (if you don't have docker you live in the middle-age)
docker run -e POSTGRES_PASSWORD=password -e POSTGRES_DB=too_good_to_go -p 5432:5432 -d postgres:15.2-alpine
# tell which settings we want to use (dev vs prod)
export DJANGO_SETTINGS_MODULE=toogoodtogo.settings.development
# the only migrations far-right has no problem with
python manage.py migrate
# "walkserver" won't do it for us, we live fast and we die young
python manage.py runserver
```

## Play with the API

*stock readings* are associated to a shop. You need to create a shop in the admin interface and
associate it to a user (yes it is a very subpar user-experience, I am sorry). Then you can post
*stock readings* for this shop.
Did I tell you we don't live in the middle-age anymore? Well, I do it again. Respect yourself and
install [httpie](https://httpie.io/): `pip install httpie`.

Then grab that superuser credentials you just created earlier, or the ones you got mailed (but any
user associated with a shop will do), and create a stock reading for the shop associated with the
user:

```bash
http POST -a <username>:<password> https://toogoodtogo-r3qg.onrender.com/api/stock-reading/ \
    gtin=1234567890123 \
    expiry=2023-03-01 \
    occurrence=2023-02-27T11:32:18Z
```

A bulk of stock readings (with conflicting *stock readings*, of course) can be created with the
following command:

```bash
http -a <username>:<password> POST https://toogoodtogo-r3qg.onrender.com/api/stock_reading/batch/ << EOF
[
  {
    "GTIN": "DANETTE VAN",
    "expiry": "2023-03-01",
    "occurrence": "2023-02-27T11:32:18Z"
  },
  {
    "GTIN": "DANETTE VAN",
    "expiry": "2023-03-04",
    "occurrence": "2023-02-28T11:32:18Z"
  },
  {
    "GTIN": "COCA COL",
    "expiry": "2023-03-01",
    "occurrence": "2023-02-27T11:32:18Z"
  }
]
EOF
```

Then take a break and contemple all the nice *stock readings* you have created. You have earned it.

```bash
http https://toogoodtogo-r3qg.onrender.com/api/stock_reading/
```

```json
[
  {
    "GTIN": "COCA COL",
    "expiry": "2023-03-01",
    "occurrence": "2023-02-27T11:32:18Z"
  },
  {
    "GTIN": "DANETTE VAN",
    "expiry": "2023-03-04",
    "occurrence": "2023-02-28T11:32:18Z"
  }
]
```

## But wait! GTIN are not actual GTIN!

Indeed. I started like this ~~because I did not think enough before starting~~ for the sake of
simplicity. Here the GTIN model is a 14-characters free-from text field. But using actual GTIN
would not change much the architecture/design of the application.

## How will it scale?

The front-end can scale horizontally infinitely. The only bottleneck will be the database. But those
are trivial create-read (not even full CRUD) operations with little to no relational work or
transactions. The cheapest managed Postgres will already be able to handle more than thousands of
requests per second.
Since there is little to no relational work nor transactions, we can even use a NoSQL database
like DynamoDB or MongoDB and scale at the database-level horizontally infinitely too.

## What to do next?

* Use actual GTIN instead of pseudo-GTIN, and use one of the many GTIN validator libraries available
  on pypi.
* Once we use proper GTIN, add a `Product` model, with a GTIN and a name. This would allow us to
  still have human-readable names for products and not have to remember the GTIN of each product.
* add a *date* filtering to the stock reading API, so we don't have to fetch all the stock readings
  when we sync, we can download only the ones that have been created since the last sync.
* Create a dedicated `Employee` model, with just an identifier and an access token. All employee do
  not need to be a full-fledged django user with nickname, first name, last name and email address.
  This would ease workload on the database and allow to handle even more load
* Home page of the project should not be a 404, but the API documentation (generated with
  OpenAPI/Swagger), or even the DRF playground to toy around with the API. But I don't know DRF
  enough to do that in time.
* Don't access environment variables ourselves in this hand-crafted way as done in the settings.
  Use a dedicated library like [django-environ](https://pypi.org/project/django-environ/) or
  [django-configurations](https://pypi.org/project/django-configurations/) or
  [python-dotenv](https://pypi.org/project/python-dotenv/)
  (but I was in a hurry)
  has kinda become the standard to load environment variables from a `.env` file.
* Enforce validation at the database level. Postgres has a module to enforce International Standard
  Numbers at the database level: the [ISN module](https://www.postgresql.org/docs/current/isn.html).
  I won't teach you that database-level validation is better than application-level validation.
* Buy me a beer, I spent more than 3 days on this (and I learnt django-rest-framework just for this
  project)(also I am now more of a DevOps guy and less of a developer and my django is rusty)(and
  my goldfish died and my dog ate my homework)

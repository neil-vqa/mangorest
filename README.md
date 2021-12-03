![mangorest-logo](mangorest-logo.png)

<p align="center"><em>Serve a RESTful API from any MongoDB database.</em></p>

<p align="center"><strong>WORK IN PROGRESS</strong></p>


## Overview

MangoREST aims to speed up serving RESTful APIs for CRUD apps utilizing MongoDB. It is built with Flask and pymongo, and is designed to simplify setting up the backend as much as possible but also giving room for extensibility.

Inspired by the giants [RESTHEART](https://restheart.org/) (written in Java), and [PostgREST](https://postgrest.org/en/v8.0/index.html) (written in Haskell).


## Table of Contents

You may also view the auto-generated TOC using the button located at the upper left corner of this readme.

- [Get Started](#get-started)
- [Configuration](#configuration)
    + [FLASK_ENV](#flask-env)
    + [FLASK_APP](#flask-app)
    + [JWT_SECRET_KEY](#jwt-secret-key)
    + [MONGODB_URI](#mongodb-uri)
    + [DATABASE](#database)
    + [COLLECTIONS](#collections)
    + [MANGO_USER_COLLECTION](#mango-user-collection)
  * [Example Config](#example-config)
- [Installation and Deployment](#installation-and-deployment)
  * [Deploy to Heroku with One-Click button](#deploy-to-heroku-with-one-click-button)
  * [Deploy to Render with One-Click button](#deploy-to-render-with-one-click-button)
  * [Install as a package + gunicorn](#install-as-a-package---gunicorn)
- [Authentication](#authentication)
  * [JWT Auth](#jwt-auth)
  * [Re: User registration](#re--user-registration)
  * [Endpoints](#endpoints)
- [API](#api)
  * [Querying Collections](#querying-collections)
  * [Getting a Document](#getting-a-document)
  * [Inserting and Updating](#inserting-and-updating)
  * [Deleting](#deleting)
- [Type Hints](#type-hints)
  * [For fields with NON-STRING values](#for-fields-with-non-string-values)
  * [When using comparison query operators](#when-using-comparison-query-operators)
  * [When using logical query operators](#when-using-logical-query-operators)
  * [Type Hinting notation](#type-hinting-notation)


## Get Started

There is no hard-ruled step-by-step guide on how to get MangoREST up and running since it actually depends on the deployment strategy. Read the [Installation and Deployment](#installation-and-deployment) section for some deployment options. Remember that MangoREST is just a Flask app.

There are specific things that must be done though to start using MangoREST. One, is to provide configuration (see [Configuration](#configuration) section for the config parameters). Also, the MangoREST *user collection* and at least one user must be created (see [Authentication](#authentication) section).


## Configuration

MangoREST configuration is set using environment variables to determine the database information and ways on how to serve REST client requests. Reading from a `.env` file is supported. Here is the complete list of configuration parameters:

#### FLASK_ENV

Optional. Sets the context to where Flask is running in. Setting to `development` will enable debug mode. Flask **default** setting is `production`.

Reference: https://flask.palletsprojects.com/en/2.0.x/config/#environment-and-debug-features

#### FLASK_APP

Required. Used to specify how to load the application. **Must** be set to `mangorest:app`. Please do change accordingly if customizing/extending MangoREST.

Reference: https://flask.palletsprojects.com/en/2.0.x/cli/

#### JWT_SECRET_KEY

Required. This will be used to sign JWT access tokens needed for MangoREST's default auth using JWT. Read the [Authentication](#authentication) section for the details. If summoning a terminal isn't your thing (woah), you may quickly generate a secret key using this web tool https://djecrety.ir/

#### MONGODB_URI

Required. For the database connection.

Reference(1): https://docs.mongodb.com/manual/reference/connection-string/

Reference(2): https://pymongo.readthedocs.io/en/stable/api/pymongo/mongo_client.html#pymongo.mongo_client.MongoClient

#### DATABASE

Required. Name of the database to be exposed to REST clients. MangoREST only allows a single database to be specified. This database should already exist. The name itself will not be exposed.

#### COLLECTIONS

Required. A sequence of `resource_name:collection_name` pairs separated by commas. To avoid exposing the database's collection names, the `resource_name`s will be used for the API endpoints. Map a `resource_name` to the name of the collection that will be exposed to REST clients. These collections should already exist even if they are still empty.

If you don't care exposing **ALL** collections and their collection names, you can use an asterisk wildcard `*`. The collection names themselves will be the `resource_name` to be used for the API endpoints.

#### MANGO_USER_COLLECTION

Optional. Name of the collection that will be used for storing data of MangoREST users created thru CLI. Default: `mangorest_users`. This does not need to exist beforehand. MangoREST will create the collection if not yet existing. Read the [Authentication](#authentication) section for more details.  

### Example Config

Here is an example config taken from the `.env.example` file in this repo:

```bash
FLASK_ENV=development
FLASK_APP=mangorest:app
JWT_SECRET_KEY=*1g$&3%an#x!+rogd@*iyhffs!a32575kd-)d*ajyr2s$kiuf!
MONGODB_URI=mongodb://userme:passme@0.0.0.0:27017/mangorest
DATABASE=mangorest
COLLECTIONS=rockets:rocket_engines,vehicles:launch_vehicles
MANGO_USER_COLLECTION=users
```


## Installation and Deployment

MangoREST is *just* a Flask app. Therefore, ways to deploy Flask also apply to deploying MangoREST. 

Reference: https://flask.palletsprojects.com/en/2.0.x/deploying/index.html

This section presents a few of the quick deployment options for MangoREST. 

### Deploy to Heroku with One-Click button

A quick and easy way to deploy and configure MangoREST as a [Heroku](https://www.heroku.com/) app.

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)

### Deploy to Render with One-Click button

A quick and easy way to deploy and configure MangoREST as a [Render](https://render.com/) app. Note that Render *asks* for Payment Information (if you haven't provided yet) when deploying thru One-Click button. But if deploying step-by-step thru the Render dashboard, *no* Payment Information will be asked.

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)

### Docker

WIP

### Install as a package + gunicorn

WIP


## Authentication

This section discusses the auth sytem that comes with installing MangoREST. You can absolutely ditch this and implement your own.

### JWT Auth

First, please don't forget to provide a JWT_SECRET_KEY for the application. By default, authentication is required to send POST, PATCH, and  DELETE to certain endpoints. The [Flask-JWT-Extended](https://flask-jwt-extended.readthedocs.io/en/stable/) extension is used to create and verify JWTs.

MangoREST provides a CLI that includes a command for creating users. Use `mangorest createuser [username]` command. This will prompt for a password and password confirmation. If it succeeds, the username and password can now be used to authenticate and access protected routes. Send a POST to `/login` endpoint to authenticate. This will respond with a JWT access token.

### Re: User registration

No REST API endpoint is available fo user registration. If needed though, this can be easily set up by using functions in the mangorest.auth module.

```python
from mangorest import auth, config, services

@app.post("/register")
def register_user():
    username = request.json.get("username", None)
    password = request.json.get("password", None)

    new_user_oid = auth.create_user(
        users_collection=db[config.MANGO_USER_COLLECTION],
        username=username, 
        password=password
    )

    parsed_oid = services.parse_object_id(new_user_id)

    return jsonify({"username": username, **parsed_oid}), 201
```

### Endpoints

As a summary for this section, here are the authentication-related endpoints:

| Endpoint | Description |
|----------|-------------|
| `POST /login` | Send username and password; returns JWT token |
| `GET /me` | Provide JWT token in Authorization header; returns the username of the authenticated user |
| `POST /register` | If set up like the above, send username and password; returns the username and oid of the newly created user |


## API

Routes provide GET, POST, PATCH, DELETE verbs. By default, only GET is available publicly, the rest require authentication. Read [Authentication](#authentication) section for authentication details. Please note that all enpoints are within `/api` which is automatically prepended by MangoREST. 

### Querying Collections

A collection can be queried using the resource name mapped to it. For example, getting all the documents of the collection named `rocket_engines` with a mapped resource name of `rockets`:

```
GET /api/rockets
```

Results can be filtered by appending query string parameters:

```
GET /api/rockets?country=USA&thrust_to_weight_ratio=gte[int].50
```

This translates to "get the rockets with country of USA and has thrust to weight ratio of greater than or equal to 50".

Let's examine the query string above: `country=USA&thrust_to_weight_ratio=gte[int].50`

The `country` param corresponds to the *country* field in the documents of *rocket_engines* collection. It has an equality condition of `USA`. We then have an ampersand `&` which is a way to logically conjoin multiple parameters. Now, the `thrust_to_weight_ratio` param has a value with a special syntax: `gte[int].50`.

**gte** corresponds to mongodb's $gte [comparison query operator](https://docs.mongodb.com/manual/reference/operator/query-comparison/). Then, **[int]** is a type hint which instructs MangoREST that the value is an integer. Finally, we have a dot "**.**" followed by the value **50**.

All of mongodb's comparison and logical query operators are supported. Just remove the `$` symbol when using them in the query string. But you may be asking more about the *type hint* thing. Pleae read the [Type Hints](#type-hints) section for the explanation.

The above query can also be done like this:

```
GET /api/rockets?and=(country.eq[str].USA,thrust_to_weight_ratio.gte[int].50)
```

This query string syntax instructs MangoREST to get the results by using mongodb's $and [logical query operator](https://docs.mongodb.com/manual/reference/operator/query-logical/). The expressions are separated by commas, and each expression is in the form of `field_name.operator[type-hint].value`.

**PROJECTION.** To specify only a subset of fields of the documents to be returned, use the `_projection` param.

```
GET /api/rockets?country=USA&_projection=name,cycle,burn_time,propellant
```

**SORT.** To sort the query results, use the `_sort` param. The query below sorts by 2 fields.

```
GET /api/rockets?country=USA&_sort=(name:ascending),(burn_time:ascending)
```

**LIMIT.** To limit the number of results, use the `_limit` param.

```
GET /api/rockets?country=USA&_sort=(name:ascending)&_limit=10
```

**SKIP.** To skip some documents (usually for pagination), use the `_skip` param.

```
GET /api/rockets?country=USA&_skip=10
```

### Getting a Document

MangoREST currently only supports getting a single document thru its [ObjectId](https://docs.mongodb.com/manual/reference/bson-types/#std-label-objectid).

```
GET /api/rockets/6195b0eb829a2784b4459a7f
```

### Inserting and Updating

Create and Update operations can only be done by authenticated users.

**SINGLE INSERT.** Using the *rocket_engine* collection above, create a new document by:

```
POST /api/rockets

{"name":"RD-180", "country":"Russia", "thrust_to_weight_ratio": 78, "manufacturer": "NPO Energomash"}
```

This responds with `201 CREATED` with the newly created document's `_id` if succcessful.

**MULTIPLE INSERTS.** To insert multiple documents into a collection, pass an array of objects.

```
POST /api/rockets

[
    {
        "name": "RD-360",
        "country": "North Pole",
        "thrust_to_weight_ratio": 150,
        "manufacturer": "Energomasher",
    },
    {
        "name": "RD-270",
        "country": "Antarctica",
        "thrust_to_weight_ratio": 110,
        "manufacturer": "Energomasher",
    },
]
```

This responds with `201 CREATED` with an array of the newly created documents' `_id`s if succcessful.

**SINGLE UPDATE.** To update a document, specify the fields to be updated:

```
PATCH /api/rockets/61a30c07032f56ecef3c845e

{
    "manufacturer": "Energomasher Luna"
    "thrust_to_weight_ratio": 150
}
```

This responds with `204 NO CONTENT` if succcessful.

### Deleting

**SINGLE DELETE.** To delete a single document, do the following:

```
DELETE /api/rockets/61a30c07032f56ecef3c845e
```

This responds with `204 NO CONTENT` if succcessful.


## Type Hints

Type hints must be used in query strings to correctly filter the data to be returned. This is necessary since MangoREST currently does not generate or maintain a schema of the collection as a reference for the types. This section presents the ways type hints are used.

### For fields with NON-STRING values

Queries where the field type is expected to be a *string* such as `GET /api/rockets?country=Antarctica` does not need any type hinting. On the other hand, type hints are needed if a field type is expected to be other than a string. Such examples are:

```
GET /api/rockets?is_active=[bool].true

GET /api/rockets?thrust_to_weight_ratio=[int].70
```

### When using comparison query operators

Comparison query operators such as `eq`, `gt`, `lte` can be used in the query string. However, type hint must be provided to correctly filter the data.

```
GET /api/rockets?thrust_to_weight_ratio=lt[int].70

GET /api/rockets?company=eq[str].Rocket+Lab&thrust_to_weight_ratio=gte[int].50
```

Some operators expect an array as the value such as `in` and `nin`. Array elements can be type hinted by:

```
GET /api/rockets?country=in[list-str].[North+Pole,Moon,Antarctica]
```

### When using logical query operators

Logical query operators such as `and`, `or` can be used in the query string. Type hints must be provided.

```
GET /api/rockets?and=(thrust_to_weight_ratio.gt[int].70,country.eq[str].North+Pole,is_active.eq[bool].true)
```

### Type Hinting notation

To conclude this section, here are the type hints you can use in query strings.

| Hint | Description/Python Type |
|------|------|
| `int` | integer |
| `float` | float |
| `bool` | boolean |
| `str` | string |
| `date` | datetime.date |
| `time` |  datetime.time |
| `datetime` | datetime.datetime |
| `timedelta` | datetime.timedelta |
| `list-int` | Array with integer elements |
| `list-float` | Array with float elements |
| `list-str` | Array with string elements |
| `list-date` | Array with datetime.date elements |
| `list-time` | Array with datetime.time elements |
| `list-datetime` | Array with datetime.datetime elements |
| `list-timedelta` | Array with datetime.timedelta elements |


## Development

The project uses [poetry](https://python-poetry.org/) to package and manage dependencies. After activating a virtual environment, run:

```bash
(.venv)$ poetry install
```

A *compose-devdb.yml* is provided for developing and testing. It is recommended to use the param values in the *.env.example* file when developing and testing.

Start containers:

```bash
(.venv)$ docker-compose -f compose-devdb.yml up -d --build
```

Then, run tests:

```bash
(.venv)$ pytest
```

Please do linting:

```bash
bash scripts/lint-check.sh
```

And fix formatting:

```bash
bash scripts/format.sh
```


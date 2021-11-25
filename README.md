![mangorest-logo](mangorest-logo.png)

<p align="center"><em>Serve a RESTful API from any MongoDB database.</em></p>

<p align="center"><strong>WORK IN PROGRESS</strong></p>


## Overview

MangoREST aims to speed up serving RESTful APIs for CRUD apps utilizing MongoDB. It is built with Flask and pymongo, and is designed to simplify setting up the backend as much as possible but also giving room for extensibility.

Inspired by the giants [RESTHEART](https://restheart.org/) (written in Java), and [PostgREST](https://postgrest.org/en/v8.0/index.html) (written in Haskell).

## Get Started

There is no hard-ruled step-by-step guide on how to get MangoREST up and running since it actually depends on the deployment strategy. Read the [Installation and Deployment](#installation-and-deployment) section for some deployment options. Remember that MangoREST is just a Flask app.

There are specific things that must be done though to start using MangoREST. One, is to provide configuration (see [Configuration](#configuration) section for the config parameters). Also, the MangoREST *user collection* and at least one superuser must be created (see [Authentication](#authentication) section).

## Configuration

MangoREST configuration is set using environment variables to determine the database information and ways on how to serve REST client requests. Reading from a `.env` file is supported. Here is the complete list of configuration parameters:

#### FLASK_ENV

Optional. Sets the context to where Flask is running in. Setting to `development` will enable debug mode. Flask **default** setting is `production`.

Reference: https://flask.palletsprojects.com/en/2.0.x/config/#environment-and-debug-features

#### FLASK_APP

Required. Used to specify how to load the application. **Must** be set to `mangorest:app`. Please do change accordingly if customizing/extending MangoREST.

Reference: https://flask.palletsprojects.com/en/2.0.x/cli/

#### MONGODB_URI

Required. For the database connection.

Reference(1): https://docs.mongodb.com/manual/reference/connection-string/

Reference(2): https://pymongo.readthedocs.io/en/stable/api/pymongo/mongo_client.html#pymongo.mongo_client.MongoClient

#### DATABASE

Required. Name of the database to be exposed to REST clients. MangoREST only allows a single database to be specified. The name itself will not be exposed.

#### COLLECTIONS

Required. A sequence of `resource_name:collection_name` pairs separated by commas. To avoid exposing the database's collection names, the `resource_name`s will be used for the API endpoints. Map a `resource_name` to the name of the collection that will be exposed to REST clients.

If you don't care exposing **ALL** collections and their collection names, you can use an asterisk wildcard `*`. The collection names themselves will be the `resource_name` to be used for the API endpoints.

Here is an example config taken from the `.env.example` file in this repo:

```bash
FLASK_ENV=production
FLASK_APP=mangorest:app
MONGODB_URI=mongodb://localhost:27017/
DATABASE=therocketcorpdb
COLLECTIONS=rockets:rocket_engines,vehicles:launch_vehicles
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

### Install as a package + gunicorn

## Authentication

WIP

## API

Routes provide GET, POST, PUT, DELETE verbs. By default, only GET is available publicly, the rest require authentication. Read [Authentication](#authentication) section for customizing this behavior. Please note that all enpoints are within `/api` which is automatically prepended by MangoREST. 

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

### Inserting or Updating

WIP

### Deleting

WIP

## Type Hints

WIP
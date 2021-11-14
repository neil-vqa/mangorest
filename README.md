![mangorest-logo](mangorest-logo.png)

<p align="center"><em>Serve a RESTful API from any MongoDB database.</em></p>

<p align="center"><strong>WORK IN PROGRESS</strong></p>

## Motivation

MangoREST aims to speed up developing RESTful APIs for simple CRUD apps utilizing MongoDB. There are far superior projects such as [RESTHEART](https://restheart.org/) (written in Java), but I would like to build with python. Inspiration came from the [PostgREST](https://postgrest.org/en/v8.0/index.html) project.

I am building this motivated by the needs of my clients whose projects usually involve simple product and order management that complements their e-commerce websites. Having MangoREST will be a great help in saving time compared to building the same order system with Django REST + Postgresql over and over again.

## Overview

MangoREST is built with Flask and pymongo. It is designed to simplify setting up the API as much as possible but also giving room for extensibility. 
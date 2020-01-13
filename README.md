# Data Scientist Case Study

Welcome to the BlockFi Data Science Case Study. In this exercise you will
demonstrate your ability to analyze data and generate reports of your findings.
This exercise is designed to reflect what day to day analytics at BlockFi may
look like.

This repository contains a database with some sample data for you to use. This
data includes historical prices for Bitcoin (BTC), Ethereum (ETH), and Litecoin 
(LTC) as well as some mock customer data. Instructions on how to setup your
environment and get to work are listed below.

If you have any questions or encounter any issues during this exercise please 
open an issue on this repo describing the problem in as much detail as possible.
Assign the issue to `@tsantero` and he will respond as soon as possible to help
resolve any issues.

## Case Study Questions

Build your local database and inspect the schema. You will find a `crypto` table
has been created during installation.

Your excercise is to:

1. Given that you can only hold one type of crypto at any time,
and assuming you start with $1,000 USD, analyze the historical price data provided
for BTC, ETH, and LTC: on which days would you trade from one currency to
another in order to maximize returns? Assume your trades are filled at the average
daily price for each coin on the days you trade. What is your trade history and ending
account balance between Jan 01, 2018 and Sept 01, 2019?

2. As above, except on days when it's disadvantage to hold any cyrpto, you have
the ability to trade into a stablecoin, such as GUSD, which is designed to track
the value of a US Dollar.

3. Same as 2, except now assume you must hold whichever currency you purchase for
three days before you are able to sell.

When possible, please generate both csv files as well as graphs (of your choosing)
to display the results of your analysis.

When you are satisfied with your solutions open a Pull Request to complete this
exercise.

Good luck, and have fun!

## Dev Environment

### Prerequisites

In order to set up your local dev environment you must have the following
dependencies installed on your machine.

* make
* docker

Docker must be running in order to proceed.

### The Makefile

If you run `make` at the toplevel of this repo you should see the following prompt:

```
$ make
You can run the following commands

build                Creates a PostgreSQL docker image
console              Opens a psql console
delete               Deletes the PostgreSQL docker container, image, and data volume
help                 Display help prompt
start                Starts the PostgreSQL docker container
stop                 Stops the PostgreSQL docker container
```

Those are the Makefile targets provided to help make setting up your environment
as seamless as possible.

### Installation

By running `make build` you will generate a docker image containing PostgreSQL 10
in an alpine linux based host OS. When you start this container for the first time,
using `make start`, the following things will happen:

1. A directory called `postgres_data_blockfi` will be created at the top-level
of this directory. This directory will serve to hold the volume data for your
container instance.
2. PostgreSQL will then be started
3. A `datascience` USER ROLE will be created
4. The database schema will be created
5. Sample data will be inserted into the database.


To check that the container is started and running you can run the following
command:

```
$ docker ps
CONTAINER ID        IMAGE               COMMAND                  CREATED                  STATUS                  PORTS                    NAMES
b1d252d1d25c        crypto-db           "docker-entrypoint.s…"   Less than a second ago   Up Less than a second   0.0.0.0:5432->5432/tcp   crypto-db
```

You can then run `make console` to launch a `psql` shell to write interactive
queries. 

Alternatively, you may prefer to connect to to the database from the
applications or scripts you write to complete this exercise. In which case
you may use the following credentials:

| CREDENTIAL | VALUE |
| ---------- | ----- |
| username   | datascience |
| password   | data |
| hostname   | 0.0.0.0 |
| port       | 5432 |
| database   | blockfi |

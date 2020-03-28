# Crypto Trading Case Study

![Screen Shot 2020-03-28 at 5.28.54 PM](/Users/matsteelelap/Desktop/ProjectFolder/blockFi_case/dashboard_image.png)

### guiding question: 

#### *HOW COULD CAINS BE IMPROVED BY THE ABILITY TO TRADE INTO A US PEGGED STABLE COIN?*

To answer this question, I built a naive model that learns based on only historical trading data for Bitcoin (BTC), Ethereum (ETH), and Litecoin (LTC). The goal of the model was to MAXIMIZE RETURNS of an investment STARTING WITH 1000, and it assumed no friction (trade cost is 0). 

The model would be built with three variations: 

1) assume YOU CAN ONLY TRADE IN CRYPTO, but hold the same position without shifting balances. The initial holdings reflect the best predicted share of crypto based on historical growth averages up until Jan 1st. 

2) assume YOU CAN ONLY TRADE IN CRYPTO, but shift balances based on which crypto was expected to perform best under the expected market conditions. 

3) allow the model to TRADE INTO A STABLE COIN, thus shifting out of the crypto market when it appeared to be down, and then strategically shifting into crypto with high up potential when the crypto market appeared to be shifting upwards. 

The period of interest was between January 1st 2018 and September 2019. The data available crossed multiple periods ensuring the model could adapt in the presence of new information.  

![Screen Shot 2020-03-28 at 4.39.45 PM](/Users/matsteelelap/Desktop/ProjectFolder/blockFi_case/crypto_data_overview.png)



A different distinct model was built for each period based on available data up until that point. As such, the model for first period, starting the first of January, was trained on all previous trading history for ethereum and bitcoin prior. A new instance of the model was created for each period thereafter and included an additional set of data from the previous period. Thus the final trading suggestions was the output of over a hundred instances of distinct models. The feature data was a rolling average aggregation of data from previous periods. The label data was the current period. The training period and the number of periods to aggregate over were hyperperamters that the user can shift in the final dashboard.  

![Screen Shot 2020-03-28 at 5.26.11 PM](/Users/matsteelelap/Desktop/ProjectFolder/blockFi_case/model_structure.png)

The model used classification models for multilayered predictions. 

![Screen Shot 2020-03-28 at 4.59.40 PM](/Users/matsteelelap/Desktop/ProjectFolder/blockFi_case/decision_framework.png)

The R2 and soft outputs (probabilities) of these models were used to designate how much of the investment pool to shift. The stronger the predictions the more of the funds were designated accordingly. 

![Screen Shot 2020-03-28 at 5.23.54 PM](/Users/matsteelelap/Desktop/ProjectFolder/blockFi_case/balance_comparison.png)



# Deploying

The project is packaged in a docker container with a postgresql data volume hosting the outputted predictions for the models built under various assumptions. 

![Screen Shot 2020-03-28 at 5.43.52 PM](/Users/matsteelelap/Desktop/ProjectFolder/blockFi_case/architecture.png)

To deploy :

In order to set up your local dev environment you must have the following

dependencies installed on your machine.

\* make

\* docker

Docker must be running in order to proceed.

First you will need to build the initial image

```bash
make build
```

Then you will need to create the container (set to port 5432). Make sure your postgresql port 5432 on your computer is not otherwise being used. 

```bash
make create
```

To check that the container is started and running you can run the following

command:

```bash
docker ps
CONTAINER ID        IMAGE               COMMAND                  CREATED                  STATUS                  PORTS                    NAMES

b1d252d1d25c        crypto-db           "docker-entrypoint.s…"   Less than a second ago   Up Less than a second   0.0.0.0:5432->5432/tcp   crypto-db
```

This will start the container automatically. If you need to stop the container you should run:

```bash
make stop
```

Then to reset you will need to start the container up again using the following command:

```bash
make start
```

To load your dashboard you will need to enter the python virtual environment and install dependencies and run the main.py script.

```bash
cd server
source venv/bin/activate
python main.py
```

If you would like to remove the container and associated image and rebuild, use the following:

```bash
make delete
```

If you would like to rebuild the model from scratch you will need to first remove the docker volume and folder using the following command

```bash
docker volume rm postgres_data_blockfi
rm -rf postgres_data_blockfi
```

You'll then have to make a new volume folder, and initialize the python model building script. 

```
mkdir -p postgres_data_blockfi
cd server
source venv/bin/activate
python initialize.py
```

\1. A directory called `postgres_data_blockfi` will be created at the top-level

of this directory. This directory will serve to hold the volume data for your

container instance.

\2. PostgreSQL will then be started

\3. A `datascience` USER ROLE will be created

\4. The database schema will be created

\5. Sample data will be inserted into the database.

You can then run `make console` to launch a `psql` shell to write interactive

queries. 

the following credentials can be used for accessing the database:

| CREDENTIAL | VALUE |

| ---------- | ----- |

| username   | datascience |

| password   | data |

| hostname   | 0.0.0.0 |

| port       | 5431 |

| database   | blockfi |








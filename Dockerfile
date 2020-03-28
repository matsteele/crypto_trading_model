FROM postgres:10-alpine

ADD sql/init.sql /docker-entrypoint-initdb.d/
COPY sql/btcusd.csv /
COPY sql/ethusd.csv /
COPY sql/ltcusd.csv /

ENV POSTGRES_DB blockfi

EXPOSE 5432
CMD ["postgres"]



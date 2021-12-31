# 
# Bases de Dados 2020/2021
# Trabalho Prático
#
# Authors: 
#   Nuno Antunes <nmsa@dei.uc.pt>
#   BD 2021 Team - https://dei.uc.pt/lei/
#   University of Coimbra

FROM library/postgres


ENV POSTGRES_USER project
ENV POSTGRES_PASSWORD project
ENV POSTGRES_DB project_bd


#BASE INPUT
COPY 1-proj_table.sql /docker-entrypoint-initdb.d/
COPY somedata.sql /docker-entrypoint-initdb.d/


# FUNCTIONS
COPY search_auctions.sql /docker-entrypoint-initdb.d/
COPY onAuctUpdate.sql /docker-entrypoint-initdb.d/
COPY onBidding.sql /docker-entrypoint-initdb.d/
COPY isFinished.sql /docker-entrypoint-initdb.d/
COPY isCanceled.sql /docker-entrypoint-initdb.d/
COPY invalid_bid.sql /docker-entrypoint-initdb.d/

EXPOSE 5432

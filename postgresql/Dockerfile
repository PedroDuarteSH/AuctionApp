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

COPY proj_tables.sql /docker-entrypoint-initdb.d/

EXPOSE 5432

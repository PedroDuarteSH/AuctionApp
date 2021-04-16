##
## =============================================
## ============== Bases de Dados ===============
## ============== LEI  2020/2021 ===============
## =============================================

## =============================================
## === Department of Informatics Engineering ===
## =========== University of Coimbra ===========
## =============================================


 
from flask import Flask, jsonify, request
import logging, psycopg2, time

app = Flask(__name__) 


@app.route('/') 
def hello(): 
    return





##      Demo GET
##
## Obtain all users, in JSON format
##
## To use it, access: 
## 
##   http://localhost:8080/users/
##

@app.route("/users/", methods=['GET'], strict_slashes=True)
def get_all_users():
    logger.info("###              DEMO: GET /users              ###");   

    conn = db_connection()
    cur = conn.cursor()

    cur.execute("SELECT username, email, password FROM users")
    rows = cur.fetchall()

    payload = []
    logger.debug("---- users  ----")
    for row in rows:
        logger.debug(row)
        content = {'username': row[0], 'email': row[1], 'password': row[2]}
        payload.append(content) # appending to the payload to be returned

    conn.close()
    return jsonify(payload)



##########################################################
## DATABASE ACCESS
##########################################################

def db_connection():
    db = psycopg2.connect(user = "project",
                            password = "project",
                            host = "db",
                            port = "5432",
                            database = "project_bd")
    return db


##########################################################
## MAIN
##########################################################
if __name__ == "__main__":

    # Set up the logging
    logging.basicConfig(filename="logs/log_file.log")
    logger = logging.getLogger('logger')
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    # create formatter
    formatter = logging.Formatter('%(asctime)s [%(levelname)s]:  %(message)s',
                              '%H:%M:%S')
                              # "%Y-%m-%d %H:%M:%S") # not using DATE to simplify
    ch.setFormatter(formatter)
    logger.addHandler(ch)


    time.sleep(1) # just to let the DB start before this print :-)


    logger.info("\n---------------------------------------------------------------\n" + 
                  "API v1.0 online: http://localhost:8080/departments/\n\n")
    

    app.run(host="0.0.0.0", debug=True, threaded=True)




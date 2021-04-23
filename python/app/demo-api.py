##
## =============================================
## ============== Bases de Dados ===============
## ============== LEI  2020/2021 ===============
## =============================================

## =============================================
## === Department of Informatics Engineering ===
## =========== University of Coimbra ===========
## =============================================

## TODO 
## add_a_user -> FALTA SEGURANÇA DA PASSWORD 

 
from flask import Flask, jsonify, request
import logging, psycopg2, time

app = Flask(__name__) 


@app.route('/') 
def hello(): 
    return





## Demo GET
##
## Obtain all users, in JSON format
##
## To use it, access: 
## 
##   http://localhost:8080/users/
##

@app.route("/user/", methods=['GET'], strict_slashes=True)
def get_all_users():
    logger.info("###              DEMO: GET /user              ###");   

    conn = db_connection()
    cur = conn.cursor()

    cur.execute("SELECT username, email, password FROM users")
    rows = cur.fetchall()

    payload = []
    logger.debug("---- user  ----")
    for row in rows:
        logger.debug(row)
        content = {'username': row[0], 'email': row[1], 'password': row[2]}
        payload.append(content) # appending to the payload to be returned

    conn.close()
    return jsonify(payload)



## Add a new department in a JSON payload
##
## To use it, you need to use postman or curl: 
##
##   curl -X POST http://localhost:8080/user/ -H "Content-Type: application/json" -d '{"username": "Adriana1234", "email": Adriana1234@gmail.com, "password": "Adriana1234"}'

@app.route("/users/", methods=['POST'], strict_slashes=True)
def add_a_user():
    logger.info("###              DEMO: POST /users              ###")

    user_add = request.get_json()
    
    conn = db_connection()
    cur = conn.cursor()
    
    logger.info("---- new user  ----")
    logger.debug(f'payload: {user_add}')
    
    statement = """INSERT INTO users (username, email, password)
                VALUES ( %s,   %s ,   %s )"""

    values = (payload["username"], payload["email"], payload["password"])


    try:
        cur.execute(statement, values)
        cur.execute("commit")
        get_user = """Select id from users where username = """ + payload["username"]
        cur.execute(get_user)
        rows = cur.fetchrow()
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        result = 'Failed!'
    finally:
        if conn is not None:
            conn.close()

    return jsonify(result)

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
                  "API v1.0 online: http://localhost:8080/user/\n\n")
    

    app.run(host="0.0.0.0", debug=True, threaded=True)




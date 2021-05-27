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
## login -> FALTA SEGURANÇA DA PASSWORD  -- DONE??
## Adicionar Id de artigo no ER 
 
from flask import Flask, jsonify, request
import logging, psycopg2, time, jwt
import datetime, time


SECRET_KEY = "hkBxrbZ9Td4QEwgRewV6gZSVH4q78vBia4GBYuqd09SsiMsIjH"


app = Flask(__name__) 

@app.route('/dbproj/') 
def hello(): 
    return ("<h1> Projeto de gestão de Leilões </h1>")






############################################### USERS ##########################################

#Get users List
##TEMPORARY
@app.route("/dbproj/user/", methods=['GET'], strict_slashes=True)
def get_all_users():
    logger.info("###              DEMO: GET /user              ###");   

    conn = db_connection()
    cur = conn.cursor()

    cur.execute("SELECT username, email, password FROM users")
    rows = cur.fetchall()

    payload = []
    logger.debug("---- List all users  ----")
    for row in rows:
        logger.debug(row)
        content = {'username': row[0], 'email': row[1], 'password': row[2]}
        payload.append(content) # appending to the payload to be returned

    conn.close()
    return jsonify(payload)
##TEMPORARY





##################################################################
#                                                                #
# Add a new user account                                         #
# Should input {"username":username, "password":password,        #
#      "email": email}                                           #
# Returns {"authToken”:authToken}} in success                    #
# Returns {"erro":AuthError} in success                          #
#                                                                #
##################################################################
@app.route("/dbproj/user/", methods=['POST'], strict_slashes=True)
def add_user():
    logger.info("\n###              POST /user -> Add a new user              ###")

    to_add = request.get_json()
    conn = db_connection()
    cur = conn.cursor()
    cur.execute("Begin")
    logger.debug(f'payload: {to_add}')
    
    statement = """INSERT INTO users (username, email, password)
                VALUES ( %s,   %s ,   %s ) RETURNING id"""

    values = (to_add["username"], to_add["email"], to_add["password"])
    
    try:
        cur.execute(statement, values)
        ## Verify statement and get added username
        
        user_id = cur.fetchone()[0]
        logger.debug(user_id)

        ## Return new username ID 
        result = {'userId': user_id}
        

    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        result = {'erro:': str(error)}
    finally:
        if conn is not None:
            cur.execute("COMMIT")
            conn.close()

    return jsonify(result)



##################################################################
#                                                                #
# Login into a user account                                      #
# Should input {"username":username, "password":password}        #
# Returns {"authToken”:authToken}} in success                    #
# Returns {"erro":AuthError} in success                          #
#                                                                #
##################################################################
@app.route("/dbproj/user/", methods=['PUT'], strict_slashes=True)
def user_login():
    logger.info("###              PUT /user -> User Trying to Login             ###")

    login_user = request.get_json()
    conn = db_connection()
    cur = conn.cursor()
    
    logger.debug(f'Login information: {login_user}')
    
    
    try:
        statement =  """Select id from users where username = %s and password = %s"""
        values = (login_user["username"], login_user["password"])
        cur.execute(statement, values)
        id = cur.fetchone()[0]
        if(id is not None):
            logger.debug(id)
            id = {'user_id': id}
            is_banned = verify_ban(id)
            if(is_banned[0] == False):
                result = {'erro:':is_banned[1]}
            else:
                result = jwt.encode(({'user_id': id}),SECRET_KEY, algorithm="HS256")
                result = {'authToken': result}
        else:
            result = {'erro:':"User was not found, invalid username or password"}

    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        result = {'erro:': str(error)}
    finally:
        if conn is not None:
            conn.close()

    return jsonify(result)


######################################################## END OF USER ###########################################################




######################################################## AUCTION ###############################################################

################################################################################
#                                                                              #
# Add a new auction to the system                                              #
# Should input                                                                 #
# {"token":AuthToken, "title": Titulo do Novo Leilão,                          #
# "min_price" : "Preço minimo", "Description": “Descrição do Novo Leilão”      #
#       "end_time": "tempo do fim do leilão YYYY-MM-DD HH:MM:SS",              #
#       "item_name": "Nome do item a vender",                                  #
#       "item_description" : "Descrição do item a vender" }                    #
# Returns {"leilaoId":id}} in success                                  #
# Returns {"erro":AuthError} in success                                        #
#                                                                              #
################################################################################
@app.route("/dbproj/leilao/", methods=['POST'], strict_slashes=True)
def add_auction():
    logger.info("###      POST /leilao ->  Trying to add an auction          ###")
    to_add = request.get_json()
    
    ##Login to user
    login = authenticate(to_add["token"])
    logger.info(to_add["token"])
    if(login[0] == False):
        return jsonify({'erro:': login[1]})

    id = login[1]['user_id']
    
    conn = db_connection()
    cur = conn.cursor()
    cur.execute("Begin")

    logger.debug(f'Auction to add: {to_add}')
    
    try:
        end_date = datetime.datetime.fromisoformat(to_add["end_time"])

        statement =  """Insert into auction (seller_id, item_id, title, description, end_time,  min_price, item_name)
                    values(%s, %s, %s, %s, %s, %s, %s) RETURNING ID""" # TODO -> FALTA START TIME
        values = (id, to_add["item_id"],  to_add["title"], to_add["Description"], end_date, 
                    to_add["min_price"], to_add["item_name"]) # TODO -> FALTA START TIME
        
        cur.execute(statement, values)
        auction_id = cur.fetchone()[0]
        if(auction_id is not None):
            logger.debug(auction_id)
            result = {'leilaoId': auction_id}
        else:
            result = {'erro:':"User was not found, invalid username or password"}

    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        result = {'erro:': str(error)}
    finally:
        if conn is not None:
            cur.execute("ROLLBACK")
            conn.close()

    return jsonify(result)


################################################################################
#                                                                              #
# Add a new auction to the system                                              #
# Should input                                                                 #
# {"token":AuthToken, "title": Titulo do Novo Leilão,                          #
# "min_price" : "Preço minimo", "Description": “Descrição do Novo Leilão”      #
#       "end_time": "tempo do fim do leilão YYYY-MM-DD HH:MM:SS",              #
#       "item_name": "Nome do item a vender",                                  #
#       "item_description" : "Descrição do item a vender" }                    #
# Returns {"leilaoId":id}} in success                                  #
# Returns {"erro":AuthError} in success                                        #
#                                                                              #
################################################################################
@app.route("/dbproj/leiloes/", methods=['GET'], strict_slashes=True)
def get_auctions():
    logger.info("###      GET /leiloes ->  Get all auctions         ###")
    to_add = request.get_json()
    
    ##Login to user
    login = authenticate(to_add["token"])
    logger.info(to_add["token"])
    if(login[0] == False):
        return jsonify({'erro:': login[1]})
    id = login[1]['user_id']
    
    conn = db_connection()
    cur = conn.cursor()
    
    cur.execute("""SELECT username, title, item_id, item_name, description, end_time, start_time, 
                current_price, min_price FROM users, auction 
                where auction.seller_id = users.id and end_time > current_timestamp""")
    rows = cur.fetchall()

    payload = []
    for row in rows:
        logger.debug(row)
        if(row[7] == None):
            row[7] = "Doensn't has a price yet"
        content = {'Seller Username': row[0], 'Auction Title': row[1], 'Item ID': row[2],
                    'Item Name': row[3], 'Description': row[4], 'End Time': row[5],
                    'Start_time': row[6], 'Current Price': row[7], 'Min Price': row[8]}
        payload.append(content) # appending to the payload to be returned
    
    logger.debug(f'Auction to add: {to_add}')
    
    try:
        end_date = datetime.datetime.fromisoformat(to_add["end_time"])

        statement =  """Insert into auction (seller_id, item_id, title, description, end_time,  min_price, item_name)
                    values(%s, %s, %s, %s, %s, %s, %s) RETURNING ID""" # TODO -> FALTA START TIME
        values = (id, to_add["item_id"],  to_add["title"], to_add["Description"], end_date, 
                    to_add["min_price"], to_add["item_name"]) # TODO -> FALTA START TIME
        
        cur.execute(statement, values)
        auction_id = cur.fetchone()[0]
        if(auction_id is not None):
            logger.debug(auction_id)
            result = {'leilaoId': auction_id}
        else:
            result = {'erro:':"User was not found, invalid username or password"}

    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        result = {'erro:': str(error)}
    finally:
        if conn is not None:
            cur.execute("COMMIT")
            conn.close()

    return jsonify(result)

##########################################################
##                  User Authentication                 ##
##########################################################
def authenticate(token):
    try:
        id = jwt.decode(token,SECRET_KEY, algorithms=["HS256"])
        return verify_ban(id)
    except jwt.ExpiredSignatureError:
        msg = 'Signature has expired.'
        return False, msg
    except jwt.DecodeError:
        msg = 'Invalid Login Token Signature'
        return False,  msg
    except jwt.InvalidTokenError:
        msg = 'Invalid token.'
        return False,  msg



##########################################################
##                Verify if user is banned              ##
##########################################################
def verify_ban(id):
    conn = db_connection()
    cur = conn.cursor()
    statement =  """Select username, is_banned from users where id = %s"""
    try:
        cur.execute(statement, str(id['user_id']))
        is_banned = cur.fetchone()
        logger.info(is_banned[1])
        if(is_banned[1] == True):
            return False, ("User "+ str(is_banned[0]) + " is banned")
        return True, id
    except (Exception, psycopg2.DatabaseError) as error:
        return False,  str(error)
    finally:
        if(conn is not None):
            conn.close()
    



##########################################################
##                  DATABASE ACCESS                     ##
##########################################################
def db_connection():
    db = psycopg2.connect(user = "project",
                            password = "project",
                            host = "db",
                            port = "5432",
                            database = "project_bd")
    return db


##########################################################
##                           MAIN                       ##
##########################################################
if __name__ == "__main__":
    # Set up the logging
    logging.basicConfig(filename="logs/log_file.log")
    logger = logging.getLogger('logger')
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    
    # create Formatter

    formatter = logging.Formatter('%(asctime)s [%(levelname)s]:  %(message)s',
                              '%H:%M:%S')
                              # "%Y-%m-%d %H:%M:%S") # not using DATE to simplify
    ch.setFormatter(formatter)
    logger.addHandler(ch)


    time.sleep(1) # just to let the DB start before this print :-)


    logger.info("\n---------------------------------------------------------------\n" + 
                  "API online: http://localhost:8080/projdb/user/\n\n")
    

    app.run(host="0.0.0.0", debug=True, threaded=True)
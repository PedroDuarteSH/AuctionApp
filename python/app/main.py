##
## =============================================
## ============== Bases de Dados ===============
## ============== LEI  2020/2021 ===============
## =============================================
## =============================================
## =============================================
## === Department of Informatics Engineering ===
## =========== University of Coimbra ===========
## =============================================


from flask import Flask, jsonify, request
import logging, psycopg2, time, jwt
import datetime


SECRET_KEY = "hkBxrbZ9Td4QEwgRewV6gZSVH4q78vBia4GBYuqd09SsiMsIjH"


app = Flask(__name__) 

@app.route('/dbproj/') 
def hello(): 
    return ("""<h1>MY BID</h1><h2>Projeto de gestão de Leilões </h2><ul>
<li><b>Criar um novo leilão</b> - <a href="url">http://localhost:8080/dbproj/leilao/</a>, no método POST</li><br>
<li><b>Listar todos os leilões existentes</b> - <a href="url">http://localhost:8080/dbproj/leiloes/</a>, no método GET.</li><br>
<li><b>Pesquisar leilões existentes</b> - <a href="url">http://localhost:8080/dbproj/leiloes/<keyword></a>, no método GET.</li><br>
<li><b>Consultar os detalhes de um leilão</b> - <a href="url">http://localhost:8080/dbproj/leilao/<id leilão></a>, no método GET.</li><br>
<li><b>Listar todos os leilões em que o utilizador tenha atividade</b> - <a href="url">http://localhost:8080/dbproj/meusLeiloes/</a>, no método GET.</li><br>
<li><b>Efetuar uma licitação num leilão</b> - <a href="url">http://localhost:8080/dbproj/licitar/<id leilão>/<licitação></a>, no método GET.</li><br>
<li><b>Editar as propriedades de um leilão</b> - <a href="url">http://localhost:8080/dbproj/leilao/<id leilão></a>, no método PUT.</li><br>
<li><b>Escrever mensagens no mural de um leilão</b> - <a href="url">http://localhost:8080/dbproj/leilao/<id leilão>/message</a>, no método POST.</li><br>
<li><b>Consultar mensagens do mural e notificações</b> - <a href="url">http://localhost:8080/dbproj/notifications</a>, no método GET.</li><br></ul>
""")


############################################### USERS ##########################################

##################################################################
#                                                                #
# Add a new user account                                         #
# Should input {"username": username, "password": password,      #
#      "email": email}                                           #
# Returns {"user_id": new user id} in success                    #
# Returns {"erro": Errorcode} in error                           #
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
                VALUES (%s, %s, %s) RETURNING id"""

    values = (to_add["username"], to_add["email"], to_add["password"])
    
    try:
        cur.execute(statement, values)

        ##Verify statement and get added username
        user_id = cur.fetchone()[0]
        logger.debug(user_id)

        ##Return new username ID 
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
# Should input {"username": username, "password": password}      #
# Returns {"authToken”: authToken}} in success                   #
# Returns {"erro": Errorcode} in error                           #
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
            id = {'user_id': id, "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}
            is_banned = verify_ban(id)
            if(is_banned[0] == False):
                result = {'erro:':is_banned[1]}
            else:
                result = jwt.encode(id,SECRET_KEY, algorithm="HS256")
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
# {"token":AuthToken, "title": Titulo do Novo Leilão, "EAN_ISBN": artigo_id    #
# "min_price": "Preço minimo", "Description": “Descrição do Novo Leilão”       #
#       "end_time": "tempo do fim do leilão YYYY-MM-DD HH:MM:SS",              #
#       "item_name": "Nome do item a vender",                                  #
#       "item_description": "Descrição do item a vender" }                     #
# Returns {"leilaoId": id}} in success                                         #
# Returns {"erro": Errorcode} in error case                                    #
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
    cur.execute("Begin transaction")
    try:
        end_date = datetime.datetime.fromisoformat(to_add["end_time"])

        statement =  """Insert into auction (seller_id, EAN_ISBN, title, description, end_time,  min_price, item_name, start_date)
                    values(%s, %s, %s, %s, %s, %s, %s, current_timestamp(0)) RETURNING ID"""
        values = (id, to_add["EAN_ISBN"],  to_add["title"], to_add["Description"], end_date, 
                    to_add["min_price"], to_add["item_name"])
        
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
            cur.execute("COMMIT");
            conn.close()

    return jsonify(result)


################################################################################
#                                                                              #
# Get all running auctions                                                     #
# Should input                                                                 #
# {"token": AuthToken"}                                                        #
# Returns  {                                                                   # 
#        "Auction ID": "----",                                                 #
#        "Description": "-----------"                                          #
#   }  {                                                                       #
#        "Auction ID": "----",                                                 #
#        "Description": "-----------"                                          #
#   } ...                                                                      #
# Returns {"erro": Errorcode} in error                                         #
#                                                                              #
################################################################################
@app.route("/dbproj/leiloes/", methods=['GET'], strict_slashes=True)
def get_auctions():
    logger.info("###      GET /leiloes ->  Get all auctions         ###")
    to_add = request.get_json()
    ##Login to user
    logger.info("HERE")
    login = authenticate(to_add["token"])
    if(login[0] == False):
        return jsonify({'erro:': login[1]})
    logger.info("HERE")

    ##Connect to DB
    conn = db_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("""SELECT id, description FROM auction 
                where end_time > current_timestamp and canceled = FALSE
                ORDER BY end_time DESC""")
        rows = cur.fetchall()
        payload = []
        for row in rows:
            logger.debug(row)
            content = {'Auction ID' : row[0], 'Description': row[1]}
            payload.append(content) ##Appending to the payload to be returned

    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        payload = {'erro:': str(error)}
    finally:
        if conn is not None:
            conn.close()

    return jsonify(payload)


################################################################################
#                                                                              #
# Search auction by keyword or item EAN_ISBN                                   #
# Should input                                                                 #
# {"token": AuthToken}                                                         #
#                                                                              #
# Returns {                                                                    # 
#        "Auction ID": "----",                                                 #
#        "Description": "-----------"                                          #
#   }  {                                                                       #
#        "Auction ID": "----",                                                 #
#        "Description": "-----------"                                          #
#   } in success                                                               #
# Returns {"erro": Errorcode} in error                                         #
#                                                                              #
################################################################################
@app.route("/dbproj/leiloes/<keyword>", methods=['GET'], strict_slashes=True)
def search_auctions(keyword):
    logger.info("###      GET /leiloes ->  Get all auctions         ###")
    input_body = request.get_json()
    ##Login to user
    login = authenticate(input_body["token"])
    if(login[0] == False):
        return jsonify({'erro:': login[1]})

    ##Connect to DB
    conn = db_connection()
    cur = conn.cursor()

    statement = ("""SELECT auct_id, descrip FROM search_auctions(%s)""")
    try:
        cur.execute(statement, (keyword,)) 
        rows = cur.fetchall()
        payload = []
        for row in rows:
            content = {'Auction ID': row[0], 'Description': row[1]}
            logger.info(content)
            payload.append(content) ##Appending to the payload to be returned

    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        payload = {'erro:': str(error)}
    finally:
        if conn is not None:
            conn.close()
    return jsonify(payload)


################################################################################
#                                                                              #
# Get auction info from ID (id should be put on endpoint, like in route)       #
# Should input                                                                 #
# {"token": AuthToken}                                                         #
# Returns 'Seller Username': -----, 'Auction Title': -----.                    #
# 'Item EAN ISBN': -----, 'Item Name': -----, 'Description': -----,            #
# 'End Time': -----,'Current Price': -----, 'Minimum Price': -----,            #
# 'Auction Start Time' : -----, 'Messages --New to old--' : -----,             #
# "Bids --New to old--": -----, "Auction State" : -----                        #
#           in success                                                         #
# Returns {"erro": error code} in error                                        #
#                                                                              #
################################################################################
@app.route("/dbproj/leilao/<leilaoid>", methods=['GET'], strict_slashes=True)
def getAuctionByID(leilaoid):
    logger.info("###      GET /leiloes ->  Get all auctions         ###")
    input_body = request.get_json()
    ##Login to user
    login = authenticate(input_body["token"])
    if(login[0] == False):
        return jsonify({'erro:': login[1]})

    ##Connect to DB
    conn = db_connection()
    cur = conn.cursor()


    try:
        ##Get auction data
        statement = ("""SELECT username, title, EAN_ISBN, item_name, description, end_time,
                    current_price, min_price, start_date, finished, canceled FROM users, auction 
                    where auction.seller_id = users.id and auction.id = (%s)""")
        cur.execute(statement, (leilaoid,)) 
        auction_data = cur.fetchone()        
        
        ##Verify if auction exists
        if(auction_data == None):
            raise Exception("Couldn't find auction")
        
        ##Get auction mural messages
        statement = ("""SELECT username, message, mes_time FROM mural_message, users
                    where mural_message.users_id = users.id and 
                    auction_id = (%s) ORDER BY mes_time DESC""")
        cur.execute(statement, (leilaoid,))
        messages = cur.fetchall()
        if len(messages) != 0:
            mess = {}
            for i in range(len(messages)):
                message = messages[i]
                this_mess = { "Sender":message[0], "Message Text":message[1], "Message Time": message[2]}
                mess["Message " + str(i+1) + ":"] = this_mess
        else:
            mess = "The mural is empty"
        
        ##Get auction bids history
        statement = ("""SELECT username, price, bid_time FROM bidding, users
                    where bidding.bidder_id = users.id and 
                    auction_id = (%s) and valid = TRUE ORDER BY bid_time DESC""")
        cur.execute(statement, (leilaoid,))
        bids = cur.fetchall()
        logger.info(bids)
        if len(bids) != 0:
            b = {}
            for i in range(len(bids)):
                bid = bids[i]
                this_bid = { "Bidder":bid[0], "Bid Value":bid[1], "Bid Time": bid[2]}
                b["Bid " + str(i+1) + ":"] = this_bid
        else:
            b = "No bids yet"
        estado_auc = "Auction running"
        if(auction_data[9] == True):
            estado_auc = "Finished auction"
        if(auction_data[10] == True):
            estado_auc = "Canceled auction"
        
        result = {'Seller Username': auction_data[0], 'Auction Title': auction_data[1], 'Item EAN ISBN': auction_data[2],
                    'Item Name': auction_data[3], 'Description': auction_data[4], 'End Time': auction_data[5],
                    'Current Price': auction_data[6], 'Minimum Price': auction_data[7], 'Auction Start Time' : auction_data[8],
                    'Messages --New to old--' : mess, "Bids --New to old--": b, "Auction State" : estado_auc}


    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        result = {'erro:': str(error)}
    finally:
        if conn is not None:
            conn.close()
    return jsonify(result)


################################################################################
#                                                                              #
# Get user auctions                                                            #
# Should input                                                                 #
# {"token":AuthToken}                                                          #
# Returns {"leilaoId":auction_data ,"leilaoId":auction_data} in success        #                                  
# Returns {"erro":Errocode} in error                                           #
#                                                                              #
################################################################################
@app.route("/dbproj/meusLeiloes/", methods=['GET'], strict_slashes=True)
def my_auctions():
    logger.info("###      GET /meusLeiloes/ ->  Get all auctions from logged user       ###")
    input_body = request.get_json()
    ##Login to user
    login = authenticate(input_body["token"])
    if(login[0] == False):
        return jsonify({'erro:': login[1]})
    
    ##Get connected user id
    id = login[1]['user_id']
    ##Connect to DB
    conn = db_connection()
    cur = conn.cursor()

    statement = ("""SELECT DISTINCT auction.id, title, EAN_ISBN, item_name, description, end_time,
                    current_price, min_price, seller_id, finished, canceled FROM auction where auction.seller_id = %s
                    UNION  SELECT DISTINCT auction.id, title, EAN_ISBN, item_name, description, end_time,
                    current_price, min_price, seller_id, finished, canceled FROM bidding, auction where (bidding.bidder_id = %s and auction.id = bidding.auction_id)""")
    try:
        cur.execute(statement, (id, id))
        rows = cur.fetchall()
        payload = []
        for row in rows:
            is_seller = "Bidder"
            if(int(row[8]) == id):
                is_seller = "Seller"
            estado_auc = "Auction running"
            if(row[9] == True):
                estado_auc = "Finished auction"
            if(row[10] == True):
                estado_auc = "Canceled auction"
            result = {'Auction_Title': row[1], 'Item_ID': row[2],
                    'Item_Name': row[3], 'Description': row[4], 'End_Time': row[5],
                    'Current_Price': row[6], 'Min_Price': row[7], 'User is a': is_seller,
                    'Auction State': estado_auc}
            payload.append(result)
        
    

    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        payload = {'erro:': str(error)}
    finally:
        if conn is not None:
            conn.close()
    return jsonify(payload)


################################################################################
#                                                                              #
# Change auction data                                                          #
# Should input                                                                 #
# {"token":AuthToken, "title": Novo titulo do Leilão,                          #
# "description": "Nova Descrição do Leilão"                                    #
#       "item_name": "Novo nome do item a vender"}                             #
# Returns {"leilaoId":id}} in success                                          #
# Returns {"erro":errorcode} in error                                          #
#                                                                              #
################################################################################
@app.route("/dbproj/leilao/<auct_id>", methods=['PUT'], strict_slashes=True)
def changeAuction(auct_id):
    logger.info("###      PUT /leilao/<auct_id> ->  Change auction data         ###")
    change = request.get_json()
    ##Login to user
    login = authenticate(change["token"])
    if(login[0] == False):
        return jsonify({'erro:': login[1]})
    
    ##Get connected user id
    id = login[1]['user_id']
    
    ##Connect to DB
    conn = db_connection()
    cur = conn.cursor()
    cur.execute("BEGIN")
    try:
        ##SELECT Auction for Update
        statement = """SELECT title, item_name, description FROM auction
        where auction.id = %s and seller_id = %s and end_time > current_timestamp 
        and finished = FALSE and canceled = FALSE FOR UPDATE"""
        values = (auct_id, id)
        cur.execute(statement, values)
        row = cur.fetchone()
        if(row is None):
            raise Exception("Invalid id or auction is no owned by logged user")
        
        ##Update Tables
        statement = """UPDATE auction set title = %s, description = %s, item_name = %s where id = %s"""
        values = (change['title'], change['description'], change['item_name'], auct_id)
        cur.execute(statement, values)
        payload = {'Sucesso': "Leilao atualizado com sucesso"}

    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        payload = {'erro:': str(error)}
    finally:
        if conn is not None:
            cur.execute("COMMIT")
            conn.close()
    return jsonify(payload)


################################################### END OF AUCTION ########################################################


#################################################### BID ##################################################################


################################################################################
#                                                                              #
# Add a new bid to the system                                                  #
# Should input                                                                 #
# {"token":AuthToken}                                                          #
# Bid Value should be in the end point                                         #
# Returns payload = {'sucesso:': "Nova licitação de --licitacao-- adicionada   # 
# ao leilão numero --numero do leilao -- "} in success                         #
# Returns {"erro":errorCode} in error                                          #
#                                                                              #
################################################################################
@app.route("/dbproj/licitar/<auct_id>/<licitacao>", methods=['GET'], strict_slashes=True)
def bid(auct_id, licitacao):
    logger.info("###      GET /licitar/<id>/<licitacao> ->  Bid in a auction         ###")
    input_body = request.get_json()
    ##Login to user
    login = authenticate(input_body["token"])
    if(login[0] == False):
        return jsonify({'erro:': login[1]})
    
    ##Get connected user id
    id = login[1]['user_id']
    
    ##Connect to DB
    conn = db_connection()
    cur = conn.cursor()

    try:
        cur.execute("Begin transaction")
        statement = ("""SELECT current_price, min_price, seller_id, id FROM auction
                    where auction.id = %s and seller_id <> %s 
                    and end_time > current_timestamp and finished = FALSE and canceled = FALSE
                    and (current_price < %s or (current_price is null and min_price < %s)) FOR UPDATE""")
        cur.execute(statement, (auct_id, id, licitacao, licitacao)) 
        row = cur.fetchone()
        if(row is None):
            raise Exception("Verifique os leilões ativos ou se está a tentar licitar no seu proprio leilão, ou o preço")
        
        ##Update Bidding table
        statement = ("""INSERT INTO BIDDING (price, bid_time, auction_id, bidder_id)
                VALUES(%s, current_timestamp(0), %s, %s)""")
        values = (licitacao, row[3], id)
        cur.execute(statement, values)
        
        ##Update auction table with the new price
        statement = ("""UPDATE auction SET current_price = %s
                        where id = %s""")
        values = (licitacao,  row[3])
        cur.execute(statement, values)
        payload = {'sucesso:': "Nova licitação de " + str(licitacao) + " adicionada ao leilão numero " + str(row[3])}
        cur.execute("COMMIT")
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        payload = {'erro:': str(error)}
        cur.execute("ROLLBACK")
    finally:
        if conn is not None:
            conn.close()
    return jsonify(payload)


############################################################ END OF BID ######################################################


########################################################### MURAL MESSAGE #####################################################


################################################################################
#                                                                              #
# Send a mural message to the system                                           #
# Should input                                                                 #
# {"token":AuthToken, "message": Mensagem a enviar}                            #
# Returns payload = {'Success:': "Message submited with success"} in success   #
# Returns {"erro": ErrorCode} in error                                         #
#                                                                              #
################################################################################
@app.route("/dbproj/leilao/<auct_id>/message", methods=['POST'], strict_slashes=True)
def mural_message(auct_id):
    logger.info("###      POST /licitar/<auct_id>/message ->  Message in a mural         ###")
    input_body = request.get_json()

    ##Login to user
    login = authenticate(input_body["token"])
    if(login[0] == False):
        return jsonify({'erro:': login[1]})
    
    ## Get connected user id
    id = login[1]['user_id']

    ##Connect to DB
    conn = db_connection()
    cur = conn.cursor()

    try:
        cur.execute("Begin transaction")
        statement = """Insert into mural_message (message, mes_time, auction_id, users_id)
                    Values (%s, current_timestamp(0), %s, %s)"""
        values = (input_body['message'], auct_id, id)
        cur.execute(statement, values)
        cur.execute("COMMIT")
        payload = {'Success:': "Message submited with success"}
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        payload = {'erro:': str(error)}
        cur.execute("ROLLBACK")
    finally:
        if conn is not None:
            conn.close()
    return jsonify(payload)


################################################################# END OF MURAL MESSAGE ############################################################


########################################################### User #####################################################


################################################################################
#                                                                              #
# User notification                                                            #
# Should input                                                                 #
# {"token": AuthToken}                                                         #
# Returns {"System Messages": Notifications,                                   #
# "Mural Messages": Notifications } in success                                 #
# Returns {"erro": AuthError} in success                                       #
#                                                                              #
################################################################################
@app.route("/dbproj/notifications", methods=['GET'], strict_slashes=True)
def user_notifications():
    logger.info("###      GET /dbproj/notifications ->  Get all notifications         ###")
    input_body = request.get_json()

    ##Login to user
    login = authenticate(input_body["token"])
    if(login[0] == False):
        return jsonify({'erro:': login[1]})
    
    ##Get connected user id
    id = login[1]['user_id']

    ##Connect to DB
    conn = db_connection()
    cur = conn.cursor()

    try:
        #Initiate output
        payload = {}

        #Get System notifications
        statement = """Select message, mes_time from notifications 
                    where users_id = %s ORDER BY mes_time DESC"""
        values = (id, )
        cur.execute(statement, values)
        system_notf = cur.fetchall()
        
        if(len(system_notf) != 0):
            s_nots = {}
            for i in range(len(system_notf)):
                noti = system_notf[i]
                s_nots['Sys Message ' + str(i+1)] = { "Message" : noti[0], "Message Time": noti[1]}
            payload['System Messages'] = s_nots
        else:
            payload['System Messages'] = "User does not has any System notification"
        
        ##Get auction id where user published on mural or created
        statement = """Select DISTINCT auction.id, auction.title from mural_message, auction 
                    where seller_id = %s or (mural_message.users_id = %s and auction.id = mural_message.auction_id)"""
        cur.execute(statement, (id, id))
        auctions = cur.fetchall()
        mural_messages = {}
        
        if(len(auctions) != 0):
            for auc in auctions:
                logger.info(auc)
                auction_messages = {}
                auction_messages = {"Auction ID": auc[0], "Auction Title": auc[1]}
                ##Get this auction messages
                statement = """Select username, message, mes_time from mural_message, users
                        where auction_id = %s and users_id <> %s and users.id = mural_message.users_id
                        Order by mural_message.mes_time DESC"""
                cur.execute(statement, (auc[0], id))
                mural_m = cur.fetchall()
                if(len(mural_m) != 0):
                    for i in range(len(mural_m)):
                        message = mural_m[i]
                        auction_messages["Message " + str(i + 1)] = {"Sender":message[0], "Message":message[1],
                                        "Message Time":message[2]}
                else:
                    auction_messages["Messages"] = "Auction does not has messages yet"
                mural_messages["Auction " + str(auc[0])] = auction_messages
            payload['Mural Messages'] = mural_messages
        else:
            payload['Mural Messages'] = "User does not has any Auction participation"

    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        payload = {'erro:': str(error)}
    finally:
        if conn is not None:
            conn.close()
    return jsonify(payload)


################################################################################
#                                                                              #
# Verify if auction is finished                                                #
# Should input                                                                 #
# Returns {"auction id": id from finished auction,                             #
# "auction id": id from finished auction} in success                           #
# Returns {"erro": AuthError} in success                                       #
#                                                                              #
################################################################################
@app.route("/dbproj/finished", methods=['GET'], strict_slashes=True)
def is_finished():
    logger.info("###      GET /dbproj/finished ->  Verify if auction is finished         ###")    #Connect to DB
    
    conn = db_connection()
    cur = conn.cursor()
    cur.execute("Begin")
    try:
        statement ="""Select id, title from auction 
        where current_timestamp > end_time and finished = False
        and canceled = False FOR UPDATE"""
        cur.execute(statement)
        rows = cur.fetchall()
        payload = {}
        if(len(rows) != 0):
            for row in rows:
                logger.info(row[0])
                statement = """UPDATE auction set finished = TRUE where auction.id = %s"""
                cur.execute(statement, (row[0],))
                payload["Auction " + str(row[0])] = "Finished"
        else:
            payload = {"Result" : "No auctions to be finished now"}


    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        payload = {'erro:': str(error)}
    finally:
        if conn is not None:
            cur.execute("COMMIT")
            conn.close()
    return jsonify(payload)


################################################################################
#                                                                              #
# Cancel an auction                                                            #
# Should input                                                                 #
# {"token": AuthToken}                                                         #
# Returns {"Auction --num--" = "Auction Canceled with success" in success      #
# Returns {"erro": ErrorCode} in error                                         #
#                                                                              #
################################################################################
@app.route("/dbproj/<auct_id>/cancel", methods=['GET'], strict_slashes=True)
def cancel_auction(auct_id):
    logger.info("###      GET /dbproj/<auct_id>/cancel ->  Cancel an auction        ###")
    input_body = request.get_json()

    ##Login to user
    login = authenticate(input_body["token"])
    if(login[0] == False):
        return jsonify({'erro:': login[1]}) 
    ##Get connected user id
    id = login[1]['user_id']
    
    ##Connect to DB
    conn = db_connection()
    cur = conn.cursor()
    cur.execute("Begin")
   
    try:
        cur.execute("""Select is_admin from users where id = %s""", (id, ))
        row = cur.fetchone()
        if(row[0] == False):
            raise Exception("User is not an admin")
        
        payload = {}
        statement ="""Select * from auction 
        where current_timestamp < end_time and finished = False
        and canceled = False and id = %s FOR UPDATE"""
        cur.execute(statement, (auct_id, ))
        row = cur.fetchone()
        if(row is None):
            raise Exception("Auction doesn't exists")
        statement = """UPDATE auction set canceled = TRUE where auction.id = %s"""
        cur.execute(statement, (row[0],))
        payload["Auction " + str(row[0])] = "Auction Canceled with success"
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        payload = {'erro:': str(error)}
    finally:
        if conn is not None:
            cur.execute("COMMIT")
            conn.close()
    return jsonify(payload)


################################################################################
#                                                                              #
# An administrator ban user                                                    #
# Should input                                                                 #
# {"token": AuthToken}                                                         #
# Returns {"Result": "User "+--username--+" is banned with success" in success #
# Returns {"erro": AuthError} in success                                       #
#                                                                              #
################################################################################
@app.route("/dbproj/<user_id>/ban", methods=['GET'], strict_slashes=True)
def ban_user(user_id):
    logger.info("###      GET /dbproj/<user_id>/ban ->  Ban an user        ###")
    input_body = request.get_json()

    ##Login to user
    login = authenticate(input_body["token"])
    if(login[0] == False):
        return jsonify({'erro:': login[1]}) 
    ##Get connected user id
    id = login[1]['user_id']
    
    ##Connect to DB
    conn = db_connection()
    cur = conn.cursor()
    cur.execute("Begin")
   
    try:
        cur.execute("""Select is_admin from users where id = %s""", (id, ))
        row = cur.fetchone()
        if(row[0] == False):
            raise Exception("User is not an administrator")
        
        payload = {}
        statement ="""Select id, is_admin, username, is_banned from users 
        where id = %s FOR UPDATE"""
        cur.execute(statement, (user_id, ))
        row = cur.fetchone()
        
        if(row is None):
            raise Exception("User doesn't exists")

        if(row[1] == True):
            raise Exception("Can't ban another administrator")
        if(row[3] == True):
            raise Exception("User was banned")


        ##Ban The user
        statement = """UPDATE users set is_banned = TRUE, ban_time = current_timestamp(0) where id = %s"""
        cur.execute(statement, (user_id, ))
        
        ##Get auctions created by user
        statement = """SELECT id From auction where seller_id = %s FOR UPDATE"""
        cur.execute(statement, (row[0],))
        to_cancel = cur.fetchall()

        ##Cancel this auctions
        statement = """UPDATE auction set canceled = True where seller_id = %s"""
        cur.execute(statement, (row[0],))
        
        ##Admin send message to mural message saying that user was banned
        for auction in to_cancel:
            statement = """Insert Into mural_message(message, mes_time, auction_id, users_id)
                            Values(%s, current_timestamp(0), %s, %s)"""
            values = ("Action Owner was Banned! Sorry for the inconvenience", auction[0], id)            
            cur.execute(statement, values)

        ##Get bids done by user
        statement = """SELECT Min(price), auction_id From bidding where bidder_id = %s Group by auction_id"""
        cur.execute(statement, (row[0],))
        to_cancel_data = cur.fetchall()
        
        if(len(to_cancel_data) != 0):
            for b in to_cancel_data:
                statement = """SELECT * From bidding where price >= %s and auction_id = %s ORDER BY PRICE ASC FOR UPDATE """
                cur.execute(statement, (b[0], b[1]))
                to_cancel_bids = cur.fetchall()
                if(len(to_cancel_bids) != 0):
                    ##Cancel Hightest Bids
                    for i in range(len(to_cancel_bids)-1):
                        cancel = to_cancel_bids[i]
                        statement = """UPDATE bidding set valid = FALSE where id = %s"""
                        values = (cancel[0],)
                        cur.execute(statement,values)
                    
                    cancel = to_cancel_bids[len(to_cancel_bids)-1]
                    ##If biggest licitition was from banned user
                    if(cancel[5] == row[0]):
                        ##Set bid to invalid
                        statement = """UPDATE bidding set valid = FALSE where id = %s"""
                        values = (cancel[0],)
                        cur.execute(statement,values)
                        
                        statement = """Select max(price) from bidding where auction_id = %s and valid = TRUE"""
                        values = (cancel[0],)
                        cur.execute(statement,values)
                        max_price = cur.fetchone()[0]

                        statement = """UPDATE auction set current_price = %s where id = %s"""
                        values = (max_price, cancel[4])
                        cur.execute(statement,values)

                    else:
                        statement = """UPDATE auction set current_price = %s where id = %s"""
                        values = (b[0], cancel[4])
                        cur.execute(statement,values)

                        statement = """UPDATE bidding set price = %s where id = %s"""
                        values = (b[0], cancel[0])
                        cur.execute(statement,values)

                        statement = """Insert into notifications(message, mes_time, users_id)
                                    Values(%s, current_timestamp(0), %s)"""
                        values = ("Um utilizador foi banido, por isso a sua licitação no leilão numero " + str(b[1]) + " foi alterada para " + str(b[0]) + ", por favor verifique", cancel[5])
                        cur.execute(statement,values)
        payload["Result"] = "User "+ row[2] + " is banned with success"
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        payload = {'erro:': str(error)}
        cur.execute("ROLLBACK")
    finally:
        if conn is not None:
            cur.execute("COMMIT")
            conn.close()
    return jsonify(payload)


################################################################################
#                                                                              #
# Admin statistics                                                             #
# Should input                                                                 #
# {"token": AuthToken}                                                         #
# Returns {                                                                    #
#   "Number auctions in last 10 days": Count(leilao),                          #
#   "Top 10 Auction Sellers":{                                                 #
#       "Position 1": {"username": ----, "count" : -----},                     #
#       "Position 2": {"username": ----, "count" : -----}                      #
#       },                                                                     #
#   "Top 10 Auction Winners":{                                                 #
#       "Position 1": {"username": ----, "count" : -----},                     #
#       "Position 2": {"username": ----, "count" : -----}                      #
#       }                                                                      #
#   } in success                                                               #
# Returns {"erro": ErrorCode} in error                                         #
#                                                                              #
################################################################################
@app.route("/dbproj/stats", methods=['GET'], strict_slashes=True)
def stats():
    logger.info("###      GET /dbproj/stats ->  Get statistics        ###")
    input_body = request.get_json()

    ##Login to user
    login = authenticate(input_body["token"])
    if(login[0] == False):
        return jsonify({'erro:': login[1]}) 
    ##Get connected user id
    id = login[1]['user_id']
    
    ##Connect to DB
    conn = db_connection()
    cur = conn.cursor()
    try:
        cur.execute("""Select is_admin from users where id = %s""", (id, ))
        row = cur.fetchone()
        if(row[0] == False):
            raise Exception("User is not an administrator")
        
        ##TOP 10 AUCTION SELLERS
        payload = {}
        statement = """SELECT username, COUNT(SELLER_ID) 
                    FROM AUCTION,users 
                    where seller_id = users.id 
                    GROUP BY username ORDER BY COUNT(SELLER_ID) DESC"""
        cur.execute(statement)
        created_auct = cur.fetchall()
        temp = {}
        i = 1
        for row in created_auct:
            top_seller = {"Username":row[0], "Created Auctions number":row[1]}
            temp["Position " + str(i)] = top_seller
            i = i+1
            if(i == 11):
                break
        payload["Top 10 Auction Sellers"] = temp
        
        ##TOP 10 AUCTION WINNERS 
        temp = {}
        statement  = """Select username, COUNT(bidder_id) from bidding, users where ROW( price, auction_id) in (SELECT  MAX(PRICE), auction_id FROM BIDDING, AUCTION WHERE AUCTION.id = BIDDING.auction_id and auction.finished = TRUE GROUP
                        BY auction_id) and users.id = bidder_id GROUP BY username ORDER BY COUNT(bidder_id) DESC"""
        cur.execute(statement)
        rows = cur.fetchall()
        i = 1
        for row in rows:
            top_seller = {"Username":row[0], "Won Auctions number":row[1]}
            temp["Position " + str(i)] = top_seller
            i = i+1
            if(i == 11):
                break
        payload["Top 10 Auction Winners"] = temp

        #NUMBER OF AUCTIONS IN LAST 10 DAYS
        statement = """SELECT COUNT(*) FROM AUCTION WHERE start_date > current_timestamp(0) - '10 days'::interval"""
        cur.execute(statement)
        n_l = cur.fetchone()[0]
        payload["Number auctions in last 10 days"] = n_l

    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        payload = {'erro:': str(error)}
        cur.execute("ROLLBACK")
    finally:
        if conn is not None:
            cur.execute("COMMIT")
            conn.close()
    return jsonify(payload)


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
        if(is_banned[1] == True):
            return False, ("User "+ str(is_banned[0]) + " is banned")
        return True, id
    except (Exception, psycopg2.DatabaseError) as error:
        return False,  "Error verifying ban"
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
    #Set up the logging
    logging.basicConfig(filename="logs/log_file.log")
    logger = logging.getLogger('logger')
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    
    #Create Formatter
    formatter = logging.Formatter('%(asctime)s [%(levelname)s]:  %(message)s',
                              '%H:%M:%S')
                              #"%Y-%m-%d %H:%M:%S") # not using DATE to simplify
    ch.setFormatter(formatter)
    logger.addHandler(ch)


    time.sleep(1) #Just to let the DB start before this print :-)


    logger.info("\n---------------------------------------------------------------\n" + 
                  "API online: http://localhost:8080/projdb/user/\n\n")
    
    app.run(host="0.0.0.0", debug=True, threaded=True)
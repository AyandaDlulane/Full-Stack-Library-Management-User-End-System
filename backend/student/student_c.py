import db_connection
import pyodbc as odbc

#===============================================================================================================================
#===============================================================================================================================
#===============================================================================================================================

# STUDENTS BACKEND SOURCE CODE FILE BY AYANDA_DLULANE
# BEFORE YOU USE THE FILE MAKE SURE YOU HAVE A STABLE QUERABLE DATABASE AND IMPORT OF CONFIGURE IT OON THIS FILE
#GOOD LUCK TO MY FUTURE SELF AND YOU
#BECAUSE RIGHT NOW ONLY ME AND GOD KNOWS WHATS GOING ON IN THIS CODEBASE
#SOON ONLY GOOD WILL KNOW WHATS GOING ON IN THIS FILE
#READE THE COMMENT I'VE PUT ALOT OF TIME IN THEM


#===============================================================================================================================
#===============================================================================================================================
#===============================================================================================================================



# connecting to a database and establishing a database
connection = db_connection.database.connect()
db = connection.cursor()   #connection cursor for command execution we will be using this connection as db across this code base 


#the st_login(stID: int ,pass : str) takes in the student ID and password
#this will use the security_table
#if the students successfully logs in the stutas of the student in  the security table will be  true
#the security table is as follows
def st_login(stID,passa):
    

    db.execute(f"SELECT COUNT(active) FROM security_table WHERE ID = {stID} AND pass = '{passa}'")

    if db.fetchone()[0] == 0:
       return {"code":12}   #code 12 for invalid inputs 

    #first check if the students is already logged in and we will return code {10} if so

    db.execute(f"SELECT active FROM security_table WHERE ID = {stID} AND pass = '{passa}'")

    
    
    results = db.fetchone()

    if results[0] == True:
       return {"code": 10}  #code 10 mean there already another login 

    elif results[0] == False:
       db.execute(f"""UPDATE security_table
                    SET active = 1
                    WHERE ID = {stID}""")
        
       db.commit()

       return {"code":0}
    
# print(st_login(102,"student")) #for testing



#The function rent_book(stID,bookID:array) is called when a student checks_out or rents a book
# the function will have code 80
#80 for successfull 81 for insufficient funds

def rent_book(stID, bookID=('978-0-09-957807-9','978-0-393-05081-8','78-0-14-118776-1'),emID = 502):
   

   #check if the students hasn't exceded 5 active rents
    query_check_active_rents = f"""
                               SELECT count(bookID)
                               FROM rents
                               WHERE stID = {stID} AND status = 1
                               """
   
    db.execute(query_check_active_rents)
    num_rents = db.fetchone()[0]

    if num_rents > 5:
        return {"code":82}  #exceded alloweded number of rents
    

    #check if books are avialable

    query_bookcheck = f"""
                      SELECT count(isbn) over(),isbn
                      FROM books
                      WHERE isbn IN {bookID} and status = 0
                      """
     
    db.execute(query_bookcheck)
    return_list = db.fetchall()

    if len(return_list) != 0:
        return {"code":83, "books":return_list}    
    # print(return_list)
    # # rented_count = return_list[0][0]

    # # if rented_count > 0:
    # #    return {"code":82, "books":return_list}    
    

    # find student_balance
    query_stbalace = f"""
            
            SELECT stBalance
            FROM Students
            WHERE stID = '{stID}'
            """
    
    db.execute(query_stbalace)

    balance = db.fetchone()[0]

    query_totalcost = f"""
                       SELECT sum(rental_price)
                       FROM books
                       WHERE isbn IN {bookID}
                
                       """
    db.execute(query_totalcost)

    total_cost = db.fetchone()[0]
    
    if total_cost > balance:
        return {"code":81} #insuficient funds
    

    # if every thing goes well the rent the books
    
    newBalance = balance - total_cost

    values = ""
    for i,b_id in enumerate(bookID):

        if i == 0:
            values += f"""('{b_id}', {stID}, {emID}, 1, CAST(GETDATE() AS DATE), DATEADD(DAY, 7, CAST(GETDATE() AS DATE)))"""
            continue

        values += f""", ('{b_id}', {stID}, {emID}, 1, CAST(GETDATE() AS DATE), DATEADD(DAY, 7, CAST(GETDATE() AS DATE)))"""


    # return values
    query_rent = f"""
                 UPDATE books
                 SET status = 0
                 WHERE isbn IN {bookID};

                 UPDATE Students
                 SET stBalance = {newBalance}
                 WHERE stID = {stID};

                 INSERT INTO rents (bookID, stID, emID, status, rentdate, returndate)
                 VALUES {values}
                 """
    
        
    
    db.execute(query_rent)
    db.commit()

    return {"code":80}
    



# print(rent_book(stID=102))


#return_book(stID,bookID: list) is a called when  a students returning books it takes in the student ID and the list of books being returned
#code 200's

def return_books(stID,books  = ('978-0-09-957807-9','978-0-393-05081-8','78-0-14-118776-1'), emID = 502):
    
    query_update = ""
    #check books that are on hold
    query_hold = f"""
                 SELECT bookID
                 FROM holds
                 WHERE bookID IN {books}
                 """
    db.execute(query_hold)
    on_holds = db.fetchall()
    

    
    #update books, rents and keep those on hold on not avialable
    if len(on_holds) == 0:
       query_update = f"""
                      UPDATE books
                      SET status = 1
                      WHERE isbn IN {books};

                      UPDATE rents
                      SET    status = 0
                      WHERE isbn IN {books} AND stID = {stID};
                      """
    else:
        not_hold = ()
        on_hold  = ()
       
        for bID in books:
           
           if  bID in on_holds:
               on_hold.append(bID)
           else:
               not_hold.append(bID)

        query_update = f"""
                       UPDATE books
                       SET status = 1
                       WHERE isbn IN {not_hold};

                       UPDATE rents
                       SET    status = 0
                       WHERE isbn IN {books} AND stID = {stID};
                       """
        
        db.execute(query_update)
        db.commit()
        return {"code":200}
    

# the st_profile(stID) function takes in a students students number a checks for the students profile in the database
# using connection and db(the database) we retrieves the student data for the table students and the table is as follows
# Students table  stID   |    stNAME   |   stBalance    |     regdate
#this will be used by the admin or the students profile page
def st_profile(stID):
    
    db.execute(f"SELECT * FROM Students WHERE stID = {stID}")
    
    profile = db.fetchone() 
    
    
    profile = {"stID":profile[0], "stNAME":profile[1], "stBalance":profile[2], "regdate":profile[3]}
    
    return profile


# print(st_profile(102))


# the check_book(book_title,category,rental_price,status,author) is called when the students are looking searching for books using the inputs
#the function uses the books table in the database

# inputs = (book_title = "not",category = "not", rental_price = "not", status = "not", author = "not")
def check_book(book_title = "not",category = "not", rental_price = "not", status = "not", author = "not"):
     
     inputs = {"book_title":book_title,"category": category, "rental_price": rental_price, "status": status, "author": author}
     choose = {}
     
     for input in inputs:
         
         if inputs[input] != "not":
            choose.update({input:inputs[input]}) 
   
     query_string = "SELECT * FROM books WHERE "


     for i,input in enumerate(choose):
         
         if  i == 0:
            query_string += f"""{input} = {inputs[input]}"""
            continue
            
         query_string += f"""AND {input} = {inputs[input]} """

 

     if len(choose) == 0:
         db.execute("SELECT * FROM books")
         return db.fetchall()
     db.execute(query_string)

     results = db.fetchall()

     return results
    #  (book_title = "not",category = "not", rental_price = "not", status = "not", author = "not")

# print(check_book(rental_price=8))

        
# The function hold(stID,bookID) take 2 inputs and updates the holds table for when the students wants to hold a book when not aviableble
#the return codes for holds is 50 seiris
def hold(stID, bookID: str):


    #first we check if the book is already on hold
    query_hold_check = f"""
                       SELECT count(bookID) as c
                       FROM holds
                       WHERE bookID = '{bookID}'
  

                       """
    
    db.execute(query_hold_check)
    count = db.fetchone()[0]

    if count > 0:
       return {"code":51} #code 51 means the book is already on hold
    


    query_hold_check = f"""
                       SELECT count(stID) as c
                       FROM holds
                       WHERE stID = '{stID}'
                       """
    
    db.execute(query_hold_check)
    count = db.fetchone()[0]

    if count > 1:
       return {"code":52} #code means the students is allready holding a book and they can not hold more than 1 book at a time
    

    #Then if the student manages to pass all these the we can grant the hold and we must allso give the student the return date

    query_return_date = f"""
                SELECT returndate
                FROM rents
                WHERE status = 1 AND bookID = '{bookID}'
                """
    
    db.execute(query_return_date)
    return_date = db.fetchone()
    
    query_hold_thebook = f"""
                         INSERT INTO holds (stID, bookID)
                         VALUES ({stID}, '{bookID}')
                        
                          """
    
    db.execute(query_hold_thebook)
    db.commit()
    return {"code":50,"return":return_date} #code 50 holding was successfull
    
   
    


# print(hold(103,'978-0-330-25864-8'))


#The function recharge(stID,amount) this is for when the students is recharging
#code 100's

def recharge(stID,amount):


    try:
        query = f"""
            UPDATE Students
            SET    stBalance = stBalance + {amount}
            WHERE stID = {stID}
            """
        db.execute(query)
        db.commit()
        return {"code":80}  #succes full
    except:
        return {"code":81}  #oops
    


# print(recharge(102,10))

#the function history(stID,active = "all")
#code 220's

def  st_history(stID,active = "all"):
     
     query_history = ""

     if active == "all":
         query_history= f"""
                       SELECT *
                       FROM   rents
                       WHERE stID = {stID}
 """
     else:
         query_history= f"""
                       SELECT *
                       FROM   rents
                       WHERE stID = {stID} AND status = {active}
 """


     db.execute(query_history)
     history = db.fetchall()

     return {"code":220,"history":history}

# print(st_history(102))








    




    
    


    



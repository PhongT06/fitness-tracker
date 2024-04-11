from flask import Flask, jsonify, request
from flask_marshmallow import Marshmallow
from marshmallow import fields, ValidationError
# local import for db connection
from connect_db import connect_db, Error

app = Flask(__name__)
app.json.sort_keys = False # maintain order of your stuff
ma = Marshmallow(app)



class MemberSchema(ma.Schema):
    member_id = fields.Int(dump_only=True)
    name = fields.String(required=True)
    email = fields.String(required=True)
    phone = fields.String(required=True)
    # bench_amount = fields.Int()
    # membership_type = fields.String()

    class Meta:  
        
        fields = ("member_id", "name", "email", "phone", "bench_amount", "membership_type")

# instantiating CustomerSchema class
# based on how many customers we're dealing with
member_schema =MemberSchema()
members_schema = MemberSchema(many=True)





@app.route('/')
def home():
    return "Welcome to our super cool Fitness Tracker, time to get swole brah!"

@app.route('/members', methods=['GET'])
def get_members(): 
    print("hello from the get")  
    try:
        conn = connect_db()
        if conn is None:
            return jsonify({"error": "Database connection failed"}), 500
        
        cursor = conn.cursor(dictionary=True) #dictionary=TRUE only for GET
        # SQL query to fetch all customers
        query = "SELECT * FROM Members"

        # executing query with cursor
        cursor.execute(query)

        # accessing stored query
        members = cursor.fetchall()

         # use Marshmallow to format the json response
        return members_schema.jsonify(members)
    
    except Error as e:
        # error handling for connection/route issues
        print(f"Error: {e}")
        return jsonify({"error": "Internal Server Error"}), 500
    
    finally:
        #checking again for connection object
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

@app.route('/members', methods = ['POST']) 
def add_member():
    try:
        # Validate the data follows our structure from the schema
        # deserialize the data using Marshmallow
        # this gives us a python dictionary
        member_data = member_schema.load(request.json)

    except ValidationError as e:
        print(f"Error: {e}")
        return jsonify(e.messages), 400  

    try:
        conn = connect_db()
        if conn is None:
            return jsonify({"error": "Database connection failed"}), 500
        cursor = conn.cursor()

        # new customer details, to be sent to our db
        # comes from customer_data which we turn into a python dictionary
        # with .load(request.json)
        new_member = (member_data['name'], member_data['email'], member_data['phone'])

        # SQL Query to insert customer data into our database
        query = "INSERT INTO Members (name, email, phone) VALUES (%s, %s, %s)"

        # execute the query 
        cursor.execute(query, new_member)

        conn.commit()

        # Succesfiul addition of our customer
        return jsonify({"message":"New member added succesfully"}), 201
    
    except Error as e:
        print(f"error: {e}")
        return jsonify({"error": "Internal Server Error"}), 500
    
    finally:
        #checking again for connection object
        if conn and conn.is_connected():
            cursor.close()
            conn.close() 


@app.route('/members/<int:id>', methods= ["PUT"])
def update_member(id):
    try:
        # Validate the data follows our structure from the schema
        # deserialize the data using Marshmallow
        # this gives us a python dictionary
        member_data = member_schema.load(request.json)

    except ValidationError as e:
        print(f"Error: {e}")
        return jsonify(e.messages), 400
    
    try:
        conn = connect_db()
        if conn is None:
            return jsonify({"error": "Database connection failed"}), 500
        cursor = conn.cursor()

        # Updating customer info
        updated_member = (member_data['name'], member_data['email'], member_data['phone'], id)

        # SQL Query to find and update a customer based on the id
        query = "UPDATE Members SET name = %s, email = %s, phone = %s WHERE member_id = %s"

        # Executing Query
        cursor.execute(query, updated_member)
        conn.commit()

        # Message for succesful update
        return jsonify({"message":"Member details were succesfully updated!"}), 200

    except Error as e:
        print(f"error: {e}")
        return jsonify({"error": "Internal Server Error"}), 500
    
    finally:
        #checking again for connection object
        if conn and conn.is_connected():
            cursor.close()
            conn.close()


@app.route('/members/<int:id>', methods=["DELETE"])
def delete_member(id):
    try:
        conn = connect_db()
        if conn is None:
            return jsonify({"error": "Database connection failed"}), 500
        cursor = conn.cursor()
        # set variable for the id passed in through the right to a tuple, with that id
        member_to_remove = (id,)
        

        # query to find customer based on their id
        query = "SELECT * FROM Members WHERE member_id = %s"
        # check if customer exists in db
        cursor.execute(query, member_to_remove)
        member = cursor.fetchone()
        if not member:
            return jsonify({"error": "User does not exist"}), 404
        
        # If customer exists, we shall delete them :( 
        del_query = "DELETE FROM Members where member_id = %s"
        cursor.execute(del_query, member_to_remove)
        conn.commit()

        # nice message about the execution of our beloved customer
        return jsonify({"message":"Member Removed succesfully"}), 200   

    except Error as e:
        print(f"error: {e}")
        return jsonify({"error": "Internal Server Error"}), 500
    
    finally:
        #checking again for connection object
        if conn and conn.is_connected():
            cursor.close()
            conn.close() 
       

# ================= ORDER SCHEMA and ROUTES ============================
class DankSchema(ma.Schema):
    member_id = fields.Int(dump_only=True)
    sesh_id = fields.Int(required=True)
    date = fields.Date(required=True)   

    class Meta:  
        
        fields = ("member_id", "sesh_id", "date")
# initialize our schemas
dank_schema = DankSchema()
danks_schema = DankSchema(many=True)

    

@app.route("/dank_sesh", methods = ["GET"])
def get_orders():
    try:
        conn = connect_db()
        if conn is None:
            return jsonify({"error": "Database connection failed"}), 500
        cursor = conn.cursor(dictionary=True)

        query = "SELECT * FROM Dank_sesh"
        cursor.execute(query)
        dank = cursor.fetchall()  

        return danks_schema.jsonify(dank)
    
    
    except Error as e:
        print(f"error: {e}")
        return jsonify({"error": "Internal Server Error"}), 500
    
    finally:
        #checking again for connection object
        if conn and conn.is_connected():
            cursor.close()
            conn.close() 
    
# POST request to add ordere
@app.route('/dank_sesh', methods=["POST"])
def add_dank():
    try:
        # Validate incoming data
        dank_data = dank_schema.load(request.json)

    except ValidationError as e:
        return jsonify(e.messages), 400

    try:
        conn = connect_db()
        if conn is None:
            return jsonify({"error": "Database connection failed"}), 500
        cursor = conn.cursor()
        
        query = "INSERT INTO Dank_sesh (date, sesh_id) VALUES (%s,%s)"
        cursor.execute(query, (dank_data['date'], dank_data['sesh_id']))
        conn.commit()
        return jsonify({"message": "Dank sesh was succesfully added"}),201

    except Error as e:
        print(f"error: {e}")
        return jsonify({"error": "Internal Server Error"}), 500

    finally:
    #checking again for connection object
        if conn and conn.is_connected():
            cursor.close()
            conn.close() 


# PUT request to Update Order####################################
@app.route('/dank_sesh/<int:member_id>', methods= ["PUT"])
def update_dank(member_id):
    try:
        # Validate incoming data
        dank_data = dank_schema.load(request.json)

    except ValidationError as e:
        return jsonify(e.messages), 400
    
    try:
        conn = connect_db()
        if conn is None:
            return jsonify({"error": "Database connection failed"}), 500
        cursor = conn.cursor()
        query = "UPDATE Dank_sesh SET date = %s, sesh_id = %s WHERE member_id = %s"
        cursor.execute(query, (dank_data['date'], dank_data['sesh_id'], member_id))
        conn.commit()
        return jsonify({"message": "Order updated succesfully"}), 200    


    except Error as e:
        print(f"error: {e}")
        return jsonify({"error": "Internal Server Error"}), 500

    finally:
    #checking again for connection object
        if conn and conn.is_connected():
            cursor.close()
            conn.close()
    
# DELETE Request
@app.route("/dank_sesh/<int:sesh_id>", methods=["DELETE"])
def delete_dank(sesh_id):
    try:
        conn = connect_db()
        if conn is None:
            return jsonify({"error": "Database connection failed"}), 500
        cursor = conn.cursor()

         # query to find order based on their id
        query = "SELECT * FROM Dank_sesh WHERE sesh_id = %s"
        # check if order exists in db
        cursor.execute(query, (sesh_id,))
        dank = cursor.fetchone()
        if not dank:
            return jsonify({"error": "Order does not exist"}), 404
        
        # If order exists, we shall delete them :( 
        del_query = "DELETE FROM Dank_sesh where sesh_id = %s"
        cursor.execute(del_query, (sesh_id,))
        conn.commit()
        return jsonify({f"message": "Succesfully delete sesh_id {sesh_id}"})    

    except Error as e:
        print(f"error: {e}")
        return jsonify({"error": "Internal Server Error"}), 500

    finally:
    #checking again for connection object
        if conn and conn.is_connected():
            cursor.close()
            conn.close()





if __name__ == "__main__":
    app.run(debug=True, port= 5001 )











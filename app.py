from flask import Flask, request, redirect, url_for, session, render_template, flash
import mysql.connector


app = Flask(__name__)
app.secret_key = 'axamparos'  # Set a secret key for session encryption

connection =  mysql.connector.connect(host='localhost', port='3306', database='library_system', user='root', password='Sporar9!')


@app.route("/")
def index():

    return '''
    <div class="container text-center">
        <h1>Welcome to ADOXOS</h1>
        <a href="/login" class="btn btn-primary">Login</a>
    </div>
    '''
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        # Establish a database connection
        try:
            connection = mysql.connector.connect(
                host='localhost',
                port='3306',
                database='library_system',
                user='root',
                password='Sporar9!'
            )

            # Create a cursor object to execute SQL queries
            cursor = connection.cursor()

            # Execute the SQL query to retrieve the user with the given username and password
            query = "SELECT * FROM users WHERE username = %s AND passwrd = %s"
            cursor.execute(query, (username, password))

            # Fetch the first row from the result
            user = cursor.fetchone()

            if user:
                user_type = user[10]  # Assuming the user_type column is at index 10 in the user tuple

                if user_type in ["student", "teacher"]:
                    # Redirect students and teachers to the same page
                    session['user'] = user  # Store the user in the session
                    return redirect(url_for("main_students_teachers"))
                elif user_type in ["school admin"]:
                    # Redirect admins and school admins to another page
                    session['user'] = user  # Store the user in the session
                    return redirect(url_for("main_school_admin"))
                elif user_type in ["admin"]:
                    # Redirect admins and school admins to another page
                    session['user'] = user  # Store the user in the session
                    return redirect(url_for("main_admin"))
                else:
                    # Unknown user type
                    return "Unknown User Type"
            else:
                # User does not exist or incorrect username/password
                return "Login Failed"
        except mysql.connector.Error as error:
            # Handle database connection error
            return f"Database Error: {error}"
        finally:
            # Close the cursor and database connection
            if 'cursor' in locals():
                cursor.close()
            if 'connection' in locals():
                connection.close()
    """
    return '''
    <form method="POST" action="/login">
        <label for="username">Username:</label>
        <input type="text" id="username" name="username"><br><br>
        <label for="password">Password:</label>
        <input type="password" id="password" name="password"><br><br>
        <input type="submit" value="Login">
    </form>
    '''
    """

    return '''
    <form method="POST" action="/login" style="max-width: 300px; margin: 0 auto; padding: 20px; border: 1px solid #ccc; border-radius: 4px;">
        <h2 style="text-align: center;">Login</h2>
        <div style="margin-bottom: 10px;">
            <label for="username">Username:</label>
            <input type="text" id="username" name="username" style="width: 100%; padding: 5px;">
        </div>
        <div style="margin-bottom: 10px;">
            <label for="password">Password:</label>
            <input type="password" id="password" name="password" style="width: 100%; padding: 5px;">
        </div>
        <div style="text-align: center;">
            <input type="submit" value="Login" style="padding: 8px 16px; background-color: #4CAF50; color: white; border: none; border-radius: 4px; cursor: pointer;">
        </div>
    </form>
    '''

@app.route("/main/admin")
def main_admin():
    first_name = session['user'][3]
    #return f"Welcome {first_name} !"
    return render_template("main_admin.html", first_name=first_name)

@app.route("/main/admin/school", methods=["GET", "POST"])
def main_admin_school():
    if 'user' not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        action = request.form.get("action")

        if action == "insert":
            school_name = request.form.get("school_name")
            postal_code = request.form.get("postal_code")
            city_name = request.form.get("city_name")
            school_phone_number = request.form.get("school_phone_number")
            school_email = request.form.get("school_email")
            school_principal = request.form.get("school_principal")
            school_admin = request.form.get("school_admin")

            try:
                cursor = connection.cursor()
                query = "INSERT INTO school (school_name, postal_code, city_name, school_phone_number, school_email, school_principal, school_admin) VALUES (%s, %s, %s, %s, %s, %s, %s)"
                values = (school_name, postal_code, city_name, school_phone_number, school_email, school_principal, school_admin)
                cursor.execute(query, values)
                connection.commit()
                cursor.close()
                flash('School added successfully.', 'success')
                return redirect(url_for("main_admin_school"))
            except mysql.connector.Error as error:
                return f"Database Error: {error}"

        elif action == "delete":
            school_id = request.form.get("school_id")

            try:
                cursor = connection.cursor()
                query = "DELETE FROM school WHERE school_id = %s"
                values = (school_id,)
                cursor.execute(query, values)
                connection.commit()
                cursor.close()
                flash('School deleted successfully.', 'success')
                return redirect(url_for("main_admin_school"))
            except mysql.connector.Error as error:
                return f"Database Error: {error}"

        elif action == "update":
            school_id = request.form.get("school_id")
            school_name = request.form.get("school_name")
            postal_code = request.form.get("postal_code")
            city_name = request.form.get("city_name")
            school_phone_number = request.form.get("school_phone_number")
            school_email = request.form.get("school_email")
            school_principal = request.form.get("school_principal")
            school_admin = request.form.get("school_admin")

            try:
                cursor = connection.cursor()
                query = "UPDATE school SET school_name = %s, postal_code = %s, city_name = %s, school_phone_number = %s, school_email = %s, school_principal = %s, school_admin = %s WHERE school_id = %s"
                values = (
                school_name, postal_code, city_name, school_phone_number, school_email, school_principal, school_admin,
                school_id)
                cursor.execute(query, values)
                connection.commit()
                cursor.close()
                flash('School updated successfully.', 'success')
                return redirect(url_for("main_admin_school"))
            except mysql.connector.Error as error:
                return f"Database Error: {error}"

        # Retrieve the list of schools
    try:
        cursor = connection.cursor()
        query = "SELECT * FROM school"
        cursor.execute(query)
        schools = cursor.fetchall()
        cursor.close()
        return render_template("main_admin_school.html", schools=schools)
    except mysql.connector.Error as error:
        return f"Database Error: {error}"

@app.route("/main/admin/registrations", methods=["GET", "POST"])
def main_admin_registrations():
@app.route("/main/user")
def main_students_teachers():
    first_name = session['user'][3]
    return f"Welcome {first_name} !"

@app.route("/main/school_admin")
def main_school_admin():
    first_name = session['user'][3]
    return f"Welcome {first_name} !"

if __name__ == "__main__":
    app.run()
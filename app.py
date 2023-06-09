from flask import Flask, request, redirect, url_for, session, render_template, flash
import mysql.connector
import calendar
import subprocess

app = Flask(__name__)
app.secret_key = 'axamparos'  # Set a secret key for session encryption

connection = mysql.connector.connect(host='localhost', port='3306', database='library_system_final', user='root',
                                     password='Sporar9!')


@app.route("/")
def index():
    return '''
    <div class="container text-center">
        <h1>Welcome to ADOXOS</h1>
        <a href="/login" class="btn btn-primary">Login</a>
        <a href="/register" class="btn btn-primary">Register</a>
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
                database='library_system_final',
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
                user_status = user[11]
                if user_status == 'inactive':
                    flash('Your account has been deactivated.', 'danger')
                else:
                    if user_type in ["student", "teacher"]:
                        # Redirect students and teachers to the same page
                        session['user'] = user  # Store the user in the session
                        return redirect(url_for("main_users"))
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
               flash('Login failed', 'danger')
        except mysql.connector.Error as error:
            # Handle database connection error
            return f"Database Error: {error}"
        finally:
            # Close the cursor and database connection
            if 'cursor' in locals():
                cursor.close()
            if 'connection' in locals():
                connection.close()

    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    schools = []
    try:
        connection = mysql.connector.connect(
            host='localhost',
            port='3306',
            database='library_system_final',
            user='root',
            password='Sporar9!'
        )

        cursor = connection.cursor()
        query = "SELECT school_name from school"
        cursor.execute(query)
        fetched_schools = cursor.fetchall()
        schools = [school[0] for school in fetched_schools]  # Extract school names from fetched results
    except mysql.connector.Error as error:
        # Handle database connection error
        return f"Database Error: {error}"

    if request.method == "POST":
        # Retrieve form data
        username = request.form.get("username")
        password = request.form.get("password")
        first_name = request.form.get("first_name")
        last_name = request.form.get("last_name")
        email = request.form.get("email")
        school_name = request.form.get("school")
        date_of_birth = request.form.get("date_of_birth")
        user_type = request.form.get("registration_type")

        try:
            cursor = connection.cursor()

            # Get school_id for the selected school
            query = "SELECT school_id from school WHERE school_name = %s"
            values = (school_name,)
            cursor.execute(query, values)
            school_id = cursor.fetchone()[0]

            if user_type == "student":
                available_loans = 2
                available_reservations = 2
                query = "INSERT INTO school_user_registration (username, passwrd, first_name, last_name, email, school_id, date_of_birth, available_loans, available_reservations, user_type) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
                values = (username, password, first_name, last_name, email, school_id, date_of_birth, available_loans, available_reservations,user_type)
                cursor.execute(query, values)
            elif user_type == "teacher":
                available_loans = 1
                available_reservations = 1
                query = "INSERT INTO school_user_registration (username, passwrd, first_name, last_name, email, school_id, date_of_birth, available_loans, available_reservations, user_type) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
                values = (username, password, first_name, last_name, email, school_id, date_of_birth, available_loans, available_reservations, user_type)
                cursor.execute(query, values)
            elif user_type == "school_admin":
                available_loans = 1
                available_reservations = 1
                query = "INSERT INTO school_admin_registration (username, passwrd, first_name, last_name, email, school_id, date_of_birth, available_loans, available_reservations) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)"
                values = (username, password, first_name, last_name, email, school_id, date_of_birth, available_loans, available_reservations)
                cursor.execute(query, values)

            connection.commit()
            flash('Your registration form has been received', 'success')
            return redirect(url_for("login"))

        except mysql.connector.Error as error:
            # Handle database connection error
            return f"Database Error: {error}"
        finally:
            # Close the cursor and database connection
            if cursor:
                cursor.close()
            if connection:
                connection.close()

    return render_template("register.html", schools=schools)

@app.route("/main/admin", methods=["GET", "POST"])
def main_admin():
    first_name = session['user'][3]
    backup_file_path = r"C:\Users\ksofr\OneDrive\Υπολογιστής\backup.sql"
    if request.method == "POST":
        action = request.form.get("action")
        if action == "backup":
            try:
                # Use subprocess to run the mysqldump command
                subprocess.run(
                    [
                        "mysqldump",
                        "--user=root",
                        "--password=Sporar9!",
                        "--host=localhost",
                        "--port=3306",
                        "library_system_final",
                        f"> {backup_file_path}"
                    ],
                    shell=True
                )
                flash('Backup Successful.', 'success')
                return redirect(url_for("main_admin"))
            except subprocess.CalledProcessError as error:
                return f"Error during backup: {error}"

        elif action == "restore":
            try:
                cursor = connection.cursor()
                with open(backup_file_path, "r") as backup_file:
                    sql_statements = backup_file.read()
                cursor.execute(sql_statements)
                connection.commit()
                cursor.close()
                flash('Restore Successful.', 'success')
                return redirect(url_for("main_admin"))
            except mysql.connector.Error as error:
                return f"Database Error: {error}"

    return render_template("main_admin.html", first_name=first_name)


@app.route("/main/admin/query_3_1_1", methods=["GET", "POST"])
def query_3_1_1():
    if (request.method == "POST"):
        try:
            year = request.form.get('year')
            month = request.form.get('month')
            year = '' if year is None else year
            month = '' if month is None else month
            print(month)
            print(year)
            cursor = connection.cursor()
            query = """
                    SELECT a.school_id, a.school_name, COALESCE(COUNT(b.loan_ID), 0) AS loan_number
                    FROM school a
                    LEFT JOIN book_loan b ON a.school_id = b.school_id
                    AND YEAR(b.starting_date) like %s
                    AND MONTH(b.starting_date) like %s
                    GROUP BY a.school_id
                    ORDER BY loan_number DESC;
                    """
            cursor.execute(query, (f'{year}%', f'{month}%'))
            loans_by_school_year_month = cursor.fetchall()
            print(loans_by_school_year_month)
            connection.commit()
            cursor.close()
            return render_template("loans_by_school_year_month.html",
                                   loans_by_school_year_month=loans_by_school_year_month)  # μπορει γενικα να μπει και 2ο ορισμα
        # '%s%'
        except mysql.connector.Error as error:
            return f"Database Error: {error}"

    else:
        try:
            month_names = list(calendar.month_name)[1:]
            return render_template("choose_year_month.html", month_names=month_names)
        except mysql.connector.Error as error:
            return f"Database Error: {error}"


@app.route("/main/admin/query_3_1_2", methods=["GET", "POST"])
def query_3_1_2():
    if (request.method == "POST"):
        try:
            selected_value = request.form.get('category')
            temp = selected_value
            # return render_template("test.html", selected_value = selected_value)
            cursor = connection.cursor()
            query = """
                select distinct d.author_name,f.category_name 
                from book a
                inner join author_books c on a.book_ID = c.book_ID
                inner join author d on d.author_ID = c.author_ID
                inner join category_books e on a.book_ID = e.book_ID
                inner join category f on f.category_ID = e.category_ID
                where f.category_ID = %s;


                """
            values = (selected_value,)
            cursor.execute(query, values)
            authors_category = cursor.fetchall()

            query2 = """
                select a.user_id, a.first_name , a.last_name, count(*) as number_of_loans
                from users a use index (index_user_type)
                inner join book_loan b on a.user_id=b.user_id
                inner join book c on b.book_id = c.book_id
                inner join category_books d on d.book_id = b.book_id
                inner join category e on d.category_id = e.category_id
                where a.user_type = 'teacher'
                and e.category_ID = %s
                and b.starting_date >= date_sub(current_date(), interval 1 year)
                group by a.user_id, b.loan_id 
                order by number_of_loans desc;

            """

            values = (temp,)
            cursor.execute(query2, values)

            teachers = cursor.fetchall()

            connection.commit()
            cursor.close()
            return render_template("category_authors_teachers.html", authors_category=authors_category,
                                   teachers=teachers)  # μπορει γενικα να μπει και 2ο ορισμα

        except mysql.connector.Error as error:
            return f"Database Error: {error}"

    else:
        try:

            cursor = connection.cursor()
            query = """select category_ID,category_name from category order by category_ID asc;"""
            cursor.execute(query)
            category = cursor.fetchall()
            connection.commit()
            cursor.close()
            # return render_template("test.html",  category=category)
            return render_template("choose_category.html", category=category)
        except mysql.connector.Error as error:
            return f"Database Error: {error}"


@app.route("/main/admin/query_3_1_3", methods=["GET", "POST"])
def query_3_1_3():
    # Code for the "Loans from young teachers" query goes here
    try:
        cursor = connection.cursor()
        query = """
            select a.user_id,a.first_name, a.last_name, count(*) as loan_number
            from users a use index (index_user_type)
            inner join book_loan b on a.user_id = b.user_id 
            where a.user_type = 'teacher'
            and  (date_format(from_days(datediff(now(),a.date_of_birth)), '%Y')  + 0 ) < 40
            group by a.user_id,a.first_name, a.last_name
            order by loan_number desc;"""

        cursor.execute(query)
        teachers_under_fourty = cursor.fetchall()
        connection.commit()
        cursor.close()
        return render_template("teachers_under_fourty.html", teachers_under_fourty=teachers_under_fourty)


    except mysql.connector.Error as error:
        return f"Database Error: {error}"


@app.route("/main/admin/query_3_1_4", methods=["GET", "POST"])
def query_3_1_4():
    # Code for the "Authors without a lent book" query goes here
    try:
        cursor = connection.cursor()
        query = """
            select distinct a.author_ID, a.author_name 
            from author a 
            inner join author_books b on a.author_ID = b.author_ID
            inner join book c on b.book_ID = c.book_ID
            where c.book_ID not in (select book_id from book_loan)
            order by a.author_ID asc; 

        """
        cursor.execute(query)
        authors_no_loan = cursor.fetchall()
        connection.commit()
        cursor.close()
        return render_template("authors_no_loan.html", authors_no_loan=authors_no_loan)
    except mysql.connector.Error as error:
        return f"Database Error: {error}"

@app.route("/main/admin/query_3_1_5", methods=["GET", "POST"])
def query_3_1_5():
    # Code for the "School admin pairs with same # of loans made (20+ loans)" query goes here
    # Code for the "Authors without a lent book" query goes here
    if(request.method == "POST"):
            try:
                year = request.form.get('year')
                print(year)
    
                cursor = connection.cursor()
                query = """
                    select distinct a1.school_admin, a1.loan_count
                    from (
                        select a.school_admin, count(*) as loan_count
                        from school as a
                        inner join book_loan as b on a.school_id = b.school_id
                        where year(b.starting_date) = %s
                        group by a.school_admin
                        having loan_count > 20
                    ) as a1
                    inner join (
                        select c.school_admin, count(*) as loan_count
                        from school as c
                        inner join book_loan as d on c.school_id = d.school_id
                        where year(d.starting_date) = %s
                        group by c.school_admin
                        having loan_count > 20
                    ) as a2 on a1.loan_count = a2.loan_count;

                """
                values = (year,year,)
                cursor.execute(query,values)
                hyperactive_operators = cursor.fetchall()
                connection.commit()
                cursor.close()
                return render_template("hyperactive_operators.html", hyperactive_operators=hyperactive_operators)
            except mysql.connector.Error as error:
                return f"Database Error: {error}"
    else:
            try:
                
                return render_template("choose_year_for_20.html")
            except mysql.connector.Error as error:
                return f"Database Error: {error}"


@app.route("/main/admin/query_3_1_6", methods=["GET", "POST"])
def query_3_1_6():
    # Code for the "Most popular book category pairs" query goes here
    try:
        cursor = connection.cursor()
        query = """
                select distinct c1.category_name, c2.category_name, count(*) as loan_count
                from book_loan bl 
                join book b on bl.book_id = b.book_id
                join category_books cb1 on b.book_id = cb1.book_id
                join category_books cb2 on b.book_id = cb2.book_id
                join category c1  on cb1.category_id = c1.category_id
                join category c2  on cb2.category_id = c2.category_id
                where c1.category_name < c2.category_name /*distinct pairs*/
                group by c1.category_name, c2.category_name
                order by loan_count desc
                limit 3;

            """
        cursor.execute(query)
        top_three = cursor.fetchall()
        connection.commit()
        cursor.close()
        return render_template("top_three.html", top_three=top_three)
    except mysql.connector.Error as error:
        return f"Database Error: {error}"


@app.route("/main/admin/query_3_1_7", methods=["GET", "POST"])
def query_3_1_7():
    try:
        cursor = connection.cursor()
        query = """
            SELECT distinct a.author_name,  a.author_ID
            FROM author a
            INNER JOIN author_books b ON a.author_ID = b.author_ID
            WHERE (
            SELECT COUNT(*)
            FROM author_books b2
            WHERE b2.author_ID = b.author_ID
            )  <= (
            SELECT MAX(count)
            FROM (
            SELECT COUNT(*) AS count
            FROM author_books
            GROUP BY author_ID
            ) AS subquery
            ) - 5
            order by a.author_ID;


        """
        cursor.execute(query)
        inactive_authors = cursor.fetchall()
        connection.commit()
        cursor.close()
        return render_template("inactive_authors.html", inactive_authors=inactive_authors)
    except mysql.connector.Error as error:
        return f"Database Error: {error}"


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
                values = (
                school_name, postal_code, city_name, school_phone_number, school_email, school_principal, school_admin)
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
                    school_name, postal_code, city_name, school_phone_number, school_email, school_principal,
                    school_admin,
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
def accept_registration():
    if 'user' not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        action = request.form.get("action")
        if action == "delete":
            admin_reg_id = request.form.get("admin_reg_id")

            try:
                cursor = connection.cursor()
                query = "DELETE FROM school_admin_registration WHERE admin_reg_id = %s"
                values = (admin_reg_id,)
                cursor.execute(query, values)
                connection.commit()
                cursor.close()
                flash('Registration form deleted successfully.', 'success')
                return redirect(url_for("accept_registration"))
            except mysql.connector.Error as error:
                return f"Database Error: {error}"
        if action == "accept":
            admin_reg_id = request.form.get("admin_reg_id")
            username = request.form.get("username")
            passwrd = request.form.get("passwrd")
            first_name = request.form.get("first_name")
            last_name = request.form.get("last_name")
            email = request.form.get("email")
            school_id = request.form.get("school_id")
            date_of_birth = request.form.get("date_of_birth")
            available_loans = 1
            available_reservations = 1
            user_type = 'school admin'

            try:
                cursor = connection.cursor()
                query = "INSERT INTO users(username, passwrd, first_name, last_name, email, school_id, date_of_birth, available_loans, available_reservations, user_type) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                values = (username, passwrd, first_name, last_name, email, school_id, date_of_birth, available_loans,
                          available_reservations, user_type)
                cursor.execute(query, values)
                connection.commit()
                cursor.close()

                cursor = connection.cursor()
                query = "DELETE FROM school_admin_registration WHERE admin_reg_id = %s"
                values = (admin_reg_id,)
                cursor.execute(query, values)
                connection.commit()
                cursor.close()

                flash('Registration accepted and user created successfully.', 'success')
                return redirect(url_for('accept_registration'))
            except mysql.connector.Error as error:
                return f"Database Error: {error}"
    try:
        cursor = connection.cursor()
        query = "SELECT * FROM school_admin_registration"
        cursor.execute(query)
        registrations = cursor.fetchall()
        cursor.close()
        return render_template("admin_registrations.html", registrations=registrations)
    except mysql.connector.Error as error:
        return f"Database Error: {error}"


@app.route("/main/admin/queries", methods=["GET", "POST"])
def main_admin_queries():
    return 0


@app.route("/main/school_admin")
def main_school_admin():
    first_name = session['user'][3]
    school_id = session['user'][6]
    return render_template("main_school_admin.html", first_name=first_name, school_id=school_id)


@app.route("/main/school_admin/books", methods=["GET", "POST"])
def main_school_admin_books():
    if 'user' not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        action = request.form.get("action")

        if action == "insert":
            ISBN = request.form.get("ISBN")
            title = request.form.get("title")
            book_language = request.form.get("book_language")
            abstract = request.form.get("abstract")
            publisher = request.form.get("publisher")
            page_nr = request.form.get("page_nr")

            try:
                cursor = connection.cursor()
                query = "INSERT INTO book (ISBN, title, book_language, abstract, publisher, page_nr) VALUES (%s, %s, %s, %s, %s, %s)"
                values = (ISBN, title, book_language, abstract, publisher, page_nr)
                cursor.execute(query, values)
                connection.commit()
                cursor.close()
                flash('Book added successfully.', 'success')
                return redirect(url_for("main_school_admin_books"))
            except mysql.connector.Error as error:
                return f"Database Error: {error}"

        elif action == "delete":
            book_id = request.form.get("book_id")

            try:
                cursor = connection.cursor()
                query = "DELETE FROM book WHERE book_id = %s"
                values = (book_id,)
                cursor.execute(query, values)
                connection.commit()
                cursor.close()
                flash('Book deleted successfully.', 'success')
                return redirect(url_for("main_school_admin_books"))
            except mysql.connector.Error as error:
                return f"Database Error: {error}"

        elif action == "update":
            book_id = request.form.get("book_id")
            ISBN = request.form.get("ISBN")
            title = request.form.get("title")
            book_language = request.form.get("book_language")
            abstract = request.form.get("abstract")
            publisher = request.form.get("publisher")
            page_nr = request.form.get("page_nr")

            try:
                cursor = connection.cursor()
                query = "UPDATE book SET ISBN = %s, title = %s, book_language = %s, abstract = %s, publisher = %s, page_nr = %s WHERE book_id = %s"
                values = (ISBN, title, book_language, abstract, publisher, page_nr, book_id)
                cursor.execute(query, values)
                connection.commit()
                cursor.close()
                flash('Book updated successfully.', 'success')
                return redirect(url_for("main_school_admin_books"))
            except mysql.connector.Error as error:
                return f"Database Error: {error}"

    try:
        cursor = connection.cursor()
        query = "SELECT * FROM book"
        cursor.execute(query)
        books = cursor.fetchall()
        cursor.close()
        return render_template("main_school_admin_book.html", books=books)
    except mysql.connector.Error as error:
        return f"Database Error: {error}"


@app.route("/main/school_admin/users", methods=["GET", "POST"])
def main_school_admin_users():
    if 'user' not in session:
        return redirect(url_for("login"))

    user_id = session['user'][0]
    school_id = session['user'][6]

    if request.method == "POST":
        action = request.form.get("action")
        if action == "activate":
            user_id = request.form.get("user_id")
            try:
                cursor = connection.cursor()
                cursor.execute("UPDATE users SET user_status = 'active' WHERE user_id = %s", (user_id,))
                connection.commit()
                cursor.close()
                flash('User activated.', 'success')
                return redirect(url_for("main_school_admin_users"))
            except mysql.connector.Error as error:
                return f"Database Error: {error}"

        elif action == "deactivate":
            user_id = request.form.get("user_id")
            try:
                cursor = connection.cursor()
                cursor.execute("UPDATE users SET user_status = 'inactive' WHERE user_id = %s", (user_id,))
                connection.commit()
                cursor.close()
                flash('User deactivated.', 'success')
                return redirect(url_for("main_school_admin_users"))
            except mysql.connector.Error as error:
                return f"Database Error: {error}"
        elif action == "delete":
            user_id = request.form.get("user_id")
            try:
                cursor = connection.cursor()
                cursor.execute("DELETE FROM users WHERE user_id = %s", (user_id,))
                connection.commit()
                cursor.close()
                flash('User deleted.', 'success')
                return redirect(url_for("main_school_admin_users"))
            except mysql.connector.Error as error:
                return f"Database Error: {error}"
    try:
        cursor = connection.cursor()
        cursor.execute(
            "SELECT user_id, username, first_name, last_name, email, date_of_birth, user_type, book_loans, book_reservations, has_overdue_books FROM users WHERE school_id = %s AND user_status = 'active'",
            (school_id,))
        active_users = cursor.fetchall()

        cursor.execute(
            "SELECT user_id, username, first_name, last_name, email, date_of_birth, user_type, book_loans, book_reservations, has_overdue_books FROM users WHERE school_id = %s AND user_status = 'inactive'",
            (school_id,))
        inactive_users = cursor.fetchall()

        cursor.close()
        return render_template("main_school_admin_users.html", active_users=active_users, inactive_users=inactive_users)
    except mysql.connector.Error as error:
        return f"Database Error: {error}"

@app.route("/main/school_admin/registrations", methods=["GET", "POST"])
def accept_user_registration():
    if 'user' not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        action = request.form.get("action")
        if action == "delete":
            user_reg_id = request.form.get("user_reg_id")

            try:
                cursor = connection.cursor()
                query = "DELETE FROM school_user_registration WHERE user_reg_id = %s"
                values = (user_reg_id,)
                cursor.execute(query, values)
                connection.commit()
                cursor.close()
                flash('Registration form deleted successfully.', 'success')
                return redirect(url_for("accept_user_registration"))
            except mysql.connector.Error as error:
                return f"Database Error: {error}"
        if action == "accept":
            user_reg_id = request.form.get("user_reg_id")
            username = request.form.get("username")
            passwrd = request.form.get("passwrd")
            first_name = request.form.get("first_name")
            last_name = request.form.get("last_name")
            email = request.form.get("email")
            school_id = request.form.get("school_id")
            date_of_birth = request.form.get("date_of_birth")
            user_type = request.form.get("user_type")
            if user_type == "student":
                available_loans = 2
                available_reservations = 2
            if user_type == "teacher":
                available_loans = 1
                available_reservations = 1
            try:
                cursor = connection.cursor()
                query = "INSERT INTO users(username, passwrd, first_name, last_name, email, school_id, date_of_birth, available_loans, available_reservations, user_type) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                values = (username, passwrd, first_name, last_name, email, school_id, date_of_birth, available_loans,
                          available_reservations, user_type)
                cursor.execute(query, values)
                connection.commit()
                cursor.close()

                cursor = connection.cursor()
                query = "DELETE FROM school_user_registration WHERE user_reg_id = %s"
                values = (user_reg_id,)
                cursor.execute(query, values)
                connection.commit()
                cursor.close()

                flash('Registration accepted and user created successfully.', 'success')
                return redirect(url_for('accept_user_registration'))
            except mysql.connector.Error as error:
                return f"Database Error: {error}"
    school_id = session['user'][6]
    try:
        cursor = connection.cursor()
        query = "SELECT * FROM school_user_registration WHERE school_id = %s"
        values = (school_id,)
        cursor.execute(query, values)
        registrations = cursor.fetchall()
        cursor.close()
        return render_template("user_registrations.html", registrations=registrations)
    except mysql.connector.Error as error:
        return f"Database Error: {error}"

@app.route("/main/school_admin/library", methods=["GET", "POST"])
def main_school_admin_library():
    if 'user' not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        action = request.form.get("action")

        if action == "create":
            # book_id = request.form.get("book_id")
            number_of_copies = request.form.get("number_of_copies")
            total_copies = request.form.get("total_copies")

            ISBN = request.form.get("ISBN")

            title = request.form.get("title")

            language = request.form.get("language")
            language = None if language is None or language.strip() == "" else language

            abstract = request.form.get("abstract")
            abstract = None if abstract is None or abstract.strip() == "" else abstract

            publisher = request.form.get("publisher")
            publisher = None if publisher is None or publisher.strip() == "" else publisher

            page_nr = request.form.get("page-nr")
            page_nr = None if page_nr is None or page_nr.strip() == "" else int(page_nr)

            categories = request.form.get("categories")
            category_list = categories.split(",")
            # τα χωριζει με βαση το ονομα της κατηγοριας
            authors = request.form.get("authors")
            author_list = authors.split(",")

            keywords = request.form.get("keywords")
            keyword_list = keywords.split(",")

            try:
                cursor = connection.cursor()
                cursor.callproc('insert_book', [ISBN, title, language, abstract, publisher, page_nr])
                connection.commit()
                cursor.close()

                ####
                cursor = connection.cursor()
                # query="""
                #    select book_id from book where title = %s

                # """
                query = """
                    select book_id from book where ISBN = %s

                """

                values = (ISBN,)
                cursor.execute(query, values)
                book_fetch = cursor.fetchall()
                book_id = book_fetch[0][0]
                connection.commit()
                cursor.close()
                ###

                cursor = connection.cursor()
                cursor.execute("SELECT COUNT(*) FROM school_library WHERE school_id = %s AND book_id = %s",
                               (session['user'][6], book_id))
                # cursor.execute("SELECT COUNT(*) FROM school_library where school_id = %s and book_id= %s ")
                # values = (session['user'][6],book_id,)
                result = cursor.fetchone()
                count = result[0]
                connection.commit()
                cursor.close()

                if count == 0:
                    cursor = connection.cursor()
                    query = "INSERT INTO school_library (school_id, book_id, number_of_copies, total_copies) VALUES (%s, %s, %s, %s)"
                    values = (session['user'][6], book_id, number_of_copies, total_copies)
                    cursor.execute(query, values)
                    connection.commit()

                    for cat in category_list:
                        cursor.callproc('insert_category', [cat])
                        connection.commit()

                        query = """
                        select category_ID from category where  category_name = %s

                        """

                        values = (cat,)
                        cursor.execute(query, values)
                        category_fetch = cursor.fetchall()
                        category_id = category_fetch[0][0]
                        connection.commit()

                        query = "INSERT INTO category_books (category_ID ,book_id) VALUES (%s, %s)"
                        values = (category_id, book_id)
                        cursor.execute(query, values)
                        connection.commit()
                        # ΤΟ ΙΔΙΟ ΓΙΑ KEYWORDS,authors
                    # author_list = authors.split(",")            keyword_list = keywords.split(",")

                    for author in author_list:
                        cursor.callproc('insert_author', [author])
                        connection.commit()

                        query = """
                        select author_ID from author where  author_name = %s

                        """

                        values = (author,)
                        cursor.execute(query, values)
                        author_fetch = cursor.fetchall()
                        author_id = author_fetch[0][0]
                        connection.commit()

                        query = "INSERT INTO author_books (author_ID ,book_id) VALUES (%s, %s)"
                        values = (author_id, book_id)
                        cursor.execute(query, values)
                        connection.commit()

                    for keyword in keyword_list:
                        cursor.callproc('insert_keyword', [keyword])
                        connection.commit()

                        query = """
                        select keyword_ID from keyword where keyword_name = %s

                        """

                        values = (keyword,)
                        cursor.execute(query, values)
                        keyword_fetch = cursor.fetchall()
                        keyword_id = keyword_fetch[0][0]
                        connection.commit()

                        query = "INSERT INTO keyword_books (keyword_ID ,book_id) VALUES (%s, %s)"
                        values = (keyword_id, book_id)
                        cursor.execute(query, values)
                        connection.commit()

                    cursor.close()
                    flash('Book added to the school library.', 'success')
                    return redirect(url_for('main_school_admin_library'))



                else:
                    flash('Already existed!!.', 'success')  ##να αλλαξω το success
                    return redirect(url_for('main_school_admin_library'))

                """
                cursor = connection.cursor()
                query = "INSERT INTO school_library (school_id, book_id, number_of_copies, total_copies) VALUES (%s, %s, %s, %s)"
                values = (session['user'][6], book_id, number_of_copies, total_copies)
                cursor.execute(query, values)
                connection.commit()
                cursor.close()

                flash('Book added to the school library.', 'success')
                return redirect(url_for('main_school_admin_library'))"""
            except mysql.connector.Error as error:
                return f"Database Error: {error}"

        elif action == "delete":
            school_lib_id = request.form.get("school_lib_id")

            try:
                cursor = connection.cursor()
                query = "DELETE FROM school_library WHERE school_lib_id = %s"
                values = (school_lib_id,)
                cursor.execute(query, values)
                connection.commit()
                cursor.close()

                flash('Book deleted from the school library.', 'success')
                return redirect(url_for('main_school_admin_library'))
            except mysql.connector.Error as error:
                return f"Database Error: {error}"

        elif action == "update":
            school_lib_id = request.form.get("school_lib_id")
            number_of_copies = request.form.get("number_of_copies")
            total_copies = request.form.get("total_copies")

            try:
                cursor = connection.cursor()
                query = "UPDATE school_library SET number_of_copies = %s, total_copies = %s WHERE school_lib_id = %s"
                values = (number_of_copies, total_copies, school_lib_id)
                cursor.execute(query, values)
                connection.commit()
                cursor.close()

                flash('Book information updated.', 'success')
                return redirect(url_for('main_school_admin_library'))
            except mysql.connector.Error as error:
                return f"Database Error: {error}"

        elif action == "make_loan":
            # Make a loan from the reservation
            reservation_id = request.form.get("reservation_id")
            try:
                cursor = connection.cursor()
                cursor.execute("CALL lendbookfromreservation(%s)", (reservation_id,))
                connection.commit()
                cursor.close()

                flash('Loan created from reservation.', 'success')
                return redirect(url_for('main_school_admin_library'))
            except mysql.connector.Error as error:
                return f"Database Error: {error}"

        elif action == "reject":
            # Reject the reservation
            reservation_id = request.form.get("reservation_id")
            try:
                cursor = connection.cursor()
                cursor.execute("CALL delete_active_reservation(%s)", (reservation_id,))
                connection.commit()
                cursor.close()

                flash('Reservation rejected.', 'success')
                return redirect(url_for('main_school_admin_library'))
            except mysql.connector.Error as error:
                return f"Database Error: {error}"


        elif action == "end_loan":
            # End the loan
            loan_id = request.form.get("loan_id")
            try:
                cursor = connection.cursor()
                query = "UPDATE book_loan SET loan_status = 'completed' WHERE loan_ID = %s"
                cursor.execute(query, (loan_id,))
                connection.commit()
                cursor.close()
                flash('Loan completed.', 'success')
                return redirect(url_for('main_school_admin_library'))
            except mysql.connector.Error as error:
                return f"Database Error: {error}"

        elif action == 'add_loan':
            # Add a new loan
            book_id = request.form.get('book_id')
            user_id = request.form.get('user_id')
            cursor = connection.cursor()
            cursor.execute("SELECT book_loans FROM users WHERE user_id = %s", (user_id,))
            loans_before = cursor.fetchone()[0]
            loaned_book_ids = [book[0] for book in cursor.fetchall()]
            cursor.execute(
                "SELECT book_id FROM reservation WHERE user_id = %s",
                (user_id,))
            reserved_book_ids = [book[0] for book in cursor.fetchall()]

            if int(book_id) in loaned_book_ids:
                flash('You already have a loan for this book.', 'danger')
            try:

                if int(book_id) in loaned_book_ids:
                    flash('This user is lending the same book right now.', 'danger')
                elif int(book_id) in reserved_book_ids:
                    flash('You already have a reservation for this book. Please accept the reservation to activate the loan', 'danger')
                else:
                    cursor = connection.cursor()
                    cursor.callproc('physical_loan', [book_id, user_id])
                    cursor.execute("SELECT book_loans FROM users WHERE user_id = %s", (user_id,))
                    loans_after = cursor.fetchone()[0]
                    connection.commit()
                    cursor.close()
                    if loans_after != loans_before:
                        flash('Loan added.', 'success')
                        return redirect(url_for('main_school_admin_library'))
                    else:
                        flash('Cannot make this loan. Make sure this book is available and the user is eligible to loan another book', 'danger')
            except mysql.connector.Error as error:
                return f"Database Error: {error}"

        elif action == 'refresh':
            try:
                cursor = connection.cursor()
                cursor.callproc('check_overdue_reservations_and_loans')
                cursor.close()
                flash('Refresh completed.', 'success')
                return redirect(url_for('main_school_admin_library'))

            except mysql.connector.Error as error:
                return f"Database Error: {error}"

    # Retrieve the school ID of the logged-in admin
    school_id = session['user'][6]

    try:
        cursor = connection.cursor()
        cursor.execute(
            "SELECT sl.school_lib_id, sl.school_id, sl.book_id, sl.number_of_copies, sl.number_of_reservations, sl.total_copies, b.title, b.ISBN "
            "FROM school_library AS sl "
            "JOIN book AS b ON sl.book_id = b.book_id "
            "WHERE sl.school_id = %s", (session["user"][6],))
        books = cursor.fetchall()

        # Fetch active reservations for the school
        cursor.execute(
            "SELECT r.reservation_ID, r.book_id, r.user_id, r.reservation_date, r.end_of_reservation_date, b.title, u.first_name, u.last_name "
            "FROM reservation AS r "
            "JOIN school_library AS sl ON r.school_id = sl.school_id AND r.book_id = sl.book_id "
            "JOIN users AS u ON r.user_id = u.user_id "
            "JOIN book AS b ON r.book_id = b.book_id "
            "WHERE r.reservation_status = 'active' AND r.school_id = %s", (session["user"][6],))
        reservations = cursor.fetchall()

        # Fetch active loans for the school
        cursor.execute(
            "SELECT bl.loan_ID, sl.book_id, bl.user_id, bl.starting_date, bl.end_date, b.title, u.first_name, u.last_name "
            "FROM book_loan AS bl "
            "JOIN school_library AS sl ON bl.school_id = sl.school_id AND bl.book_id = sl.book_id "
            "JOIN users AS u ON bl.user_id = u.user_id "
            "JOIN book AS b ON bl.book_id = b.book_id "
            "WHERE bl.loan_status = 'in_progress' AND bl.school_id = %s", (session["user"][6],))
        loans = cursor.fetchall()

        # Fetch overdue loans for the school
        cursor.execute(
            "SELECT bl.loan_ID, sl.book_id, bl.user_id, bl.starting_date, bl.end_date, b.title, u.first_name, u.last_name "
            "FROM book_loan AS bl "
            "JOIN school_library AS sl ON bl.school_id = sl.school_id AND bl.book_id = sl.book_id "
            "JOIN users AS u ON bl.user_id = u.user_id "
            "JOIN book AS b ON bl.book_id = b.book_id "
            "WHERE bl.loan_status = 'overdue' AND bl.school_id = %s", (session["user"][6],))
        overdue_loans = cursor.fetchall()
        cursor.close()
        return render_template("main_school_admin_library.html", books=books, reservations=reservations, loans=loans,
                               overdue_loans=overdue_loans)
    except mysql.connector.Error as error:
        return f"Database Error: {error}"


@app.route("/main/school_admin/reviews", methods=["GET", "POST"])
def main_school_admin_reviews():
    if 'user' not in session:
        return redirect(url_for("login"))

    user_id = session['user'][0]
    school_id = session['user'][6]

    if request.method == "POST":
        action = request.form.get("action")
        if action == "verify":
            review_id = request.form.get("review_id")
            try:
                cursor = connection.cursor()
                cursor.execute("UPDATE book_review SET verification = 'verified' WHERE review_id = %s", (review_id,))
                connection.commit()
                cursor.close()
                flash('Review verified.', 'success')
                return redirect(url_for("main_school_admin_reviews"))
            except mysql.connector.Error as error:
                return f"Database Error: {error}"

    try:
        cursor = connection.cursor()
        cursor.execute("""
            SELECT br.review_id, br.book_id, b.title, br.user_id, u.first_name, u.last_name, br.loan_ID, br.rating, br.review, br.verification
            FROM book_review br
            JOIN users u ON br.user_id = u.user_id
            JOIN book b ON br.book_id = b.book_id
            JOIN category_books cb ON b.book_id = cb.book_id
            JOIN category c ON cb.category_ID = c.category_ID
            WHERE u.school_id = %s AND br.verification = 'not_verified'
            UNION
            SELECT br.review_id, br.book_id, b.title, br.user_id, u.first_name, u.last_name, br.loan_ID, br.rating, br.review, br.verification
            FROM book_review br
            JOIN users u ON br.user_id = u.user_id
            JOIN book b ON br.book_id = b.book_id
            JOIN category_books cb ON b.book_id = cb.book_id
            JOIN category c ON cb.category_ID = c.category_ID
            WHERE u.school_id = %s AND br.verification = 'verified'
        """, (school_id, school_id))
        reviews = cursor.fetchall()

        cursor.execute("""
            SELECT c.category_name, AVG(br.rating)
            FROM book_review br
            JOIN book b ON br.book_id = b.book_id
            JOIN category_books cb ON b.book_id = cb.book_id
            JOIN category c ON cb.category_ID = c.category_ID
            WHERE br.verification = 'verified'
            GROUP BY c.category_name
        """)
        category_averages = cursor.fetchall()

        cursor.execute("""
            SELECT u.user_id, u.first_name, u.last_name, AVG(br.rating)
            FROM book_review br
            JOIN users u ON br.user_id = u.user_id
            WHERE br.verification = 'verified'
            GROUP BY u.user_id, u.first_name, u.last_name
        """)
        user_averages = cursor.fetchall()

        cursor.close()
        return render_template("main_school_admin_reviews.html", reviews=reviews, category_averages=category_averages, user_averages=user_averages)
    except mysql.connector.Error as error:
        return f"Database Error: {error}"


@app.route("/main/school_admin/queries", methods=["GET", "POST"])
def main_school_admin_queries():
        print(session)
        school_id = session['user'][6]
        print(school_id)

        if(request.method == "POST"):
            try:
                category = request.form.get("category") #το id
                category = "" if category is None or category.strip() == "" else category

                

                author = request.form.get("author")  #το id
                author = "" if author is None or author.strip() == "" else author

                title = request.form.get("title")   #το title
                title = "" if title is None or title.strip() == "" else title
                
                nr_copies = request.form.get("nr_copies")   #το title
                nr_copies = 0 if nr_copies is None or nr_copies.strip() == "" else nr_copies

                print(category)
                print(author)
                print(title)
                print(nr_copies)

                cursor = connection.cursor()
                # Get the books in the user's school library
                #NA ELEGXW GIA DISTINCT B* 
                query="""
                    SELECT DISTINCT sl.book_id, b.title, authors.author_names, sl.number_of_copies
                    FROM school_library AS sl
                    INNER JOIN book b ON sl.book_id = b.book_id
                    INNER JOIN category_books c ON c.book_id = sl.book_id
                    INNER JOIN (
                        SELECT d.book_id, GROUP_CONCAT(e.author_name SEPARATOR ', ') AS author_names
                        FROM author_books d
                        INNER JOIN author e use index (index_author_name) ON e.author_ID = d.author_ID
                        GROUP BY d.book_id
                    ) AS authors ON authors.book_id = sl.book_id
                    WHERE c.category_ID LIKE %s
                    AND authors.author_names LIKE %s
                    AND b.title LIKE %s
                    AND sl.number_of_copies >= %s
                    AND sl.school_id = %s

                    """
                cursor.execute(query, (f'{category}%', f'%{author}%', f'{title}%',nr_copies, school_id))
                print(f'%{author}%')
                books_filtered_admin = cursor.fetchall()
                print(books_filtered_admin)
                #μπορω να κανω redirect με 

                connection.commit()
                cursor.close()
                return render_template("books_filtered_admin.html", books_filtered_admin = books_filtered_admin )
            except mysql.connector.Error as error:
                return f"Database Error: {error}"
            
            #εδω το if method= Post + to ;θερυ που θα καθορισει τα books
        else:
            try:
                school_id = session['user'][6]
                cursor = connection.cursor()
                    # Get the books in the user's school library
                cursor.execute(
                        "select distinct f.category_ID,f.category_name  "
                        "from school_library a "
                        "inner join category_books e on a.book_ID = e.book_ID "
                        "inner join category f on f.category_ID = e.category_ID "
                        "where a.school_id = %s",
                        (school_id,))
                categories = cursor.fetchall()

                cursor.execute(
                        "select distinct d.author_ID, d.author_name "
                        "from school_library a "
                        "inner join author_books c on a.book_ID = c.book_ID "
                        "inner join author d on d.author_ID = c.author_ID "
                        "where a.school_id = %s",
                        (school_id,))
                authors = cursor.fetchall()

                cursor.close()
                try:
                    return render_template("filter_by_admin.html", categories = categories, authors = authors )
                except mysql.connector.Error as error:
                    return f"Database Error: {error}"
            except mysql.connector.Error as error:
                return f"Database Error: {error}"


@app.route("/main/users")
def main_users():
    user_id = session['user'][0]
    first_name = session['user'][3]
    school_id = session['user'][6]
    user_type = session['user'][10]
    return render_template("main_users.html", user_id=user_id, first_name=first_name, school_id=school_id,
                           user_type=user_type)


@app.route("/main/users/library", methods=["GET", "POST"])
def main_users_library():
    if 'user' not in session:
        return redirect(url_for("login"))

    user_id = session['user'][0]
    school_id = session['user'][6]

    if request.method == "POST":
        action = request.form.get("action")
        if action == "Cancel Reservation":
            reservation_id = request.form.get("reservation_id")
            try:
                cursor = connection.cursor()
                cursor.execute("CALL delete_active_reservation(%s)", (reservation_id,))
                connection.commit()
                cursor.close()

                flash('Reservation cancelled.', 'success')
                return redirect(url_for('main_users_library'))
            except mysql.connector.Error as error:
                return f"Database Error: {error}"

        if action == "Make Reservation":
            book_id = request.form.get("book_id")

            try:
                cursor = connection.cursor()
                cursor.execute("SELECT book_reservations FROM users WHERE user_id = %s", (user_id,))
                reservations_before = cursor.fetchone()[0]
                cursor.execute("SELECT book_id FROM reservation WHERE user_id = %s", (user_id,))
                reservations = [reservation[0] for reservation in cursor.fetchall()]
                cursor.execute(
                    "SELECT book_id FROM book_loan WHERE user_id = %s AND loan_status IN ('overdue', 'in_progress')",
                    (user_id,))
                loaned_book_ids = [book[0] for book in cursor.fetchall()]

                if int(book_id) in loaned_book_ids:
                    flash('You already have a loan for this book.', 'danger')
                elif int(book_id) in reservations:
                    flash('You have already reserved this book.', 'danger')
                else:
                    cursor.callproc("reserve_book", (book_id, user_id))
                    cursor.execute("SELECT book_reservations FROM users WHERE user_id = %s", (user_id,))
                    reservations_after = cursor.fetchone()[0]
                    if reservations_after > reservations_before:
                        connection.commit()
                        flash('Book reserved successfully.', 'success')
                    else:
                        flash('No more reservations allowed.', 'danger')

                cursor.close()
                return redirect(url_for("main_users_library"))

            except mysql.connector.Error as error:
                return f"Database Error: {error}"

    try:
        cursor = connection.cursor()
        # Get the books in the user's school library
        cursor.execute(
            "SELECT sl.school_lib_id, sl.book_id, sl.number_of_copies, b.title "
            "FROM school_library AS sl "
            "JOIN book AS b ON sl.book_id = b.book_id "
            "WHERE sl.school_id = %s",
            (school_id,))
        books = cursor.fetchall()

        # Get the user's loans
        cursor.execute(
            "SELECT l.loan_ID, l.book_id, l.starting_date, l.end_date, l.loan_status, b.title "
            "FROM book_loan AS l "
            "JOIN book AS b ON l.book_id = b.book_id "
            "WHERE l.user_id = %s",
            (user_id,))
        loans = cursor.fetchall()

        # Get the user's reservations
        cursor.execute(
            "SELECT r.reservation_ID, r.book_id, b.title, r.reservation_status "
            "FROM reservation AS r "
            "JOIN book AS b ON r.book_id = b.book_id "
            "WHERE r.user_id = %s",
            (user_id,))
        reservations = cursor.fetchall()

        cursor.close()
        return render_template("main_users_library.html", books=books, loans=loans, reservations=reservations)
    except mysql.connector.Error as error:
        return f"Database Error: {error}"


@app.route("/main/users/library/reviews", methods=["GET", "POST"])
def main_users_library_reviews():
    if request.method == "POST":
        book_id = request.form.get("book_id")
        loan_id = request.form.get("loan_id")
        rating = request.form.get("rating")
        review = request.form.get("review")
        user_id = session['user'][0]
        try:
            cursor = connection.cursor()
            cursor.execute("SELECT loan_id FROM book_review WHERE user_id = %s AND book_id = %s", (user_id, book_id))
            same_loan = [loan[0] for loan in cursor.fetchall()]
            if int(loan_id) in same_loan:
                flash('You have already submitted a review for this loan.', 'danger')
            else:
                query = """
                    INSERT INTO book_review (book_id, user_id, loan_id, rating, review)
                    VALUES (%s, %s, %s, %s, %s)
                    """
                values = (book_id, user_id, loan_id, rating, review)
                cursor.execute(query, values)
                connection.commit()
                flash('Review submitted.', 'success')

            return redirect(url_for("main_users_library"))

        except mysql.connector.Error as error:
            # Handle database connection error
            return f"Database Error: {error}"

    return render_template("main_users_library_reviews.html")


@app.route("/main/users/personal_info", methods=["GET", "POST"])
def main_users_personal_info():
    if "user" not in session:
        return redirect(url_for("login"))

    user_id = session["user"][0]
    user_type = session["user"][10]

    if request.method == "POST":
        # Handle form submission
        username = request.form.get("username")
        password = request.form.get("password")
        first_name = request.form.get("first_name")
        last_name = request.form.get("last_name")
        email = request.form.get("email")
        if user_type not in ["teacher", "admin", "school admin"]:
            try:
                cursor = connection.cursor()
                cursor.execute(
                    "UPDATE users SET passwrd = %s WHERE user_id = %s",
                    (password, user_id)
                )
                connection.commit()
                cursor.close()

                flash("Password updated.", "success")
                return redirect(url_for("main_users_personal_info"))
            except mysql.connector.Error as error:
                return f"Database Error: {error}"

            return render_template("main_users_personal_info.html", user_info=user_info)
        else:
            # Update the user's personal information
            try:
                cursor = connection.cursor()
                cursor.execute(
                    "UPDATE users SET username = %s, passwrd = %s, first_name = %s, last_name = %s, email = %s WHERE user_id = %s",
                    (username, password, first_name, last_name, email, user_id)
                )
                connection.commit()
                cursor.close()

                flash("Personal information updated.", "success")
                return redirect(url_for("main_users_personal_info"))
            except mysql.connector.Error as error:
                return f"Database Error: {error}"

    try:
        cursor = connection.cursor()
        cursor.execute(
            "SELECT * FROM users WHERE user_id = %s",
            (user_id,)
        )
        user_info = cursor.fetchone()
        cursor.close()

        return render_template("main_users_personal_info.html", user_info=user_info)
    except mysql.connector.Error as error:
        return f"Database Error: {error}"


@app.route("/main/users/queries", methods=["GET", "POST"])
def main_users_queries():
    user_id = session['user'][0]
    school_id = session['user'][6]
    print(school_id)
    if(request.method == "POST"):
        try:
            category = request.form.get("category") #το id
            category = "" if category is None or category.strip() == "" else category

            

            author = request.form.get("author")  #το id
            author = "" if author is None or author.strip() == "" else author

            title = request.form.get("title")   #το title
            title = "" if title is None or title.strip() == "" else title
            
            print(category)
            print(author)
            print(title)

            cursor = connection.cursor()
            # Get the books in the user's school library
            #NA ELEGXW GIA DISTINCT B* 
            query="""
                select distinct sl.school_lib_id, sl.book_id, sl.number_of_copies, b.title
                from school_library as sl
                inner join book b on sl.book_id = b.book_id
                inner join category_books c on c.book_id = sl.book_id
                inner join author_books d on d.book_id = sl.book_id
                where c.category_ID like %s
                and d.author_ID like %s
                and b.title like %s
                and sl.school_id = %s
                """
            cursor.execute(query, (f'{category}%', f'{author}%', f'{title}%', school_id))
            books = cursor.fetchall()
            print(books)
            

            # Get the user's loans
            cursor.execute(
                "SELECT l.loan_ID, l.book_id, l.starting_date, l.end_date, l.loan_status, b.title "
                "FROM book_loan AS l "
                "JOIN book AS b ON l.book_id = b.book_id "
                "WHERE l.user_id = %s",
                (user_id,))
            loans = cursor.fetchall()

            # Get the user's reservations
            cursor.execute(
                "SELECT r.reservation_ID, r.book_id, b.title, r.reservation_status "
                "FROM reservation AS r "
                "JOIN book AS b ON r.book_id = b.book_id "
                "WHERE r.user_id = %s",
                (user_id,))
            reservations = cursor.fetchall()

            #μπορω να κανω redirect με 

            cursor.close()
            return render_template("main_users_library.html", books=books, loans=loans, reservations=reservations)
        except mysql.connector.Error as error:
            return f"Database Error: {error}"
        
        #εδω το if method= Post + to ;θερυ που θα καθορισει τα books
    else:
        try:
            
            cursor = connection.cursor()
                # Get the books in the user's school library
            cursor.execute(
                    "select distinct f.category_ID,f.category_name  "
                    "from school_library a "
                    "inner join category_books e on a.book_ID = e.book_ID "
                    "inner join category f on f.category_ID = e.category_ID "
                    "where a.school_id = %s",
                    (school_id,))
            categories = cursor.fetchall()
            print(categories)
            cursor.execute(
                    "select distinct d.author_ID, d.author_name "
                    "from school_library a "
                    "inner join author_books c on a.book_ID = c.book_ID "
                    "inner join author d on d.author_ID = c.author_ID "
                    "where a.school_id = %s",
                    (school_id,))
            authors = cursor.fetchall()

            cursor.close()
            return render_template("filter_by.html", categories = categories, authors=authors )
        except mysql.connector.Error as error:
            return f"Database Error: {error}"



if __name__ == "__main__":
    app.run()

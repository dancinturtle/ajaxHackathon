from flask import Flask, render_template, request, redirect, session, flash
from mysqlconnection import connectToMySQL as c
import math
app = Flask(__name__)
app.secret_key = "unicornswithpants"

@app.route('/')
def index():
    if 'userid' not in session:
        session['userid'] = None
    return render_template('index.html')

@app.route("/register", methods=['POST'])
def register():
    session.clear()
    errors = False
    for key in request.form:
        flash(request.form[key], key)
        if len(request.form[key]) < 1:
            if errors == False:
                flash("Please complete the form!", "register")
            errors = True
    if errors:
        return redirect('/')
    query = "SELECT * FROM users WHERE username = %(name)s;"
    data = {"name" : request.form['username']}
    mysql = c('ajaxWall')
    results = mysql.query_db(query, data)
    if results:
        flash("This username is already taken!", "register")
    else:
        query2 = "INSERT INTO users (username, first_name, last_name, created_at, updated_at) VALUES (%(username)s, %(first_name)s, %(last_name)s, NOW(), NOW());"
        mysql = c('ajaxWall')
        newuserid = mysql.query_db(query2, request.form)
        if newuserid:
            session['username'] = request.form['username']
            session['userid'] = newuserid
            flash("You have been successfully registered!", "register")
            return redirect('/wall')
        else:
            flash("We're sorry, we could not register you at this time", "register")
    return redirect('/')

@app.route('/login', methods=['POST'])
def login():
    session.clear()
    query = "SELECT * FROM users WHERE username = %(name)s;"
    data = {"name" : request.form['username']}
    mysql = c('ajaxWall')
    results = mysql.query_db(query, data)
    if results:
        session['userid'] = results[0]['id']
        session['username'] = results[0]['username']
        return redirect('/wall')
    flash("We're sorry, we could not log you in", "login")
    return redirect("/")

@app.route('/wall')
@app.route('/wall/<page>')
def wall(page=1):
    if check_login():
        perpage = 5
        offset = (int(page) -1) * perpage
        countquery = "SELECT COUNT(*) as count from messages;"
        mysql = c('ajaxWall')
        count = mysql.query_db(countquery)[0]['count']
        pages_needed = math.ceil(count/perpage)
        query = "SELECT messages.id, messages.message, messages.created_at, users.username from messages JOIN users on messages.user_id = users.id ORDER BY messages.created_at DESC LIMIT %(offset)s, %(perpage)s;"
        data = {
            "offset" : offset,
            "perpage" : perpage
        }
        mysql = c('ajaxWall')
        results = mysql.query_db(query, data)
        query2 = "SELECT comments.comment, messages.id as msgid, users.username, comments.created_at FROM comments JOIN messages on comments.message_id = messages. id JOIN users ON comments.user_id = users.id ORDER BY comments.created_at DESC;"
        mysql = c('ajaxWall')
        results2 = mysql.query_db(query2)
        return render_template("wall.html", data = results, comments = results2, pages = pages_needed)
    return redirect('/')

@app.route("/messages", methods=["POST"])
def messages():
    if check_login():
        if len(request.form['message']) < 3:
            flash("All messages must contain at least 3 characters", "nosave")
            flash(request.form['message'], "usermsg")
            return redirect('/wall')
        
        query = "INSERT INTO messages (message, user_id, created_at, updated_at) VALUES (%(content)s, %(id)s, NOW(), NOW());"
        data = {
            "content" : request.form['message'],
            "id" : session['userid']
        }
        mysql = c('ajaxWall')
        newid = mysql.query_db(query, data)
        if newid:
            flash("Message saved", "save")
        else:
            flash("We're sorry, we could not save your message at this time", "nosave")
            flash(request.form['message'], "usermsg")
        return redirect('/wall')
    return redirect('/')

@app.route("/comments", methods=['POST'])
def comments():
    if check_login():
        if len(request.form['comment']) < 3 or len(request.form['comment']) > 45:
            flash("All comments must contain between 3 and 45 characters", "comment")
            return redirect('/wall')
        query = "INSERT INTO comments (comment, created_at, updated_at, message_id, user_id) VALUES (%(content)s, NOW(), NOW(), %(msgid)s, %(userid)s);"
        data = {
            "content" : request.form['comment'],
            "msgid" : request.form['msgid'],
            "userid" : session['userid']
        }
        mysql = c('ajaxWall')
        newid = mysql.query_db(query, data)
        if not newid:
            flash("We're sorry, we could not save your comment at this time", "comment")
        return redirect('/wall')
    return redirect('/')

@app.route('/users_noajax')
def users_noajax():
    query = "SELECT * FROM users WHERE first_name LIKE %%(name)s or last_name LIKE %%(name)s;"
    data = {
        'name' : request.args.get('name') + "%"
    }
    mysql = c('ajaxWall')
    results = mysql.query_db(query, data)
    return render_template('index.html', users = results)

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

@app.route("/username", methods=['POST'])
def username():
    query = "SELECT * FROM users WHERE username = %(name)s;"
    data = {"name":request.form['username']}
    mysql = c('ajaxWall')
    result = mysql.query_db(query, data)
    if result:
        return render_template('username.html', passed = False)
    return render_template("username.html", passed = True)

def check_login():
    if 'userid' not in session or session['userid'] == None:
        flash("You must be logged in to enter the website", "permission")
        return False
    return True


if __name__ == "__main__":
    app.run(debug = True)

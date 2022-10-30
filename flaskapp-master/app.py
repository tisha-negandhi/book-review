from flask import Flask, render_template, request, redirect, flash, session,url_for
from flask_session import Session
from flask_mysqldb import MySQL
from datetime import date
import yaml
from functools import wraps
import random
import os
import alert
import base64
from PIL import Image
import io 
  


app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)



# Configure db
db = yaml.full_load(open('db.yaml'))
app.config['MYSQL_HOST'] = db['mysql_host']
app.config['MYSQL_USER'] = db['mysql_user']
app.config['MYSQL_PASSWORD'] = db['mysql_password']
app.config['MYSQL_DB'] = db['mysql_db']

mysql = MySQL(app)
from models import Table

def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session and session['logged_in']:
            return f(*args, **kwargs)
        else:
            flash("You need to login first","danger")
            return redirect('/login')
    return wrap

def log_in_user(email):
        users = Table("users", "name", "phone", "email", "password")
        user = users.getone("email", email)
        session['logged_in'] = True
        session['id'] = user[0]
        session['name'] = user[1]
        session['email'] = user[2]
        
def log_in_user1(email):
        users = Table("admin", "name", "phone", "email", "password")
        user = users.getone1("email", email)
        session['logged_in'] = True
        session['id'] = user[0]
        session['name'] = user[1]
        session['email'] = user[2]
        
def searchb(book):
    cur = mysql.connection.cursor()
    resultValue = cur.execute("SELECT * FROM %s WHERE %s = \"%s\"" %("book", "title", book))
    if resultValue > 0:
        userDetails1 = cur.fetchall()
        return userDetails1

        
    
        
@app.route('/',methods=['GET', 'POST'])
def index():
    cur = mysql.connection.cursor()
    resultValue = cur.execute("SELECT title,author,cover,rating,book_id FROM book")
    if resultValue > 0:
        userDetails = cur.fetchall()
    resultValue1 = cur.execute("SELECT name,feedback,date_of_feedback FROM feedback")
    if resultValue1 > 0:
        userDetails1 = cur.fetchall()
    if request.method == 'POST':
        if request.form["section"] == "search":
            userDetails2 = request.form
            book=userDetails2["searchbook"]
            return redirect(url_for('search', name=book)) 
        else:
            userDetails = request.form
            book_id = userDetails['section']
            return redirect(url_for('viewmore', bookid=book_id))
            
    # if request.method == 'GET':
    #         like=request.form
    #         likes=like.get("like")
    #         users = Table("book", "title", "author", "rating", "likes_count","price","year","genre","summary")
    #         users.update(likes)
    #         return redirect('/') 
    return render_template('index.html',context=userDetails,context1=userDetails1)
    

    
@app.route('/register', methods=['GET', 'POST'])
def register():
    users = Table("users", "name", "phone", "email", "password")
    users.logout()
    if request.method == 'POST':
        userDetails = request.form
        name = userDetails['name']
        phone = userDetails['phone']
        email = userDetails['email']
        password = userDetails['password']
        users.insert(name,phone,email,password)
        log_in_user(email)
        flash("Registration successful", "success")
        return redirect('/login')
    
    return render_template('register.html')

@app.route("/login", methods = ['GET', 'POST'])
def login():
    users = Table("users", "name", "phone", "email", "password")
    users.logout()
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if email=="tishanegandhi27@gmail.com":
            users1=Table("admin", "name", "phone", "email", "password")
            user=users1.getone1("email",email)
            log_in_user1(email)
            return redirect('/admin')
        else:
            user = users.getone("email", email)
            if user is None:
                flash("Invalid Email",'danger')
                return render_template('login.html')
            else:
                og_pass=user[3]
                if password!=og_pass:
                    flash("Password invalid", 'danger')
                    return render_template('login.html')
                else:
                    log_in_user(email)
                    return redirect('/')           

    return render_template('login.html')

@app.route("/wishlist",methods=['GET', 'POST'])
@login_required
def wishlist():
    ud=[]
    id=session['id']
    cur = mysql.connection.cursor()
    resultValue = cur.execute("SELECT * FROM %s WHERE %s = \"%s\"" %("wishlist", "user_id", id))
    if resultValue > 0:
        userDetails = cur.fetchall()
        for user in userDetails:
            book_id=user[2]
            cur = mysql.connection.cursor()
            resultValue1 = cur.execute("SELECT title,author,rating,cover,book_id FROM %s WHERE %s = \"%s\"" %("book", "book_id", book_id))
            if resultValue1 > 0:
                userDetails1 = cur.fetchall()
                ud.extend(userDetails1)
    if request.method == 'POST':
        userDetails2 = request.form
        book=userDetails2["searchbook"]
        return redirect(url_for('search', name=book))        
    return render_template('wishlist.html',context=ud)

@app.route("/contact",methods=['GET', 'POST'])
@login_required
def contact():
    
    if request.method == 'POST':
        if request.form["section_name"] == "Send":
            userDetails = request.form
            name = userDetails['name']
            subject = userDetails['drop']
            email = userDetails['email']
            message = userDetails['message']
            if subject=="Query":
                users = Table("queries", "name", "email", "query", "date_of_query")
                users.insert(name,email,message,date.today())
                flash("Query submitted","success")
                return redirect('/contact') 
            else:
                users = Table("feedback", "name", "email", "feedback", "date_of_feedback")
                users.insert(name,email,message,date.today())
                flash("Feedback submitted","success")
                return redirect('/contact') 
        if request.form["section_name"] == "book_search":
            userDetails2 = request.form
            book=userDetails2["searchbook"]
            return redirect(url_for('search', name=book))
            
    return render_template('contactus.html')

@app.route("/search",methods=['GET', 'POST'])
@login_required
def search():
    book = request.args.get('name')
    booksearch=searchb(book)
    cur = mysql.connection.cursor()
    resultValue = cur.execute("SELECT title,author,cover,rating,book_id FROM book")
    if resultValue > 0:
        userDetails = cur.fetchall()
    if request.method == 'POST':
        if request.form["section"] == "search":
            userDetails2 = request.form
            book=userDetails2["searchbook"]
            return redirect(url_for('search', name=book))
        else:
            userDetails = request.form
            book_id = userDetails['section']
            return redirect(url_for('viewmore', bookid=book_id))
    return render_template("search.html",book=booksearch,book1=book,context=userDetails)

@app.route("/about",methods=['GET', 'POST'])
@login_required
def about():
    if request.method == 'POST':
        userDetails2 = request.form
        book=userDetails2["searchbook"]
        return redirect(url_for('search', name=book))
    return render_template('aboutus.html')

@app.route("/admin",methods=['GET', 'POST'])
@login_required
def admin():
    cur = mysql.connection.cursor()
    resultValue = cur.execute("SELECT book_id,title,author FROM book")
    if resultValue > 0:
        userDetails = cur.fetchall()
        
    if request.method == 'POST':
        if request.form["section"] == "Add now":
            userDetails = request.form
            title = userDetails['title']
            author = userDetails['author']
            rating = userDetails['rating']
            likes = userDetails['likes']
            price = userDetails['price']
            year = userDetails['year']
            genre = userDetails['genre']
            summary = userDetails['summary']
            users = Table("book", "title", "author", "rating", "likes_count","price","year","genre","summary")
            users.insert(title,author,rating,likes,price,year,genre,summary)
            return redirect('/admin') 
        else:
            userDetails = request.form
            book_id = userDetails['section']
            print(book_id)
            users = Table("book", "title", "author", "rating", "likes_count","price","year","genre","summary")
            users.delete(book_id)
            return redirect('/admin') 
    return render_template('adminhome.html',context=userDetails)

@app.route('/viewmore' ,methods=['GET', 'POST'])
@login_required
def viewmore():
    book_id = request.args.get('bookid')
    cur = mysql.connection.cursor()
    resultValue = cur.execute("SELECT title,author,summary,cover,rating,book_id FROM %s WHERE %s = \"%s\"" %("book", "book_id", book_id))
    if resultValue > 0:
        bookdetails = cur.fetchall()
        cur = mysql.connection.cursor()
        resultValue = cur.execute("SELECT name,review,likes,review_id FROM %s WHERE %s = \"%s\"" %("book_reviews", "book_id", book_id))
        if resultValue > 0:
            reviewdetails = cur.fetchall()
    if request.method == 'POST':
        if request.form["section"] == "search":
            userDetails2 = request.form
            book=userDetails2["searchbook"]
            return redirect(url_for('search', name=book)) 
        else: 
            userDetails4 = request.form
            review=userDetails4["review"]
            book_id=userDetails4["section"]
            users = Table("book_reviews", "book_id", "review", "likes", "name")
            users.insert(book_id,review,0,session['name'])
            return redirect(url_for('viewmore', bookid=book_id))
    return render_template('viewmore.html',context=bookdetails,context1=reviewdetails)  

@app.route('/viewmore1', methods=["GET",'POST'])
@login_required
def viewmore1():
    if request.method == 'POST':
        like=request.form
        likes=like.get("like")
        users = Table("book", "title", "author", "rating", "likes_count","price","year","genre","summary")
        users.update(likes)
        return redirect(url_for('viewmore', bookid=likes))
    
@app.route('/viewmore2', methods=["GET",'POST'])
@login_required
def viewmore2():
    if request.method == 'POST':
        wishlist=request.form
        wish=wishlist.get("wishlist")
        users = Table("wishlist", "user_id", "book_id")
        users.insert(session['id'],wish)
        return redirect(url_for('viewmore', bookid=wish))
          
@app.route('/likes', methods=["GET",'POST'])
@login_required
def likes():
    if request.method == 'POST':
        like=request.form
        likes=like.get("like")
        users = Table("book", "title", "author", "rating", "likes_count","price","year","genre","summary")
        users.update(likes)
        return redirect('/')
    
@app.route('/wish', methods=["GET",'POST'])
@login_required
def wish():
    if request.method == 'POST':
        wishlist=request.form
        wish=wishlist.get("wishlist")
        users = Table("wishlist", "user_id", "book_id")
        users.insert(session['id'],wish)
        return redirect('/')
    
@app.route('/like1', methods=["GET",'POST'])
@login_required
def like1():
    if request.method == 'POST':
        review_like=request.form
        likee=review_like.get("like")
        users = Table("book_reviews", "review_id", "book_id", "review", "likes", "name")
        users.updatelike(likee)
        cur = mysql.connection.cursor()
        resultValue = cur.execute("SELECT book_id FROM %s WHERE %s = \"%s\"" %("book_reviews", "review_id", likee))
        if resultValue > 0:
            book_id = cur.fetchall()
            return redirect(url_for('viewmore', bookid=book_id[0]))
        
@app.route('/remove',methods=["GET",'POST'])
@login_required
def remove():
    if request.method == 'POST':
        remove_book=request.form
        book_id=remove_book.get("section")
        users = Table("wishlist", "wishlist_id", "user_id", "book_id")
        users.delete_book(session['id'],book_id)
        return redirect('/wishlist')
        
    
if __name__ == '__main__':
    app.run(debug=True,port=8080,use_reloader=False)

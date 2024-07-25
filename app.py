from flask import Flask, render_template, url_for, flash, redirect, request
from flask_mysqldb import MySQL
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, login_user, current_user, logout_user, login_required
from config import Config
from models import User
from forms import RegistrationForm, LoginForm

app = Flask(__name__)
app.config.from_object(Config)

mysql = MySQL(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    user = cur.fetchone()
    if user:
        return User(user[0], user[1], user[2])
    return None

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (form.username.data, hashed_password))
        mysql.connection.commit()
        cur.close()
        flash('Your account has been created!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE username = %s", (form.username.data,))
        user = cur.fetchone()
        if user and bcrypt.check_password_hash(user[2], form.password.data):
            user_obj = User(user[0], user[1], user[2])
            login_user(user_obj, remember=True)
            return redirect(url_for('dashboard'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html', form=form)

@app.route('/dashboard')
@login_required
def dashboard():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM items")
    items = cur.fetchall()
    return render_template('dashboard.html', items=items)

@app.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']

        cur = mysql.connection.cursor()

        # Find the next available ID
        cur.execute("SELECT COALESCE(MIN(id), 0) FROM items WHERE id > 0")
        next_id = cur.fetchone()[0]

        if next_id == 0:
            # No items exist, so start with ID 1
            next_id = 1
        else:
            # Assign the next ID in sequence
            cur.execute("SELECT MAX(id) FROM items")
            max_id = cur.fetchone()[0]
            next_id = max_id + 1

        # Insert the new item with the determined ID
        cur.execute("INSERT INTO items (id, name, description) VALUES (%s, %s, %s)", (next_id, name, description))
        mysql.connection.commit()
        cur.close()

        return redirect(url_for('dashboard'))

    return render_template('add.html')


@app.route('/update/<int:id>', methods=['GET', 'POST'])
@login_required
def update(id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM items WHERE id = %s", (id,))
    item = cur.fetchone()
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        cur.execute("UPDATE items SET name = %s, description = %s WHERE id = %s", (name, description, id))
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('dashboard'))
    return render_template('update.html', item=item)

@app.route('/delete/<int:id>')
@login_required
def delete(id):
    cur = mysql.connection.cursor()

    # Delete the item
    cur.execute("DELETE FROM items WHERE id = %s", (id,))
    mysql.connection.commit()

    # Renumber IDs sequentially
    cur.execute("SET @rank := 0;")
    cur.execute("""
        UPDATE items
        SET id = (@rank := @rank + 1)
        ORDER BY id;
    """)
    mysql.connection.commit()

    cur.close()
    return redirect(url_for('dashboard'))



@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)

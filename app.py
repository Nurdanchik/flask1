from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from peewee import IntegrityError
from models import MyUser, Note , Card
from PIL import Image
from io import BytesIO
import datetime
import io
import base64

app = Flask(__name__)
app.secret_key = 'your_secret_key'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return MyUser.get(MyUser.id == int(user_id))

@app.route('/')
def index ():
    if current_user.is_authenticated:
        notes = Note.select().where(Note.user == current_user.id)
        return render_template('index.html', notes=notes)
    else:
        return redirect(url_for('login'))

@app.route('/add_note', methods=['POST'])
@login_required
def add_note():
    note_text = request.form['note_text']
    note_color = request.form['note_color']
    Note.create(user=current_user.id, note_text=note_text, note_color=note_color)
    return index()

@app.route('/delete_note/<int:note_id>', methods=['POST'])
@login_required
def delete_note(note_id):
    note = Note.get(Note.id == note_id)
    if note.user.id == current_user.id:
        note.delete_instance()
    return index()

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        age = int(request.form['age'])
        full_name = request.form['full_name']
        password = generate_password_hash(request.form['password'])

        try:
            MyUser.create(username=username, email=email, age=age, full_name=full_name, password=password)
            flash('Registration successful! You can now log in.')
            return redirect(url_for('login'))
        except IntegrityError:
            flash('Username or email already exists.')

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        try:
            user = MyUser.get(MyUser.username == username)
            if user and check_password_hash(user.password, password):
                login_user(user)
                flash('Login successful!')
                return redirect(url_for('index'))
            else:
                flash('Invalid username/password.')
        except MyUser.DoesNotExist:
            flash('Invalid username/password.')

    return render_template('login.html')

@app.route('/logout', methods=['GET'])
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('login'))

@app.route('/update_note/<int:note_id>', methods=['GET', 'POST'])
@login_required
def update_note(note_id):
    note = Note.get(Note.id == note_id)
    if request.method == 'POST':
        note_text = request.form['note_text']
        note_color = request.form['note_color']
        note.note_text = note_text
        note.note_color = note_color
        note.save()
        flash('Note updated successfully!')
        return redirect(url_for('index'))
    return render_template('update_note.html', note=note)


@app.route('/search', methods=['GET'])
@login_required
def search():
    search_text = request.args.get('search_text')
    if len(search_text) < 3:
        flash('Search term must be at least 3 characters long')
        return redirect(url_for('index'))
    notes = Note.select().where(Note.user == current_user.id, Note.note_text.contains(search_text))
    return render_template('index.html', notes=notes)

@app.route('/forcards', methods=['GET'])
@login_required
def forcards():
    cards = Card.select().where(Card.user == current_user)
    return render_template('forcards.html', cards=cards)

@app.route('/add_card', methods=['GET', 'POST'])
@login_required
def add_card():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']

        card = Card.create(user=current_user.id, title=title, description=description)

        return redirect(url_for('forcards'))

    return render_template('add_card.html')


@app.route('/update_card/<int:card_id>', methods=['GET', 'POST'])
@login_required
def update_card(card_id):
    card = Card.get(Card.id == card_id)
    if request.method == 'POST':
        card.title = request.form['title']
        card.description = request.form['description']
        card.save()
        return redirect(url_for('forcards'))
    return render_template('update_card.html', card=card)

@app.route('/delete_card/<int:card_id>', methods=['POST'])
@login_required
def delete_card(card_id):
    card = Card.get(Card.id == card_id)
    card.delete_instance()
    return redirect(url_for('forcards'))

if __name__ == '__main__':
    app.run(debug=True)

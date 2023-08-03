from flask.helpers import flash
from main import app, bcrypt
from flask import render_template,url_for,request,flash, redirect,  jsonify
from main.models import User, Archive
from flask_login import login_user, login_required,current_user, logout_user
from main.models import db

# for  voice acitvation 
import speech_recognition as sr
import pywhatkit
import datetime
import wikipedia
import pyttsx3
running = True

@app.route('/', methods=['GET', 'POST'])
@app.route('/home', methods=['GET', 'POST'])
def index(): 
    if request.method == 'POST':
        message = request.form.get('message')

        if not message:
            error_message = "Please enter a message."
            return render_template('index.html', error_message=error_message)

        try:
            # Ensure the input is not empty before proceeding with Wikipedia search
            description = message.strip()
            response = wikipedia.summary(description, sentences=2)
            return render_template('index.html', message=message, response=response)
        except wikipedia.exceptions.DisambiguationError as e:
            # Handle the case when Wikipedia is unable to resolve the search term
            error_message = "The search term is ambiguous. Please provide more specific input."
            return render_template('index.html', error_message=error_message)
        except wikipedia.exceptions.PageError as e:
            # Handle the case when the search term does not match any Wikipedia page
            error_message = "No information found for the given search term."
            return render_template('index.html', error_message=error_message)
        except wikipedia.exceptions.HTTPTimeoutError as e:
            # Handle the case when there is a timeout issue with the Wikipedia API
            error_message = "Unable to fetch information from Wikipedia due to a timeout issue."
            return render_template('index.html', error_message=error_message)
        except Exception as e:
            # Handle any other unexpected errors that might occur during summary retrieval
            error_message = "An error occurred while fetching information from Wikipedia."
            return render_template('index.html', error_message=error_message)

    return render_template('index.html')

# audio processing
def process_audio():
    recognizer = sr.Recognizer()
    engine = pyttsx3.init()
    voices = engine.getProperty("voices")
    engine.setProperty("voice", voices[1].id)

    with sr.Microphone() as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source, duration = 0.2)
        audio = recognizer.listen(source)

    try:
        # Perform speech recognition
        action = recognizer.recognize_google(audio)
        print("You said:", action)
        return action
    except sr.UnknownValueError:
        return "Hello there, I couldn't understand what you said. Please try again."
    except sr.RequestError as e:
        print("Error occurred during recognition. Check your internet connection or API key:", e)
        return None

@app.route('/voice', methods=['GET', 'POST'])
def speech():
    action = " "
    information = ' '
    
    if request.method == 'POST' and running:
        action = process_audio()
        if action:
            if "play" in action.lower():
                song = action.replace("play", "")
                print("Playing.....")
                information= "Playing " + song
                pywhatkit.playonyt(song)
               

            elif "play me" in action.lower():
                song = action.replace("play me", "")
                print("Playing.....")
                information = "Playing " + song
                pywhatkit.playonyt(song)
                

            elif "time" in action.lower():
                current_time = datetime.datetime.now().strftime("%I:%M %p")
                print(current_time)
                information  = "The current time is " + current_time
                return render_template('speech.html', action=action, information=information)  # Pass 'action' variable to the template

            elif 'how' in action.lower():
                description = action.replace("how", "")
                information = wikipedia.summary(description, 2)
                print(information)
                return render_template('speech.html', action=action, information=information)  # Pass 'action' variable to the template


            elif 'what' in action.lower():
                description = action.replace("what", "")
                information = wikipedia.summary(description, 2)
                print(information)
                return render_template('speech.html', action=action, information=information)  # Pass 'action' variable to the template


            elif 'who' in action.lower():
                description = action.replace("what", "")
                information = wikipedia.summary(description, 2)
                print(information)
                return render_template('speech.html', action=action, information=information)  # Pass 'action' variable to the template

            
            elif '' in action.lower():
                description = action.replace("", "")
                information = wikipedia.summary(description, 2)
                print(information)
                return render_template('speech.html', action=action, information=information)  # Pass 'action' variable to the template


            else:
                information = 'Can you say that again?'
        else:
            information = "Hello there, I couldn't understand what you said. Please try again."

            
        
    return render_template('speech.html', action=action, information=information)  # Pass 'action' variable to the template


@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password1 = request.form['password1']
        password2 = request.form['password2']

        if password1 == password2:
            hash_pawd= bcrypt.generate_password_hash(request.form['password1']).decode('utf-8')
            users = User(username = username, email = email, password = hash_pawd)
            db.session.add(users)
            db.session.commit()
            return redirect('login')
        else:
            flash("Your password doesn't match!! please try again")
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if  request.method ==   'POST':
        user = User.query.filter_by(username= request.form['username']).first()
        if user and bcrypt.check_password_hash(user.password, request.form['password']):
            flash(f'You are now logged-in as {user.username}')
            login_user(user)
            next_page = request.args.get("next")
            return redirect(next_page) if next_page else redirect(url_for("index"))
       
    return render_template('login.html')

@login_required
@app.route('/account')
def account():
    return render_template('account.html')

@login_required
@app.route('/logout')
def logout():
    logout_user()
    return render_template('logout.html')


@login_required
@app.route('/deletearchive', methods=['GET', 'POST'])
def deletearchive():
    if request.method == 'POST':
        action = request.form['delete']

        deleted_archive = Archive.query.filter_by(id = action).first()
        db.session.delete(deleted_archive)
        db.session.commit()
    return redirect('achive')

@login_required
@app.route("/achive", methods=['GET', 'POST'])
def achive():
    user = current_user.get_id()
    data = []
    archived_data = Archive.query.all()
    for make in archived_data:
        print (make)        
        data.append(make)

    if request.method  == 'POST':
        #action = request.form['delete']
        action_title = request.form['add']
        action_discription = request.form['add_discription']

        archives = Archive(title = action_title, discription=action_discription, archived_id = user)
        db.session.add(archives)
        db.session.commit()
        return redirect('home')
    return render_template("archive.html", context= data)
    
     
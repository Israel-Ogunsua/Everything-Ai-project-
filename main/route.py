from app import app, bcrypt, db
from flask import render_template,url_for,request,flash, redirect,  jsonify, Response
from flask_login import login_user, login_required,current_user, logout_user
from  models import  User, ChatPost, Image
# for  voice acitvation 
import speech_recognition as sr
import pywhatkit
import datetime
import wikipedia
import pyttsx3
import cv2
from ConstructFace import ConstructFace
import numpy as np
import os

sfr = ConstructFace()
sfr.load_encoding_images(Image)
# Load Camera
cap = cv2.VideoCapture(0) 
facing = []

def savedate(message, response, user_id):
    print("process 1")
    print(type(response))

    content_searched = ChatPost( content_ai=response, user_id=user_id)
    db.session.add(content_searched)
    db.session.commit()
           
  
@app.route('/', methods=['GET', 'POST'])
@app.route('/home', methods=['GET', 'POST'])
def index(): 
    if request.method == 'POST':
        message = request.form.get('message')
        if not message:
            error_message = "Please enter a message."
            return render_template('index.html', error_message=error_message)
        
        print("gibe")
        try:
            description = message.strip()
            response = wikipedia.summary(description, sentences=2)
            print(response)
            if current_user.is_authenticated:
                if hasattr(current_user, 'get_id') and callable(getattr(current_user, 'get_id')):
                    user_id = current_user.get_id()
                    print("seen")
                    
                savedate(message, response, user_id)
                print("yeah")
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
        recognizer.adjust_for_ambient_noise(source, duration = 0.2)
        audio = recognizer.listen(source)

    try:
        # Perform speech recognition
        action = recognizer.recognize_google(audio)
        return action
    except sr.UnknownValueError:
        return "Hello there, I couldn't understand what you said. Please try again."
    except sr.RequestError as e:
        return None

def generate_frames():
  while True:
        ret, frame = cap.read()

        # Detect Faces
        face_locations, face_names = sfr.detect_known_faces(frame)
        facing.append(face_names)
        for face_loc, name in zip(face_locations, face_names):
            y1, x2, y2, x1 = face_loc[0], face_loc[1], face_loc[2], face_loc[3]

            cv2.putText(frame, name, (x1, y1 - 10), cv2.FONT_HERSHEY_DUPLEX, 1, (0, 0, 200), 2)
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 200), 4)

        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

#@login_required
@app.route('/face', methods=['GET', 'POST'])
def face():
    if request.method == 'POST':
        if 'file' not in request.files:
             return 'No file part', 400

        file = request.files['file']
        if file.filename == '':
            return 'No selected file', 400

        image_data = file.read()
        image_filename = request.form['filename']  # Get the filename from the form input
        image_record = Image(filename=image_filename, data=image_data)
        db.session.add(image_record)
        db.session.commit()

    faceUpdate = []

    for i in facing:
        if i == "Unknown" or i == "":
            pass 
        else:
            faceUpdate.append(i)
    return render_template('face.html', facing = faceUpdate)

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@login_required
@app.route('/voice', methods=['GET', 'POST'])
def speech():
    action = " "
    information = ' '
    
    if request.method == 'POST':
        action = process_audio()
        if action:
            if "play" in action.lower():
                song = action.replace("play", "")
                information= "Playing " + song
                pywhatkit.playonyt(song)

            elif "play me" in action.lower():
                song = action.replace("play me", "")
                information = "Playing " + song
                pywhatkit.playonyt(song)
                

            elif "time" in action.lower():
                current_time = datetime.datetime.now().strftime("%I:%M %p")
                information  = "The current time is " + current_time
                  # Your code for adding a new record to the database
                Content= ChatPost(content_me=action, content_ai=information, user_id=current_user.get_id())
                db.session.add(Content)
                db.session.commit()  # Commit the changes to the database
                return render_template('speech.html', action=action, information=information)  # Pass 'action' variable to the template

            elif 'how' in action.lower():
                description = action.replace("how", "")
                information = wikipedia.summary(description, 2)
                  # Your code for adding a new record to the database
                Content= ChatPost(content_me=action, content_ai=information, user_id=current_user.get_id())
                db.session.add(Content)
                db.session.commit()  # Commit the changes to the database
                return render_template('speech.html', action=action, information=information)  # Pass 'action' variable to the template


            elif 'what' in action.lower():
                description = action.replace("what", "")
                information = wikipedia.summary(description, 2)
                  # Your code for adding a new record to the database
                Content= ChatPost(content_me=action, content_ai=information, user_id=current_user.get_id())
                db.session.add(Content)
                db.session.commit()  # Commit the changes to the database
                return render_template('speech.html', action=action, information=information)  # Pass 'action' variable to the template


            elif 'who' in action.lower():
                description = action.replace("what", "")
                information = wikipedia.summary(description, 2)
                  # Your code for adding a new record to the database
                Content= ChatPost(content_me=action, content_ai=information, user_id=current_user.get_id())
                db.session.add(Content)
                db.session.commit()  # Commit the changes to the database
                return render_template('speech.html', action=action, information=information)  # Pass 'action' variable to the template

            elif '' in action.lower():
                description = action.replace("", "")
                information = wikipedia.summary(description, 2)
                  # Your code for adding a new record to the database
                Content= ChatPost(content_me=action, content_ai=information, user_id=current_user.get_id())
                db.session.add(Content)
                db.session.commit()  # Commit the changes to the database
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
        user = User.query.filter_by(email= request.form['email']).first()
        if user and bcrypt.check_password_hash(user.password, request.form['password']):
            flash(f'You are now logged-in as {user.username}')
            login_user(user)
            next_page = request.args.get("next")
            return redirect(next_page) if next_page else redirect(url_for("index"))
    return render_template('login.html')

@login_required
@app.route('/account')
def account():
    user = User.query.filter_by(id = current_user.get_id()).first()
    
    return render_template('account.html', username = user.username, email = user.email)


@login_required
@app.route('/setting')
def setting():
    return render_template('setting.html')

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
        deleted_archive = ChatPost.query.filter_by(id = action).first()
        db.session.delete(deleted_archive)
        db.session.commit()
    return redirect('achive')

@login_required
@app.route("/achive", methods=['GET', 'POST'])
def achive():
    data = []
    user_id = current_user.get_id()
    # Query archived data from the database using SQLAlchemy where id matches the user's ID
    archived_data = ChatPost.query.filter_by(id=user_id).all()
    for make in archived_data:
        data.append(make)
    
    
    return render_template("archive.html", post = data)
    
     
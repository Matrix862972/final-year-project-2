## 📁 File: `app.py`

### 🔢 Lines 1–17

### 🧠 Purpose: Setup core libraries, modules, and dependencies for the AI-based exam surveillance system.

```python
import math                          # Used for geometric calculations (e.g., angles in gaze tracking)
from concurrent.futures import ThreadPoolExecutor  # Runs parallel tasks like camera + audio monitoring
from flask import Flask, render_template, request, jsonify, session,redirect,url_for,Response,flash
# Core Flask components for handling routing, rendering, and web response
import os                            # Used for file path management, file I/O
from flask_mysqldb import MySQL      # MySQL integration to store candidate/session data
import json                          # Handles JSON serialization for data exchange
import io                            # In-memory file-like object handling
import numpy as np                   # Fast numerical operations (frame processing, detection)
from enum import Enum                # Helps define readable constants (e.g., warning levels)
import warnings                      # To suppress unnecessary log warnings
import threading                     # For non-blocking background tasks
import utils                         # Custom utility module (likely contains helper functions)
import random                        # Used for mock data, randomness in gamification, etc.
import time                          # For delays, time logs, and timestamps
import cv2                           # OpenCV library for webcam access, image processing
import keyboard                      # Detects key presses (e.g., Ctrl+C, Alt+Tab) for monitoring behavior

```

## 📁 File: `app.py`

### 🔢 Lines 18–37

### 🧠 Purpose: Global variables, Flask app initialization, and MySQL database configuration.

````python

app.config['MYSQL_PASSWORD'] = 'password'
app.config['MYSQL_DB'] = 'examproctordb'
mysql = MySQL(app)
# Initializes MySQL connection to a local database named `examproctordb`
# Thread Pool Executor
executor = ThreadPoolExecutor(max_workers=4)
# Allows running background tasks (e.g., face detection, logging) on up to 4 parallel threads

## 📷 Function: capture_by_frames

### Purpose
This function is responsible for capturing real-time webcam frames, detecting faces using Haar Cascades, drawing rectangles around detected faces, and streaming the video feed to the web browser in MJPEG format.

---

### Code with Line-by-Line Explanation

```python
# Function to show face detection's Rectangle in Face Input Page
def capture_by_frames():  # Defines the streaming function for face detection preview
    global camera  # Uses the global variable `camera` (if initialized elsewhere)

    # Initializes the video capture with the default webcam using DirectShow backend (for Windows)
    utils.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    while True:  # Starts an infinite loop to continuously capture and process frames
        success, frame = utils.cap.read()  # Attempts to read a frame from the webcam

### Purpose
This function initializes multiple cheat detection subsystems (video, face recognition, and audio monitoring) by launching them in background threads using `ThreadPoolExecutor`. It is automatically called before processing each HTTP request.

---
### Code with Line-by-Line Explanation

```python
# Function to run Cheat Detection when we start run the Application

# This decorator tells Flask to call the function before every incoming request
@app.before_request
def start_loop():  # Defines the function that launches background detection modules

    # Submits cheat_Detection2() to the executor as a background thread.
    # Possibly handles one type of cheating behavior (e.g., posture analysis or eye tracking).
    task1 = executor.submit(utils.cheat_Detection2)

    # Submits another type of cheat detection algorithm.
    # It could handle a different modality like object detection or environment scanning.
    task2 = executor.submit(utils.cheat_Detection1)

    # Starts the facial recognition system from the utils.fr module.
    # Typically used to continuously verify student identity during the exam.
    task3 = executor.submit(utils.fr.run_recognition)

    # Starts audio recording or monitoring in a separate thread.
    # Likely used to detect background conversation or unauthorized help.
    task4 = executor.submit(utils.a.record)

    ## 🔐 Function: main (Login Route)

This route handles the default landing page (`'/'`) of the web application and displays the login interface to the user.

---

### **Code with Line-by-Line Explanation**

```python
# Login Related

# This Flask decorator maps the root URL to the main() function.
@app.route('/')
def main():  # Defines the view function for the homepage
    # Renders the login.html template from the templates/ folder
    return render_template('login.html')

## 🔐 Function: login (User Login Route)

### **Purpose**
Handles POST login requests from the login form, verifies credentials against the database, and redirects users to the appropriate page based on their role (STUDENT or ADMIN).

---

### **Code with Line-by-Line Explanation**

```python
# Route handler for '/login', only accepts POST requests
@app.route('/login', methods=['POST'])
def login():
    global studentInfo  # Use global variable to store logged-in student info

    if request.method == 'POST':  # Confirm that request is a POST
        username = request.form['username']  # Get the entered username (email) from the login form
        password = request.form['password']  # Get the entered password from the login form

        cur = mysql.connection.cursor()  # Create a cursor object to interact with the database

        # ⚠️ SQL Injection risk! Use parameterized queries instead in production
        cur.execute("SELECT * FROM students where Email='" + username + "' and Password='" + password + "'")
        data = cur.fetchone()  # Fetch the first matching user record

        if data is None:  # No match found → invalid login
            flash('Your Email or Password is incorrect, try again.', category='error')  # Show error message
            return redirect(url_for('main'))  # Redirect back to login page

        else:  # Match found → user is valid
            # Unpack the result into individual fields
            id, name, email, password, role, created_at, updated_at = data
            # Store essential user info in a global dictionary
            studentInfo = { "Id": id, "Name": name, "Email": email, "Password": password }

            if role == 'STUDENT':  # If user is a student
                utils.Student_Name = name  # Set global student name for use elsewhere
                return redirect(url_for('rules'))  # Redirect to rules page before exam starts

            else:  # If user is an admin or teacher
                return redirect(url_for('adminStudents'))  # Redirect to admin student dashboard


## 🔓 Function: logout (User Logout Route)

### **Purpose**
Handles the logout route (`/logout`) by rendering the login page again. Currently, this function does **not** clear session data, so it does not securely log out the user.

---

### **Code with Line-by-Line Explanation**

```python
@app.route('/logout')



## 📘 Route: /rules (Exam Rules Page)

### **Purpose**
This route displays the exam rules to students after they successfully log in, helping them understand the policies before they proceed with the test.

---

### **Code with Inline Comments**
```python
# Student Related

# Define a route in Flask that listens on the '/rules' URL
@app.route('/rules')
def rules():
    # Renders and returns the HTML page 'ExamRules.html' from the templates folder
    return render_template('ExamRules.html')


## 🧑‍💻 Route: /faceInput (Face Input Page)

### **Purpose**
This route is responsible for serving the page where the candidate's face will be captured for authentication or smart attendance using the webcam.

---

### **Code with Inline Comments**
```python
# Define a route for the face input page where students align their face for verification
@app.route('/faceInput')  # Flask route for handling requests to "/faceInput"
def faceInput():
    # Renders and returns the 'ExamFaceInput.html' page from the templates directory
    return render_template('ExamFaceInput.html')


## 📸 Route: /video_capture (Live Video Stream Endpoint)

### **Purpose**
This route provides a live video feed from the user's webcam in MJPEG format. It enables real-time streaming of frames to a web page using a video tag or `img` element.

---

### **Code with Inline Comments**
```python
# Flask route to serve a continuous webcam stream using MJPEG format
@app.route('/video_capture')  # Endpoint to start streaming video
def video_capture():
    # Returns a Response object that streams webcam frames as JPEG images
    return Response(
        capture_by_frames(),  # Generator function yielding encoded image frames
        mimetype='multipart/x-mixed-replace; boundary=frame'  # MIME type for MJPEG streaming
    )



🖼️ Function: saveFaceInput
Purpose
Captures a frame from the webcam, saves it as the student's profile image, moves the image to the designated "Profiles" folder, and redirects to a confirmation page.

Code with Explanations
```python
# Route for saving the face input image
@app.route('/saveFaceInput')
def saveFaceInput():
    global profileName  # Use the global variable to store the profile image name

    # Check if the webcam (stored in utils.cap) is already in use
    if utils.cap.isOpened():
        utils.cap.release()  # Release it to prevent access conflict

    # Start a new webcam session using OpenCV
    cam = cv2.VideoCapture(0)

    # Capture a single frame from the webcam
    success, frame = cam.read()

    # Generate a unique filename using the student's name and a 3-digit result ID
    profileName = f"{studentInfo['Name']}_{utils.get_resultId():03}" + "Profile.jpg"

    # Save the captured frame to disk as a JPEG image
    cv2.imwrite(profileName, frame)

    # Move the saved image file into the "Profiles" folder for organization
    utils.move_file_to_output_folder(profileName, 'Profiles')

    # Release the webcam to free it for future use
    cam.release()

    # Redirect to the face input confirmation page
    return redirect(url_for('confirmFaceInput'))

## 📸 Route: /confirmFaceInput
### **Purpose**
This route is responsible for:

Encoding the face image captured earlier (for recognition).

Displaying the face back to the student for confirmation before proceeding.

```python
# Route to confirm the face input taken previously
@app.route('/confirmFaceInput')
def confirmFaceInput():
    # Use the global variable that stores the filename of the captured profile image
    profile = profileName

    # Call the face recognition module's encode_faces() method to process the captured image.
    # This typically extracts face encodings so they can be matched during monitoring.
    utils.fr.encode_faces()

    # Render the confirmation page where the student can verify their captured photo
    return render_template('ExamConfirmFaceInput.html', profile=profile)


    🧪 Route: /systemCheck
Purpose
This route is used to render the System Check page, which ensures that the candidate's hardware and environment (e.g., webcam, microphone, internet) are ready for the proctored exam.


```python
# Flask route for the system check page
@app.route('/systemCheck')
def systemCheck():
    # Render the HTML template that allows candidates to check their system readiness
    # Typically includes webcam, microphone, screen resolution, and browser compatibility
    return render_template('ExamSystemCheck.html')

⚙️ Route: /systemCheck (POST)
Purpose
This route handles the POST request made during the system check process. It receives system information (e.g., webcam, microphone status) from the frontend and responds with a status indicating whether the system is ready or not.

Code with Line-by-Line Comments
```python
# Flask route that listens for POST requests to /systemCheck
@app.route('/systemCheck', methods=["POST"])
def systemCheckRoute():
    # Check if the request method is POST
    if request.method == 'POST':
        # Get JSON data sent from frontend (likely system information)
        examData = request.json

        # Default output is set to "exam" (means system is OK)
        output = 'exam'

        # If any system input info contains 'Not available', set output to 'systemCheckError'
        if 'Not available' in examData['input'].split(';'):
            output = 'systemCheckError'

    # Return the result as JSON back to frontend
    return jsonify({"output": output})

❌ Route: /systemCheckError
Purpose
This route serves the system check error page when the user's hardware (like webcam/microphone) does not meet exam requirements.

Code with Comments
```python
# Route to handle system check failure
@app.route('/systemCheckError')
def systemCheckError():
    # Renders the error page informing the candidate their system check failed
    return render_template('ExamSystemCheckError.html')


Route: /exam
Purpose
This route initializes the actual exam session. It starts webcam capture and sets up a keyboard hook to monitor shortcut key usage (e.g., for copy/paste detection) and renders the main exam interface.

Code with Comments
```python
# Route to start the exam session
@app.route('/exam')
def exam():
    # Initializes webcam capture using the DirectShow backend for better Windows support
    utils.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

    # Hooks into all keyboard input to detect prohibited shortcuts (e.g., Ctrl+C, Alt+Tab)
    keyboard.hook(utils.shortcut_handler)

    # Loads the main exam interface HTML page
    return render_template('Exam.html')


🧠 examAction – Exam Evaluation & Result Handling
Purpose
This function processes the submitted exam score, calculates the final marks and trust score, detects cheating, and generates the result with a status (Pass/Fail/Cheating). It also saves the result to a JSON file for records.

```python
@app.route('/exam', methods=["POST"])  # Define a POST route at '/exam'
def examAction():
    link = ''  # Initialize redirect link for result page

    if request.method == 'POST':  # Ensure it's a POST request
        examData = request.json  # Get JSON data from request body

        if examData['input'] != '':  # Proceed if exam input is not empty
            utils.Globalflag = False  # Stop any active monitoring threads

            utils.cap.release()  # Release webcam

            # Log any detected prohibited shortcuts
            utils.write_json({
                "Name": ('Prohibited Shorcuts (' + ','.join(list(dict.fromkeys(utils.shorcuts))) + ') are detected.'),
                "Time": (str(len(utils.shorcuts)) + " Counts"),
                "Duration": '',
                "Mark": (1.5 * len(utils.shorcuts)),  # Assign penalty marks
                "Link": '',
                "RId": utils.get_resultId()  # Unique result ID
            })

            utils.shorcuts = []  # Reset shortcut list

            trustScore = utils.get_TrustScore(utils.get_resultId())  # Get AI-determined trust score

            # Calculate final marks (scale input to 100)
            totalMark = math.floor(float(examData['input']) * 6.6667)

            # Apply rules based on trust score and total marks
            if trustScore >= 30:  # If cheating suspected
                status = "Fail(Cheating)"
                link = 'showResultFail'
            else:
                if totalMark < 50:  # If failed due to marks
                    status = "Fail"
                    link = 'showResultFail'
                else:  # Otherwise, passed
                    status = "Pass"
                    link = 'showResultPass'

            # Save final result to JSON file
            utils.write_json({
                "Id": utils.get_resultId(),
                "Name": studentInfo['Name'],
                "TotalMark": totalMark,
                "TrustScore": max(100 - trustScore, 0),  # Convert to positive trust score
                "Status": status,
                "Date": time.strftime("%Y-%m-%d", time.localtime(time.time())),
                "StId": studentInfo['Id'],
                "Link": profileName
            }, "result.json")

            # Format result status to send to frontend
            resultStatus = studentInfo['Name'] + ';' + str(totalMark) + ';' + status + ';' + time.strftime("%Y-%m-%d", time.localtime(time.time()))

        else:
            utils.Globalflag = True  # Keep monitoring running
            print('sfdsfsdsfdsfdsfdsfdsfdsfdsfds')  # Debug print (can be removed)
            resultStatus = ''  # Return empty result if input is empty

    # Return result and page link to frontend
    return jsonify({"output": resultStatus, "link": link})
🔎 Notes
The trust score system provides an automated cheat-detection mechanism.

Use of utils.shorcuts allows keyboard-based violations to be penalized.

Result is saved as JSON – suitable for later retrieval or dashboard rendering.

Debug text (print('sfdsfsdsfdsfdsfdsfdsfdsfdsfds')) is junk and should be cleaned.


✅ showResultPass – Display Exam Pass Result
Purpose
This route handles displaying the "Pass" result page after an exam. It takes the result details (passed from the previous route) and renders them on a success template.

```python
@app.route('/showResultPass/<result_status>')  # Define a dynamic route that accepts a result_status value
def showResultPass(result_status):
    # Renders the 'ExamResultPass.html' template and passes the result_status value to it
    return render_template('ExamResultPass.html', result_status=result_status)


❌ showResultFail – Display Exam Fail Result
Purpose
This route is used to display the "Fail" result page after a student finishes the exam and does not meet the passing criteria or is caught cheating.

Code with Line-by-Line Comments
```python
@app.route('/showResultFail/<result_status>')  # Flask route with a dynamic URL parameter: result_status
def showResultFail(result_status):
    # Renders the 'ExamResultFail.html' page and sends the result_status value for display
    return render_template('ExamResultFail.html', result_status=result_status)


🛠️ adminResults – Admin Results View
Purpose
This route allows the administrator to view the full list of student exam results. It retrieves stored result data from the system and displays it in a structured format.

Code with Line-by-Line Comments
```python
# Admin-Related Route
@app.route('/adminResults')  # Flask route for viewing all exam results
def adminResults():
    results = utils.getResults()  # Calls a utility function to fetch all saved exam results (likely from a JSON or DB)
    return render_template('Results.html', results=results)  # Renders the results page with retrieved data


📋 adminResultDetails – Admin View of Individual Result
Purpose
This route allows an admin to view the detailed information of a specific exam result based on a unique resultId. It loads the information using a helper function and renders it on a detailed result page.

Code with Line-by-Line Comments
python
Copy code
@app.route('/adminResultDetails/<resultId>')  # Dynamic route that takes a result ID as part of the URL
def adminResultDetails(resultId):
    result_Details = utils.getResultDetails(resultId)  # Calls a utility function to fetch result details by ID
    return render_template('ResultDetails.html', resultDetails=result_Details)  # Passes the data to the HTML page for display

## 📼 Function: adminResultDetailsVideo

### Purpose:
Serves the route to display video-related result details for a specific exam record. Passes the `videoInfo` to the HTML template for rendering.

---

### Code with Comments

```python
# Route to view video analysis or footage of a specific result
@app.route('/adminResultDetailsVideo/<videoInfo>')  # Binds dynamic URL segment to variable
def adminResultDetailsVideo(videoInfo):
    # Renders the HTML page for showing video results, passing the video info to the template
    return render_template('ResultDetailsVideo.html', videoInfo=videoInfo)


## 👨‍🎓 Function: adminStudents

### Purpose:
Displays a list of all students (users with `Role='STUDENT'`) from the database on the admin page.

---

### Code with Inline Comments

```python
# Route to display all students to the admin
@app.route('/adminStudents')
def adminStudents():
    # Create a database cursor for executing SQL queries
    cur = mysql.connection.cursor()

    # Execute SQL query to retrieve students with role 'STUDENT'
    cur.execute("SELECT * FROM students where Role='STUDENT'")

    # Fetch all results returned by the query
    data = cur.fetchall()

    # Close the database cursor
    cur.close()

    # Render the Students.html page, passing the list of students
    return render_template('Students.html', students=data)


## ➕ Function: insertStudent
````

### Purpose:

Handles the insertion of a new student record submitted via an admin form. Adds the student to the database and redirects back to the student listing page.

---

### Code with Inline Comments

```python
# Route to insert a new student (only accepts POST requests)
@app.route('/insertStudent', methods=['POST'])
def insertStudent():
    # Check if the request is a POST (redundant but safe)
    if request.method == "POST":
        # Get submitted form data
        name = request.form['username']
        email = request.form['email']
        password = request.form['password']

        # Create a database cursor
        cur = mysql.connection.cursor()

        # Execute INSERT query with provided form data and default role as 'STUDENT'
        cur.execute("INSERT INTO students (Name, Email, Password, Role) VALUES (%s, %s, %s, %s)",
                    (name, email, password, 'STUDENT'))

        # Commit changes to the database
        mysql.connection.commit()

        # Redirect back to admin's student list page
        return redirect(url_for('adminStudents'))

    ## 🗑️ Function: deleteStudent

```

### Purpose:

Deletes a student record from the database based on the provided student ID and redirects back to the admin student listing page.

---

### Code with Inline Comments

```python
# Route to delete a student by ID, accepts GET requests
@app.route('/deleteStudent/<string:stdId>', methods=['GET'])
def deleteStudent(stdId):
    # Show a flash message indicating success
    flash("Record Has Been Deleted Successfully")

    # Open a MySQL cursor
    cur = mysql.connection.cursor()

    # Execute the DELETE query using parameterized input to avoid SQL injection
    cur.execute("DELETE FROM students WHERE ID=%s", (stdId,))

    # Commit the transaction to make deletion permanent
    mysql.connection.commit()

    # Redirect to the student admin view after deletion
    return redirect(url_for('adminStudents'))


```

## 🛠️ Route: /updateStudent

### **Purpose**

This route handles the update of a student's information in the database through an admin interface.

---

```python
@app.route('/updateStudent', methods=['POST', 'GET'])  # Allows POST (for form submission) and GET (unused)
def updateStudent():
    if request.method == 'POST':  # Only process when form is submitted via POST
        id_data = request.form['id']  # Get student ID to update
        name = request.form['name']  # New name
        email = request.form['email']  # New email
        password = request.form['password']  # New password

        cur = mysql.connection.cursor()  # Open DB connection

        # SQL Update query (secure with placeholders)
        cur.execute("""
               UPDATE students
               SET Name=%s, Email=%s, Password=%s
               WHERE ID=%s
            """, (name, email, password, id_data))

        mysql.connection.commit()  # Save changes to DB

        return redirect(url_for('adminStudents'))  # Return to student list after update



```

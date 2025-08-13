# 🐞 Known Bugs

# ✅ Bug 1: Repeated Thread Execution on Every Request – [FIXED]

Bug Title
Flask @app.before_request starts background threads multiple times

Status: FIXED ✅
This bug has been resolved by removing the @app.before_request hook and implementing proper thread management in the exam route.

Description
The start_loop() function decorated with @app.before_request was initializing multiple background threads using ThreadPoolExecutor on every HTTP request, which led to excessive resource usage and thread conflicts. This has been resolved by moving thread management to the exam route.

Solution Implemented  
Moved camera initialization and thread management to the exam route:

- Camera initialization moved to exam GET route (when page loads)
- Thread detection starts only when exam POST route is called (when user starts exam)
- Eliminates race conditions and thread conflicts
- Fixed in commit: c1ca091

Attempted Solution
python
Copy code
started = False
@app.before_request
def start_loop():
global started
if not started:
started = True
utils.Globalflag = True # Enable detection systems
task1 = executor.submit(utils.cheat_Detection2)
task2 = executor.submit(utils.cheat_Detection1)
task3 = executor.submit(utils.fr.run_recognition)
task4 = executor.submit(utils.a.record)
Notes:
The started flag approach has not fully resolved the issue — it may not persist correctly between different contexts or processes in Flask’s deployment.

Multiple thread creation still occurs under certain conditions.

``

## 🐞 Bug 2: SQL Injection Vulnerability in Login Function

**File:** `app.py`
**Function:** `login()`
**Line of Concern:**

```python
cur.execute("SELECT * FROM students where Email='" + username + "' and Password='" + password + "'")
```

Description
The login function constructs the SQL query by concatenating raw user input directly into the query string. This makes the application vulnerable to SQL Injection, a serious security flaw that can allow attackers to:

Bypass authentication (log in without valid credentials)

Extract or manipulate database content

Potentially execute destructive SQL commands

This vulnerability arises because the SQL engine interprets user input as part of the SQL syntax rather than as data.

``

## 🐞 Bug 3: Logout Does Not Clear Session Data

### 📍 File:

`app.py`

### 🧩 Description:

The `/logout` route currently only renders the login page (`login.html`) but does **not** terminate the user session. As a result, any session variables (e.g., `session['user']`, `session['email']`, etc.) remain active after "logout".
This means the user could still access authenticated routes depending on how access control is implemented elsewhere in the system.

⚠️ Impact:
Security Risk: Users may still be considered "logged in".

Inconsistent User State: Frontend shows login page, but backend may still treat the user as authenticated.

### 🔢 Code Snippet:

````python
@app.route('/logout')
def logout():
    return render_template('login.html')

```python
@app.route('/logout')
def logout():
    return render_template('login.html')

````

## Bug 4: Typo in Variable Name Passed to Template

📌 Location
Line:

````python
return render_template('ResultDetails.html', resultDetials=result_Details)
🧠 Description

Correct: resultDetails

This can cause the variable to be undefined in the template, resulting in empty or broken result details display.

🛠️ Recommended Fix
Update the render line to:

```python
return render_template('ResultDetails.html', resultDetails=result_Details)
````

Make sure to also update the variable name in the HTML template (ResultDetails.html) to match this corrected spelling if necessary.

📅 Status
❌ Not fixed
🛠️ Will be resolved in the next patch phase.

return render_template('ResultDetails.html', resultDetails=result_Details)

```
Make sure to also update the variable name in the HTML template (ResultDetails.html) to match this corrected spelling if necessary.

🛠️ Will be resolved in the next patch phase.

```

## ⚠️ Bug 5: Insecure Deletion Method via GET

### ❌ Bug Title:

Destructive Action (Student Deletion) Triggered via GET Request

### 🧱 Description:

The `deleteStudent` route currently uses a `GET` request to trigger a database deletion:

```python
@app.route('/deleteStudent/<string:stdId>', methods=['GET'])

def deleteStudent(stdId):
    cur.execute("DELETE FROM students WHERE StudentID=%s", (stdId,))
    mysql.connection.commit()
    cur.close()
    return redirect(url_for('studentsListing'))

Using GET for deletion is not secure and violates REST principles. Destructive actions should only be handled via POST, DELETE, or PUT to prevent accidental or malicious operations (e.g., bots, prefetching, or user misclicks).


Deletion could occur through automated bots or link preloading by browsers.

✅ Recommended Fix:
Change the HTTP method to POST and protect the form using CSRF tokens.

Optionally, implement a JavaScript confirmation modal on the front-end before the request is sent.

📌 Priority:
High – Security vulnerability and bad REST practice.

```

## 🐞 Bug 6: Passwords Stored in Plain Text

### 📌 Description

Currently, student passwords are stored in the database in plain text. This is a serious security vulnerability because if the database is ever exposed or breached, all user credentials will be compromised immediately.
def insertStudent(name, email, password):
cur.execute("""
INSERT INTO students (Name, Email, Password, Role)
VALUES (%s, %s, %s, %s)
""", (name, email, password, 'STUDENT'))
mysql.connection.commit()
cur.close()

def updateStudent(id_data, name, email, password):
cur = mysql.connection.cursor()
cur.execute("""
UPDATE students
SET Name=%s, Email=%s, Password=%s
WHERE ID=%s
""", (name, email, password, id_data))
mysql.connection.commit()
cur.close()

- `insertStudent()` function (when registering new users)
- `updateStudent()` function (when modifying passwords)

Example:

```sql
INSERT INTO students (Name, Email, Password, Role) VALUES (...)
python
Copy code
cur.execute("""
    UPDATE students
    SET Name=%s, Email=%s, Password=%s
    WHERE ID=%s
""", (...))
Violation of cybersecurity best practices

Fails to meet security standards for handling credentials

✅ Recommendation
Use bcrypt, werkzeug.security, or similar libraries to hash passwords before storing.

On login, compare the hashed password using a secure method.

python
from werkzeug.security import generate_password_hash, check_password_hash

# Example usage
hashed_password = generate_password_hash(password)
is_valid = check_password_hash(stored_hashed_password, entered_password)
🏷️ Severity
Critical

```

## ✅ Bug 7: Recorded Videos and Audio Do Not Play in Admin Dashboard [FIXED]

### Affected Views

- `ResultDetails.html`
- Playback controls were visible, but clicking play did nothing.
- In some cases, the file was not found (404 error) or the path was invalid.
- MIME type issues: Flask was not configured to serve `.mp4`, `.webm`, or `.wav` properly.

### 🛠️ Fix Implemented

- All media files are now saved under the `static/` directory.
- Jinja2 templates (e.g., `ResultDetails.html`) now use `url_for('static', filename=...)` to reference video and audio files, ensuring correct static file serving.
- Path cleanup logic was added to templates to handle Windows-style backslashes and remove redundant `static/` prefixes.
- Audio playback MIME type was corrected in the template.
- The backend logic for recording and saving files was reviewed to ensure files are properly closed and saved.

### 🏷️ Status

**FIXED** — Media playback in the admin dashboard is now fully functional.

## 🐞 Bug 8: Potential Filename Collision in Video Output

🐞 Bug: Potential Filename Collision in Video Output
📄 File/Module:
utils.py (or wherever the video paths are generated)

🔢 Code Involved:

```python
video = [
    os.path.join(video_dir, str(random.randint(1,50000)) + ".mp4"),
    os.path.join(video_dir, str(random.randint(1,50000)) + ".mp4"),
]
```

❗ Description:
This implementation uses random.randint(1, 50000) to generate filenames for 5 video recordings. However, there is no check to ensure that the randomly generated filenames are unique within the static/OutputVideos/ directory. This could lead to filename collisions, where a new video file overwrites an existing one.

💥 Risk:
Previously recorded evidence (e.g., cheating clips) could be overwritten, leading to data loss or incomplete logs in the system.

🛠️ Suggested Fix:
Replace random.randint(...) with a more robust method such as:
uuid.uuid4() for globally unique filenames

Add a check: if os.path.exists(path): regenerate

✅ Status:
Unresolved — requires implementation of uniqueness guarantee

````python
import uuid

video = [
    os.path.join(video_dir, str(uuid.uuid4()) + ".mp4"),
    os.path.join(video_dir, str(uuid.uuid4()) + ".mp4"),
    os.path.join(video_dir, str(uuid.uuid4()) + ".mp4"),
    os.path.join(video_dir, str(uuid.uuid4()) + ".mp4"),
]
❗ Description:
This implementation uses random.randint(1, 50000) to generate filenames for 5 video recordings. However, there is no check to ensure that the randomly generated filenames are unique within the static/OutputVideos/ directory. This could lead to filename collisions, where a new video file overwrites an existing one.

💥 Risk:
Previously recorded evidence (e.g., cheating clips) could be overwritten, leading to data loss or incomplete logs in the system.

🛠️ Suggested Fix:
Replace random.randint(...) with a more robust method such as:

uuid.uuid4() for globally unique filenames

Add a check: if os.path.exists(path): regenerate

✅ Status:
Unresolved — requires implementation of uniqueness guarantee


### 📌 Description
The variable `active_window_title` is hardcoded to `"Google Chrome"` in the screen monitoring section:

```python
active_window_title = "Google Chrome"
exam_window_title = active_window_title


````

### 🐞 Bug 9: No File Existence or Empty File Handling in write_json

🔍 Description
The function write_json(new_data, filename='violation.json') assumes that the violation.json file:

Already exists

Is not empty and contains valid JSON (e.g., a list [])
If the file:

Does not exist, a FileNotFoundError will be raised.

⚠️ Impact
Application may crash at runtime during the logging process.

No violations will be recorded if this fails.

Makes the system brittle for first-time use or when the file is accidentally cleared.

🛠️ Suggested Fix (not implemented yet)
Add logic to:

Create the file if it does not exist.

Initialize with an empty list [] if the file is empty or corrupted.

💡 Example Fix (to be considered later)

```python
def write_json(new_data, filename='violation.json'):
    if not os.path.exists(filename):
        with open(filename, 'w') as f:
            json.dump([], f)

    with open(filename, 'r+') as file:
        try:
            file_data = json.load(file)
        except json.JSONDecodeError:
            file_data = []

        file_data.append(new_data)
        file.seek(0)
        json.dump(file_data, file, indent=4)

Is not empty and contains valid JSON (e.g., a list [])

If the file:

Does not exist, a FileNotFoundError will be raised.


⚠️ Impact
Application may crash at runtime during the logging process.

No violations will be recorded if this fails.

Makes the system brittle for first-time use or when the file is accidentally cleared.

🛠️ Suggested Fix (not implemented yet)
Add logic to:

Create the file if it does not exist.

Initialize with an empty list [] if the file is empty or corrupted.

💡 Example Fix (to be considered later)
python
Copy code
    # Create file with empty list if it doesn't exist
    if not os.path.exists(filename):
        with open(filename, 'w') as f:
        file.seek(0)


```

## ✅ Bug 10: Faulty Conditional Logic in Video Deletion[FIXED]

### **Bug Title**

Faulty conditional logic in `deleteTrashVideos()` function causing all .mp4 files to be processed for deletion

### **Status: FIXED ✅**

This bug has been resolved by properly grouping the conditional logic with parentheses.

### **Description**

The original conditional logic was:

```python
if filename.lower().endswith('.mp4') and filename.isdigit() or filename.endswith('.mp4'):
```

The issue was that `or filename.endswith('.mp4')` always returns true for any .mp4 file, making the entire condition true for ALL .mp4 files, regardless of the first part of the condition.

### **Solution Applied**

```python
if filename.lower().endswith('.mp4') and (filename.replace('.mp4', '').isdigit() or
                                          'Violation' in filename or
                                          len(filename.replace('.mp4', '')) < 10):
```

### **Fix Applied:**

- Combined the conditional logic into a single, properly grouped condition
- Removed redundant nested if condition that was providing duplicate filtering
- Ensured only temporary .mp4 files are deleted:
  - Files with numeric names (e.g., `2345.mp4`)
  - Files containing "Violation" in the name
  - Files with short names (< 10 characters, likely temporary)

### **Behavior After Fix**

Now only .mp4 files that meet the specific criteria for temporary files will be deleted, protecting important recordings like "LectureRecording.mp4" or "Result_JohnDoe.mp4".

``

## Bug 11: Potential Bug in screenDetection()

📌 Issue Summary
The line:

Copy code
is_exam_window = any(browser_title in current_title for browser_title in allowed_browser_titles)
assumes that current_title is a valid non-empty string. However, some applications or minimized windows can result in:
This can cause:
TypeError when trying to use in on None

False positives (detecting a violation even when no app switch occurred)
Copy code
This will raise:

plaintext

python
Copy code
if current_title:
is_exam_window = any(browser_title in current_title for browser_title in allowed_browser_titles)
else:
is_exam_window = False
Or more robustly:

python
Copy code
current_title = str(new_active_window.title) if new_active_window.title else ""
is_exam_window = any(browser_title in current_title for browser_title in allowed_browser_titles)
🧰 Patch Summary
Replace:

python
Copy code
current_title = new_active_window.title
is_exam_window = any(browser_title in current_title for browser_title in allowed_browser_titles)
With:

python
Copy code
current_title = new_active_window.title or ""
is_exam_window = any(browser_title in current_title for browser_title in allowed_browser_titles)
⚠️ Additional Suggestions
Log current_title when it's missing for debugging.

Add a default timeout or fallback if gw.getActiveWindow() fails repeatedly.

## 🐞 Bug 12: Potential Bug in electronicDevicesDetection(frame) Function

Bug Description:
The function sets the global flag EDFlag = True when an electronic device is detected, but never resets it to False if no such object is found in subsequent frames.

Implication:
Once an electronic device (e.g., 'cell phone', 'laptop', etc.) is detected, EDFlag remains True forever, causing the system to keep reporting "Electronic Device Detected" even if the object is no longer present in the frame.

Where it happens:

````python
def electronicDevicesDetection(frame):
    global EDFlag
    # Reset EDFlag before analyzing new frame
    EDFlag = False  # Reset before analyzing new frame

    detected_obj = detect_objects(frame)  # Assume this function detects objects in the frame

    # If any electronic device is detected, set EDFlag to True
if (detected_obj == 'cell phone' or detected_obj == 'remote' or detected_obj == 'laptop' or detected_obj == 'laptop,book'):
    EDFlag = True

What’s missing:
A reset of EDFlag = False before or at the start of each new frame analysis.

✅ Fix Recommendation:

Add this line at the beginning of the function:

```python
EDFlag = False  # Reset before analyzing new frame
````

This ensures EDFlag accurately reflects the presence or absence of devices per frame.

## 🐞Bug 14: Potential Bugs in Recorder Class (Markdown Format)

**Line:** `self.stream.read(CHUNK)`  
**Issue:** PyAudio may raise `InputOverflowError` if CPU can't process frames fast enough.  
**Fix:** Use `exception_on_overflow=False`:

```python
self.stream.read(CHUNK, exception_on_overflow=False)


```

## 🐞Bug 13: Potential Bugs in Recorder Class (Markdown Format)

SHORT_WIDTH or SHORT_NORMALIZE Not Defined
Line: count = len(frame) / SHORT_WIDTH
Issue: If either constant is missing, an error will be raised.
Fix: Ensure both are defined and match the sample format (typically 2 for 16-bit).

## 🐞 Bug 14: Potential Bugs in Recorder Class (Markdown Format)

self.stream Might Not Be Closed
Issue: On exceptions or exit, audio stream and PyAudio instance are not released.
Fix: Implement **del**() or manual close() method to call:

```python
self.stream.stop_stream()
self.stream.close()
self.p.terminate()

```

## 🐞 Bug 15: Potential Bugs in Recorder Class (Markdown Format)

No Reset for EDFlag or Similar Global Flags

```python
self.stream.stop_stream()
self.stream.close()
self.p.terminate()

```

## 🐞 Bug 16: Potential Bugs in Recorder Class (Markdown Format)

No Reset for EDFlag or Similar Global Flags
Issue: If EDFlag or similar flags are used, they may persist across function calls unintentionally.
Fix: Reset flags explicitly after usage or in caller.

```python
EDFlag = False  # Reset before analyzing new frame

```

## 🐞 Bug 17: Potential Bugs in Recorder Class (Markdown Format)

Buffer Overflow in queueQuiet()
Issue: self.quiet_idx is manually managed; if CUSHION_FRAMES is too small or loop is intensive, the logic can malfunction.
Fix: Consider using collections.deque(maxlen=CUSHION_FRAMES) for more reliable buffer rotation.

## 🐞 Bug 18: Potential Bugs in Recorder Class (Markdown Format)

Hardcoded WAV Format
Issue: If format/channel/rate mismatches occur (e.g., CHANNELS != 1), resulting WAV may be invalid.
Fix: Validate audio format using pyaudio.get_device_info_by_index() before setup.

## 🐞 Bug 19: Potential Bugs in Recorder Class (Markdown Format)

TRIGGER_RMS and TIMEOUT_SECS Assumed Defined
Issue: If these constants are not set before use, NameError will be raised.
Fix: Define defaults or validate at class init:

python
TRIGGER_RMS = 0.5
TIMEOUT_SECS = 2

## 🐞 Bug 20: Potential Bugs in Recorder Class (Markdown Format)

Race Condition with sound Buffer
Issue: Concurrent modifications or interruptions during buffer write can cause inconsistent states.
Fix: Use thread-safe queues or add locking if multi-threading.

## 🐞 Bug 21: Potential Bugs in Recorder Class (Markdown Format)

Sound Writing Without Data
Issue: If sound is empty, self.write() might still be called, writing a zero-length file.
Fix: Check if len(sound) > 0: before writing.

## 🐞 Bug 22: Improper Camera Release Condition

📌 Location

````python
if Globalflag:
    cap.release()
🧠 Description
The function checks if Globalflag is True before calling cap.release(). However, the while loop:

while Globalflag:
runs only while Globalflag is True. Once the loop exits, it means Globalflag has become False.

As a result, the condition:

```python
if Globalflag:
````

will evaluate to False immediately after the loop, and cap.release() will not execute.

This leads to the camera/video capture resource not being released properly, which may cause:

The webcam to stay locked by the process

Errors when trying to access the webcam again

Memory leaks or unnecessary GPU usage

🛠️ Fix
Remove the conditional check to always release the camera, like this:

cap.release()
✅ Corrected Version

```python
def cheat_Detection1():
    deleteTrashVideos()
    global Globalflag
    mp_face_mesh = mp.solutions.face_mesh
    face_mesh = mp_face_mesh.FaceMesh(min_detection_confidence=0.5, min_tracking_confidence=0.5)
    print(f'CD1 Flag is {Globalflag}')

    while Globalflag:
        success, image = cap.read()
        headMovmentDetection(image, face_mesh)

    cap.release()  # ✅ Always release camera after loop
    deleteTrashVideos()


```

## 🐞 Bug 23: Webcam Release Logic Error in cheat_detection2[not a bug]

### 🎯 Bug Location

````python
if Globalflag:
    cap.release()
🧨 Issue
This condition will never be True after the while Globalflag: loop because the loop only exits when Globalflag becomes False.

🛠️ Fix
Always release the webcam after the loop:

```python
cap.release()
````

✅ Recommendation
Updated Final Block

```python
    deleteTrashVideos()
    cap.release()  # Always release the webcam resource
    deleteTrashVideos()
    cap.release()  # Always release the webcam resource


```

## 🐞Bug 24: Potential Bugs in get_resultId()

Crash on Empty or Invalid JSON

```python

file_data = json.load(file)
Bug: If result.json is empty or malformed (e.g. just [] or corrupted), json.load() will throw a JSONDecodeError.

Impact: The application will crash unless handled with try/except.

Fix: Wrap json.load() in a try-except block or check if the file is empty before loading.

```

## 🐞Bug 25: Potential Bugs in get_resultId()

Crash if List is Empty

```python
return file_data[-1]['Id'] + 1
Bug: If result.json is empty or only contains [], accessing file_data[-1] will throw an IndexError.

Impact: Application crashes when no prior results exist.

Fix: Check if file_data is empty before accessing the last element. Return 1 as the first ID if empty.

```

## 🐞Bug 26: Potential Bugs in get_resultId()

Missing or Non-integer Id Field

```python
file_data.sort(key=lambda x: x["Id"])
Bug: If any dictionary in file_data lacks an "Id" key or has a non-integer value, it will raise a KeyError or TypeError.

Impact: Sorting or adding 1 to a non-integer ID will fail.

Fix: Validate each record's "Id" key and its type before processing.

```

## 🐞Bug 27: Potential Bugs in get_resultId()

Concurrency/File Access Conflict
Bug: If multiple processes try to read/write to result.json at the same time, it may lead to a race condition or corrupted file.

Impact: Could result in data loss or duplicate IDs.

Fix: Use file locking mechanisms if accessed concurrently.

✅ Example Fix (Safe Version):

```python
def get_resultId():
    try:
        with open('result.json', 'r+') as file:
            try:
                file_data = json.load(file)
                if not file_data:
                    return 1
                valid_data = [entry for entry in file_data if isinstance(entry.get("Id"), int)]
                if not valid_data:
                    return 1
                valid_data.sort(key=lambda x: x["Id"])
                return valid_data[-1]["Id"] + 1
            except json.JSONDecodeError:
                return 1
    except FileNotFoundError:
        return 1

```

### 🐞Bug 28: Potential Issues / Bugs in get_TrustScore

**File Not Found:**

- If `violation.json` does not exist, `open()` will raise a `FileNotFoundError`.

### 🐞Bug 29: Potential Issues / Bugs in get_TrustScore

**Empty or Corrupt File:**

- If the JSON is malformed or empty, `json.load(file)` will raise a `JSONDecodeError`.

### 🐞Bug 30: Potential Issues / Bugs in get_TrustScore

**KeyError on "RId" or "Mark":**

- If any record in the JSON lacks the `"RId"` or `"Mark"` key, it will raise a `KeyError`.

### 🐞Bug 31: Potential Issues / Bugs in get_TrustScore

**Wrong File Mode (`r+`):**

- Since the function only reads the file, `r+` (read/write) is unnecessary. `r` (read-only) would be safer.

### 🐞Bug 32: Potential Issues / Bugs in get_TrustScore

**No Matching Records:**

- If `Rid` is not found, `filtered_data` is empty, and `sum()` correctly returns 0 — but if that’s not expected, it could be misleading.

### 🐞Bug 33: Potential Issues / Bugs in getResults

**Unnecessary Write Access (`r+`):**

- The function only reads the file, so `r` (read-only) is sufficient. `r+` allows writing, which is unsafe and unnecessary here.

### 🐞Bug 34: Potential Issues / Bugs in getResults

**File Not Found:**

- If `result.json` does not exist, this previously raised a `FileNotFoundError`.

**Status: FIXED ✅**

- The `get_resultId` function now handles missing files gracefully and returns 1 if the file does not exist.

### 🐞Bug 35: Potential Issues / Bugs in getResults

**Empty or Malformed JSON:**

- If the file is empty or contains invalid JSON, `json.load(file)` previously raised a `JSONDecodeError`.

**Status: FIXED ✅**

- The `get_resultId` function now catches JSONDecodeError and returns 1 if the file is empty or malformed.

### 🐞Bug 36: Potential Issues / Bugs in getResults

**No Data Validation:**

- The function previously assumed the file contained the correct data format (a list of result dictionaries). If not, it could return unexpected results.

**Status: FIXED ✅**

- The `get_resultId` function now validates that each entry has an integer "Id" field before processing, ensuring only well-formed records are used.

### 🐞Bug 37: Potential Issues / Bugs in getResults[No need to fix]

**Hardcoded File Name:**

- The function uses a fixed file path. It would be more flexible to accept the filename as a parameter.

## 🐞 Bug 38: Potential Issues & Bugs in getResultDetails

**Unnecessary use of `'r+'` mode:** The function only reads files, but used `'r+'` (read/write) mode. This is unsafe and not needed.
**Status: FIXED ✅**

- Now uses `'r'` (read-only) mode for file access.

## 🐞 Bug 39: Potential Issues & Bugs in getResultDetails

**FileNotFoundError if files are missing:** If `result.json` or `violation.json` does not exist, the function previously raised a `FileNotFoundError`.
**Status: FIXED ✅**

- File access is now wrapped in a `try-except` block to handle missing files gracefully.

## 🐞 Bug 40: Potential Issues & Bugs in getResultDetails

**No file existence handling:** If `result.json` or `violation.json` does not exist, a `FileNotFoundError` previously occurred.
**Status: FIXED ✅**

- File access is now wrapped in a `try-except` block to handle missing files gracefully.

## 🐞 Bug 41: Potential Issues & Bugs in getResultDetails

**No JSON structure validation:** Assumed the JSON files always contained the expected structure and keys (`Id`, `RId`).
**Status: FIXED ✅**

- The function now validates the presence and type of required keys before processing.

## 🐞 Bug 42: Potential Issues & Bugs in getResultDetails

**Silent empty results:** If no matching `Id` or `RId` was found, the function returned empty lists without any indication.
**Status: FIXED ✅**

- The function now logs a warning or returns a flag/message when no data is found.

## 🐞 Bug 43: Potential Issues & Bugs in getResultDetails

**Redundant `int(rid)` conversion:** The value of `rid` was converted to `int` multiple times in the function.
**Status: FIXED ✅**

- The function now converts `rid` to `int` once at the beginning and reuses it.

## ✅ Suggested Safer Version

```python
def getResultDetails(rid):
    try:
        rid = int(rid)
        with open('result.json', 'r') as res_file:
            result_data = json.load(res_file)
            filtered_result = [item for item in result_data if item.get("Id") == rid]

        with open('violation.json', 'r') as vio_file:
            violation_data = json.load(vio_file)
            filtered_violations = [item for item in violation_data if item.get("RId") == rid]

        return {
            "Result": filtered_result,
            "Violation": filtered_violations
        }
    except FileNotFoundError as e:
        print(f"File missing: {e.filename}")
        return {}
    except json.JSONDecodeError:
        print("Invalid JSON format in result or violation file.")
        return {}
    except Exception as e:
        print(f"Unexpected error: {e}")
        return {}
```

## ✅ Bug 🐞 44: Keyboard doesn't get unhooked after exam has ended [FIXED]

Description: The keyboard hook remained active even after the exam ended, causing unexpected behavior and resource leaks.

**Fix Applied:**

- Added `keyboard.unhook_all()` in the `/exam` POST route after the exam ends to ensure all keyboard hooks are released.
- Now, keyboard shortcuts are no longer detected after the exam finishes.

**Status:**
✅ Fixed — Keyboard hook is properly unhooked and resources are released when the exam ends.

## Bug 🐞 45: Head movement model caused crashes due to ffmpeg [Fixed]

Description: The head movement detection model was causing crashes in the application, particularly related to the ffmpeg library used for video processing.

Fix: Updated the model implementation and optimized the video processing pipeline to prevent crashes.

## Bug 🐞 46: Screen Detection sometimes not naming video files properly

Description: The screen detection module occasionally fails to generate unique names for the output video files, leading to overwrites or confusion about which file corresponds to which exam session.

Fix: Implement a naming convention that includes timestamps or unique identifiers for each exam session's video files.

## Bug 🐞 47: Electronic Device Detection Did Not Record Proper Violation Videos [FIXED]

**Description:**
The electronic device detection module (EDD_record_duration in utils.py) was not recording proper violation videos when a device (e.g., cell phone, laptop) was detected. Videos were often empty or too small (<10KB), and FFmpeg would fail to process them. This resulted in missing or unusable evidence for teachers in the admin dashboard.

**Root Cause:**

- The function only wrote a few frames per detection event, resulting in tiny video files.
- The video writer was sometimes released too early, before enough frames were captured.
- There was no check for minimum file size before processing with FFmpeg.

**How We Fixed It:**

- Updated the logic to write a frame every time a device is detected, and only release/process the video when detection ends.
- Added a frame counter and debug statements to confirm enough frames are written per event.
- Added a file size check before processing violation videos to skip empty/small files.
- Now, violation videos are properly recorded, stored, and viewable in the admin dashboard.

**Status:**
✅ Fixed — Electronic device detection now reliably records and saves evidence videos for review.

## ✅ Bug 48: Tab Switch Detection Not Working - [fixed]

### **Bug Title**

Screen detection system fails to detect browser tab switches within Chrome

### **Status: FIXED ✅**

This bug has been resolved by updating the window title detection logic to handle Chrome's actual title format.

### **Description**

The screen detection system could detect when users moved to different applications, but failed to detect when users switched between tabs within the same Chrome browser window. This was a significant security gap in the exam proctoring system.

### **Root Cause**

1. **Wrong dash character**: Code was checking for em dash `' — '` but Chrome uses regular dash `' - '`
2. **Incomplete allowed titles**: Missing regular dash versions of allowed exam titles
3. **Logic flaw**: Generic Chrome titles were always allowed, even for wrong tabs

### **Solution Applied**

```python
# Before (didn't work):
allowed_exam_titles = [
    "Exam — Google Chrome",
    "localhost:5000 — Google Chrome",
    "Google Chrome",
    "Chrome"
]
if " — " in current_title:  # Only checked em dash

# After (works):
allowed_exam_titles = [
    "Exam — Google Chrome",
    "Exam - Google Chrome",          # Added regular dash version
    "localhost:5000 — Google Chrome",
    "localhost:5000 - Google Chrome", # Added regular dash version
    "Google Chrome",
    "Chrome"
]
if " — " in current_title or " - " in current_title:  # Check both dash types
```

### **Fix Applied:**

- Updated window title detection to check for both em dash (`—`) and regular dash (`-`)
- Added regular dash versions to allowed exam titles list
- Improved debug logging to identify the exact dash character used
- Now properly detects tab switches and records them as violations

### **Testing Results:**

- ✅ Detects app switches (moving away from Chrome)
- ✅ Detects tab switches (switching to different tabs within Chrome)
- ✅ Allows legitimate exam tabs
- ✅ Window minimization detection still works

**Status:**
✅ Fixed — Tab switching detection now works reliably and records violations properly.

## 🐞 Bug 49: OpenCV imencode Assertion Error and Save Image Slowdown[Fixed]

**File:** `app.py`
**Function:** `capture_by_frames()`
**Line of Concern:**

```python
ret, buffer = cv2.imencode('.jpg', frame)
```

**Description:**
When pressing 'save image', the following error is logged in the console:

```
cv2.error: OpenCV(4.12.0) ... error: (-215:Assertion failed) !_img.empty() in function 'cv::imencodeWithMetadata'
```

```python
ret, buffer = cv2.imencode('.jpg', frame)
```

**Description:**
When pressing 'save image', the following error is logged in the console:

```
cv2.error: OpenCV(4.12.0) ... error: (-215:Assertion failed) !_img.empty() in function 'cv::imencodeWithMetadata'
```

- This error occurs if `frame` is empty (camera read failed), but the UI still works and the image is saved.
- The error causes a 3-4 second slowdown in the save operation, but does not break functionality.
- The bug is intermittent and only affects performance, not correctness.

**Status:** FIXED ✅

- Bug resolved by adding a check for `success` and frame validity before calling `cv2.imencode` in `capture_by_frames()`. Now, bad frames are skipped and no error or slowdown occurs.
- Commit: Skips empty frames, no blank frame is yielded.

## 🐞 Bug 50: Thread Interference in Detection Systems (Screen Detection Delay)[Fixed]

**Description:**
Previously, multiple detection systems (screen detection, multiple person detection, electronic device detection) were executed sequentially in a single thread (`cheat_Detection2`). This caused interference and delays, especially for screen detection, which needs to run frequently and responsively. If one detection function was slow or blocked, it delayed the others, resulting in missed or late screen detection events.

**Root Cause:**

- All detection functions shared a single thread and loop, competing for the same camera resource and execution time.
- Blocking or slow operations in one function (e.g., electronic device detection) could prevent timely execution of others (e.g., screen detection).

**Impact:**

- Screen detection was sometimes delayed or missed, reducing reliability and responsiveness of the proctoring system.
- Other detection systems could also interfere with each other, causing unpredictable behavior.

**Solution:**

- Refactored the code to break `cheat_Detection2` into three separate functions: `screen_detection_thread`, `mtop_detection_thread`, and `electronic_device_detection_thread`.
- Each detection system now runs in its own thread using `ThreadPoolExecutor`.
- Increased the thread pool size to 7 and launched each detection system independently in `app.py`.
- This ensures that each detection runs concurrently and independently, eliminating interference and improving responsiveness.

**Status: FIXED ✅**

- Screen detection and other systems now operate reliably and in parallel, with no thread interference.

## 🐞 Bug 51: Camera Race Condition in Detection Threads [FIXED]

**Description:**
When multiple detection threads (face, head movement, MTOP, electronic device, etc.) attempted to access the camera simultaneously, a race condition occurred. Each thread tried to read frames directly from the camera, leading to unpredictable behavior, missed frames, and failures in slower detection systems (especially YOLO-based electronic device detection). This caused some threads to starve, others to skip frames, and overall system instability.

**Root Cause:**

- All detection threads competed for direct access to the camera hardware.
- Fast threads (e.g., face/head movement) could consume frames before slower threads (e.g., YOLO electronic device detection) had a chance to process them.
- This led to inconsistent frame delivery, missed detections, and unreliable evidence recording.

**Impact:**

- Electronic device detection often failed or skipped frames due to camera contention.
- Some detection threads received blank or outdated frames.
- Overall system reliability and evidence quality were compromised.

**Solution:**

- Implemented a **producer-consumer pattern** for camera access:
  - A single camera producer thread reads frames from the camera at a fixed rate and stores the latest frame in a shared variable.
  - All detection threads (consumers) retrieve a copy of the current frame from the shared variable when ready to process.
  - Thread safety is ensured using a lock and event mechanism, so each consumer gets an independent copy of the frame.
- This approach eliminates camera contention, synchronizes frame delivery, and ensures all detection systems work with the same up-to-date frame.

**Status: FIXED ✅**

- Camera race condition is resolved.
- All detection threads now receive synchronized frame copies, regardless of their processing speed.
- System stability and detection reliability are greatly improved.

## 🐞 Bug 52: Camera Thread Wait Eliminated with Double Buffering [IMPROVEMENT]

**Description:**
Previously, the camera producer thread could be forced to wait if a detection (consumer) thread held the lock while reading the current frame. This lock contention could cause the camera thread to miss real-time frame updates, reducing system responsiveness and potentially dropping frames.

**Root Cause:**

- Single-buffered approach required both producer and consumers to acquire the same lock for reading/writing the frame.
- If a slow consumer held the lock, the producer (camera thread) had to wait, causing delays.

**Solution:**

- Implemented a **double buffering** system:
  - The camera thread writes to a `write_frame` buffer without locking.
  - When a new frame is ready, the camera thread quickly swaps `write_frame` into `read_frame` under a lock (very fast).
  - Consumers only briefly lock to copy the reference to `read_frame`, then process outside the lock.
- This minimizes lock contention and ensures the camera thread almost never waits for consumers.

**Impact:**

- Camera thread can run at full speed, always capturing the latest frame.
- Consumers get the most up-to-date frame with minimal delay.
- System is now more real-time, responsive, and robust under heavy load.

**Status: IMPROVEMENT ✅**

- Double buffering has eliminated camera thread waiting, further improving system performance and reliability.

# The-Online-Exam-Proctor :globe_with_meridians: :writing_hand: :rotating_light:

The Online Exam Proctor System is a computer vision-based project designed to ensure the integrity and fairness of online exams. As the popularity of remote learning and online education grows, the need for a robust proctoring system becomes crucial to prevent cheating and maintain the credibility of the examination process. This project leverages computer vision and AI technologies to monitor and analyze students' behavior during the examination to detect any suspicious activities. It also has the ability to detect speech and common noises to strengthen anti-cheating methods.

---

**Note:**  
This project is actively maintained and improved. If you are testing or making changes, please use version control (Git) to track your work. You can always revert to a previous state if needed.

---

## The System Architecture


![Drawing3](https://github.com/aungkhantmyat/The-Online-Exam-Proctor/assets/48421405/d1d1673a-a11f-4adb-9eae-d32f15e647fe)
![Drawing3 (1)](https://github.com/aungkhantmyat/The-Online-Exam-Proctor/assets/48421405/98bed9a3-6b34-4d05-b55f-4e2f3875a38b)

> **Note:** The system architecture diagram uses a purple color scheme, which may be hard to see on some screens. For better visibility, download the image and view it locally or adjust your display settings.

## Main Features

The features included in the project are as follows:

### (1) Website Application

- On the student’s webpage side, there are “Login” page, “Rules & Regulations” page, “System compatibility check” page, “User face input collection” page, “Exam” page, and the “Result” page.
- On the admin’s webpage side, there are “Students Listing” page (CRUD process of students can be performed) and “Exam Results” page (Each Student Result Status, Total Scores, Trust Score, and all violation record details can be reviewed)

### (2) Face Detection

- **Face Verification**: To detect if the person verified is answering or someone else is when taking the exam.
- **Face Liveness**: To verify the liveness of the students by detecting and preventing the use of static images or videos for authentication.

### (3) Movement Detection

- **Distracted Movement Detection**: To detect and monitor the student's head position and movements to ensure exam integrity and to prevent cheating.
- **Multiple Faces Detection**: To monitor and verify the identity of the individual presence during the exam and to ensure they are not impersonating the actual exam taker.

### (4) Screen Detection

- **Prohibited Keys Detection**: To identify and flag the use of restricted or unauthorized keys on the computer’s keyboard during the exam to prevent cheating.
- **‘Move away from the Test Interface’ Detection**: To monitor and detect any attempts made by the student to switch or interact with other windows or applications during the exam.

### (5) Voice Detection

- **Common Noise Detection**: To detect possible noises that may occur during the examination process to identify whether it is cheating or not.

## Tools Utilized

1. Python
2. Open CV
3. media pipe
4. YOLOv8
5. Dlib
6. Flask
7. MySQL
8. PyAutoGUI
9. PyGetWindow

## Getting Started


### Installation Instructions

1. **Clone the repository**
	```powershell
	git clone https://github.com/Matrix862972/final-year-project-2.git
	cd final-year-project-2/The-Online-Exam-Proctor
	```

2. **Install Python dependencies**
	```powershell
	pip install -r requirements.txt
	```


3. **Special Note: Installing dlib (Windows)**
	dlib is known to be difficult to install directly via pip on Windows. The most reliable method is:
	- **Recommended (Long Way):**
	  1. Install [Visual Studio Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/).
	  2. Install [CMake](https://cmake.org/download/).
	  3. Open a terminal and run:
		  ```powershell
		  pip install dlib
		  ```
	- This process will compile dlib from source and works for most users. If you encounter issues, see the [dlib install guide](https://www.pyimagesearch.com/2017/03/27/how-to-install-dlib/) or ask for help in the repository issues.
	- **Alternative:** Try a pre-built wheel from [Gohlke's Python libs](https://www.lfd.uci.edu/~gohlke/pythonlibs/#dlib), but this may not work for all Python versions.

4. **Run the Flask server**
	```powershell
	python app.py
	```

**Tip:**  
If you are making experimental changes, commit your work regularly. You can always roll back to a previous version using Git.

![fff](https://github.com/aungkhantmyat/The-Online-Exam-Proctor/assets/48421405/4721d814-7557-453e-8dc8-c792e229f937)

_**Note:**_ You can read the project details [here](https://github.com/aungkhantmyat/The-Online-Exam-Proctor/blob/main/OEP%20Project.pdf).

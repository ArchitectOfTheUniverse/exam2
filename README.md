# Quiz Application  

## About the Project  
The **Quiz Application** is designed to allow users to test their knowledge in various fields. The application provides a user-friendly interface and offers diverse features such as quizzes on specific topics, mixed quizzes, and a results tracking system.  

---

## Features  
### User Functionality:  
- **User Authentication**:  
  - Login with a username and password.  
  - Registration for new users with the following details:  
    - Unique username (existing usernames cannot be reused).  
    - Password.  
    - Date of birth.  

- **Main Menu**:  
  - Start a new quiz.  
  - View results of past quizzes.  
  - View the top-20 leaderboard for a specific quiz.  
  - Update settings (password and date of birth).  
  - Exit the application.  

- **Quizzes**:  
  - Choose from different quiz topics (e.g., History, Geography, Biology).  
  - Mixed quiz option to get random questions from various topics.  
  - Each quiz consists of 20 questions.  
  - Questions can have one or multiple correct answers. Incorrect or incomplete answers do not score points.  
  - After completing a quiz, users receive:  
    - Their total correct answers.  
    - Their rank in the leaderboard.  

### Admin Utility:  
- Create and edit quizzes and their questions.  
- Secure login for administrators.  

---

## Design Principles  
- **SOLID Principles**: Applied to ensure maintainable, scalable, and flexible code.  
- **Design Patterns**: Includes patterns like Singleton, Strategy, Observer, and Factory to enhance code structure.  

---

## Technologies  
- **Programming Language**: Python  
- **Libraries**:  
  - `colorama`: For colored terminal output.  
  - `random`: For generating random quizzes.  
  - `json`: For data storage.
  - `rich`: For table menu  

---

## Getting Started  
### Prerequisites  
- Python 3.10 or higher installed on your system.  


### Running
python quiz_app.py


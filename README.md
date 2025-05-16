# MyHealthFirst - Your Personalized Healthcare Platform

## Overview

MyHealthFirst is a comprehensive healthcare website designed to connect patients and doctors, offering features for registration, login, and role-based dashboards. This platform aims to provide a seamless experience for users to manage their health information and interact with healthcare professionals.

## Features

* **User Registration:** Allows new users to create accounts, specifying whether they are a patient or a doctor. Includes fields for personal details, contact information, and profile picture upload.
* **Role-Based Login:** Enables registered users to log in securely. Upon successful login, users are redirected to their specific dashboards based on their role (Patient or Doctor).
* **Patient Dashboard:** Provides patients with an overview of their profile information, including name, email, address, and profile picture. (Further features for patients can be added here, e.g., appointment booking, health records).
* **Doctor Dashboard:** Offers doctors a dedicated space to manage their profiles and potentially interact with patients. (Further features for doctors can be added here, e.g., appointment management, patient records).
* **Profile Picture:** Users can upload a profile picture during registration, which is displayed on their respective dashboards.
* **State and City Dropdowns:** Registration form includes dynamic dropdowns for selecting state and city.
* **Interactive Background:** Features a visually engaging `particles.js` background.
* **Responsive Design:** The layout is designed to be responsive and work well on various screen sizes.
* **Secure Form Handling:** Utilizes Django's CSRF protection for form submissions.

## Technologies Used

* **Django:** A high-level Python web framework used for the backend development.
* **HTML:** Markup language for structuring the web pages.
* **CSS:** Styling language for controlling the presentation of the web pages.
* **JavaScript:** Used for interactive elements, such as the dynamic state/city dropdowns and the `particles.js` background.
* **particles.js:** A lightweight JavaScript library for creating dynamic particle backgrounds.
* **Bootstrap:** A CSS framework for responsive layout and styling.
* **Font Awesome:** A library of icons for enhanced visual appeal.
** Used SQLite3 for database**

## Setup and Installation

1.  **Clone the repository:**
    ```bash
    git clone [repository_url]
    cd myhealthfirst
    ```

2.  **Create a virtual environment (recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On macOS/Linux
    venv\Scripts\activate  # On Windows
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
    *(You might need to create a `requirements.txt` file if you haven't already. You can generate it using `pip freeze > requirements.txt` after installing the necessary Django packages.)*

4.  **Make migrations:**
    ```bash
    python manage.py makemigrations your_app_name  # Replace 'your_app_name'
    python manage.py migrate
    ```

5.  **Create a superuser (for Django admin access, optional but recommended):**
    ```bash
    python manage.py createsuperuser
    ```

6.  **Run the development server:**
    ```bash
    python manage.py runserver
    ```

7.  **Open your web browser and navigate to `http://127.0.0.1:8000/`** (or the address provided by the development server).


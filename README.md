# Ave Geofence System

## Description

AveGeofencing is a startup built and maintained by me and my roommate Daniel ([https://github.com/ELECTRON11111]). This is the backend API built with FastAPI and SQLAlchemy that enables users to create, manage, and track geofences. It allows students to join geofences, record attendance, and provides real-time updates.

## Features

- Admin can create geofences and generate unique fence codes.
- Students can join geofences using a code.
- Attendance tracking for students within a geofence.
- Real-time updates on students joining geofences.
- Secure authentication and authorization. Session management with cookies.
- Data persistence using MySQL with SQLAlchemy ORM.
- Users can request for reset password emails to reset their passwords.

## Technologies Used

- **FastAPI** - High-performance web framework for building APIs.
- **SQLAlchemy** - ORM for database interactions.
- **Uvicorn** - ASGI server for running FastAPI applications.
- **MySQL** - Database for storing user and geofence data.
- **Docker** - Containerized deployment.

## Installation

### Prerequisites

Ensure you have the following installed:

- Python 3.10+
- Virtual environment (optional but recommended)
- MySQL (if using MySQL as the database)
- Docker

### Steps
#### With vanilla FastAPI and Uvicorn
1. Clone the repository:
   ```sh
   git clone https://github.com/yourusername/geofence-system.git
   cd geofence-system
   ```
2. Create and activate a virtual environment:
   ```sh
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```
3. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
4. Set up environment variables:
   ```sh
   cp .env.example .env  # Update .env with database credentials
   ```
5. Start the server:
   ```sh
   uvicorn Backend:app --reload
   ```
# With Docker Compose
1. Clone the repository
2. Build and run the docker image using Docker Compose:
    ```sh
    docker compose build
    docker compose up
    ```
## Contributing

Contributions are welcome! Feel free to open an issue or submit a pull request.

## Contact

For any inquiries, reach out to [courageadedara@gmail.com] or visit the repository at [https://github.com/TechBroAdedara/Ave].


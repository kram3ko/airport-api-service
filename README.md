# Airport API Service

![Application Diagram](https://github.com/user-attachments/assets/8dc6f28d-7e73-4101-a9fb-39120e3dcd8a)

---

## Overview

**Airport API Service** is a RESTful API built with Django to manage airport, flight, ticket, and user data. The service
ensures high performance and reliability with PostgreSQL, containerization via Docker, and reverse proxying through
Nginx. It also includes a user-friendly database management interface powered by pgAdmin.

---

## Key Features

- Comprehensive API for managing airports, flights, tickets, routes, and users
- JWT-based authentication with role-based access control (admin and regular users)
- PostgreSQL as a robust relational database ensuring data integrity
- Efficient static file hosting and API proxying via Nginx
- Seamless database visualization and management with pgAdmin
- Fully containerized deployment using Docker and Docker Compose
- Swagger Documentation

---

## Technology Stack

- **Python 3.13**
- **Django 5.2** with Django Rest Framework (DRF) — Backend framework
- **PostgreSQL** — Primary relational database
- **Docker & Docker Compose** — Containerization and orchestration
- **Nginx** — Web server and reverse proxy
- **pgAdmin** — Web-based GUI for PostgreSQL

---

## Getting Started

### 1. Clone the Repository

```bash
git clone git@github.com:kram3ko/airport-api-service.git
```
Full docker version
```bash
git clone git@github.com:kram3ko/docker-airport-api.git

```

### 2. Set Up Environment Variables

Create a `.env` file in the project root directory.
Refer to the provided `.env.example` file for default values and structure.

### 3. Build and Run All Services

Ensure that Docker and Docker Compose are installed on your system. Then run:

```bash
docker-compose up --build
```

This will start the following containers:

- Django application (API)
- PostgreSQL database
- Nginx server
- pgAdmin (for database management)

### Service Endpoints

- **API Swagger Documentation root**: [http://localhost/api/doc/swagger/](http://localhost/api/doc/swagger/)
- **Django Admin**: [http://localhost/admin/](http://localhost/admin/)
- **pgAdmin**: [http://localhost:5050/](http://localhost:5050/) (login credentials from `.env`)
- **User Registration page**: [http://localhost/users/register](http://localhost/users/register/)

---

## Using the API

- All main endpoints are rooted under `/api/`
- Obtain tokens via `/api/auth/login/` (JWT authentication)
- Manage users, tickets, flights, and more using the OpenAPI schema (if `/api/docs/` is implemented)

### Example: Retrieve All Airports

```bash
GET http://localhost/api/airports/
```

---

## Managing the Database via pgAdmin

1. Open pgAdmin: [http://localhost:8888](http://localhost:8888)
2. Login using the email and password specified in the `.env` file.
3. Create a new server with the following settings:
    - **Host**: `db`
    - **Database/User/Password**: from your `.env` file

---

## Common Management Commands

Run the following commands inside the Django container:

- **Apply Database Migrations**:
  ```bash
  docker-compose exec django python manage.py migrate
  ```
- **Load fixture**:
  ```bash
  docker-compose exec django python manage.py loaddata airport-api.json
  ```
- **Create a Superuser**:
  ```bash
  docker-compose exec django python manage.py createsuperuser 
  ```

- **View Logs**:
  ```bash
  docker-compose logs -f
  ```

---

## Dependency Management

To install new Python dependencies, add them to `pyproject.toml` and rebuild the container:

```bash
docker-compose build --no-cache
```

---

## Project Structure

```plaintext
.
├── airports/                # Django app: airports
├── airplanes/               # Django app: airplanes
├── flights/                 # Django app: flights
├── tickets/                 # Django app: tickets
├── users/                   # Django app: users
├── config/                  # Django project configuration (settings, urls, etc.)
├── docker/
│   ├── django/              # Dockerfile for Django
│   └── nginx/               # Nginx configuration files
├── docker-compose.yml       # Docker Compose configuration
├── .env                     # Environment variables
├── .env.example             # Example environment variable file
└── README.md                # Project documentation
```

---

## Running Tests

Run the Django test suite inside the container:

```bash
docker-compose exec django python manage.py test
```

---

## License

This project is licensed under the [MIT License](LICENSE).


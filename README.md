# Mattilda

This is the code challenge for [Mattilda](https://mattilda.io/). The full details and requirements [here](./docs/Proyecto%20Mattilda_Devs.pdf).

The most general implentation requirements ask for:

- CRUD implementations for school, students and invoices.

- Add support models to get things like:
  - How much a student owes to a school.
  - How many students are enrolled in a school.

The proposed solution leverages on [ports and adapters](<https://en.wikipedia.org/wiki/Hexagonal_architecture_(software)>) architecture which allows for a clean separation of concerns and easy testing.

There are four modules in the project:

- School
- Student
- Invoice
- Shared. Which holds non business|domain related code.

## Project setup

### Running

- The development environment leverages on docker compose to run three containers:

  1. A Postgres DB
  2. A Redis pubsub and cache server
  3. The application server

- Open a terminal in the `deployment` folder and execute

```cmd
make start
```

- Run database migrations. The project uses alembic to manage the database schema. Run

```cmd
make run.migrations
```

For local code adjustments

- This project requires [Python](https://www.python.org/downloads/) version 3.10+ installation
- After installation. Optionally create a virtual env. Open a terminal and run

```bash
python3 -m venv venv
source venv/bin/activate
```

- Install the project dependencies

```bash
pip install -r requirements.txt
```

### Supported operations

The base supported operations to get a working solution are:

- Create school </mattilda/schools>
- Create student </mattilda/students>
- Create enrollment </mattilda/schools/{school_id}/enrollments/>. Basically a student enrolls in a school and a monthly fee is set.
- Generate invoices </mattilda/schools/{school_id}/invoices/>.

With service running, visit the [API documentation](http://localhost:8000/docs#/) for more details and supported operations.

### Running tests
```bash
pytest test
```

### Proposed enhacements

- Enrich automated tests
- Build a full featured UI for the app.
- Leverage on cache for read operations.
- Leverage fully on event driven architecture already mounted.
- Notifications to parties. Collections Notifications, etc.

# Database Development

The application uses PostgreSQL as the primary relational database.

Database access is implemented with SQLAlchemy, while schema migrations are managed with Alembic.

## Configuration

The database connection is configured through the `DATABASE_URL` environment variable.

Example:

```env
DATABASE_URL=postgresql+psycopg://app:app@localhost:5432/intelligent_saas
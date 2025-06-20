# PriceFetch - Bitcoin Price Service

A real-time Bitcoin price service that fetches data from CoinGecko API, stores it in PostgreSQL, and serves requests through Redis caching.

## Features

-   Real-time Bitcoin price fetching from CoinGecko API
-   Historical price data storage and retrieval
-   Redis caching with configurable TTL
-   Docker support for easy deployment
-   Comprehensive test suite
-   RESTful API endpoints

## Architecture

### Components

1. **FastAPI Application**

    - RESTful API endpoints
    - Request validation
    - Error handling
    - Rate limiting

2. **PostgreSQL Database**

    - Time-series data storage
    - Efficient range queries
    - ACID compliance

3. **Redis Cache**

    - In-memory caching
    - Configurable TTL
    - Fast response times

4. **CoinGecko API Integration**
    - Real-time price data
    - Historical price data
    - Error handling
    - Rate limit management

### Database Choice Justification

I chose PostgreSQL for this project because:

1. **Time-Series Data**

    - Efficient timestamp-based queries
    - Built-in timestamp operations
    - Range query optimization

2. **Data Consistency**

    - ACID compliance ensures data integrity
    - Transaction support
    - Reliable data storage

3. **Query Performance**

    - Indexed timestamp columns
    - Efficient range queries
    - Built-in optimization for time-series data

4. **Scalability**
    - Horizontal scaling capabilities
    - Partitioning support
    - Mature ecosystem

## API Endpoints

### 1. Get Current Price

```http
GET /api/v1/current-price
```

Response:

```json
{
	"price": 105487.095,
	"timestamp": 1749994297000
}
```

### 2. Get Price History

```http
GET /api/v1/price-history?from_timestamp={from}&to_timestamp={to}
```

Query Parameters:

-   `from_timestamp`: Start time in seconds (required)
-   `to_timestamp`: End time in seconds (required)

1. 24-hour range:

```http
GET /api/v1/price-history?from_timestamp=1749752399&to_timestamp=1749838799
```

2. 5-day range:

```http
GET /api/v1/price-history?from_timestamp=1749397199&to_timestamp=1749838799
```

Note: Timestamps are in Unix timestamp format (seconds since epoch). The examples above use:

-   24-hour range: June 12, 2025 6:19:59 PM to June 13, 2025 6:19:59 PM
-   5-day range: June 8, 2025 6:19:59 PM to June 13, 2025 6:19:59 PM

**Important Notes:**
- **Query parameters** use **seconds** (Unix timestamp format)
- **Response timestamps** are in **milliseconds** for precision
- Results are ordered by timestamp descending (newest first)

Response:

```json
{
	"prices": [
		{
			"timestamp": 1749981787521,
			"price": 104941.085
		},
		{
			"timestamp": 1749978205180,
			"price": 105211.979
		}
	]
}
```

## Setup & Installation

### Prerequisites

-   Docker and Docker Compose
-   Python 3.11+
-   PostgreSQL 14+
-   Redis

## Environment Variables

### For Docker Compose

When running with Docker Compose, create a `.env` file with:

```env
POSTGRES_SERVER=db    #  use 'db' as it's the service name in docker-compose
POSTGRES_USER=your_user
POSTGRES_PASSWORD=your_password
POSTGRES_DB=your_db
POSTGRES_PORT=your_port_number (not 5432 for me because I have my own postgres running on it.)
COINGECKO_API_KEY=your_api_key
```

### Running with Docker

1. Build and start the services:

```bash
docker compose up --build
```

or

```bash
docker compose up -d
```

2. Run database migrations (required for first-time setup):

```bash
# Get into the API container
docker compose exec api bash

# Run the migrations
alembic upgrade head
```

3. The API will be available at `http://localhost:8000`

## Testing

Run the test suite:

```bash
pytest
```

Run with coverage:

```bash
pytest --cov=app tests/
```

## Database Management

### PgAdmin Access

The project includes PgAdmin for database management. Access it at:

-   URL: `http://localhost:5050`
-   Email: `admin@admin.com`
-   Password: `admin`

#### Adding the Database Server in PgAdmin

1. Log in to PgAdmin
2. Right-click on "Servers" → "Register" → "Server"
3. In the "General" tab:
    - Name: `PriceFetch` (or any name you prefer)
4. In the "Connection" tab:
    - Host: `db` (when using Docker)
    - Port: `5432` (when using Docker)
    - Database: `your_db` (your POSTGRES_DB value)
    - Username: Your POSTGRES_USER value
    - Password: Your POSTGRES_PASSWORD value
5. Click "Save"

#### Common PgAdmin Operations

-   View database tables
-   Execute SQL queries
-   Monitor database performance
-   Manage database users
-   Backup and restore data

## Caching Strategy

-   Current price is cached for 300 seconds (configurable via `CACHE_TTL`, coingecko public api is 1 min cache)
-   Cache-through pattern: check cache → fetch from API → store in DB → update cache
-   Redis provides fast response times for repeated requests
-   Makes user not waste CoinGecko API requests
-   Simple TTL expiration (no active invalidation)

## Error Handling

-   Rate limit handling for CoinGecko API
-   Cache miss handling
-   Input validation

## Performance Considerations

-   Redis caching for fast response times
-   Database indexes on timestamp columns
-   Connection pooling
-   Efficient batch operations
-   Configurable TTL for cache

## Future Enhancements

-   Pagination for historical data
-   More cryptocurrency options

## License

MIT License

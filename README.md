# Automated Events Scraper

## An Intelligent Web Scraping System for Architectural Events

This project automates the collection and publication of architectural events from multiple sources to WordPress, featuring AI-powered content enhancement and image processing.

## Quick Start Guide 🚀

### Comprehensive Event Processing and Deployment Pipeline (Single Command). For pro user (not recommended for everybody.)
```commandline
podman-compose up -d && \
./restore_data.sh db_data_backup.sql.gz && \
uv run main.py event-url all && \
uv run main.py process-image all && \
uv run main.py event-web-content all && \
uv run main.py generate-content-by-gemini-ai all && \
uv run main.py upload-media all && \
uv run main.py create-event all && \
uv run main.py update-event-category all && \
uv run main.py update-event all && \
./dump_db.sh && \
git add db_data_backup.sql.gz && \
git commit -m "latest db data added." && \
git push -u origin dev && \
git checkout master && \
git merge dev && \
git push -u origin master && \
git checkout dev && \
podman-compose down
```
---

### Event Statistics SQL Queries

This document explains how to retrieve event statistics from the `events` table, either for today's date or any specific date, using SQL queries. These statistics include counts of events per `website_name` and a total count of all matching events.

---

### i. Get Today's Event Statistics

This query returns the number of events per `website_name` for today, along with a total row at the end.

### Query

```sql
SELECT website_name, COUNT(*) AS total_events
FROM events
WHERE DATE(created_at) = CURRENT_DATE
  AND DATE(updated_at) = CURRENT_DATE
  AND remote_event_id IS NOT NULL
GROUP BY website_name

UNION ALL

SELECT 'total' AS website_name, COUNT(*) AS total_events
FROM events
WHERE DATE(created_at) = CURRENT_DATE
  AND DATE(updated_at) = CURRENT_DATE
  AND remote_event_id IS NOT NULL;
```

### Terminal command
```commandline
podman exec -it $(podman ps --filter "ancestor=postgres:16-alpine" --format "{{.Names}}") \
  psql -U user -d mydb -c "
SELECT website_name, COUNT(*) AS total_events
FROM events
WHERE DATE(created_at) = CURRENT_DATE
  AND DATE(updated_at) = CURRENT_DATE
  AND remote_event_id IS NOT NULL
GROUP BY website_name
UNION ALL
SELECT 'total' AS website_name, COUNT(*) AS total_events
FROM events
WHERE DATE(created_at) = CURRENT_DATE
  AND DATE(updated_at) = CURRENT_DATE
  AND remote_event_id IS NOT NULL;
"

```

### Explanation

* Filters events created and updated **today**.
* Ignores events where `remote_event_id` is `NULL`.
* Groups the result by `website_name` and counts entries.
* Appends a `total` row with the overall count using `UNION ALL`.

---

### ii. Get Statistics for a Specific Date

Replace `2025-08-03` with any desired date to get statistics for that specific day.

### Query

```sql
SELECT website_name, COUNT(*) AS total_events
FROM events
WHERE DATE(created_at) = '2026-02-03'
  AND DATE(updated_at) = '2026-02-03'
  AND remote_event_id IS NOT NULL
GROUP BY website_name

UNION ALL

SELECT 'total' AS website_name, COUNT(*) AS total_events
FROM events
WHERE DATE(created_at) = '2026-02-03'
  AND DATE(updated_at) = '2026-02-03'
  AND remote_event_id IS NOT NULL;
```


### Terminal command
```commandline
podman exec -it $(podman ps --filter "ancestor=postgres:16-alpine" --format "{{.Names}}") \
  psql -U user -d mydb -c "
SELECT website_name, COUNT(*) AS total_events
FROM events
WHERE DATE(created_at) = '2026-02-03'
  AND DATE(updated_at) = '2026-02-03'
  AND remote_event_id IS NOT NULL
GROUP BY website_name

UNION ALL

SELECT 'total' AS website_name, COUNT(*) AS total_events
FROM events
WHERE DATE(created_at) = '2026-02-03'
  AND DATE(updated_at) = '2026-02-03'
  AND remote_event_id IS NOT NULL;
"
```

### Explanation

* Same logic as the previous query, but allows targeting any **specific date**.
* This is useful for historical data audits or reporting.

---

### Notes

* `DATE(created_at)` and `DATE(updated_at)` ensure only the **date part** is compared, ignoring time.
* `UNION ALL` is used to include both grouped and total counts in the same result set.
* You can replace the static date with a placeholder if integrating into an application.
---


### 1. System Requirements

- Linux-based OS
- Python 3.9+
- Podman
- Podman Compose
- Chrome browser and Chromedriver (for Selenium)

### 2. Initial Setup

```bash
# Install Podman and Podman Compose (Ubuntu/Debian)
sudo apt-get update
sudo apt-get install -y podman podman-compose

# Verify Podman installation
podman --version
podman-compose --version

# Install uv (Python package manager)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone repository
git clone https://github.com/Beedier/Automated-Events-Scraper.git
cd Automated-Events-Scraper

# Install dependencies from pyproject.toml
uv sync

# Verify installed packages
uv pip list
```

### 3. Configuration

1. Create environment file:

   ```bash
   cp .env.example .env
   ```
2. Configure the following in `.env`:

   - WordPress API credentials
   - Database settings
   - AI API keys (Gemini/LLaMA)
   - Scraping targets configuration

### 4. Using Podman Compose

```bash
# Build and start all services defined in docker-compose.yml
podman-compose up -d

# View running containers
podman-compose ps

# View logs
podman-compose logs -f

# Stop services
podman-compose down
```

The `docker-compose.yml` file contains all necessary service configurations, including:

- Database service
- Application service with required volumes and environment variables
- Network configurations


### 5. Database Setup

```bash
# Apply database migrations
alembic upgrade head

# (Optional) Restore sample data
./restore_data.sh db_data_backup.sql.gz
```

## Project Components 🔧

### 1. Event Sources

- RIBA (Royal Institute of British Architects)
- NLA London (New London Architecture)
- BCO (British Council for Offices)
- Eventbrite (Architecture-related events) UK and Ireland

### 2. Key Features

- Multi-source event scraping
- AI-powered content enhancement
- Automated image processing
- WordPress integration
- Duplicate event detection
- Category management

## Running the Application 🏃

### Development Mode

The application follows a pipeline architecture with distinct phases. Each command can target all sources or a specific source.

#### 1. Event URL Collection Phase

Scrapes and stores event URLs from architectural websites.

```bash
# Collect event URLs from all sources
uv run main.py event-url all

# Collect event URLs from a specific source
uv run main.py event-url [riba|nla|bco|eventbrite]
```

- Collects event URLs and metadata
- Downloads thumbnail images
- Handles pagination automatically
- Respects rate limiting

#### 2. Image Processing Phase

Processes and optimizes downloaded images.

```bash
# Process images from all sources
uv run main.py process-image all

# Process images from a specific source
uv run main.py process-image [riba|nla|bco|eventbrite]
```

- Applies organizational watermarks
- Optimizes image sizes
- Handles various image formats
- Maintains quality standards

#### 3. Event Content Extraction Phase

Scrapes detailed content from collected URLs.

```bash
# Extract content from all sources
uv run main.py event-web-content all

# Extract content from a specific source
uv run main.py event-web-content [riba|nla|bco|eventbrite]
```

- Extracts comprehensive event details
- Handles different page structures
- Manages timeouts and retries
- Validates data integrity

#### 4. AI Content Enhancement Phase

Uses AI models to enhance and standardize content.

```bash
# Generate enhanced content for all sources
uv run main.py generate-content all

# Generate enhanced content for specific source
uv run main.py generate-content [riba|nla|bco|eventbrite]
```

- Enhances event descriptions
- Standardizes formatting
- Improves SEO-friendliness
- Maintains content authenticity

#### 5. WordPress Integration Phase

Manages the synchronization of content with WordPress.

##### Media Management

```
# Upload images to WordPress
uv run main.py upload-media all                 # All sources
uv run main.py upload-media [source]            # Specific source

# Remove unused media
uv run main.py delete-media all                 # All sources
uv run main.py delete-media [source]            # Specific source
```

**Features:**

- Handles bulk media uploads efficiently
- Manages WordPress media library integration
- Supports various image formats and sizes
- Maintains media metadata and relationships

##### Event Management

```
# Create events in WordPress
uv run main.py create-event all                 # All sources
uv run main.py create-event [source]            # Specific source

# Manage event categories
uv run main.py update-event-category all        # All sources
uv run main.py update-event-category [source]   # Specific source

# Update existing events
uv run main.py update-event all                 # All sources
uv run main.py update-event [source]            # Specific source

# Remove events
uv run main.py delete-event all                 # All sources
uv run main.py delete-event [source]            # Specific source
```

**Features:**

- Complete event lifecycle management
- Automatic category assignment
- Batch processing capabilities
- Data integrity validation
- Conflict resolution handling

Each command supports the following options:

- `--include-existing`: Override conflict checks

## Project Structure 📁

```commandline
.
├── alembic/                    # Database migrations
│   ├── versions/              # Migration version files
│   ├── env.py                 # Alembic environment configuration
│   └── script.py.mako         # Migration script template
├── bco_org/                   # BCO website scraper
│   ├── event_url_scraper.py   # Scrapes event URLs from BCO
│   └── event_web_content_scraper.py  # Extracts event details
├── beedier/                   # WordPress integration
│   ├── create_category.py     # Category management
│   ├── create_event.py        # Event creation
│   ├── delete_event.py        # Event deletion
│   ├── delete_media.py        # Media cleanup
│   ├── update_event.py        # Event updates
│   └── upload_media.py        # Media upload
├── controllers/               # Main application controllers
│   ├── get_all_targets.py     # Scraping target management
│   ├── get_scrapers.py        # Scraper initialization
│   └── run_scraper.py         # Scraper execution
├── dbcore/                    # Database core
│   ├── config.py              # Database configuration
│   ├── create.py              # Create operations
│   ├── database.py            # Database setup
│   ├── get.py                 # Read operations
│   ├── models.py              # SQLAlchemy models
│   ├── session.py             # DB session management
│   └── update.py              # Update operations
├── event_bright/              # Eventbrite scraper
│   ├── event_url_scraper.py   # Scrapes event URLs
│   └── event_web_content_scraper.py  # Extracts event details
├── gemini_ai/                 # Google Gemini AI integration
│   ├── create_prompt.py       # Prompt engineering
│   └── generate_content.py    # Content generation
├── images/                    # Image processing
│   ├── overlay/               # Watermark overlays
│   └── process-image/         # Processed images
├── library/                   # Utility functions
│   ├── date_utils.py          # Date handling
│   ├── event_category_mapper.py  # Category mapping
│   ├── existing_events_checker.py  # Duplicate detection
│   ├── html_utils.py          # HTML processing
│   ├── image_processor.py     # Image operations
│   ├── json_parser.py         # JSON handling
│   ├── text_utils.py          # Text processing
│   └── url_utils.py           # URL handling
├── llama_ai/                  # LLaMA AI integration
├── nla_london/                # NLA website scraper
│   ├── event_url_scraper.py   # Scrapes event URLs
│   └── event_web_content_scraper.py  # Extracts event details
├── ollama_ai/                 # Ollama AI integration
│   └── generate_fine_tuning_input_dataset.py  # Dataset generation
├── riba/                      # RIBA website scraper
│   ├── event_url_scraper.py   # Scrapes event URLs
│   └── event_web_content_scraper.py  # Extracts event details
├── selenium_webdriver/        # Selenium configuration
│   ├── chrome_driver.py       # Chrome WebDriver setup
│   ├── cookies_loader.py      # Cookie management
│   └── README.md              # Setup instructions
├── tests/                     # Test suite
│   ├── test_build_url_with_params.py  # URL tests
│   ├── test_dateutils.py      # Date utility tests
│   ├── test_image_processor.py  # Image processing tests
│   ├── test_json_parser.py    # JSON handling tests
│   └── test_text_utils.py     # Text processing tests
├── docker-compose.yml         # Container orchestration
├── Dockerfile                 # Container build instructions
├── main.py                    # Application entry point
├── pyproject.toml            # Project dependencies
└── uv.lock                   # Dependency lock file
```

## Development Guide 👩‍💻

### Running Tests

```bash
uv run pytest
```

### Creating Database Migrations

```bash
alembic revision -m "description"
alembic upgrade head
```

### Backup/Restore Data

```bash
# Backup database
./dump_db.sh

# Restore database
./restore_data.sh db_data_backup.sql
```

## Monitoring & Maintenance 🔍

### Logs

- Container logs: `podman logs events-scraper`

### Common Issues

1. **Selenium WebDriver Issues**

   - Ensure Chrome/ChromeDriver versions match
   - Check `selenium_webdriver/README.md` for details
2. **WordPress API Timeouts**

   - Verify API credentials in `.env`
   - Check WordPress site accessibility
3. **Image Processing Errors**

   - Verify disk space
   - Check image directory permissions

## Contributing 🤝

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License 📄

This project is licensed under the MIT License - see the LICENSE file for details.

## Support & Contact 📧

For support or queries:

1. Open an issue on GitHub
2. Check existing issues for solutions
3. Review documentation in respective component directories

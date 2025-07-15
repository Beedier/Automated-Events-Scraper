# Automated Events Scraper

## An Intelligent Web Scraping System for Architectural Events

This project automates the collection and publication of architectural events from multiple sources to WordPress, featuring AI-powered content enhancement and image processing.

## Quick Start Guide 🚀

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

### 4. Database Setup

```bash
# Apply database migrations
alembic upgrade head

# (Optional) Restore sample data
./restore_data.sh db_data_backup.sql
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

### Using Podman Compose

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

### Development Mode

```bash
# Basic usage
uv run main.py [command] [options]
```

Available Commands:

1. **Scraping Commands**

```bash
# Scrape all sources event urls
uv run main.py event-url all

# Scrape specific source event urls
uv run main.py event-url [riba|nla|bco|eventbrite]

# Process Image for all source
uv run main.py process-image all

# Process specific source Image
uv run main.py process-image [riba|nla|bco|eventbrite]

# Scrape all sources web content
uv run main.py event-web-content all

# Scrape specific source event web content
uv run main.py event-web-content [riba|nla|bco|eventbrite]

# Generate Content for all source
uv run main.py generate-content all

# Generate Content for specific source
uv run main.py generate-content [riba|nla|bco|eventbrite]
```

2. **WordPress Management**

```bash
# Upload Media to wordpress for all source
uv run main.py upload-media all

# Upload Media to wordpress for specific source
uv run main.py upload-media [riba|nla|bco|eventbrite]

# Create Event to wordpress for all source
uv run main.py create-event all

# Create Event to wordpress for specific source
uv run main.py create-event [riba|nla|bco|eventbrite]

# Update Event Category to wordpress for all source
uv run main.py update-event-category all

# Update Event Category to wordpress for specific source
uv run main.py update-event-category [riba|nla|bco|eventbrite]

# Update Event to wordpress for all source
uv run main.py update-event all

# Update Event to wordpress for specific source
uv run main.py update-event [riba|nla|bco|eventbrite]

# Delete event from WordPress
uv run main.py delete-event all
uv run main.py delete-event [riba|nla|bco|eventbrite]

# Delete media from WordPress
uv run main.py delete-media all
uv run main.py delete-media [riba|nla|bco|eventbrite]
```

## Project Structure 📁

```
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

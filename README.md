# University Clubs Management Application

A Django-based web application for managing university clubs, events, resources, and forums.

## Features

- User authentication and profiles
- Club management and memberships
- Event organization and participation
- Resource sharing and aids
- Forum discussions
- AI-powered chatbot for recommendations (using Google Gemini)
- Admin panel for management

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd Genie_Logiciel_Application_Clubs_Universitaires
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   - Copy `.env.example` to `.env`
   - Fill in your API keys and other settings

5. Run migrations:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. Create a superuser:
   ```bash
   python manage.py createsuperuser
   ```

7. Run the development server:
   ```bash
   python manage.py runserver
   ```

## Environment Variables

Create a `.env` file in the project root with the following variables:

- `GOOGLE_API_KEY`: Your Google Gemini API key
- `SECRET_KEY`: Django secret key
- `DEBUG`: Set to True for development
- `ALLOWED_HOSTS`: Comma-separated list of allowed hosts
- `EMAIL_HOST_USER` and `EMAIL_HOST_PASSWORD`: For email functionality

## API Keys Required

- **Google Gemini API Key**: Required for the AI chatbot functionality
  - Get it from: https://makersuite.google.com/app/apikey

## Usage

- Access the application at `http://127.0.0.1:8000`
- Admin panel at `http://127.0.0.1:8000/admin/`
- Use the chatbot for personalized recommendations

## Testing

Run tests with:
```bash
python manage.py test
```

## Deployment

For production deployment:
- Set `DEBUG=False`
- Configure proper database (PostgreSQL recommended)
- Set up static files serving
- Use environment variables for sensitive data
- Configure web server (nginx + gunicorn)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

## License

This project is licensed under the MIT License.

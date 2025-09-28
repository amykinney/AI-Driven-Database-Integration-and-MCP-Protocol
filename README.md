# Employee Management System
<img width="1438" height="861" alt="Screenshot 2025-09-28 at 5 43 21 PM" src="https://github.com/user-attachments/assets/ce9713c8-8a82-4d55-b491-afd2362d32e7" />


A comprehensive Flask web application with MCP (Model Context Protocol) server integration for managing employee records. This project demonstrates a full CRUD (Create, Read, Update, Delete) system with a modern web interface and safe database operations through MCP.

## 🚀 Features

### Web Application

- **Full CRUD Operations**: Create, read, update, and delete employee records
- **Modern UI**: Bootstrap-based responsive interface with intuitive navigation
- **Department Management**: Link employees to departments
- **Data Validation**: Form validation and error handling
- **RESTful API**: JSON API endpoints for external integrations

### MCP Server Integration

- **Safe Database Operations**: Read-only access with guardrails against destructive queries
- **Cursor Integration**: Direct database interaction through Cursor IDE
- **Multiple Tools**: List, search, and analyze employee data
- **SQL Safety**: Prevents DROP, DELETE, INSERT, UPDATE, and other destructive operations

## 📁 Project Structure

```
├── app/                          # Flask application
│   ├── __init__.py              # App factory and configuration
│   ├── models/                  # SQLAlchemy models
│   │   ├── __init__.py
│   │   └── employee.py          # Employee and Department models
│   ├── views/                   # Flask routes and controllers
│   │   ├── __init__.py
│   │   └── main.py              # Main application routes
│   ├── templates/               # Jinja2 HTML templates
│   │   ├── base.html            # Base template with navigation
│   │   ├── index.html           # Home page
│   │   └── employees/           # Employee-specific templates
│   │       ├── list.html        # Employee listing
│   │       ├── create.html      # Add new employee
│   │       └── edit.html        # Edit employee
│   └── static/                  # Static files (CSS, JS, images)
├── mcp/                         # MCP server
│   ├── __init__.py
│   └── employees_server.py      # MCP server implementation
├── employees.db                 # SQLite database
├── app.py                       # Flask application entry point
├── requirements.txt             # Python dependencies
└── README.md                    # This file
```

## 🛠️ Installation & Setup

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

### 1. Clone the Repository

```bash
git clone <your-repository-url>
cd AI-Driven-Database-Integration-and-MCP-Protocol-1
```

### 2. Create Virtual Environment (Recommended)

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the Flask Application

```bash
# Method 1: Using Flask CLI
export FLASK_APP=app.py
export FLASK_ENV=development
flask run

# Method 2: Direct Python execution
python app.py
```

The application will be available at `http://localhost:5000`

## 🎯 Usage

### Web Interface

1. **Home Page**: Navigate to the main dashboard with quick access to all features
2. **View Employees**: Browse all employee records in a table format
3. **Add Employee**: Create new employee records with form validation
4. **Edit Employee**: Update existing employee information
5. **Delete Employee**: Remove employee records with confirmation

### MCP Server Integration

The MCP server provides safe database access through Cursor IDE with the following tools:

#### Available Tools:

- `list_employees`: List all employees with department information
- `get_employee`: Retrieve a specific employee by ID
- `search_employees`: Search employees by name or department
- `list_departments`: List all departments
- `get_employee_stats`: Get employee statistics (count, average salary, etc.)
- `safe_query`: Execute safe SELECT queries (read-only)

#### Example MCP Usage in Cursor:

```
# List all employees
list_employees

# Search for employees named "John"
search_employees(name="John")

# Get employee statistics
get_employee_stats

# Safe SQL query
safe_query(query="SELECT * FROM employees WHERE salary > 50000")
```

## 🗄️ Database Schema

### Employees Table

- `id`: Primary key (auto-increment)
- `name`: Employee full name (required)
- `department_id`: Foreign key to departments table
- `salary`: Annual salary (decimal)
- `hire_date`: Date of hire (string format)

### Departments Table

- `id`: Primary key (auto-increment)
- `name`: Department name (required)

## 🔒 Security Features

### MCP Server Guardrails

- **Read-Only Access**: Only SELECT queries are allowed
- **SQL Injection Protection**: Parameterized queries and input validation
- **Destructive Operation Prevention**: Blocks DROP, DELETE, INSERT, UPDATE operations
- **Query Validation**: Validates SQL syntax and safety before execution

### Web Application Security

- **CSRF Protection**: Flask-WTF CSRF tokens (can be added)
- **Input Validation**: Form validation and sanitization
- **SQL Injection Prevention**: SQLAlchemy ORM with parameterized queries

## 🧪 Testing

### Manual Testing

1. Start the Flask application
2. Navigate to `http://localhost:5000`
3. Test all CRUD operations:
   - Create a new employee
   - View the employee list
   - Edit an existing employee
   - Delete an employee

### MCP Server Testing

1. Ensure the MCP server is properly configured in Cursor
2. Test various MCP tools through Cursor's interface
3. Verify that destructive operations are blocked

## 🚀 Deployment

### Development

```bash
python app.py
```

### Production (using Gunicorn)

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Environment Variables

- `FLASK_ENV`: Set to `production` for production deployment
- `SECRET_KEY`: Change the default secret key in production

## 📝 API Endpoints

### Web Routes

- `GET /`: Home page
- `GET /employees`: List all employees
- `GET /employees/new`: Show create employee form
- `POST /employees/new`: Create new employee
- `GET /employees/<id>/edit`: Show edit employee form
- `POST /employees/<id>/edit`: Update employee
- `POST /employees/<id>/delete`: Delete employee

### API Endpoints

- `GET /api/employees`: JSON list of all employees

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Troubleshooting

### Common Issues

1. **Database Connection Error**

   - Ensure `employees.db` exists in the project root
   - Check file permissions

2. **Import Errors**

   - Verify virtual environment is activated
   - Check that all dependencies are installed

3. **MCP Server Not Working**

   - Ensure MCP server is properly configured in Cursor
   - Check that the database path is correct

4. **Port Already in Use**
   - Change the port in `app.py` or kill the process using port 5000

### Getting Help

- Check the Flask documentation: https://flask.palletsprojects.com/
- MCP documentation: https://modelcontextprotocol.io/
- SQLAlchemy documentation: https://docs.sqlalchemy.org/

## 🎉 Acknowledgments

- Flask team for the excellent web framework
- Bootstrap for the responsive UI components
- SQLAlchemy for the powerful ORM
- MCP team for the protocol specification

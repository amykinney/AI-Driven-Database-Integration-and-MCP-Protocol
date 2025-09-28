#!/usr/bin/env python3
"""
MCP Server for Employee Management System
Provides safe database operations with guardrails to prevent destructive queries.
"""

import asyncio
import json
import sqlite3
import os
import sys
from typing import Any, Dict, List, Optional

# Add the project root to the path to import from app
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

try:
    from mcp.server import Server
    from mcp.server.models import InitializationOptions
    from mcp.server.stdio import stdio_server
    from mcp.types import (
        Resource,
        Tool,
        TextContent,
        ImageContent,
        EmbeddedResource,
        LoggingLevel
    )
    MCP_AVAILABLE = True
except ImportError:
    print("MCP package not available. Creating a simple database interface instead.")
    MCP_AVAILABLE = False

# Initialize the MCP server
server = Server("employees-db-server")

# Database path
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "employees.db")

def get_db_connection():
    """Get a database connection"""
    return sqlite3.connect(DB_PATH)

def validate_sql_safety(sql: str) -> bool:
    """
    Validate that SQL query is safe (no destructive operations)
    """
    sql_lower = sql.lower().strip()
    
    # Block destructive operations
    dangerous_keywords = [
        'drop', 'delete', 'truncate', 'alter', 'create', 'insert', 'update',
        'grant', 'revoke', 'exec', 'execute', 'sp_', 'xp_', '--', '/*', '*/'
    ]
    
    for keyword in dangerous_keywords:
        if keyword in sql_lower:
            return False
    
    # Only allow SELECT statements
    if not sql_lower.startswith('select'):
        return False
    
    return True

@server.list_resources()
async def handle_list_resources() -> List[Resource]:
    """List available database resources"""
    return [
        Resource(
            uri="employees://employees",
            name="Employees Table",
            description="Employee records with department information",
            mimeType="application/json"
        ),
        Resource(
            uri="employees://departments", 
            name="Departments Table",
            description="Department information",
            mimeType="application/json"
        )
    ]

@server.read_resource()
async def handle_read_resource(uri: str) -> str:
    """Read database resources"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        if uri == "employees://employees":
            cursor.execute("""
                SELECT e.id, e.name, e.department_id, d.name as department_name, 
                       e.salary, e.hire_date
                FROM employees e
                LEFT JOIN departments d ON e.department_id = d.id
                ORDER BY e.id
            """)
            rows = cursor.fetchall()
            columns = [description[0] for description in cursor.description]
            
            result = []
            for row in rows:
                result.append(dict(zip(columns, row)))
            
            return json.dumps(result, indent=2)
            
        elif uri == "employees://departments":
            cursor.execute("SELECT * FROM departments ORDER BY id")
            rows = cursor.fetchall()
            columns = [description[0] for description in cursor.description]
            
            result = []
            for row in rows:
                result.append(dict(zip(columns, row)))
            
            return json.dumps(result, indent=2)
        else:
            raise ValueError(f"Unknown resource: {uri}")
            
    finally:
        conn.close()

@server.list_tools()
async def handle_list_tools() -> List[Tool]:
    """List available tools"""
    return [
        Tool(
            name="list_employees",
            description="List all employees with their department information",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of employees to return (default: 100)",
                        "minimum": 1,
                        "maximum": 1000
                    }
                }
            }
        ),
        Tool(
            name="get_employee",
            description="Get a specific employee by ID",
            inputSchema={
                "type": "object",
                "properties": {
                    "employee_id": {
                        "type": "integer",
                        "description": "The ID of the employee to retrieve"
                    }
                },
                "required": ["employee_id"]
            }
        ),
        Tool(
            name="search_employees",
            description="Search employees by name or department",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Search by employee name (partial match)"
                    },
                    "department": {
                        "type": "string", 
                        "description": "Search by department name"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results (default: 50)",
                        "minimum": 1,
                        "maximum": 500
                    }
                }
            }
        ),
        Tool(
            name="list_departments",
            description="List all departments",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="get_employee_stats",
            description="Get statistics about employees (count, average salary, etc.)",
            inputSchema={
                "type": "object",
                "properties": {
                    "department_id": {
                        "type": "integer",
                        "description": "Filter by department ID (optional)"
                    }
                }
            }
        ),
        Tool(
            name="safe_query",
            description="Execute a safe SELECT query (read-only, no destructive operations)",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "SQL SELECT query to execute"
                    }
                },
                "required": ["query"]
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle tool calls"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        if name == "list_employees":
            limit = arguments.get("limit", 100)
            cursor.execute("""
                SELECT e.id, e.name, e.department_id, d.name as department_name, 
                       e.salary, e.hire_date
                FROM employees e
                LEFT JOIN departments d ON e.department_id = d.id
                ORDER BY e.id
                LIMIT ?
            """, (limit,))
            
            rows = cursor.fetchall()
            columns = [description[0] for description in cursor.description]
            
            result = []
            for row in rows:
                result.append(dict(zip(columns, row)))
            
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
            
        elif name == "get_employee":
            employee_id = arguments["employee_id"]
            cursor.execute("""
                SELECT e.id, e.name, e.department_id, d.name as department_name, 
                       e.salary, e.hire_date
                FROM employees e
                LEFT JOIN departments d ON e.department_id = d.id
                WHERE e.id = ?
            """, (employee_id,))
            
            row = cursor.fetchone()
            if row:
                columns = [description[0] for description in cursor.description]
                result = dict(zip(columns, row))
                return [TextContent(type="text", text=json.dumps(result, indent=2))]
            else:
                return [TextContent(type="text", text="Employee not found")]
                
        elif name == "search_employees":
            name_filter = arguments.get("name", "")
            department_filter = arguments.get("department", "")
            limit = arguments.get("limit", 50)
            
            query = """
                SELECT e.id, e.name, e.department_id, d.name as department_name, 
                       e.salary, e.hire_date
                FROM employees e
                LEFT JOIN departments d ON e.department_id = d.id
                WHERE 1=1
            """
            params = []
            
            if name_filter:
                query += " AND e.name LIKE ?"
                params.append(f"%{name_filter}%")
                
            if department_filter:
                query += " AND d.name LIKE ?"
                params.append(f"%{department_filter}%")
                
            query += " ORDER BY e.id LIMIT ?"
            params.append(limit)
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            columns = [description[0] for description in cursor.description]
            
            result = []
            for row in rows:
                result.append(dict(zip(columns, row)))
            
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
            
        elif name == "list_departments":
            cursor.execute("SELECT * FROM departments ORDER BY id")
            rows = cursor.fetchall()
            columns = [description[0] for description in cursor.description]
            
            result = []
            for row in rows:
                result.append(dict(zip(columns, row)))
            
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
            
        elif name == "get_employee_stats":
            department_id = arguments.get("department_id")
            
            if department_id:
                cursor.execute("""
                    SELECT 
                        COUNT(*) as total_employees,
                        AVG(salary) as avg_salary,
                        MIN(salary) as min_salary,
                        MAX(salary) as max_salary
                    FROM employees 
                    WHERE department_id = ?
                """, (department_id,))
            else:
                cursor.execute("""
                    SELECT 
                        COUNT(*) as total_employees,
                        AVG(salary) as avg_salary,
                        MIN(salary) as min_salary,
                        MAX(salary) as max_salary
                    FROM employees
                """)
            
            row = cursor.fetchone()
            columns = [description[0] for description in cursor.description]
            result = dict(zip(columns, row))
            
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
            
        elif name == "safe_query":
            query = arguments["query"]
            
            if not validate_sql_safety(query):
                return [TextContent(type="text", text="Error: Query contains unsafe operations. Only SELECT statements are allowed.")]
            
            try:
                cursor.execute(query)
                rows = cursor.fetchall()
                columns = [description[0] for description in cursor.description]
                
                result = []
                for row in rows:
                    result.append(dict(zip(columns, row)))
                
                return [TextContent(type="text", text=json.dumps(result, indent=2))]
                
            except sqlite3.Error as e:
                return [TextContent(type="text", text=f"SQL Error: {str(e)}")]
        
        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]
            
    finally:
        conn.close()

async def main():
    """Main function to run the MCP server"""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="employees-db-server",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=None,
                    experimental_capabilities=None,
                ),
            ),
        )

if __name__ == "__main__":
    asyncio.run(main())

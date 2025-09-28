#!/usr/bin/env python3
"""
Simple Database Interface for Employee Management System
Provides safe database operations with guardrails to prevent destructive queries.
This is a simplified version that works without the full MCP package.
"""

import json
import sqlite3
import os
from typing import Any, Dict, List, Optional

# Database path
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "employees.db")

class EmployeeDBInterface:
    """Simple database interface with safety guardrails"""
    
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
    
    def get_db_connection(self):
        """Get a database connection"""
        return sqlite3.connect(self.db_path)
    
    def validate_sql_safety(self, sql: str) -> bool:
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
    
    def list_employees(self, limit: int = 100) -> List[Dict]:
        """List all employees with their department information"""
        conn = self.get_db_connection()
        cursor = conn.cursor()
        
        try:
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
            
            return result
        finally:
            conn.close()
    
    def get_employee(self, employee_id: int) -> Optional[Dict]:
        """Get a specific employee by ID"""
        conn = self.get_db_connection()
        cursor = conn.cursor()
        
        try:
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
                return dict(zip(columns, row))
            return None
        finally:
            conn.close()
    
    def search_employees(self, name: str = "", department: str = "", limit: int = 50) -> List[Dict]:
        """Search employees by name or department"""
        conn = self.get_db_connection()
        cursor = conn.cursor()
        
        try:
            query = """
                SELECT e.id, e.name, e.department_id, d.name as department_name, 
                       e.salary, e.hire_date
                FROM employees e
                LEFT JOIN departments d ON e.department_id = d.id
                WHERE 1=1
            """
            params = []
            
            if name:
                query += " AND e.name LIKE ?"
                params.append(f"%{name}%")
                
            if department:
                query += " AND d.name LIKE ?"
                params.append(f"%{department}%")
                
            query += " ORDER BY e.id LIMIT ?"
            params.append(limit)
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            columns = [description[0] for description in cursor.description]
            
            result = []
            for row in rows:
                result.append(dict(zip(columns, row)))
            
            return result
        finally:
            conn.close()
    
    def list_departments(self) -> List[Dict]:
        """List all departments"""
        conn = self.get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("SELECT * FROM departments ORDER BY id")
            rows = cursor.fetchall()
            columns = [description[0] for description in cursor.description]
            
            result = []
            for row in rows:
                result.append(dict(zip(columns, row)))
            
            return result
        finally:
            conn.close()
    
    def get_employee_stats(self, department_id: Optional[int] = None) -> Dict:
        """Get statistics about employees (count, average salary, etc.)"""
        conn = self.get_db_connection()
        cursor = conn.cursor()
        
        try:
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
            return dict(zip(columns, row))
        finally:
            conn.close()
    
    def safe_query(self, query: str) -> List[Dict]:
        """Execute a safe SELECT query (read-only, no destructive operations)"""
        if not self.validate_sql_safety(query):
            raise ValueError("Query contains unsafe operations. Only SELECT statements are allowed.")
        
        conn = self.get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(query)
            rows = cursor.fetchall()
            columns = [description[0] for description in cursor.description]
            
            result = []
            for row in rows:
                result.append(dict(zip(columns, row)))
            
            return result
        except sqlite3.Error as e:
            raise ValueError(f"SQL Error: {str(e)}")
        finally:
            conn.close()

def main():
    """Command line interface for the database"""
    db = EmployeeDBInterface()
    
    print("Employee Database Interface")
    print("Available commands:")
    print("1. list_employees [limit]")
    print("2. get_employee <id>")
    print("3. search_employees [name] [department] [limit]")
    print("4. list_departments")
    print("5. get_employee_stats [department_id]")
    print("6. safe_query <sql>")
    print("7. quit")
    
    while True:
        try:
            command = input("\nEnter command: ").strip().split()
            if not command:
                continue
                
            cmd = command[0].lower()
            
            if cmd == "quit":
                break
            elif cmd == "list_employees":
                limit = int(command[1]) if len(command) > 1 else 100
                result = db.list_employees(limit)
                print(json.dumps(result, indent=2))
            elif cmd == "get_employee":
                if len(command) < 2:
                    print("Usage: get_employee <id>")
                    continue
                employee_id = int(command[1])
                result = db.get_employee(employee_id)
                if result:
                    print(json.dumps(result, indent=2))
                else:
                    print("Employee not found")
            elif cmd == "search_employees":
                name = command[1] if len(command) > 1 else ""
                department = command[2] if len(command) > 2 else ""
                limit = int(command[3]) if len(command) > 3 else 50
                result = db.search_employees(name, department, limit)
                print(json.dumps(result, indent=2))
            elif cmd == "list_departments":
                result = db.list_departments()
                print(json.dumps(result, indent=2))
            elif cmd == "get_employee_stats":
                department_id = int(command[1]) if len(command) > 1 else None
                result = db.get_employee_stats(department_id)
                print(json.dumps(result, indent=2))
            elif cmd == "safe_query":
                if len(command) < 2:
                    print("Usage: safe_query <sql>")
                    continue
                query = " ".join(command[1:])
                try:
                    result = db.safe_query(query)
                    print(json.dumps(result, indent=2))
                except ValueError as e:
                    print(f"Error: {e}")
            else:
                print("Unknown command")
                
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from app import db
from app.models.employee import Employee, Department

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Home page with navigation"""
    return render_template('index.html')

@main_bp.route('/employees')
def list_employees():
    """List all employees"""
    employees = Employee.query.join(Department, Employee.department_id == Department.id, isouter=True).all()
    return render_template('employees/list.html', employees=employees)

@main_bp.route('/employees/new', methods=['GET', 'POST'])
def create_employee():
    """Create a new employee"""
    if request.method == 'POST':
        name = request.form['name']
        department_id = request.form.get('department_id') or None
        salary = request.form.get('salary') or None
        hire_date = request.form.get('hire_date') or None
        
        if salary:
            try:
                salary = float(salary)
            except ValueError:
                flash('Invalid salary format', 'error')
                return render_template('employees/create.html', departments=get_departments())
        
        employee = Employee(
            name=name,
            department_id=department_id,
            salary=salary,
            hire_date=hire_date
        )
        
        try:
            db.session.add(employee)
            db.session.commit()
            flash('Employee created successfully!', 'success')
            return redirect(url_for('main.list_employees'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating employee: {str(e)}', 'error')
    
    return render_template('employees/create.html', departments=get_departments())

@main_bp.route('/employees/<int:employee_id>/edit', methods=['GET', 'POST'])
def edit_employee(employee_id):
    """Edit an employee"""
    employee = Employee.query.get_or_404(employee_id)
    
    if request.method == 'POST':
        employee.name = request.form['name']
        employee.department_id = request.form.get('department_id') or None
        salary = request.form.get('salary') or None
        employee.hire_date = request.form.get('hire_date') or None
        
        if salary:
            try:
                employee.salary = float(salary)
            except ValueError:
                flash('Invalid salary format', 'error')
                return render_template('employees/edit.html', employee=employee, departments=get_departments())
        else:
            employee.salary = None
        
        try:
            db.session.commit()
            flash('Employee updated successfully!', 'success')
            return redirect(url_for('main.list_employees'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating employee: {str(e)}', 'error')
    
    return render_template('employees/edit.html', employee=employee, departments=get_departments())

@main_bp.route('/employees/<int:employee_id>/delete', methods=['POST'])
def delete_employee(employee_id):
    """Delete an employee"""
    employee = Employee.query.get_or_404(employee_id)
    
    try:
        db.session.delete(employee)
        db.session.commit()
        flash('Employee deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting employee: {str(e)}', 'error')
    
    return redirect(url_for('main.list_employees'))

@main_bp.route('/api/employees')
def api_employees():
    """API endpoint for MCP server"""
    employees = Employee.query.join(Department, Employee.department_id == Department.id, isouter=True).all()
    return jsonify([employee.to_dict() for employee in employees])

def get_departments():
    """Helper function to get all departments"""
    return Department.query.all()


# Sci-Lab Inventory Management System (SLIMS)

## Project Description
Sci-Lab Inventory Management System (SLIMS) is a web application designed to manage laboratory materials and apparel for students, teachers, and lab technicians. The system facilitates material requests, inventory management, and checking liabilities for science laboratory equipment, while offering a streamlined process for borrowing and approving lab resources. Students can request materials as guest users, which require teacher approval before processing by lab technicians. Teachers have the ability to request materials without the need for approval, and the system also handles lab apparel borrowing requests and their approval process.

## Installation

### Windows
1. Clone the repository to your local machine:
   ```bash
   git clone https://github.com/yourusername/slims.git
   ```
2. Navigate to the project directory:
   ```bash
   cd slims
   ```
3. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```
4. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Linux
1. Clone the repository to your local machine:
   ```bash
   git clone https://github.com/yourusername/slims.git
   ```
2. Navigate to the project directory:
   ```bash
   cd slims
   ```
3. Create and activate a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
4. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Application

1. Apply migrations to set up the database:
   ```bash
   python manage.py migrate
   ```
2. Create a superuser:
   ```bash
   python manage.py createsuperuser
   ```
3. Run the development server:
   ```bash
   python manage.py runserver
   ```
5. Open your browser and go to `http://127.0.0.1:8000` to view the application.

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

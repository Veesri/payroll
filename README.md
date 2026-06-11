# Enterprise HRMS (Human Resource Management System)

This repository contains the complete codebase for the Enterprise HRMS application, split into a Flask-based backend and a Vite+React-based frontend.

---

## System Prerequisites

Ensure you have the following installed on your machine:
* **Python** (version 3.8 or higher)
* **Node.js** (LTS version recommended)
* **npm** (comes packaged with Node.js)

---

## 1. Backend Setup & Run (Flask)

The backend manages user authentication (JWT), employee records, attendance tracking, leaves, payroll calculations, and PDF/Excel generation.

### Step 1.1: Navigate to the backend directory
Open a terminal and navigate to the backend:
```bash
cd backend
```

### Step 1.2: Set up a virtual environment (Optional but Recommended)
If your virtual environment is corrupted or pointing to a different path, recreate it:
```powershell
# Remove old virtual environment if needed
Remove-Item -Recurse -Force venv

# Create a new virtual environment
python -m venv venv
```

### Step 1.3: Activate the virtual environment
* **Windows (PowerShell):**
  ```powershell
  .\venv\Scripts\Activate.ps1
  ```
* **Windows (Command Prompt):**
  ```cmd
  .\venv\Scripts\activate.bat
  ```
* **macOS / Linux:**
  ```bash
  source venv/bin/activate
  ```

### Step 1.4: Install dependencies
Install the required packages using the generated requirements file:
```bash
pip install -r requirements.txt
```

### Step 1.5: Seed the database
The SQLite database tables are created automatically when the application starts. To populate default user roles (`superadmin`, `hradmin`, `employee1` with the password `password123`), run:
```bash
python seed.py
```

### Step 1.6: Run database migrations (Leaves table update)
Apply the migration script to add requested schema updates:
```bash
python migrate_leaves.py
```

### Step 1.7: Start the backend server
Run the Flask development server:
```bash
python app.py
```
The backend server will run on `http://127.0.0.1:5000`.

---

## 2. Frontend Setup & Run (Vite + React)

The frontend is a modern SPA dashboard built using React, React Router, Bootstrap, and Axios.

### Step 2.1: Navigate to the frontend directory
Open a new terminal session and navigate to the frontend:
```bash
cd frontend
```

### Step 2.2: Install npm dependencies
Download and install all Node packages:
```bash
npm install
```

### Step 2.3: Start the development server
Run Vite in development mode:
```bash
npm run dev
```
The development server will launch at `http://localhost:5173`. Open this URL in your browser to view the application.

---

## 3. Building for Production

To compile and bundle the frontend application for production deployment:

### Step 3.1: Build the frontend assets
In the `frontend/` directory, run:
```bash
npm run build
```
This compiles React components and bundles styling into static assets optimized for production. The output files will be saved in the `frontend/dist/` directory.

### Step 3.2: Production Deployment
* **Frontend:** Serve the contents of `frontend/dist/` using any static file web server (Nginx, Apache, Vercel, Netlify, etc.).
* **Backend:** Serve Flask using a production WSGI server like Gunicorn or Waitress (on Windows), behind a reverse proxy (like Nginx).



# Warehouse Management System (WMS)

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A complete desktop application for managing warehouse inventory, orders, and reporting. Built with Python and a custom GUI framework.

## 📋 Table of Contents
- [Features](#-features)
- [Project Structure](#-project-structure)
- [Installation](#-installation)
- [Running the Application](#-running-the-application)
  - [Using `run.py` (Production Mode)](#using-runpy-production-mode)
  - [Using `main.py` (Development Mode)](#using-mainpy-development-mode)
- [Configuration](#-configuration)
- [Database](#-database)
- [Screenshots](#-screenshots)
- [Contributing](#-contributing)
- [License](#-license)

## ✨ Features
- **Inventory Management** – Add, update, delete, and search products
- **Order Processing** – Create and track customer/supplier orders
- **Stock Alerts** – Automatic low-stock notifications
- **Reporting** – Generate inventory reports and sales analytics
- **User-friendly GUI** – Intuitive interface with custom styling
- **Persistent Storage** – SQLite database for reliable data storage

## 📁 Project Structure
```
Warehouse-management-system/
├── gui/                    # Graphical user interface modules
├── database/               # Database connection and CRUD operations
├── utils/                  # Helper functions and utilities
├── __pycache__/            # Compiled Python bytecode
├── main.py                 # Development mode entry point
├── run.py                  # Production mode entry point
├── config.json             # Application configuration
├── requirements.txt        # Python dependencies
├── B-NAZANIN.TTF           # Custom font file
└── .credentials/           # Secure credential storage (if used)
```

## 🔧 Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Steps
1. **Clone the repository**
   ```bash
   git clone https://github.com/ErfanShahbazzadeh/Warehouse-management-system.git
   cd Warehouse-management-system
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Verify database setup**
   The database will be automatically initialized on first run.

## 🚀 Running the Application

The system provides **two separate entry points** for different use cases:

### Using `run.py` (Production Mode)
```bash
python run.py
```
**Purpose:** Production environment deployment  
**Characteristics:**
- Optimized for end-users
- Suppresses debug logs and development consoles
- Handles errors gracefully with user-friendly messages
- Includes startup validation (checks config, database connectivity)
- Recommended for **daily operations**

### Using `main.py` (Development Mode)
```bash
python main.py
```
**Purpose:** Development, testing, and debugging  
**Characteristics:**
- Enables detailed debug logging
- Shows full traceback for errors
- Hot-reload support for UI changes
- Additional development tools and test data generators
- Recommended for **modifying code or testing new features**

> **💡 Tip:** If you're a system administrator or regular user, always use `run.py`. Developers should use `main.py` for debugging and feature development.


**Login info:**
- USERNAME: admin
- PASSWORD: admin123


## ⚙️ Configuration

Edit `config.json` to customize behavior:

```json
{
  "database": {
    "path": "database/warehouse.db",
    "backup_enabled": true
  },
  "app": {
    "theme": "default",
    "language": "en",
    "low_stock_threshold": 10
  },
  "logging": {
    "level": "INFO",
    "file": "logs/wms.log"
  }
}
```

## 🗄️ Database

- **Type:** SQLite
- **Location:** `database/warehouse.db`
- **Management:** All schema migrations are handled automatically
- **Backup:** Automatic backups are created daily (configurable)

## 📸 Screenshots

*(Add your screenshots here)*
```
[Login Window]
![Login window](https://github.com/user-attachments/assets/2289389c-4e39-4ac4-a9d3-3cdc7c9d3269)

[Main Dashboard]
![Main Dashboard](https://github.com/user-attachments/assets/6dd1c4f9-eb75-4f71-bfd2-cc82fc5a3b8c)
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

**Development workflow:**
- Use `main.py` during development
- Test thoroughly before creating a pull request
- Update documentation as needed

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.

## 👤 Author

**Erfan Shahbazzadeh**
- GitHub: [@ErfanShahbazzadeh](https://github.com/ErfanShahbazzadeh)

## 🙏 Acknowledgements

- Custom font: B-NAZANIN.TTF
- Python community for excellent libraries

---

**Star this repository** ⭐ if you find it useful for your warehouse management needs!

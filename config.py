import os


class Config:
    """Application configuration for the airline reservation system."""

    SECRET_KEY = os.getenv("SECRET_KEY", "airline-reservation-secret-key")
    MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
    MYSQL_PORT = int(os.getenv("MYSQL_PORT", "3306"))
    MYSQL_USER = os.getenv("MYSQL_USER", "root")
    MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
    MYSQL_DB = os.getenv("MYSQL_DB", "airline_reservation")
    MYSQL_CHARSET = "utf8mb4"

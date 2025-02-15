from setuptools import setup, find_packages

setup(
    name="ultrastar-queue",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "alembic>=1.7.5",
        "uvicorn[standard]>=0.18.2",
        "fastapi>=0.95.0",
        "SQLAlchemy>=1.4.0",
        "databases>=0.5.0",
    ],
    entry_points={
        'console_scripts': [
            'alembic = alembic.config:main',  # Entry point for Alembic commands
        ],
    },
)


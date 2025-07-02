from setuptools import setup, find_packages

setup(
    name="insurance-models",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "sqlalchemy>=2.0.0",
        "pydantic[email]>=2.0.0",
        "redis>=5.0.0",
        "boto3>=1.26.0",
        "python-dotenv>=1.0.0",
        "asyncpg>=0.28.0",
        "alembic>=1.12.0"
    ],
    python_requires=">=3.11",
)

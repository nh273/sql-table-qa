from setuptools import setup, find_packages

setup(
    name='sql_table_qa',
    version='1.0.0',
    description='A package for SQL table question-answering',
    author='Your Name',
    author_email='your@email.com',
    packages=find_packages(),
    install_requires=[
        'openai',  # Add any other dependencies here
    ],
    extras_require={
        'dev': [
            'pytest',  # Add any other dev dependencies here
        ]
    },
)
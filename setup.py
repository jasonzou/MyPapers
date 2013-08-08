from setuptools import setup, find_packages

setup(
    name = 'mypapers',
    version = '0.0.1',
    packages = find_packages(),
    install_requires = [
        "Flask==0.10",
        "Flask-Login",
        "Flask-WTF",
        "pyes==0.16",
        "chardet",
        "requests",
    ],
    url = 'http://mypapers.allkos.info/',
    author = 'Jason Zou',
    author_email = 'jason.zou@gmail.com',
    description = 'MyPapers is a personal papers management system.',
    license = 'AGPL',
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
)


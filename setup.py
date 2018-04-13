from setuptools import setup, find_packages

with open('README.rst') as fd:
    description = fd.read()

VERSION = '1.2.0'  # maintained by release tool

setup(
    name='pyramid_google_login',
    version=VERSION,
    description='Google Login for Pyramid',
    long_description=description,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Framework :: Pyramid',
        'Topic :: Internet :: WWW/HTTP :: WSGI',
    ],
    keywords=['google', 'login', 'wsgi', 'pyramid', 'auth', 'authentication'],
    author='Pior Bastida',
    author_email='pior@pbastida.net',
    url='https://github.com/ludia/pyramid_google_login',
    license='BSD-derived (http://www.repoze.org/LICENSE.txt)',

    packages=find_packages(),
    package_data={'pyramid_google_login': ['static/*.*', 'templates/*.*']},

    install_requires=['pyramid_mako', 'requests', 'six'],
)

import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))

requires = [
    "django",
]

setup(
    name="team",
    version="0.0",
    description="Team Intranet",
    long_description="",
    classifiers=[
        "Programming Language :: Python",
        "Framework :: Django",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
    ],
    author="Igalia",
    url="igalia.com",
    keywords="web wsgi django",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    test_suite="team",
    install_requires=requires,
)

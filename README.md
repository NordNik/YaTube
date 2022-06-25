# Description

This project is made by [Dr. Nikolai Orlov](t.me/Nikolai_Orlov) as a simple pet-project. The aim was to inhale a bit of life in my theoretical Django knowledge and, in this way, to get practice in backend development.

The project is a simple blog platform to share your thoughts and, in reverse, to read interesting and valuable for your life authors.

# Getting started
The project was made using Django 2.2.16 and Python 3.7. Other necessary packajes are noticed in requirements.txt.

First, clone the repository from Github and switch to the new directory:

    $ git clone git@github.com/USERNAME/{{ project_name }}.git
    $ cd {{ project_name }}

Secondly, create a new environment using

    $ python3 -m venv venv

Further activate the environment and instal all requirements using

    $ pip3 install -r requirements.txt

Then apply the migrations

    $ python manage.py migrate

and run a server

    $python3 manage.py runserver
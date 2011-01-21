Django-skeleton
===============

Django-skeleton is a tool and the bunch of config templates for a Django project generation
Inspired by `django-site-gen`_.

Features
--------

* Works out of the box
* Almost fully configurable. It's possible to use in templates all variables from config file
* `Fabric` library for project deployment


Requirements
------------

* Python 2.4 or later
* `PyYAML`_
* `virtualenv`_


Get Django-skeleton
-------------------

Clone `repository`_.


Usage
-----

Change settings in conf.yaml file and run::
  
  python generate_site.py

That's all.

Some tips about settings variable for default templates:

* project_name - Project name (used by `python manage.py statproject {{ project_name }}`)
* site_name - Domain name (used by nginx config file and fabfile)
* port - port of `gunicorn`_ (uses for Nginx proxy settings)
* base_site - place where to create virtualenv
* production_base_site - place where to create project structure on a production server


.. _Fabric: http://fabfile.org/
.. _repository: https://github.com/spoof/django-skeleton
.. _django-site-gen: https://github.com/coleifer/django-site-gen
.. _gunicorn: http://gunicorn.org/
.. _PyYAML: http://pyyaml.org/
.. _virtualenv: http://pypi.python.org/pypi/virtualenv

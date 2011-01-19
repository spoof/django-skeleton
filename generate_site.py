#!/usr/bin/env python
# encoding: utf-8
"""
generate_site.py

Created by Sergey Safonov on 2011-01-14.
Copyright (c) 2011 . All rights reserved.
"""

import os, sys
import re
import yaml

RE_VALID_PROJECT_NAME = re.compile('\w+$')
RE_VALID_PORT = re.compile('\d+$')

CONFIG_DIR = 'conf'

def check_file_exist(filename, paths=[]):
    """Check ether or not file exist in `paths` or in $PATH variable"""
    if not paths:
        paths = os.environ["PATH"].split(os.pathsep)
    return any([os.path.exists(os.path.join(p, filename)) for p in paths])

def initialize(config_file='conf.yaml'):
    config = {
        'base_site': os.getcwd()
    }
    while 1:
        input_msg = 'Project name'
        project_name = raw_input(input_msg + ': ')
        if not RE_VALID_PROJECT_NAME.match(project_name):
            sys.stderr.write("Error: That project name is invalid. It must not contain spaces.\n")
            continue
        
        if project_name:
            config['project_name'] = project_name
            break
    while 1:
        input_msg = 'Site name'
        site_name = raw_input(input_msg + ': ')
        if site_name:
            config['site_name'] = site_name
            break
    while 1:
        input_msg = 'HTTP/FastCGI port'
        port = raw_input(input_msg + ': ')
        if not RE_VALID_PORT.match(port):
            sys.stderr.write("Error: That port is invalid. Use only digits.\n")
            continue
        
        if port:
            config['port'] = port
            break
    input_msg = 'Project directory (Leave blank to use current directory)'
    base_site = raw_input(input_msg + ': ')
    if base_site:
        base_site = os.path.expanduser(base_site)
        try:
            if not os.path.exists(base_site):
                os.makedirs(base_site)
        except OSError, e:
            print "Error: ", e
    
    site_root = os.path.join(config['base_site'], project_name)
    current_dir = os.path.dirname(os.path.realpath(__file__))
    config_file = os.path.join(current_dir, config_file)
    configs_dir = os.path.join(current_dir, "conf")
    project_root = os.path.join(site_root, project_name)
    
    try:
        f = open(config_file, 'r')
        config = yaml.load(f)
        f.close() 
    except OSError, e:
        sys.stderr.write("Couldn't read config file. %s \n" % (str(e)))
    
    config['settings'].update({
        'site_root': site_root,
        'project_name': project_name,
        'site_name': site_name,
        'port': port,
        'base_site': base_site or os.getcwd(),
        'configs_dir': configs_dir,
        'project_root': project_root,
    })
    print config
    return config

def generate():
    try:
        config = initialize()
        settings = config['settings']
        directories = config['directories']
        files = config['files']
        print 'Creating a virtualenv for the project'
        os.system('cd %(base_site)s && virtualenv --no-site-packages %(project_name)s' % settings)
        os.chdir(settings['site_root'])
        os.system('pip -E . install -r %(configs_dir)s/dev_requirements.pip && pip -E . install -r %(configs_dir)s/requirements.pip' % settings)
        print 'Creating the Django project \'%(project_name)s\'' % (settings)
        os.system('source bin/activate && django-admin.py startproject %(project_name)s' % settings)
        
        if directories:
            print "Creating directory stucture"
        for directory_dict in directories:
            for k, v in directory_dict.items():
                try:
                    os.makedirs(v % settings)
                except OSError, e:
                    if e.errno != 17:
                        raise OSError(e)
        
        execfile('bin/activate_this.py', dict(__file__='bin/activate_this.py'))
        from django.conf import settings as django_settings
        from django.template import Context
        from django.template.loader import get_template
        
        django_settings.configure(
                TEMPLATE_DIRS=(settings['configs_dir'],),
            )
        
        context = Context(settings)
        def render_template(template_name, dest, context):
            content = get_template(template_name).render(context)
            f = open(dest % context, 'w')
            print "Writing %s" % (dest % context)
            f.write(content)
            f.close()
        
        for f, template_name in files.items():
            render_template(template_name, f, context)
        
    except KeyboardInterrupt:
        sys.stderr.write("\nOperation cancelled.\n")
        sys.exit(1)

if __name__ == "__main__":
  generate()

#!/usr/bin/env python
# encoding: utf-8
"""
generate_site.py

Created by Sergey Safonov on 2011-01-14.
Copyright (c) 2011 . All rights reserved.
"""

import os, sys
import re, copy
import yaml


AVAILABLE_SECTIONS = ['settings', 'directories', 'files', 'copy']
RE_VALID_PROJECT_NAME = re.compile('\w+$')
RE_VALID_PORT = re.compile('\d+$')

CONFIG_DIR = 'conf'

def normalize_to_dict(data, context={}, update_context=False):
    result = {}
    def _update_result(k, v, context=context, update_context=update_context):
        r = context and v % context or v
        if update_context:
            if not context.has_key(k):
                context[k] = r
        result[k] = r
    
    if isinstance(data, list):
        for value in data:
            for k, v in value.items():
                _update_result(k, v)
    
    elif isinstance(data, dict):
        for k, v in data.items():
            _update_result(k, v)
    return result
    
def get_variable(settings, var, description, error='Cannot be empty', test_function=lambda x: x, empty=False):
    if settings.has_key(var):
        return settings[var]
    
    while 1:
        var = raw_input(description + ': ')
        if not empty:
            if not test_function(var):
                sys.stderr.write("Error: %s\n" % error)
                continue
            else:
                break
        else:
            break
    return var

def initialize(config_file='conf.yaml'):
    current_dir = os.path.dirname(os.path.realpath(__file__))
    config_file = os.path.join(current_dir, config_file)
    configs_dir = os.path.join(current_dir, CONFIG_DIR)
    
    try:
        f = open(config_file, 'r')
        config = yaml.load(f)
        f.close() 
    except OSError, e:
        sys.stderr.write("Couldn't read config file. %s \n" % (str(e)))
    
    settings = normalize_to_dict(config['settings'])
    project_name = get_variable(settings, 'project_name', description='Project name', 
                                 error='That project name is invalid. It must not contain spaces.', 
                                 test_function=lambda x: RE_VALID_PROJECT_NAME.match(x))
    site_name = get_variable(settings, 'site_name', description='Site name')
    port = get_variable(settings, 'port', description='HTTP/FastCGI port', 
                                 error='That port is invalid. Use only digits', 
                                 test_function=lambda x: RE_VALID_PORT.match(x))
    base_site = get_variable(settings, 'base_site', description='Project directory (Leave blank to use current directory)',  
                                 empty=True)
    
    if base_site:
        base_site = os.path.expanduser(base_site)
        try:
            if not os.path.exists(base_site):
                os.makedirs(base_site)
        except OSError, e:
            print "Error: ", e
    else:
        base_site = os.getcwd()
    
    production_root = get_variable(settings, 'production_root', description='Production site root', error='Production site root cannot be empty')
    production_root = production_root.rstrip("/")
    site_root = os.path.join(base_site, project_name)
    project_root = os.path.join(site_root, project_name)
    
    config['context'] = {
        'site_root': site_root,
        'project_name': project_name,
        'site_name': site_name,
        'port': port,
        'base_site': base_site,
        'configs_dir': configs_dir,
        'project_root': project_root,
        'production_root': os.path.join(production_root, project_name),
    }
    
    for section_name in AVAILABLE_SECTIONS:
        try:
            section = config[section_name]
        except KeyError:
            continue
        
        update_context = section_name in ('settings', 'directories')
        section_normalized = normalize_to_dict(section, context=config['context'], update_context=update_context)
        if not update_context:
            config[section_name].update(section_normalized)
    
    return config

def generate():
    try:
        config = initialize()
        context = config['context']
        directories = config['directories']
        files = config['files']
        print 'Creating a virtualenv for the project'
        os.system('cd %(base_site)s && virtualenv --no-site-packages %(project_name)s' % context)
        os.chdir(context['site_root'])
        os.system('pip -E . install -r %(configs_dir)s/dev_requirements.pip && pip -E . install -r %(configs_dir)s/requirements.pip' % context)
        print 'Creating the Django project \'%(project_name)s\'' % (context)
        os.system('source bin/activate && django-admin.py startproject %(project_name)s' % context)
        
        if directories:
            print "Creating directory stucture"
        for directory_dict in directories:
            for k, v in directory_dict.items():
                try:
                    os.makedirs(v % context)
                except OSError, e:
                    if e.errno != 17:
                        raise OSError(e)
        
        execfile('bin/activate_this.py', dict(__file__='bin/activate_this.py'))
        from django.conf import settings as django_settings
        from django.template import Context
        from django.template.loader import get_template
        
        django_settings.configure(
                TEMPLATE_DIRS=(context['configs_dir'],),
            )
        
        context = Context(context)
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

#!/usr/bin/env python
# encoding: utf-8
"""
generate_site.py

Created by Sergey Safonov on 2011-01-14.
Copyright (c) 2011 . All rights reserved.
"""

import sys
import re


RE_VALID_PORT = re.compile('\d+$')

def generate():
    try:
        while 1:
            input_msg = 'Project name'
            project_name = raw_input(input_msg + ': ')
            if project_name:
                break
        
        while 1:
            input_msg = 'Site name'
            site_name = raw_input(input_msg + ': ')
            if site_name:
                break
        while 1:
            input_msg = 'Port'
            port = raw_input(input_msg + ': ')
            if not RE_VALID_PORT.match(port):
                sys.stderr.write("Error: That port is invalid. Use only digits.\n")
                continue
            
            if port:
                break
        
    except KeyboardInterrupt:
        sys.stderr.write("\nOperation cancelled.\n")
        sys.exit(1)

if __name__ == "__main__":
  generate()

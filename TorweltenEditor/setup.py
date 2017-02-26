# coding=utf 8
"""
This setup.py is used to compile a standalone windows version of the program
to call it execute: python setup.py py2exe
"""

from distutils.core import setup
import py2exe
import os


#building data_files lists ... 
dirs = ['images','ui_img','data','fonts','templates','chars']
data_files = []

for dir in dirs:
    files = os.listdir(dir)
    file_list = []
    for file in files:
        if os.path.isfile(dir+"/"+file): file_list.append(dir+"/"+file)
    data_files.append((dir,file_list))


data_files.append(("",["LICENSE_DE","README_DE"]))
    
setup(windows=['TorweltenEditor.py'],data_files = data_files)
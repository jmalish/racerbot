import json
import random
import time
import urllib
import xml.etree.ElementTree as ET


a = 0


def changeA(newVar):
    a = newVar

print a  # returns 0
changeA(1)
print a  # returns 1

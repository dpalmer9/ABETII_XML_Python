import xml.etree.ElementTree as ET
from lxml import etree

active_xml = ET.parse('Test.xml') #Open XML Object

active_xml_root = active_xml.getroot() #Get Core Root Structure

active_mouse_id = active_xml_root[1][10][1].text


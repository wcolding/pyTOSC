import xml.etree.ElementTree as ET
import uuid
from enum import Enum

class ObjType(Enum):
    LABEL = 0


def HexToColorTuple(hex_string: str):
    if len(hex_string) < 8:
        return (0,0,0,0)
    
    r = int(hex_string[0:2], 16) / 255
    g = int(hex_string[2:4], 16) / 255
    b = int(hex_string[4:6], 16) / 255
    a = int(hex_string[6:8], 16) / 255
    return (r,g,b,a)

def SetProperty(element: ET.Element, name: str, value: str):
    property = element.find(f".//*[key='{name}']")
    property[1].text = value

def SetMidiCC(element: ET.Element, channel: int, controller: int):
    midi_msg = element.find(".//*[type='CONTROLCHANGE']")
    midi_msg[1].text = str(channel - 1)
    midi_msg[2].text = str(controller)

def GetChildByName(element: ET.Element, name: str):
    children = element.findall(".//node")
    for child in children:
        name_attribute = child.find(".//*[key='name']")
        if name_attribute[1].text == name:
            return child

def GetChildByType(element: ET.Element, type: ObjType):
    children = element.findall(".//node")

    for child in children:
        if child.get('type') == type.name:
            return child

def SetColor(element: ET.Element, color: tuple):
    if len(color) < 4:
        return
    
    color_attribute = element.find(".//*[key='color']")
    for i in range(0, 4):
        color_attribute[1][i].text = f'{color[i]:.6f}'

def SetTextValue(element: ET.Element, value: str):
    text_element = element.find(".//*[key='text']")
    text_element[3].text = value

def SetRect(element: ET.Element, rect_name: str, x: int, y: int, w: int, h: int):
    rect = element.find(f".//*[key='{rect_name}']")
    rect[1][0].text = str(x)
    rect[1][1].text = str(y)
    rect[1][2].text = str(w)
    rect[1][3].text = str(h)

def SetNewUUIDs(element: ET.Element):
    element.set('ID', str(uuid.uuid4()))

    children = element.findall(".//node")     
    for child in children:
        child.set('ID', str(uuid.uuid4()))
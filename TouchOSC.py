import xml.etree.ElementTree as ET

def HexToColorTuple(hex_string: str):
    if len(hex_string) < 8:
        return (0,0,0,0)
    
    r = int(hex_string[0:2], 16) / 255
    g = int(hex_string[2:4], 16) / 255
    b = int(hex_string[4:6], 16) / 255
    a = int(hex_string[6:8], 16) / 255
    return (r,g,b,a)

def SetAttribute(element: ET.Element, name: str, value: str):
    attribute = element.find(f".//*[key='{name}']")
    attribute[1].text = value

def GetChildByName(element: ET.Element, name: str):
    children = element.findall(".//node")
    for child in children:
        name_attribute = child.find(".//*[key='name']")
        if name_attribute[1].text == name:
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
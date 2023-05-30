from configparser import ConfigParser
import xml.etree.ElementTree as ET
import copy
import uuid
import math

class IterableObject():
    def __init__(self, config_file: str):
        self.__configparser = ConfigParser()
        self.__configparser.read(config_file)
        self.__header = ""

    def GetPropertyValue(self, property: str):
        return self.__configparser[self.__header][property]

    def GetInt(self, property: str):
        return int(self.GetPropertyValue(self.__header, property))

    def Iterate(self, root: ET.Element):
        pass


class IterableButton(IterableObject):
    def __init__(self, config_file:str):
        super.__init__(self, config_file)
        self.__header = 'Buttons'
        
        self.grid_start_x = self.GetInt('GridStartX')
        self.grid_start_y = self.GetInt('GridStartY')

        self.button_width = self.GetInt('ButtonWidth')
        self.button_height = self.GetInt('ButtonHeight')

        self.padding_x = self.GetInt('PaddingX')
        self.padding_y = self.GetInt('PaddingY')

        self.auto_channels = self.GetInt('AutoChannels')
        self.buttons_per_row = self.GetInt('ButtonsPerRow')
        self.text_size = self.GetInt('TextSize')

    def Iterate(self, root: ET.Element):
        xml_iterable_buttons_groups = root.findall(".//*[key='iterableButton']......")

        if len(xml_iterable_buttons_groups) < 1:
            return
        
        for group in xml_iterable_buttons_groups:
            xml_iterable_buttons = group.findall(".//*[key='iterableButton']....")
        
            for i in range(self.auto_channels):
                if i == 0:
                    curButton = xml_iterable_buttons[0]
                else:
                    curButton = copy.deepcopy(xml_iterable_buttons[0])
                
                children = curButton.findall(".//node")

                name = curButton.find(".//*[key='name']")
                tag = curButton.find(".//*[key='tag']")
                iterable = curButton.find(".//*[key='iterableButton']")
                frame = curButton.find(".//*[key='frame']")
                name[1].text = f'Ch{i+1:02}'
                tag[1].text = f'{i+1:02}'
                if i > 0:
                    iterable[1].text = '0'

                if i == 0:
                    # Resize button
                    frame[1][2].text = str(self.button_width)
                    frame[1][3].text = str(self.button_height)

                    # Position button
                    frame[1][0].text = str(self.grid_start_x)
                    frame[1][1].text = str(self.grid_start_y)

                    # Operate on children (button and label)
                    for child in children:
                        child_frame = child.find(".//*[key='frame']")
                        child_frame[1][2].text = str(self.button_width)
                        child_frame[1][3].text = str(self.button_height)
                else:
                    # Reposition duplicate buttons
                    row = math.floor(i / self.buttons_per_row)
                    column = i % self.buttons_per_row

                    new_x = self.grid_start_x + ((self.button_width + self.padding_x) * column)
                    new_y = self.grid_start_y + ((self.button_height + self.padding_y) * row)

                    frame[1][0].text = str(new_x)
                    frame[1][1].text = str(new_y)

                # Write default names for button labels and set text size
                for child in children:
                    if child.get('type') == 'LABEL':
                        text_val = child.find(".//*[key='text']")
                        text_val[3].text = name[1].text
                        text_size_val = child.find(".//*[key='textSize']")
                        text_size_val[1].text = str(self.text_size)

                # For all but the first button, update all UUIDs
                if i > 0:
                    curButton.set('ID', str(uuid.uuid4()))

                    for child in children:
                        child.set('ID', str(uuid.uuid4()))
                        
                    # Append new button
                    group.append(curButton)
from configparser import ConfigParser
import xml.etree.ElementTree as ET
import copy
import uuid
import math
from pyTOSC.TouchOSC import *

class IterableObject():
    def __init__(self, config_file: str, header: str = 'Default'):
        self.__configparser = ConfigParser()
        self.__configparser.read(config_file)
        self.__header = header
        self.sections = self.__configparser.sections()

    def GetPropertyValue(self, property: str, header: str = ''):
        if header == '':
            header = self.__header
        return self.__configparser[header][property]

    def GetInt(self, property: str, header: str = ''):
        return int(self.GetPropertyValue(property, header))

    def Iterate(self, root: ET.Element):
        pass


class IterableButton(IterableObject):
    def __init__(self, config_file: str):
        super().__init__(config_file, 'Buttons')
        
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

class AutoPager(IterableObject):
    def __init__(self, config_file:str):
        super().__init__(config_file, 'Default')
        self.tabs = self.sections

    def Iterate(self, root: ET.Element):
        xml_auto_pagers = root.findall(".//*[key='autoPager']....")

        if len(xml_auto_pagers) < 1:
            return

        print(f'Tabs defined: {self.tabs}')

        for pager in xml_auto_pagers:
            pager_id = int(pager.find(".//*[key='autoPager']")[1].text)
            print(f'Pager id: {pager_id}')
            pager_children = pager.find(".//children")
            current_tab_index = 0

            for tab in self.tabs:
                if self.GetInt('Pager', tab) == pager_id:
                    tab_object = pager.find(".//children/node")
                    if tab_object != None:
                        if current_tab_index > 0:
                            tab_object = copy.deepcopy(tab_object)

                        tab_name = tab_object.find(".//*[key='name']")
                        tab_label = tab_object.find(".//*[key='tabLabel']")
                        tab_name[1].text = self.GetPropertyValue('Label', tab)
                        tab_label[1].text = self.GetPropertyValue('Label', tab)

                        tab_group = tab_object.find(".//children/node")
                        if tab_group != None:
                            tab_group_tag = tab_group.find(".//*[key='tag']")
                            mix_number = self.GetInt('Index', tab)
                            print(f'Creating tab for index {mix_number:02}...')
                            tab_group_tag[1].text = f'{mix_number:02}'
                            
                            if current_tab_index > 0:
                                # Reassign UUIDs
                                tab_nodes = tab_object.findall(".//children/node")
                                if len(tab_nodes) > 0:
                                    for node in tab_nodes:
                                        node.set('ID', str(uuid.uuid4()))
                                
                                # Add new tab 
                                pager_children.append(tab_object)

                            current_tab_index += 1

            print()

class IterableCamera(IterableObject):
    def __init__(self, layout_config: str, camera_config: str):
        super().__init__(layout_config, 'Cameras')
        self.__cam_config = IterableObject(camera_config)

        self.cams_per_row = self.GetInt('CamerasPerRow')

        self.grid_start_x = self.GetInt('GridStartX')
        self.grid_start_y = self.GetInt('GridStartY')

        self.cam_width = self.GetInt('CameraWidth')
        self.cam_height = self.GetInt('CameraHeight')

        self.padding_x = self.GetInt('PaddingX')
        self.padding_y = self.GetInt('PaddingY')

        self.cameras = self.__cam_config.sections

    def Iterate(self, root: ET.Element):
        xml_iterable_camera_groups = root.findall(".//*[key='iterableCamera']......")

        if len(xml_iterable_camera_groups) < 1:
            return

        print(f'Cameras defined: {self.cameras}')
        for group in xml_iterable_camera_groups:
            xml_iterable_cameras = group.findall(".//*[key='iterableCamera']....")

            for i in range(len(self.cameras)):
                if i == 0:
                    cur_cam = xml_iterable_cameras[0]
                else:
                    cur_cam = copy.deepcopy(xml_iterable_cameras[0])

                children = cur_cam.findall(".//node")
                
                xml_frame = cur_cam.find(".//*[key='frame']")                

                bus = self.__cam_config.GetInt('Bus', self.cameras[i])
                SetAttribute(cur_cam, 'mixbus', str(bus))
                SetAttribute(cur_cam, 'tag', f'{bus:02}')

                if i > 0:
                    SetAttribute(cur_cam, 'iterableCamera', str(0))
                
                main_color = self.__cam_config.GetPropertyValue('MainColor', self.cameras[i])
                bg_color = self.__cam_config.GetPropertyValue('BGColor', self.cameras[i])

                SetAttribute(cur_cam, 'cameraName', self.cameras[i])
                SetAttribute(cur_cam, 'mainColor', main_color)
                SetAttribute(cur_cam, 'bgColor', bg_color)

                main_color_tuple = HexToColorTuple(main_color)
                bg_color_tuple = HexToColorTuple(bg_color)

                cam_bg_obj = GetChildByName(cur_cam, 'CameraBackground')
                cam_color_obj = GetChildByName(cur_cam, 'CameraColor')
                cam_label_obj = GetChildByName(cur_cam, 'CameraLabel')

                SetColor(cam_bg_obj, bg_color_tuple)
                SetColor(cam_color_obj, main_color_tuple)
                SetColor(cam_label_obj, main_color_tuple)
                SetTextValue(cam_label_obj, self.cameras[i])

                if i == 0:
                    # Resize camera
                    xml_frame[1][2].text = str(self.cam_width)
                    xml_frame[1][3].text = str(self.cam_height)

                    # Position camera
                    xml_frame[1][0].text = str(self.grid_start_x)
                    xml_frame[1][1].text = str(self.grid_start_y)

                    # Operate on children (button and label)
                    # todo
                else:
                    # Reposition duplicate cameras
                    row = math.floor(i / self.cams_per_row)
                    column = i % self.cams_per_row

                    new_x = self.grid_start_x + ((self.cam_width + self.padding_x) * column)
                    new_y = self.grid_start_y + ((self.cam_height + self.padding_y) * row)

                    xml_frame[1][0].text = str(new_x)
                    xml_frame[1][1].text = str(new_y)

                # For all but the first button, update all UUIDs
                if i > 0:
                    cur_cam.set('ID', str(uuid.uuid4()))

                    for child in children:
                        child.set('ID', str(uuid.uuid4()))
                        
                    # Append new button
                    group.append(cur_cam)
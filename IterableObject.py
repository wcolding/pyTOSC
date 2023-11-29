from configparser import ConfigParser
import copy
import math
from pyTOSC.TouchOSC import *

class IterableObject():
    def __init__(self, xml_root: ET.Element, config_file: str, header: str = 'Default'):
        self.__configparser = ConfigParser()
        self.__configparser.read(config_file)
        self.__header = header
        self.sections = self.__configparser.sections()
        self.root = xml_root

    def GetPropertyValue(self, property: str, header: str = ''):
        header = header or self.__header
        return self.__configparser.get(header, property, fallback=None)

    def GetInt(self, property: str, header: str = ''):
        value = self.GetPropertyValue(property, header)
        try:
            return int(value)
        except(TypeError, ValueError):
            return 0

    def Iterate(self):
        pass

    def GetChildNodes(self, parent_node: ET.Element, key: str, outer_offset: int):
        search_string = f'.//*[key=\'{key}\']'
        search_string += '..' * outer_offset
        return parent_node.findall(search_string)
        
    def GetChildNodesByValue(self, parent_node: ET.Element, value: str, outer_offset: int):
        search_string = f'.//*[value=\'{value}\']'
        search_string += '..' * outer_offset
        return parent_node.findall(search_string)

class IterableButton(IterableObject):
    def __init__(self, xml_root: ET.Element, layout_config: str, channel_config: str = "Default", colors_config: str = "colors.ini"):
        super().__init__(xml_root, layout_config, 'Buttons')

        self.auto_channels = self.GetInt('AutoChannels')
        self.channel_count = self.auto_channels

        if channel_config != "Default" and self.auto_channels == 0:
            self.__channel_config = IterableObject(xml_root, channel_config)
            self.channels = self.__channel_config.sections
            self.channel_count = len(self.channels)
        else:
            self.__channel_config = None

        self.__colors_config = IterableObject(xml_root, colors_config)
        
        self.grid_start_x = self.GetInt('GridStartX')
        self.grid_start_y = self.GetInt('GridStartY')

        self.button_width = self.GetInt('ButtonWidth')
        self.button_height = self.GetInt('ButtonHeight')

        self.padding_x = self.GetInt('PaddingX')
        self.padding_y = self.GetInt('PaddingY')

        self.buttons_per_row = self.GetInt('ButtonsPerRow')
        self.text_size = self.GetInt('TextSize')

        self.latefill_buttons = []

    def Iterate(self):
        xml_iterable_buttons_groups = self.GetChildNodes(self.root, 'iterableButton', 3)

        if len(xml_iterable_buttons_groups) < 1:
            return
        
        for group in xml_iterable_buttons_groups:
            xml_iterable_buttons = self.GetChildNodes(group, 'iterableButton', 2)
        
            for i in range(self.channel_count):
                if i == 0:
                    cur_button = xml_iterable_buttons[0]
                else:
                    cur_button = copy.deepcopy(xml_iterable_buttons[0])

                SetProperty(cur_button, 'name', f'Ch{i+1:02}')

                if i > 0:
                    SetProperty(cur_button, 'iterableButton', str(0))

                label_obj = GetChildByType(cur_button, ObjType.LABEL)
                SetProperty(label_obj, 'textSize', str(self.text_size))

                if self.auto_channels > 0:
                    # Tag
                    SetProperty(cur_button, 'tag', f'{i+1:02}')

                    # Frame
                    row = math.floor(i / self.buttons_per_row)
                    column = i % self.buttons_per_row
                    start_x = self.grid_start_x + ((self.button_width + self.padding_x) * column)
                    start_y = self.grid_start_y + ((self.button_height + self.padding_y) * row)
                    SetRect(cur_button, 'frame', start_x, start_y, self.button_width, self.button_height)
                    
                    # Label
                    SetTextValue(label_obj, f'Ch{i+1:02}')
                else:
                    # Set manually according to config

                    # Tag
                    channel = self.__channel_config.GetInt('X32Channel', self.channels[i])
                    SetProperty(cur_button, 'tag', f'{channel:02}')

                    # Frame
                    position = self.__channel_config.GetPropertyValue('Position', self.channels[i])
                    if position:
                        x, y = position.split(',')
                        start_x = int(x)
                        start_y = int(y)
                        SetRect(cur_button, 'frame', start_x, start_y, self.button_width, self.button_height)

                    # Label
                    SetTextValue(label_obj, self.channels[i])

                    # Color
                    color_name = self.__channel_config.GetPropertyValue('Color', self.channels[i])
                    hex_color_string = self.__colors_config.GetPropertyValue('Hex', color_name)
                    color_tuple = (0,0,0,0)
                    if hex_color_string != None:
                        color_tuple = HexToColorTuple(hex_color_string)
                    
                    button_obj = GetChildByName(cur_button, 'ChannelButton')
                    SetColor(button_obj, color_tuple)

                    # Midi
                    midi_channel = self.__channel_config.GetInt('MidiChannel', self.channels[i])
                    midi_controller = self.__channel_config.GetInt('MidiController', self.channels[i])
                    SetProperty(cur_button, 'midiChannel', str(midi_channel))
                    SetProperty(cur_button, 'midiController', str(midi_controller))

                    fader_obj = GetChildByName(cur_button, 'ChannelTrim')
                    SetMidiCC(fader_obj, midi_channel, midi_controller)

                # Scale child objects
                children = cur_button.findall(".//node")
                for child in children:
                        SetRect(child, 'frame', 0, 0, self.button_width, self.button_height)

                # Add button
                if i > 0:  
                    cameras = None
                    if self.__channel_config != None:                      
                        # Check if camera-specific
                        cameras = self.__channel_config.GetPropertyValue('Cameras', self.channels[i])

                    if cameras:
                        self.latefill_buttons.append([cur_button, cameras])
                    else:
                        SetNewUUIDs(cur_button)
                        group.append(cur_button)

    def LateFill(self):
        if self.__channel_config == None:
            return
        
        latefill_cameras = self.GetChildNodes(self.root, 'iterableCamera', 2)

        for button in self.latefill_buttons:
            for camera in latefill_cameras:
                cam_name = GetProperty(camera, "cameraName")
                if cam_name in button[1]:
                    camera_channels = self.GetChildNodesByValue(camera, 'Channels', 2)
                    if (camera_channels):
                        new_button = copy.deepcopy(button[0])
                        SetNewUUIDs(new_button)

                        channels_children_node = GetImmediateChild(camera_channels[0], 'children')
                        if (channels_children_node):
                            channels_children_node.append(new_button)
                            button_name = GetTextValue(new_button)
                            print(f'Button \'{button_name}\' placed in {cam_name}')

class AutoPager(IterableObject):
    def __init__(self, xml_root: ET.Element, config_file:str):
        super().__init__(xml_root, config_file, 'Default')
        self.tabs = self.sections

    def Iterate(self):
        xml_auto_pagers = self.GetChildNodes(self.root, 'autoPager', 2)

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
    def __init__(self, xml_root: ET.Element, layout_config: str, camera_config: str):
        super().__init__(xml_root, layout_config, 'Cameras')
        self.__cam_config = IterableObject(xml_root, camera_config)

        self.cams_per_row = self.GetInt('CamerasPerRow')

        self.grid_start_x = self.GetInt('GridStartX')
        self.grid_start_y = self.GetInt('GridStartY')

        self.cam_width = self.GetInt('CameraWidth')
        self.cam_height = self.GetInt('CameraHeight')

        self.padding_x = self.GetInt('PaddingX')
        self.padding_y = self.GetInt('PaddingY')

        self.cameras = self.__cam_config.sections

    def Iterate(self):
        xml_iterable_camera_groups = self.GetChildNodes(self.root, 'iterableCamera', 3)

        if len(xml_iterable_camera_groups) < 1:
            return

        print(f'Cameras defined: {self.cameras}')
        for group in xml_iterable_camera_groups:
            xml_iterable_cameras = self.GetChildNodes(group, 'iterableCamera', 2)

            for i in range(len(self.cameras)):
                if i == 0:
                    cur_cam = xml_iterable_cameras[0]
                else:
                    cur_cam = copy.deepcopy(xml_iterable_cameras[0])
    
                bus = self.__cam_config.GetInt('Bus', self.cameras[i])
                SetProperty(cur_cam, 'mixbus', str(bus))
                SetProperty(cur_cam, 'tag', f'{bus:02}')

                SetProperty(cur_cam, 'mixIndex', str(i+1))

                if i > 0:
                    SetProperty(cur_cam, 'iterableCamera', str(0))
                
                main_color = self.__cam_config.GetPropertyValue('MainColor', self.cameras[i])
                bg_color = self.__cam_config.GetPropertyValue('BGColor', self.cameras[i])

                SetProperty(cur_cam, 'cameraName', self.cameras[i])
                SetProperty(cur_cam, 'mainColor', main_color)
                SetProperty(cur_cam, 'bgColor', bg_color)

                main_color_tuple = HexToColorTuple(main_color)
                bg_color_tuple = HexToColorTuple(bg_color)

                cam_bg_obj = GetChildByName(cur_cam, 'CameraBackground')
                cam_color_obj = GetChildByName(cur_cam, 'CameraColor')
                cam_label_obj = GetChildByName(cur_cam, 'CameraLabel')

                cam_clear_obj = GetChildByName(cur_cam, 'CameraClear')
                cam_tone_obj = GetChildByName(cur_cam, 'CameraTone')

                mix_group_obj = GetChildByName(cur_cam, 'MixGroupSelect')
                mute_obj = GetChildByName(cur_cam, 'Mute')
                solo_obj = GetChildByName(cur_cam, 'Solo')

                cam_select_obj = GetChildByName(cur_cam, 'CameraSelect')
                cam_select_label_obj = GetChildByName(cam_select_obj, 'CameraLabel')
                cam_select_obj_children = cam_select_obj.find('children')

                SetColor(cam_bg_obj, bg_color_tuple)
                SetColor(cam_color_obj, main_color_tuple)
                SetColor(cam_label_obj, main_color_tuple)
                SetTextValue(cam_label_obj, self.cameras[i])

                row = math.floor(i / self.cams_per_row)
                column = i % self.cams_per_row
                start_x = self.grid_start_x + ((self.cam_width + self.padding_x) * column)
                start_y = self.grid_start_y + ((self.cam_height + self.padding_y) * row)
                SetRect(cur_cam, 'frame', start_x, start_y, self.cam_width, self.cam_height)

                # Scale child objects
                SetRect(cam_bg_obj, 'frame', 0, 0, self.cam_width, self.cam_height)
                SetRect(cam_clear_obj, 'frame', 0, 0, self.cam_width, self.cam_height)
                SetRect(cam_tone_obj, 'frame', 0, 0, self.cam_width, self.cam_height)

                mix_group_frame = GetFrame(mix_group_obj)
                SetRect(mix_group_obj, 'frame', mix_group_frame[0], self.cam_height - 48, mix_group_frame[2], mix_group_frame[3])

                mute_frame = GetFrame(mute_obj)
                SetRect(mute_obj, 'frame', mute_frame[0], self.cam_height - 48, mute_frame[2], mute_frame[3])

                solo_frame = GetFrame(solo_obj)
                SetRect(solo_obj, 'frame', solo_frame[0], self.cam_height - 58, solo_frame[2], solo_frame[3])

                # Set camera dropdown values
                for dd in range(len(self.cameras)):
                    if dd == 0:
                        cur_dd = cam_select_label_obj
                    else:
                        cur_dd = copy.deepcopy(cam_select_label_obj)
                    
                    dd_color = self.__cam_config.GetPropertyValue('MainColor', self.cameras[dd])
                    dd_color_tuple = HexToColorTuple(dd_color)
                    dd_label = self.cameras[dd]

                    dd_color_obj = GetChildByName(cur_dd, 'Color')
                    dd_label_obj = GetChildByName(cur_dd, 'Label')
                    SetColor(dd_color_obj, dd_color_tuple)
                    SetTextValue(dd_label_obj, dd_label)

                    if dd > 0:
                        dd_frame = GetFrame(cur_dd)
                        SetRect(cur_dd, 'frame', dd_frame[0], int(dd_frame[1]) + (dd * 26), dd_frame[2], dd_frame[3])
                        SetNewUUIDs(cur_dd)

                        cam_select_obj_children.insert(-1, cur_dd) # Second to last


                # For all but the first camera, update all UUIDs
                if i > 0:
                    SetNewUUIDs(cur_cam)
                        
                    # Append new camera
                    group.append(cur_cam)
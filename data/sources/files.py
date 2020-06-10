from pygame import mixer
from os import walk, sep, path

class Files:
    
    paths = {}
    
    @classmethod
    def load(cls):
        
        #====# load images #====#
        main_folders = ['images', 'enemy', 'ground', 'npc', 'player', 'potions', 'screens']
        raw_folders = ['idle', 'born', 'hurted', 'run', 'born', 'bg_gif']
        cls.load_files(main_folders, raw_folders)
        cls.paths['images']['icon'] = path.join('.', 'data', 'images', 'icon.png')
        
        #====# load sounds #====#
        main_folders = ['sounds', 'loops', 'sfx']
        raw_folders = []
        cls.load_files(main_folders, raw_folders)
        
        #====# load font #====#
        font_path = path.join('.', 'data', 'font', 'arcade-classic.TTF')
        cls.paths['font'] = font_path
    
    @classmethod
    def load_files(cls, main_folders, raw_folders):
        start_folder = main_folders[0]
        cls.paths[start_folder] = {}
        
        for folder_name in main_folders[1:]:
            cls.paths[start_folder][folder_name] = {}
            
            start_path = path.join('.', 'data', start_folder, folder_name)
            
            for root, dirs, files in walk(start_path):
                if len(files) != 0:
                    nested_keys = root.split(sep)
                    start_index = nested_keys.index(start_folder) + 1
                    nested_keys = nested_keys[start_index:]

                    cls.make_nested_keys(cls.paths[start_folder], nested_keys)
                    
                    last_dir = root.split(sep)[-1]
                    if last_dir in raw_folders:
                        cls.assign_nested_key(cls.paths[start_folder], nested_keys, root)
                    else:
                        for file in files:
                            file_path = path.join(root, file)
                            
                            file_key = file.split('.')[0]
                            prev_key = nested_keys.copy()
                            nested_keys.append(file_key)
                            cls.assign_nested_key(cls.paths[start_folder], nested_keys, file_path)
                            nested_keys = prev_key.copy()
    
    @classmethod
    def get_full_path(cls, *dirs):
        alt_dict = cls.paths[dirs[0]]
        dirs_len = len(dirs)
            
        for directory in dirs[1:-1]:
            alt_dict = alt_dict[directory]
        
        try:
            full_path = alt_dict[dirs[-1]]
        except KeyError:
            print('\n\tKeyError: Are you sure there is such file or directory?')
            print('\tHint: double check your directory or file names')
        else:
            return full_path
    
    @staticmethod
    def make_nested_keys(dic: dict, keys: list):
        ref_dic = dic[keys[0]]
        keys = keys[1:]
        for i in range(len(keys)):
            key = keys[i]
            if key not in ref_dic.keys():
                ref_dic[key] = {}
                
            ref_dic = ref_dic[key]
            
    @staticmethod
    def assign_nested_key(dic: dict, keys: list, value):
        ref_dic = dic[keys[0]]
        for key in keys[1:-1]:
            ref_dic = ref_dic[key]
            
        ref_dic[keys[-1]] = value
    
    @staticmethod
    def play_sound(file_path, volume=1, loops=0):
        sound = mixer.Sound(file_path)
        sound.set_volume(volume)
        sound.play(loops)
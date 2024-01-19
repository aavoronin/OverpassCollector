import objects3D.globe_countries_i18n
import objects3D.globe_continents
import objects3D.globe_continents2
from objects3D.overpass_base import *
from objects3D.test_overpass import test_overpass1, test_overpass2


import os 
dirs = ['C:\\Video', 'C:\\Cache\\cache_geo', 'C:\\Cache\\cache_overpass']
for dir in dirs:
    if not os.path.exists(dir): 
        os.makedirs(dir)
#test_overpass1()
#test_overpass2()
#run_scene()

#t3d = objects3D.globe_countries_i18n.globe_countries_i18n()
t3d = objects3D.globe_continents2.globe_continents2()
t3d.set_output_file(f'c:\\Video\\t3d_3.avi')
t3d.gen_video_from_data()
os.system(f'"C:\\Program Files\\VideoLAN\\VLC\\vlc.exe" {t3d.videoFile}')
"""
"""

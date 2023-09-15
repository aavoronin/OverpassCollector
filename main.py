from objects3D.globe_countries_i18n import globe_countries_i18n
from objects3D.overpass_base import *
from objects3D.test_overpass import test_overpass1, test_overpass2

#test_overpass1()
#test_overpass2()
#run_scene()

t3d = globe_countries_i18n()
t3d.set_output_file(f'c:\\Video\\t3d_3.avi')
t3d.gen_video_from_data()
os.system(f'"C:\\Program Files\\VideoLAN\\VLC\\vlc.exe" {t3d.videoFile}')
"""
"""

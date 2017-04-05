import time
import os.path
import sox

name = "[226612700]_[226612700]_[30-03-2017]_[16-48-00].flac"
filename = "./uploads/"+name
file_name, file_extension = os.path.splitext(filename)
tfm = sox.Transformer()
tfm.build(file_name+file_extension, file_name+'.raw')
# convert output to 8000 Hz stereo

print file_name
print file_extension
print os.path.splitext(filename)[0]
print os.path.splitext(filename)[1]

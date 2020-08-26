import os
from shutil import copy2

teacher_icon = 'assets/IMG/snapshotA.png'
student_icon = 'assets/IMG/snapshotB.png'

for each_folder in os.listdir('user_upload'):
    if each_folder[0] == 's':
        copy2(student_icon, os.path.join('user_upload', each_folder, 'snapshot.png'))
    else:
        copy2(teacher_icon, os.path.join('user_upload', each_folder, 'snapshot.png'))
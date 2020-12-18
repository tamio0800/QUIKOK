
import re

def cln_phone(target):
    p = r'^9\d{8}(.){0,1}\d{0,1}|^09\d{8}'
    result = re.search(p, re.sub(r'-|\s', '', target))
    if result is not None:
        raw_phone = result[0]
        if raw_phone[-2] == '.':
            raw_phone = raw_phone[:-2]
        if raw_phone[0] == '9':
            raw_phone = '0' + raw_phone
        raw_phone = raw_phone[:4] + '-' + raw_phone[4:7] + '-' + raw_phone[7:]
        return (True, raw_phone)
    else:
        return (False, target)

for each_h in h_all:
    ret, result = cln_phone(each_h.receiver_phone_nbr)
    if ret:
        setattr(each_h, 'receiver_phone_nbr', result)
        each_h.save()

for each_h in h_all::
    print(each_














mport os
from shutil import copy2

teacher_icon = 'assets/IMG/snapshotA.png'
student_icon = 'assets/IMG/snapshotB.png'

for each_folder in os.listdir('user_upload'):
    if each_folder[0] == 's':
        copy2(student_icon, os.path.join('user_upload', each_folder, 'snapshot.png'))
    else:
        copy2(teacher_icon, os.path.join('user_upload', each_folder, 'snapshot.png'))




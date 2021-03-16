
# 8B6FA01313CE51AFC09E610F819250DA501778AD363CBA4F9E312A6EC823D42A
def batch_student_batch_created_sql(ids_as_list, thumbnails_dir, password='        '):
    predix = 'insert into student_profile'
    column_names = '(auth_id, username, password)'
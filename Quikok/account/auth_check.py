
class auth_ckeck(**kwargs):
    url = ''
    user_id = ''
    # read tabel

    def url_role():
        
        url_cate_role = {
            '會員中心': '^/account/info/teacherS+',
            
            #/account/info/teacher
        }

        for role in url_cate_role.values():
        print(role)
#re.findall('^/account/info/teacherS+','/account/info/teacherS+')
    # 先拿 url 找 url的type
       # 用正則來處理前端給的url
       # 處理出來只有前面沒有後面
       # 再用處理出來的 url去db找 type
    # 如果 url_type == public:
        #直接 success有權限
    # else
    #   用 auth_id來看他有沒有資格看
    #
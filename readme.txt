test 1
0454 在local 新增一行

##使用批次匯入學生與老師並同時建立聊天室的方法

1.首先去 test_folder 下載範例檔案:批次註冊資.xlsx
2. runserver之後進入 http://127.0.0.1:8000/api/account/admin_import_user/
3. 選擇檔案、跳出視窗後選"範例檔案"
4. 按最左邊那顆確認送出之後即成功

##使用批次匯入課程的方法
# 請注意要先建立老師才能依照該老師的"id"建立課程 (先批次匯入學生與老師的意思)
1.首先去 test_folder 下載範例檔案:批次匯入課程.xlsx
2. runserver之後進入 http://127.0.0.1:8000/api/lesson/import_lesson/
3. 選擇檔案、跳出視窗後選"範例檔案"
4. 按最左邊那顆確認送出之後即成功

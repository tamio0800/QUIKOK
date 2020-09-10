use quikok_db;   
-- 選擇我們要編輯的DB/schema, 另外sql跟python、JS不一樣，沒有大小寫之分。


delete from account_student_profile where id < 10;  -- 單純刪除資料
-- truncate table account_student_profile; -- 清空該table裡面的資料，autoincrement歸0


insert into account_student_profile
	(username, password, name, nickname, is_male,
	role, mobile, balance, withholding_balance, intro, picture_folder, info_folder,
    update_someone_by_email, date_join)
values
	('s1@s1', '00000000', 'student1', 's_one', 1, 'myself', '0912345678',
	0, 0, '', 'user_upload/student/s1ats1/pictures',
	'user_upload/student/s1ats1/info','', now()),
    ('s2@s2', '00000000', 'student2', 's_two', 0, 'sister', '0912345678',
	0, 0, '', 'user_upload/student/s2ats2/pictures',
	'user_upload/student/s2ats2/info','', now());
-- 新增學生資料


insert into account_teacher_profile
	(username, password, balance, withholding_balance, unearned_balance,
    name, nickname, birth_date, is_male, intro, mobile,
    picture_folder, info_folder, tutor_experience, subject_type,
    education_1, education_2, education_3, cert_unapproved, cert_approved,
    id_approved, education_approved, work_approved, other_approved,
    occupation, company, is_approved, date_join)
values
	('t1@t1', '00000000', 0, 0, 0, 'teacher1', 't_one', '19901225',
    1, '臣亮言：先帝創業未半，而中道崩殂。今天下三分，益州疲弊，此誠危急存亡之秋也。然侍衛之臣，不懈於內；忠志之士，忘身於外者，蓋追先帝之殊遇，欲報之於陛下也。誠宜開張聖聽，以光先帝遺德，恢弘志士之氣；不宜妄自菲薄，引喻失義，以塞忠諫之路也。宮中府中，俱為一體，陟罰臧否，不宜異同。',
    '0912345678', 'user_upload/teacher/t1att1/pictures', 'user_upload/teacher/t1att1/info',
    '3 - 5 年', '國中數學；高中理化；國小咿咿呀呀語言；魔鬼戰鬥營',
    '北美洲大學釣魚系畢業', '高屏一中畢業', '', '', '',
    '', '', '', '', 
    '釣魚小王子', '太平洋海產', 0, now()),
    ('t2@t2', '00000000', 0, 0, 0, 'teacher2', 't_two', '19901225',
    1, '臣亮言：先帝創業未半，而中道崩殂。今天下三分，益州疲弊，此誠危急存亡之秋也。然侍衛之臣，不懈於內；忠志之士，忘身於外者，蓋追先帝之殊遇，欲報之於陛下也。誠宜開張聖聽，以光先帝遺德，恢弘志士之氣；不宜妄自菲薄，引喻失義，以塞忠諫之路也。宮中府中，俱為一體，陟罰臧否，不宜異同。',
    '0912345678', 'user_upload/teacher/t1att1/pictures', 'user_upload/teacher/t1att1/info',
    '10年以上', '國、高中、大學英文; 微積分',
    '榴槤大學量子力學所畢業', '', '', '', '',
    '', '', '', '', 
    '科學家', '', 0, now()),
    ('t3@t3', '00000000', 0, 0, 0, 'teacher3', 't_3', '19901225',
    0, '不知所云。',
    '0912345678', 'user_upload/teacher/t1att1/pictures', 'user_upload/teacher/t1att1/info',
    '1年以下', '穢土轉生術',
    '', '', '', '', '',
    '', '', '', '', 
    '', '', 0, now());
-- 新增老師資料


-- 因為foreign key的關係，這裡的user_id是指teacher在teacher_profile中的id
insert into account_general_available_time 
	(user_id, week, time)  
values
	(1, 1, '1,2,3,4,5,6,7'),
    (1, 2, '5,6,7,23,24,25,33,34,35,36,41,42'),
    (1, 6, '1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45'),
    (2, 3, '26,27,28,29,30,31,32,33,34,35,36,37,38,39,40'),
    (2, 4, '26,27,28,29,30,31,32,33,34,35,36,37,38,39,40'),
    (2, 5, '26,27,28,29,30,31,32,33,34,35,36,37,38,39,40'),
    (3, 1, '1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37'),
    (3, 2, '1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37'),
    (3, 3, '1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37'),
    (3, 4, '1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37'),
    (3, 5, '1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37'),
    (3, 6, '1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37'),
    (3, 7, '1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37');
-- 新增老師的時間資料



    


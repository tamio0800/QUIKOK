from account_finance.models import student_purchase_record, student_remaining_minutes_of_each_purchased_lesson_set
from account.models import teacher_profile
from lesson.models import lesson_info, lesson_sales_sets, lesson_booking_info
from datetime import datetime, timedelta, date as date_function
from handy_functions import check_if_all_variables_are_true


class update_student_remaining_time:
    def check_if_purchased_lesson_before():
    #def update_student_remaining_minutes_of_each_purchased_lesson_set(**kwargs):
    #    student_remaining_minutes_of_each_purchased_lesson_set.objects.create(
    #        student_auth_id= kwargs['']
    #    )
#data = {'userID':2,'teacherID':1,'lessonID':1,'sales_set': selected_set,'total_amount_of_the_lesson_set': 300,'q_discount':0}
#response = self.client.post(path='/api/account_finance/storageOrder/', data=data)
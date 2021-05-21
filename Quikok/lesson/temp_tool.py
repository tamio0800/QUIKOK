from lesson.models import lesson_sales_sets

for each_set in lesson_sales_sets.objects.all():
    obj = lesson_sales_sets.objects.get(id = each_set.id)
    obj.price_per_10_minutes = round((obj.price_per_hour_after_discount/6)+0.00001,4)
    obj.save()

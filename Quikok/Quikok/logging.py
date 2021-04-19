import logging


class SpecialFilter(logging.Filter):
    content = '這是一封由系統自動發送的信，當收到這封信時，表示有Quikok發生error以上的問題，\
                請盡快檢查伺服器！'
    # 這個filter是預設名稱不能改會壞掉
    def filter(self):
        return True
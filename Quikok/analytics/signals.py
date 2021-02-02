from django.dispatch import Signal


object_accessed_signal = \
    Signal(providing_args= \
        [
            'auth_id', 
            'ip_address',
            'url_path',
            'api_name',
            'model_name',
            'object_id',
            'user_agent',
            'action_type',
            'remark',
        ])

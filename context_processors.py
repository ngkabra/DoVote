def user_msg(request):
    msg = request.GET.get('user_msg')
    if msg:
        return dict(user_msg=msg)
    return {}


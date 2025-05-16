def get_token(request):
    user_token = request.COOKIES.get('user_token')
    return user_token

def get_user_HTTP_Auth_token(request):
    token  = request.META.get('HTTP_AUTHORIZATION')
    return token


def paymentId(userId):
    if userId is not None:
        return userId
    else:
        return 'null'
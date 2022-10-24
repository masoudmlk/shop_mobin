
class Client:
    @staticmethod
    def get_user_agent(request):
        return request.META.get('HTTP_USER_AGENT')

    @staticmethod
    def get_authorization_header(request):
        return request.headers.get('Authorization')

    @staticmethod
    def valid_user_agent(request):
        user_agent_str = Client.get_user_agent(request)
        return bool(user_agent_str)
        # if user_agent_str:
        #     userAgent = parse(user_agent_str)
        #     #return userAgent.is_pc or userAgent.is_mobile or userAgent.is_tablet
        # return False



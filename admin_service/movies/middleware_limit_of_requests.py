from django.http import JsonResponse

from movies.utils.limit_of_requests import check_limit_of_user_requests


def check_limit_of_requests(get_response):
    def middleware(request):
        user_ip = request.headers.get("X-Forwarded-For")
        response = get_response(request)

        result_of_checking_limit_of_requests = check_limit_of_user_requests(
            user_ip=user_ip
        )

        if result_of_checking_limit_of_requests:
            return JsonResponse({"detail": "Too many requests"}, status=429)
        return response

    return middleware

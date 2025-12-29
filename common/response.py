from rest_framework.response import Response
from rest_framework import status as http_status


class APIResponse:
    """
    Standard API response format
    """

    @staticmethod
    def success(
        message="Success",
        data=None,
        status=http_status.HTTP_200_OK
    ):
        return Response(
            {
                "status": True,
                "message": message,
                "data": data
            },
            status=status
        )

    @staticmethod
    def error(
        message="Something went wrong",
        data=None,
        status=http_status.HTTP_400_BAD_REQUEST
    ):
        return Response(
            {
                "status": False,
                "message": message,
                "data": data
            },
            status=status
        )

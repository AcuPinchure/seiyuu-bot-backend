from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.utils.serializer_helpers import ReturnDict


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 20  # Set the default page size
    page_size_query_param = "page_size"
    max_page_size = 100  # Set the maximum page size

    def get_paginated_response(self, data: ReturnDict) -> Response:

        if not self.page or not self.request:
            return Response(
                {
                    "status": False,
                    "total_pages": 1,
                    "current_page": 1,
                    "total_items": 0,
                    "page_size": self.page_size,
                    "results": [],
                }
            )

        return Response(
            {
                "status": True,
                "total_pages": self.page.paginator.num_pages,
                "current_page": self.page.number,
                "total_items": self.page.paginator.count,
                "page_size": self.get_page_size(self.request),
                "results": data,
            }
        )

    def get_paginated_response_schema(self, schema: dict) -> dict:
        return {
            "type": "object",
            "properties": {
                "status": {
                    "type": "boolean",
                    "example": True,
                },
                "total_items": {
                    "type": "integer",
                    "example": 25,
                },
                "page_size": {
                    "type": "integer",
                    "example": 5,
                },
                "total_pages": {
                    "type": "integer",
                    "example": 2,
                },
                "current_page": {
                    "type": "integer",
                    "example": 1,
                },
                "results": schema,
            },
        }

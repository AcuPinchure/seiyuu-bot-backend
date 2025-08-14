import hashlib
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
from elasticsearch import Elasticsearch
from django.conf import settings


class LogsElasticsearchClient:
    """
    Elasticsearch client for log management with SSL certificates
    """

    PAGE_SIZE = 20

    def __init__(self):
        # Get certificate paths from environment variables
        ca_cert_path = os.path.join(settings.BASE_DIR, "data", os.getenv("ES_CA_CERT"))
        client_cert_path = os.path.join(
            settings.BASE_DIR, "data", os.getenv("ES_CLIENT_CERT")
        )
        client_key_path = os.path.join(
            settings.BASE_DIR, "data", os.getenv("ES_CLIENT_KEY")
        )

        # Initialize Elasticsearch client with SSL
        self.client = Elasticsearch(
            [os.getenv("ES_HOST")],
            ca_certs=ca_cert_path,
            client_cert=client_cert_path,
            client_key=client_key_path,
            basic_auth=("elastic", os.getenv("ELASTIC_PASSWORD")),
            verify_certs=True,
        )

    def _convert_datetime_to_es_datetime(self, dt: datetime) -> Optional[str]:
        """
        Convert datetime object to Elasticsearch datetime string format
        """
        if dt:
            return dt.strftime("%Y-%m-%d %H:%M:%S")
        return None

    def _convert_es_datetime_to_datetime(self, es_datetime: str) -> Optional[datetime]:
        """
        Convert Elasticsearch datetime string to datetime object
        """
        if es_datetime:
            return datetime.strptime(es_datetime, "%Y-%m-%d %H:%M:%S")
        return None

    def _get_index_name(self, log_type: str) -> str:
        """Get index name based on log type"""
        if log_type == "post":
            return "post-logs"
        elif log_type == "data":
            return "data-logs"
        else:
            raise ValueError(f"Invalid log type: {log_type}")

    def create_log(
        self, log_type: str, log_time: datetime, file_name: str, content: str
    ) -> str:
        """
        Create a new log document in Elasticsearch

        Args:
            log_type: 'post' or 'data'
            log_time: datetime object
            file_name: name of the log file
            content: log content

        Returns:
            str: The MD5 hash of the log_time as document ID
        """

        index_name = self._get_index_name(log_type)
        # 將 log_time 轉為字串後取 md5
        log_time_str = self._convert_datetime_to_es_datetime(log_time)
        doc_id = hashlib.md5(log_time_str.encode("utf-8")).hexdigest()

        doc = {
            "log_time": log_time_str,
            "file_name": file_name,
            "content": content,
        }

        self.client.index(index=index_name, id=doc_id, document=doc)

        return doc_id

    def get_log(self, log_type: str, doc_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a log document by ID

        Args:
            log_type: 'post' or 'data'
            doc_id: document ID

        Returns:
            Dict with log data or None if not found
        """
        index_name = self._get_index_name(log_type)

        try:
            response = self.client.get(index=index_name, id=doc_id)

            source = response["_source"]
            return {
                "id": doc_id,
                "type": log_type,
                "log_time": self._convert_es_datetime_to_datetime(source["log_time"]),
                "file_name": source["file_name"],
                "content": source["content"],
            }
        except Exception:
            return None

    def list_logs(
        self,
        log_type: str,
        page: int = 1,
        keyword: Optional[str] = None,
        min_date: Optional[str] = None,
        max_date: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        List log documents with optional filtering and highlighting

        Args:
            log_type: 'post' or 'data'
            page: page number (1-based)
            keyword: search keyword for file_name and content
            min_date: minimum date filter (yyyy-mm-dd)
            max_date: maximum date filter (yyyy-mm-dd)

        Returns:
            List of log documents with id and preview
        """
        index_name = self._get_index_name(log_type)

        # Validate page
        if page > 50:
            raise ValueError("Page number cannot exceed 50")

        # Build query
        query = {"bool": {"must": []}}

        # Add keyword search if provided
        if keyword:
            query["bool"]["must"].append(
                {"query_string": {"query": keyword, "fields": ["file_name", "content"]}}
            )

        # Add date range filters
        if min_date or max_date:
            date_range = {"format": "yyyy-MM-dd"}
            if min_date:
                date_range["gte"] = min_date
            if max_date:
                date_range["lte"] = max_date

            query["bool"]["must"].append({"range": {"log_time": date_range}})

        # If no filters, match all
        if not query["bool"]["must"]:
            query = {"match_all": {}}

        # Calculate from offset
        size = self.PAGE_SIZE
        from_offset = (page - 1) * size

        # Build search body
        search_body = {
            "query": query,
            "from": from_offset,
            "size": size,
            "sort": [{"log_time": {"order": "desc"}}],
            "_source": ["log_time", "file_name", "content"],  # Include content in response
        }

        # Add highlight configuration if keyword exists
        if keyword:
            search_body["highlight"] = {
                "fields": {
                    "content": {
                        "fragment_size": 150,
                        "number_of_fragments": 1,
                        "pre_tags": ["<mark>"],
                        "post_tags": ["</mark>"],
                    },
                    "file_name": {
                        "fragment_size": 150,
                        "number_of_fragments": 1,
                        "pre_tags": ["<mark>"],
                        "post_tags": ["</mark>"],
                    }
                }
            }

        print(query)

        try:
            response = self.client.search(
                index=index_name,
                body=search_body,
            )

            results = []
            for hit in response["hits"]["hits"]:
                source = hit["_source"]
                
                # Extract preview
                preview = ""
                if keyword and "highlight" in hit:
                    # Prefer content highlights over file_name highlights when keyword exists
                    if "content" in hit["highlight"]:
                        preview = hit["highlight"]["content"][0]
                    elif "file_name" in hit["highlight"]:
                        preview = hit["highlight"]["file_name"][0]
                else:
                    # No keyword provided, use first 100 chars of content as preview
                    content = source.get("content", "")
                    if content:
                        # Take first 100 characters and add ellipsis if truncated
                        preview = content[:100]
                        if len(content) > 100:
                            preview += "..."
                
                results.append(
                    {
                        "id": hit["_id"],
                        "type": log_type,
                        "log_time": self._convert_es_datetime_to_datetime(
                            source["log_time"]
                        ),
                        "file_name": source["file_name"],
                        "preview": preview,
                    }
                )

            return results
        except Exception as e:
            print(f"Error searching logs: {e}")
            return []


# Global instance
es_logs_client = LogsElasticsearchClient()

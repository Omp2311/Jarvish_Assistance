from django.db import models

class SearchQuery(models.Model):
    query = models.CharField(max_length=255, unique=True)  # User query
    result = models.TextField()  # Search result (could be a cached snippet or summary)
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp of when the query was made

    def __str__(self):
        return self.query

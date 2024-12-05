# models/extension.py
from .base_model import BaseModel

class Extension(BaseModel):
    @classmethod
    def get_all(cls):
        query = "SELECT id, context FROM ps_endpoints"
        return cls.execute_query(query)

    @classmethod
    def get_by_id(cls, extension_id):
        query = "SELECT id, context FROM ps_endpoints WHERE id = %s"
        return cls.execute_single(query, (extension_id,))
    
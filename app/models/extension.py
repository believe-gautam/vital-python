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
    

    @classmethod
    def create(cls, extension_data):
        """Create a new extension"""
        query = """
        INSERT INTO ps_endpoints (id, transport, aors, auth, context, disallow, allow, direct_media)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        auth_query = """
        INSERT INTO ps_auths (id, auth_type, password, username)
        VALUES (%s, %s, %s, %s)
        """
        aor_query = """
        INSERT INTO ps_aors (id, max_contacts, qualify_frequency)
        VALUES (%s, %s, %s)
        """
        
        try:
            # Insert extension
            cls.execute_query(query, (
                extension_data['extension'],
                'transport-udp',
                extension_data['extension'],
                extension_data['extension'],
                'testing',
                'all',
                'ulaw,alaw,gsm',
                'no'
            ))
            
            # Insert auth
            cls.execute_query(auth_query, (
                extension_data['extension'],
                'userpass',
                extension_data['password'],
                extension_data['extension']
            ))
            
            # Insert AOR
            cls.execute_query(aor_query, (
                extension_data['extension'],
                1,
                30
            ))
            
            return True
        except Exception as e:
            raise Exception(f"Failed to create extension: {str(e)}")

    @classmethod
    def update(cls, extension_id, extension_data):
        """Update an existing extension"""
        query = """
        UPDATE ps_auths 
        SET password = %s
        WHERE id = %s
        """
        return cls.execute_query(query, (extension_data['password'], extension_id))

    @classmethod
    def delete(cls, extension_id):
        """Delete an extension"""
        queries = [
            "DELETE FROM ps_auths WHERE id = %s",
            "DELETE FROM ps_aors WHERE id = %s",
            "DELETE FROM ps_endpoints WHERE id = %s"
        ]
        
        for query in queries:
            cls.execute_query(query, (extension_id,))
        return True

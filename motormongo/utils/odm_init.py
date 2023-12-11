from motormongo.abstracts.document import Document


async def initialize_odm():
    for document_cls in Document._registered_documents:
        if hasattr(document_cls, 'initialize_collection'):
            await document_cls.initialize_collection()
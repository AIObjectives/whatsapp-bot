# import firebase_admin
# from firebase_admin import credentials, firestore

# # Firebase Initialization - Assuming it's already done in your current setup
# cred = credentials.Certificate('/Users/emreturan/Desktop/firebase/aoiwhatsappbot-firebase-adminsdk-rki5n-9526831994.json')
# firebase_admin.initialize_app(cred)
# db = firestore.client()

# def print_collection(collection_ref, indent=0):
#     """ Recursively print all collections, subcollections and document IDs """
#     docs = collection_ref.stream()
#     for doc in docs:
#         print(" " * indent + f"Document ID: {doc.id}")
#         subcollections = doc.reference.collections()
#         for subcol in subcollections:
#             print(" " * (indent + 2) + f"Subcollection: {subcol.id}")
#             print_collection(subcol, indent + 4)

# def delete_collection(coll_ref, batch_size):
#     """ Recursively delete a collection, in batches of batch_size """
#     docs = coll_ref.limit(batch_size).stream()
#     deleted = 0
#     for doc in docs:
#         print(f"Deleting doc {doc.id} =>")
#         doc.reference.delete()
#         delete_subcollections(doc.reference)
#         deleted += 1

#     if deleted >= batch_size:
#         return delete_collection(coll_ref, batch_size)  # Recursive delete until all docs are deleted

# def delete_subcollections(doc_ref):
#     """ Delete all subcollections of a document """
#     subcollections = doc_ref.collections()
#     for subcol in subcollections:
#         delete_collection(subcol, 50)

# # Example usage to print all collections and documents
# print("Firestore DB Structure:")
# all_collections = db.collections()
# for collection in all_collections:
#     print(f"Collection: {collection.id}")
#     print_collection(collection)



#####

# Example usage to delete a specific collection
# Be cautious with deletions, ensure you truly want to delete before uncommenting
# delete_collection(db.collection('your_collection_name'), 50)


######





### preview:

import firebase_admin
from firebase_admin import credentials, firestore

# Firebase Initialization - Assuming it's already done in your current setup
cred = credentials.Certificate('/Users/emreturan/Desktop/firebase/aoiwhatsappbot-firebase-adminsdk-rki5n-9526831994.json')
firebase_admin.initialize_app(cred)
db = firestore.client()

def print_collection(collection_ref, indent=0):
    """ Recursively print all documents and subcollections """
    docs = collection_ref.stream()
    for doc in docs:
        print(" " * indent + f"Document ID: {doc.id}")
        subcollections = doc.reference.collections()
        for subcol in subcollections:
            print(" " * (indent + 2) + f"Subcollection: {subcol.id}")
            print_collection(subcol, indent + 4)

def preview_delete_collection(coll_ref, batch_size):
    """ Preview documents and subcollections that would be deleted """
    docs = coll_ref.limit(batch_size).stream()
    for doc in docs:
        print(f"Preview deleting doc {doc.id} =>")
        preview_delete_subcollections(doc.reference)

def preview_delete_subcollections(doc_ref):
    """ Preview subcollections that would be deleted for a document """
    subcollections = doc_ref.collections()
    for subcol in subcollections:
        print(f"Preview deleting subcollection: {subcol.id}")
        preview_delete_collection(subcol, 50)

# Target specific collection to preview deletion
collection_to_preview = 'whatsapp_conversations1'
coll_ref = db.collection(collection_to_preview)
print(f"Previewing deletion for collection: {collection_to_preview}")
preview_delete_collection(coll_ref, 50)
print(f"Preview completed for collection {collection_to_preview}.")


##### TO DELETE


# def delete_collection(coll_ref, batch_size):
#     """ Recursively delete a collection, in batches of batch_size """
#     docs = coll_ref.limit(batch_size).stream()
#     deleted = 0
#     for doc in docs:
#         print(f"Deleting doc {doc.id} =>")
#         doc.reference.delete()
#         delete_subcollections(doc.reference)
#         deleted += 1

#     if deleted >= batch_size:
#         return delete_collection(coll_ref, batch_size)  # Recursive delete until all docs are deleted

# def delete_subcollections(doc_ref):
#     """ Delete all subcollections of a document """
#     subcollections = doc_ref.collections()
#     for subcol in subcollections:
#         delete_collection(subcol, 50)

# # Target specific collection to delete
# collection_to_delete = 'whatsapp_conversations1'
# coll_ref = db.collection(collection_to_delete)
# print(f"Deleting collection: {collection_to_delete}")
# delete_collection(coll_ref, 50)
# print(f"Collection {collection_to_delete} deleted successfully.")


##### not the collection just the data

def delete_documents_in_collection(coll_ref, batch_size):
    """ Delete only the documents within a collection in batches """
    docs = coll_ref.limit(batch_size).stream()
    deleted = 0
    for doc in docs:
        print(f"Deleting doc {doc.id} from {coll_ref.id} =>")
        doc.reference.delete()
        deleted += 1

    # Check if there are more documents to delete
    if deleted >= batch_size:
        return delete_documents_in_collection(coll_ref, batch_size)  # Continue deleting until all docs are gone

# Target specific collection to delete documents from
collection_to_delete = 'whatsapp_conversations1'
coll_ref = db.collection(collection_to_delete)
print(f"Starting deletion of documents from collection: {collection_to_delete}")
delete_documents_in_collection(coll_ref, 50)
print(f"All documents in {collection_to_delete} have been deleted successfully.")
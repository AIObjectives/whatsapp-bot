# import firebase_admin
# from firebase_admin import credentials, firestore, storage

# def initialize_firebase():
#     cred = credentials.Certificate('/Users/emreturan/Desktop/firebase/aoiwhatsappbot-firebase-adminsdk-rki5n-9526831994.json')
#     firebase_admin.initialize_app(cred, {
#         'storageBucket': 'aoiwhatsappbot.appspot.com'
#     })

# def upload_image_to_storage(image_path, image_name):
#     bucket = storage.bucket()
#     blob = bucket.blob(image_name)
#     blob.upload_from_filename(image_path)
#     blob.make_public()  # Make the image publicly accessible
#     return blob.public_url

# def save_image_url_to_firestore(url, doc_id):
#     db = firestore.client()
#     doc_ref = db.collection('animal_images').document(doc_id)
#     doc_ref.set({'url': url})

# initialize_firebase()
# image_url = upload_image_to_storage('/Users/emreturan/Desktop/Animal+check+in+18.jpg', 'animal.jpg')
# save_image_url_to_firestore(image_url, 'random_animal')



# import firebase_admin
# from firebase_admin import credentials, firestore, storage

# def initialize_firebase():
#     cred = credentials.Certificate('/Users/emreturan/Desktop/firebase/aoiwhatsappbot-firebase-adminsdk-rki5n-9526831994.json')
#     firebase_admin.initialize_app(cred, {
#         'storageBucket': 'aoiwhatsappbot.appspot.com'
#     })

# def save_image_url_to_firestore(doc_id, file_name):
#     db = firestore.client()
#     # Construct the URL
#     url = f"https://storage.googleapis.com/aoiwhatsappbot.appspot.com/{file_name}"
#     # Save the URL in Firestore
#     doc_ref = db.collection('animal_images').document(doc_id)
#     doc_ref.set({'url': url})

# # Main code
# def main():
#     initialize_firebase()

#     # List of image file names stored in Firebase Storage
#     image_names = [
#         "Animals+4.jpg",
#         "Cute+animals+check-in.jpg",
#         "animal.jpg",
#         "cute+animals+3.jpg"
#     ]

#     # Loop through and save URLs to Firestore
#     for image_name in image_names:
#         # Use image name without extension as document ID
#         doc_id = image_name.split('.')[0]
#         save_image_url_to_firestore(doc_id, image_name)

# # Run the main function
# if __name__ == '__main__':
#     main()








####
import firebase_admin
from firebase_admin import credentials, firestore, storage

def initialize_firebase():
    cred = credentials.Certificate('/Users/emreturan/Desktop/firebase/aoiwhatsappbot-firebase-adminsdk-rki5n-9526831994.json')
    firebase_admin.initialize_app(cred, {
        'storageBucket': 'aoiwhatsappbot.appspot.com'
    })

def make_image_public_and_save_url(doc_id, file_name):
    bucket = storage.bucket()
    blob = bucket.blob(file_name)
    blob.make_public()  # Make the image publicly accessible
    url = blob.public_url
    # Save the URL in Firestore
    db = firestore.client()
    doc_ref = db.collection('animal_images').document(doc_id)
    doc_ref.set({'url': url})

# Main code
def main():
    initialize_firebase()

    # List of image file names stored in Firebase Storage
    image_names = [
        "Animals+4.jpg",
        "Cute+animals+check-in.jpg",
        "animal.jpg",
        "cute+animals+3.jpg"
    ]

    # Loop through and make each image public, then save URLs to Firestore
    for image_name in image_names:
        # Use image name without extension as document ID
        doc_id = image_name.replace('+', ' ').split('.')[0]  # Removing '+' to match Firestore document naming
        make_image_public_and_save_url(doc_id, image_name)

# Run the main function
if __name__ == '__main__':
    main()

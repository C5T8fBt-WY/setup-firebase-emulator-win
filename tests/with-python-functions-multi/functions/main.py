"""
Multiple Firebase Cloud Functions for testing.
This tests the scenario where multiple callable functions need to be served.
"""
from firebase_functions import https_fn
from firebase_admin import firestore, initialize_app
import logging

# Initialize Firebase Admin
initialize_app()

@https_fn.on_call()
def getAccountInfo(req: https_fn.CallableRequest):
    """Get account information from Firestore."""
    try:
        account_id = req.data.get('accountId')
        if not account_id:
            raise https_fn.HttpsError('invalid-argument', 'accountId is required')
        
        db = firestore.client()
        doc_ref = db.collection('accounts').document(account_id)
        doc = doc_ref.get()
        
        if not doc.exists:
            raise https_fn.HttpsError('not-found', f'Account {account_id} not found')
        
        return {'account': doc.to_dict()}
    except https_fn.HttpsError:
        raise
    except Exception as e:
        logging.error(f"Error in getAccountInfo: {e}")
        raise https_fn.HttpsError('internal', str(e))

@https_fn.on_call()
def uploadMeasurement(req: https_fn.CallableRequest):
    """Upload measurement data."""
    try:
        data = req.data.get('data')
        if not data:
            raise https_fn.HttpsError('invalid-argument', 'data is required')
        
        db = firestore.client()
        doc_ref = db.collection('measurements').document()
        doc_ref.set(data)
        
        return {'id': doc_ref.id, 'success': True}
    except https_fn.HttpsError:
        raise
    except Exception as e:
        logging.error(f"Error in uploadMeasurement: {e}")
        raise https_fn.HttpsError('internal', str(e))

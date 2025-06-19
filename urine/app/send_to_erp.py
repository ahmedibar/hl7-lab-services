import os
import logging
from frappeclient import FrappeClient
from local_config import ERP_URL, ERP_USER, ERP_PASSWORD

# Configure logging
logging.basicConfig(filename='errlog.txt', level=logging.ERROR)

def send_to_erp(lab_test_name, results):
    """
    Sends lab test results to the ERP system.

    Parameters:
    - lab_test_name: The name of the lab test to update.
    - results: A list of dictionaries containing result data.
    """
    try:
        # conn = FrappeClient("http://192.168.1.170/")
        # conn.login("administrator", "Rasiin@@2025@@")
        conn = FrappeClient(ERP_URL)
        conn.login(ERP_USER, ERP_PASSWORD)

        doc_name = conn.get_value("Lab Result", "name", {"lab_ref": int(lab_test_name),"template":"Urine Routine"})
        if not doc_name:
            raise ValueError("Lab Result not found")

        doc = conn.get_doc("Lab Result", doc_name['name'])
        print(f"Processing lab test for patient: {doc['patient_name']}")

        # Print the results to be processed
        # print("Results to process:", results)

        if 'normal_test_items' in doc:
            # Create a mapping of lab test events to their corresponding results
            results_map = {}
            for result in results:
                par = result['par']
                # If par already exists, append value to a list
                if par in results_map:
                    results_map[par].append(result['value'])
                else:
                    results_map[par] = [result['value']]

            # Print the results mapping
            # print("Results mapping:", results_map)

            for test in doc['normal_test_items']:
                lab_test_name_value = test.get('lab_test_name')
                lab_test_event_value = test.get('lab_test_event')

                # print(f"Processing test item: {test}")

                if lab_test_name_value:
                    print(f"Lab Test Name: {lab_test_name_value}")
                else:
                    logging.debug("lab_test_name not found in test item: %s", test)

                if lab_test_event_value:
                    print(f"Lab Test Event: {lab_test_event_value}")

                    # Check if the event has corresponding results
                    if lab_test_event_value in results_map:
                        # Get the first value and remove it from the list
                        test['result_value'] = results_map[lab_test_event_value].pop(0)
                        # print(f"rest result map: {results_map}")
                        print(f"Assigned value '{test['result_value']}' to {lab_test_event_value}")
                    else:
                        print(f"No matching result for {lab_test_event_value}")

                else:
                    logging.debug("lab_test_event not found in test item: %s", test)

            conn.update(doc)
        else:
            logging.warning("normal_test_items not found in document: %s", doc)

    except Exception as e:
        logging.error("Error occurred: %s", str(e))
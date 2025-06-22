from frappeclient import FrappeClient
import os
from local_config import ERP_URL, ERP_USER, ERP_PASSWORD


def send_to_erp(lab_test_name, results, hormone):  # FIXED name here
    # conn = FrappeClient("http://192.168.1.170")
    # conn.login("administrator", "Rasiin@@2025@@")
    conn = FrappeClient(ERP_URL)
    conn.login(ERP_USER, ERP_PASSWORD)
    doc_name = conn.get_value("Lab Result", "name", {"lab_ref": lab_test_name, "template": "CBC"})
    if doc_name:
        doc = conn.get_doc("Lab Result", doc_name['name'])
        for test in doc['normal_test_items']:
            test_result_doc = conn.get_doc("Normal Test Result", test['name'])

            for result in results:  # FIXED name here
                lab_t_tem = result['par']
                if lab_t_tem == test['lab_test_event']:
                    test['result_value'] = result['value']
                    test['normal_range'] = result.get('normal_range', '')
                    # test['lab_test_uom'] = result['uom']
                    # test['flag'] = result['flag']
        conn.update(doc)
    print("inserted Result",lab_test_name)

from frappeclient import FrappeClient
import os
from local_config import ERP_URL, ERP_USER, ERP_PASSWORD


def send_to_erp(lab_test_name, results, hormone):
    if not lab_test_name:
        print("Lab test name is empty. Aborting operation.")
        return

    print("For Barcode:", lab_test_name)

    # conn = FrappeClient("http://192.168.1.170")
    # conn.login("administrator", "Rasiin@@2025@@")
    
    conn = FrappeClient(ERP_URL)
    conn.login(ERP_USER, ERP_PASSWORD)

    processed_any = False

    # Process Blood type
    blood_list = conn.get_list(
        "Lab Result",
        fields=["name"],
        filters={"lab_ref": lab_test_name, "type": "Blood"}
    )
    print("Blood records found:", blood_list)

    for blood_doc in blood_list:
        process_lab_result(conn, blood_doc['name'], results, hormone)
        processed_any = True

    # Process Group type (only if profile == Biochemistry Report)
    group_list = conn.get_list(
        "Lab Result",
        fields=["name"],
        filters={"lab_ref": lab_test_name, "type": "Group"}
    )

    for group_doc in group_list:
        lab_result_doc = conn.get_doc("Lab Result", group_doc['name'])
        profile = lab_result_doc.get('profile')

        if profile == "Biochemistry Report":
            process_lab_result(conn, group_doc['name'], results, hormone)
            processed_any = True

    if processed_any:
        print("jawaabtii waa la xareeyay Marwo/Mudane")
    else:
        print("No matching Lab Result found or profile is not 'Biochemistry Report'")



def process_lab_result(conn, doc_name, results, hormone):
    doc = conn.get_doc("Lab Result", doc_name)

    for test in doc['normal_test_items']:
        test_result_doc = conn.get_doc("Normal Test Result", test['name'])

        for result in results:
            inserted = False

            # Special logic only for GLU
            if result['par'] == "GLU":
                lab_t_list = conn.get_list("Lab Test Template", fields=["name"], filters={"machine_test": result['par']})
                for lab_t in lab_t_list:
                    lab_t_tem_value = lab_t['name']
                    # print("Checking template (GLU):", lab_t_tem_value)

                    if lab_t_tem_value.lower().strip() == test['lab_test_name'].lower().strip():
                        # print(f"Matched {lab_t_tem_value} with {test['lab_test_name']}")
                        test['result_value'] = result['value']
                        inserted = True
                        break  # Stop checking other templates once matched

            else:
                # Existing logic for non-GLU tests
                lab_t_tem = conn.get_value("Lab Test Template", "name", {"machine_test": result['par']})
                lab_t_tem_value = lab_t_tem.get('name') if lab_t_tem else None

                if lab_t_tem_value:
                    # print("Checking template:", lab_t_tem_value)

                    if lab_t_tem_value.lower().strip() == test['lab_test_name'].lower().strip():
                        # print(f"Matched {lab_t_tem_value} with {test['lab_test_name']}")
                        test['result_value'] = result['value']
                        inserted = True

            if inserted:
                print(f"✅{test['lab_test_name']}")
                

           
                
    conn.update(doc)


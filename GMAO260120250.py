import os
import json
import glob
import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd

# List of countries in Africa
payees_afrique = [
    'Morocco', 'Tunisia', 'Algeria', 'Angola', 'Ivory Coast', 'Mauritania', 'Togo', 'Guinea', 'Mali', 'Senegal', 'Chad', 'Gabon', 'Cameroon', 'Burkina Faso', 'Congo'
]

# Client and intervention databases
CLIENTS_DB = "clients.json"
INTERVENTIONS_DB = "interventions.json"  # File to store interventions
PASSWORD = "0000"  # Password for modifications

# New database path for storage
base_path = "C:\\Users\\fer1cas\\OneDrive - Bosch Group\\New GMAO TEST"

# Load existing clients
def load_clients():
    if os.path.exists(os.path.join(base_path, CLIENTS_DB)):
        with open(os.path.join(base_path, CLIENTS_DB), 'r') as f:
            return json.load(f)
    return {}

# Load existing interventions
def load_interventions():
    if os.path.exists(os.path.join(base_path, INTERVENTIONS_DB)):
        with open(os.path.join(base_path, INTERVENTIONS_DB), 'r') as f:
            return json.load(f)
    return []

# Save clients
def save_clients(clients):
    with open(os.path.join(base_path, CLIENTS_DB), 'w') as f:
        json.dump(clients, f, indent=4)

# Save interventions
def save_interventions(interventions):
    with open(os.path.join(base_path, INTERVENTIONS_DB), 'w') as f:
        json.dump(interventions, f, indent=4)

# Check if the client already exists
def client_exists(base_path, client_name, payee_name, classification):
    client_path = os.path.join(base_path, classification, payee_name, client_name)
    return os.path.exists(client_path)

# Create folder structure
def create_structure(base_path, payee_name, client_name, year, classification):
    classification_path = os.path.join(base_path, classification)
    os.makedirs(classification_path, exist_ok=True)

    payee_path = os.path.join(classification_path, payee_name)
    os.makedirs(payee_path, exist_ok=True)

    client_path = os.path.join(payee_path, client_name)
    os.makedirs(client_path, exist_ok=True)

    for month in range(1, 13):
        month_str = f"{month:02d}"
        month_path = os.path.join(client_path, month_str)
        os.makedirs(month_path, exist_ok=True)

        for doc_type in [
            "Intervention_Report", "Service_Offer", "PDR_Offer",
            "Service_BC", "PDR_BC", "Documentation"
        ]:
            os.makedirs(os.path.join(month_path, doc_type), exist_ok=True)

# Interface to create a client with additional information
def create_client():
    st.header("Create a Client")
    clients = load_clients()

    client_name = st.text_input('Client Name')
    payee_name = st.selectbox('Select the payee in Africa', payees_afrique)
    classification = st.selectbox('Select the client classification', ['Sacofrina', 'Others'])

    address = st.text_input('Address')
    contact = st.text_input('Contact')
    email = st.text_input('Email')
    sector = st.selectbox('Sector of Activity', ['Agro', 'Textile', 'Refining'])

    num_boilers = st.number_input('Number of Boilers', min_value=1, step=1)
    boiler_serial_numbers = []
    for i in range(num_boilers):
        serial_number = st.text_input(f'Boiler Serial Number {i+1}')
        if serial_number:
            boiler_serial_numbers.append(serial_number)

    burner_type = st.selectbox('Burner Type', ['Saacke SKVA', 'Saacke SKVGA', 'Weishaupt'])

    if st.button('Create Client'):
        if client_exists(base_path, client_name, payee_name, classification):
            st.warning(f"The client '{client_name}' already exists in the specified path.")
        elif client_name and payee_name:
            create_structure(base_path, payee_name, client_name, 2024, classification)
            clients[client_name] = {
                "payee": payee_name, "address": address, "contact": contact,
                "email": email, "sector": sector,
                "num_boilers": num_boilers,
                "boiler_serial_numbers": boiler_serial_numbers,
                "burner_type": burner_type
            }
            save_clients(clients)
            st.success(f"Client {client_name} created successfully under payee {payee_name}.")
        else:
            st.error("Please fill in all required fields.")

# Interface to add reports or offers
def add_document(doc_type):
    st.header(f"Add a {doc_type}")
    clients = load_clients()

    if not clients:
        st.warning("No clients available.")
        return

    client_name = st.selectbox('Select Client', list(clients.keys()))
    payee_name = st.selectbox('Select the payee in Africa', payees_afrique)
    classification = st.selectbox('Select the client classification', ['Sacofrina', 'Others'])

    if client_name and payee_name:
        correct_payee = clients[client_name]["payee"]
        if correct_payee != payee_name:
            st.error(f"Error: The client '{client_name}' belongs to the payee '{correct_payee}', not '{payee_name}'. Please correct your selection.")
            return

    month = st.selectbox('Select Month', [str(i).zfill(2) for i in range(1, 13)])

    if doc_type == "Service_BC" or doc_type == "PDR_BC":
        st.subheader("Add a Purchase Order (BC)")
        
        # Select existing offer
        offer_type = st.selectbox("Select Offer Type", ["Service_Offer", "PDR_Offer"])
        offer_month = st.selectbox('Select Offer Month', [str(i).zfill(2) for i in range(1, 13)])
        
        # Check if offer exists
        offer_path = os.path.join(base_path, classification, payee_name, client_name, offer_month, offer_type)
        if os.path.exists(offer_path):
            offers = glob.glob(os.path.join(offer_path, '*'))
            offer_selection = st.selectbox("Select an Offer", offers)
        else:
            st.warning("No offers found for this client and month.")
            return
        
        # Upload BC file
        doc_file = st.file_uploader(f'Upload the {doc_type} file', type=['pdf', 'docx', 'jpg'])
        
        if st.button(f'Add the {doc_type}'):
            if doc_file:
                save_path = os.path.join(base_path, classification, payee_name, client_name, month, doc_type, doc_file.name)
                os.makedirs(os.path.dirname(save_path), exist_ok=True)
                with open(save_path, 'wb') as f:
                    f.write(doc_file.getbuffer())
                st.success(f"{doc_type} added for client {client_name}, month {month}. Linked to the offer: {offer_selection}.")
            else:
                st.error(f"Please upload a file for the {doc_type}.")
    else:
        # Original document upload process for other types
        doc_file = st.file_uploader(f'Upload the {doc_type} file', type=['pdf', 'docx', 'jpg'])

        if st.button(f'Add the {doc_type}'):
            if doc_file:
                save_path = os.path.join(base_path, classification, payee_name, client_name, month, doc_type, doc_file.name)
                os.makedirs(os.path.dirname(save_path), exist_ok=True)
                with open(save_path, 'wb') as f:
                    f.write(doc_file.getbuffer())
                st.success(f"{doc_type} added for client {client_name}, month {month}.")
            else:
                st.error(f"Please upload a file for the {doc_type}.")

# Interface to modify client data
def modify_client():
    st.header("Modify Client Data")
    clients = load_clients()

    if not clients:
        st.warning("No clients available.")
        return

    client_name = st.selectbox('Select Client to Modify', list(clients.keys()))
    if client_name:
        payee_name = st.text_input('New Payee', clients[client_name]["payee"])
        address = st.text_input('New Address', clients[client_name]["address"])
        contact = st.text_input('New Contact', clients[client_name]["contact"])
        email = st.text_input('New Email', clients[client_name]["email"])

        sectors = ['Agro', 'Textile', 'Refining']
        sector = st.selectbox('New Sector of Activity', sectors, index=sectors.index(clients[client_name]["sector"]) if clients[client_name]["sector"] in sectors else 0)

        num_boilers = st.number_input('Number of Boilers', min_value=1, step=1, value=clients[client_name].get("num_boilers", 1))
        boiler_serial_numbers = clients[client_name].get("boiler_serial_numbers", [])

        # Define burner types
        burner_types = ['Saacke SKVA', 'Saacke SKVGA', 'Weishaupt']
        current_burner_type = clients[client_name].get("burner_type", burner_types[0])
        if current_burner_type not in burner_types:
            current_burner_type = burner_types[0]  # Fallback to the first option if not found

        burner_type = st.selectbox('Burner Type', burner_types, index=burner_types.index(current_burner_type))

        password = st.text_input("Password", type="password")

        if st.button("Save Changes"):
            if password == PASSWORD:
                clients[client_name] = {
                    "payee": payee_name, "address": address, "contact": contact,
                    "email": email, "sector": sector,
                    "num_boilers": num_boilers,
                    "boiler_serial_numbers": boiler_serial_numbers,
                    "burner_type": burner_type
                }
                save_clients(clients)
                st.success(f"Data for client '{client_name}' updated successfully.")
            else:
                st.error("Incorrect password.")

        if st.button("Delete Client"):
            if password == PASSWORD:
                del clients[client_name]
                save_clients(clients)
                st.success(f"Client '{client_name}' deleted successfully.")
            else:
                st.error("Incorrect password.")

# Interface for quick offer search
def quick_search_offers():
    st.header("Quick Offer Search")
    clients = load_clients()

    if not clients:
        st.warning("No clients available.")
        return

    selected_payees = st.multiselect('Select Payees', payees_afrique)
    selected_clients = st.multiselect('Select Clients', list(clients.keys()))
    doc_type = st.selectbox("Type of offer to search", ["Intervention_Report", "Service_Offer", "PDR_Offer"])
    start_month = st.text_input('Start Month (01-12)', "01")
    end_month = st.text_input('End Month (01-12)', "12")

    if st.button('Search'):
        results = []
        for payee in selected_payees:
            for client in selected_clients:
                for month in range(int(start_month), int(end_month) + 1):
                    month_str = str(month).zfill(2)
                    for classification in ['Sacofrina', 'Others']:
                        doc_path = os.path.join(base_path, classification, payee, client, month_str, doc_type)
                        if os.path.exists(doc_path):
                            documents = glob.glob(os.path.join(doc_path, '*'))
                            for document in documents:
                                results.append({
                                    "Client": client,
                                    "Date": f"{month_str}/2024",  # Adding year to the date
                                    "Type": doc_type,
                                    "File": document
                                })

        if results:
            df_results = pd.DataFrame(results)
            st.dataframe(df_results)  # Display results table
        else:
            st.warning(f"No {doc_type} found in the selected period.")

# Interface for Offers and BC Summary
def bilan_offres_bc():
    st.header("Summary of Offers and BC")

    clients = load_clients()

    if not clients:
        st.warning("No clients available.")
        return

    selected_payees = st.multiselect('Select Payees', payees_afrique)
    selected_clients = st.multiselect('Select Clients', list(clients.keys()))
    doc_type = st.selectbox("Select Offer Type", ["Service_Offer", "PDR_Offer", "Service_BC", "PDR_BC"])

    start_month = st.text_input('Start Month (01-12)', "01")
    end_month = st.text_input('End Month (01-12)', "12")

    if st.button('Generate Summary'):
        month_counts = {str(i).zfill(2): 0 for i in range(1, 13)}
        results = []

        for payee in selected_payees:
            for client in selected_clients:
                for month in range(int(start_month), int(end_month) + 1):
                    month_str = str(month).zfill(2)
                    for classification in ['Sacofrina', 'Others']:
                        doc_path = os.path.join(base_path, classification, payee, client, month_str, doc_type)
                        if os.path.exists(doc_path):
                            documents = glob.glob(os.path.join(doc_path, '*'))
                            count = len(documents)
                            month_counts[month_str] += count

                            # Add results for the table
                            for document in documents:
                                results.append({
                                    "Client": client,
                                    "Date": f"{month_str}/2024",  # Adding year to the date
                                    "Type": doc_type,
                                    "Count": count,
                                    "File": document
                                })

        # Display results in a table
        if results:
            df_results = pd.DataFrame(results)
            st.dataframe(df_results)  # Display results table

            # Generate the graph
            months = [month for month, count in month_counts.items() if count > 0]
            counts = [month_counts[month] for month in months]

            if counts:
                fig, ax = plt.subplots(figsize=(10, 6))
                ax.bar(months, counts, color='skyblue')
                ax.set_xlabel('Months')
                ax.set_ylabel('Number of Documents')
                ax.set_title(f"Summary of {doc_type} by Month")
                st.pyplot(fig)
        else:
            st.warning(f"No {doc_type} found for the selected period.")

# Interface to display clients in a table
def display_clients():
    st.header("Client List")
    clients = load_clients()

    if not clients:
        st.warning("No clients available.")
        return

    # Convert client data to DataFrame
    data = []
    for client_name, info in clients.items():
        data.append({
            "Client Name": client_name,
            "Payee": info["payee"],
            "Address": info["address"],
            "Contact": info["contact"],
            "Email": info["email"],
            "Sector": info["sector"],
            "Number of Boilers": info["num_boilers"],
            "Burner Type": info["burner_type"],
            "Boiler Serial Numbers": ", ".join(info["boiler_serial_numbers"])  # Add serial numbers
        })

    df = pd.DataFrame(data)

    # Filter by payee
    selected_payee = st.selectbox("Filter by Payee", ['All'] + payees_afrique)
    if selected_payee != 'All':
        df = df[df["Payee"] == selected_payee]

    st.dataframe(df)  # Display table

# Adding function for intervention planning
def planification_interventions():
    st.header("Intervention Planning")
    clients = load_clients()

    if not clients:
        st.warning("No clients available.")
        return

    client_name = st.selectbox('Select Client', list(clients.keys()))
    payee_name = st.selectbox('Select the payee in Africa', payees_afrique)

    if client_name:
        correct_payee = clients[client_name]["payee"]
        if correct_payee != payee_name:
            st.error(f"Error: The client '{client_name}' belongs to the payee '{correct_payee}', not '{payee_name}'. Please correct your selection.")
            return

    start_date = st.date_input('Start Date of Intervention')
    end_date = st.date_input('End Date of Intervention')

    if end_date < start_date:
        st.error("The end date must be after the start date.")
        return

    intervention_type = st.selectbox('Type of Intervention', [
        'Preventive Maintenance', 'Corrective Maintenance', 
        'Commissioning', 'Energy Audit', 'Other'
    ])

    technician = st.selectbox('Choose Technician', [
        'Ferjeni Ramzi', 'El Mahi Mouhcine', 
        'Marzouk Abdelhadi', 'El Najjar Abdessamad', 'Moustafa'
    ])

    status = st.selectbox('Intervention Status', ['Confirm', 'Plan', 'Propose'])

    # Calculate the number of intervention days
    num_intervention_days = (end_date - start_date).days + 1

    if st.button('Plan the Intervention'):
        # Save the intervention
        interventions = load_interventions()
        new_intervention = {
            "Client": client_name,
            "Payee": payee_name,
            "Start Date": str(start_date),
            "End Date": str(end_date),
            "Number of Intervention Days": num_intervention_days,
            "Technician": technician,
            "Status": status
        }
        interventions.append(new_intervention)
        save_interventions(interventions)

        st.success(f"Intervention planned successfully!\n"
                   f"Client: {client_name}\n"
                   f"Payee: {payee_name}\n"
                   f"Start Date: {start_date}\n"
                   f"End Date: {end_date}\n"
                   f"Type of Intervention: {intervention_type}\n"
                   f"Technician: {technician}\n"
                   f"Number of Intervention Days: {num_intervention_days}")

# Function to display intervention summary
def bilan_interventions():
    st.header("Intervention Summary")
    interventions = load_interventions()

    if not interventions:
        st.warning("No interventions available.")
        return

        clients = load_clients()
    data = []

    for intervention in interventions:
        client_name = intervention["Client"]
        payee_name = intervention["Payee"]
        if client_name in clients:
            data.append({
                "Client": client_name,
                "Payee": payee_name,
                "Start Date": intervention["Start Date"],
                "End Date": intervention["End Date"],
                "Number of Days": intervention["Number of Intervention Days"],
                "Technician": intervention["Technician"],
                "Status": intervention["Status"]
            })

    df = pd.DataFrame(data)
    st.dataframe(df)  # Display intervention summary

# Main application structure
def main():
    st.title("Client and Intervention Management System")

    menu = ["Create Client", "Add Document", "Modify Client", "Quick Offer Search",
            "Summary of Offers and BC", "Display Clients", "Intervention Planning", "Intervention Summary"]

    choice = st.sidebar.selectbox("Select an option", menu)

    if choice == "Create Client":
        create_client()
    elif choice == "Add Document":
        doc_type = st.selectbox("Select Document Type", ["Intervention_Report", "Service_Offer", "PDR_Offer", "Service_BC", "PDR_BC"])
        add_document(doc_type)
    elif choice == "Modify Client":
        modify_client()
    elif choice == "Quick Offer Search":
        quick_search_offers()
    elif choice == "Summary of Offers and BC":
        bilan_offres_bc()
    elif choice == "Display Clients":
        display_clients()
    elif choice == "Intervention Planning":
        planification_interventions()
    elif choice == "Intervention Summary":
        bilan_interventions()

if __name__ == "__main__":
    main()


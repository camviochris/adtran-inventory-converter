import streamlit as st
import pandas as pd
import io
import re
import datetime

st.set_page_config(page_title="Adtran Inventory Converter", layout="centered")
st.title("📦 Adtran Inventory Import Tool")

st.markdown("""
Upload your inventory file (.csv or .xlsx), choose a device and location, and download your cleaned import file. 
**No data is stored. Everything is handled in memory and disappears when you leave the page.**
""")

# Device and template setup
default_status = 'UNASSIGNED'
device_numbers_template_map = {
    'SDX622V': 'MAC=<<MAC>>|SN=<<SN>>|ONT_FSAN=<<FSAN>>|ONT_ID=no value|ONT_NODENAME=no value|ONT_PORT=1|ONT_PROFILE_ID=164|ONT_MOMENTUM_PASSWORD=no value',
    'ADTN-611': 'MAC=<<MAC>>|SN=<<SN>>|ONT_PORT=1',
    'ADTN-622': 'MAC=<<MAC>>|SN=<<SN>>|ONT_PORT=2',
    'SDX630': 'MAC=<<MAC>>|SN=<<SN>>|ONT_PORT=1',
    'ADTN-632': 'MAC=<<MAC>>|SN=<<SN>>|ONT_PORT=2',
    'SDG841-T6': 'MAC=<<MAC>>|SN=<<SN>>',
    'SDG8612': 'MAC=<<MAC>>|SN=<<SN>>',
    'SDG854-V6': 'MAC=<<MAC>>|SN=<<SN>>'
}

device_profile_name_map = {
    'ADTN-622': 'ADTN_ONT',
    'SDX622V': 'ADTN_ONT',
    'ADTN-611': 'ADTN_ONT',
    'SDX630': 'ADTN_ONT',
    'SDG841-T6': 'ADTN_ROUTER',
    'SDG8612': 'ADTN_ROUTER',
    'SDG854-V6': 'ADTN_ROUTER',
    'ADTN-632': 'ADTN_ONT'
}

def find_column(columns, patterns):
    for pat in patterns:
        for col in columns:
            if re.search(pat, col, re.IGNORECASE):
                return col
    return None

uploaded_file = st.file_uploader("Upload your inventory file (.csv or .xlsx)", type=["csv", "xlsx"])
company_name = st.text_input("Enter your company name (for the output file name)")

if uploaded_file:
    try:
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        df.columns = df.columns.str.strip()

        st.success("File uploaded successfully.")

        selected_device = st.selectbox("Select device type", list(device_numbers_template_map.keys()))

        if selected_device:
            st.info(f"""
🔍 **Preview Configuration for {selected_device}**

**Device Profile:** `{device_profile_name_map[selected_device]}`

**Device Numbers Template Example:**
```
{device_numbers_template_map[selected_device].replace('<<MAC>>', 'A1B2C3D4E5F6').replace('<<SN>>', 'SN123456').replace('<<FSAN>>', 'FSAN0001')}
```
""")
            st.warning("⚠️ Please verify this template against your provisioning system **before going live**. If this is a new device type, ensure it's fully tested in your environment.")

        selected_location = st.selectbox("Select location", ["WAREHOUSE", "ITG", "Custom..."])
        if selected_location == "Custom...":
            selected_location = st.text_input("Enter custom location")
            st.warning("⚠️ The custom location name must match exactly what is in your system — including capitalization, spelling, and formatting. Any mismatch may cause issues during import.")
            confirmed = st.checkbox("✅ I confirm that this custom location exactly matches the name in our system (case-sensitive, no typos)")
        else:
            confirmed = True

        if selected_location and selected_device and company_name and confirmed:
            serial_col = find_column(df.columns, [r'^serial number$', r'^serial$', r'^sn$'])
            mac_col = find_column(df.columns, [r'^mac$', r'^mac address(es)?$'])
            fsan_col = find_column(df.columns, [r'^fsan$'])

            missing = []
            if serial_col is None: missing.append("Serial Number")
            if mac_col is None: missing.append("MAC Address")
            if missing:
                st.error(f"Missing required columns: {', '.join(missing)}")
            else:
                output_rows = []
                for _, row in df.iterrows():
                    try:
                        serial = str(row[serial_col]).strip()
                        mac = str(row[mac_col]).strip()
                        fsan = str(row[fsan_col]).strip() if fsan_col else ''

                        profile = device_profile_name_map[selected_device]
                        template = device_numbers_template_map[selected_device]
                        device_numbers = template.replace("<<MAC>>", mac).replace("<<SN>>", serial).replace("<<FSAN>>", fsan)

                        output_rows.append({
                            "device_profile": profile,
                            "device_name": selected_device,
                            "device_numbers": device_numbers,
                            "location": selected_location,
                            "status": default_status
                        })
                    except Exception as e:
                        st.warning(f"Error on row: {e}")

                result_df = pd.DataFrame(output_rows)

                today = datetime.date.today().strftime("%Y%m%d")
                safe_company = re.sub(r'[^a-zA-Z0-9_\-]', '', company_name.lower().replace(' ', '_'))
                file_name = f"{safe_company}_{today}_{selected_device}.csv"

                st.success("Conversion complete! Click below to download.")
                csv_buffer = io.StringIO()
                result_df.to_csv(csv_buffer, index=False)
                st.download_button(
                    label="📥 Download Converted File",
                    data=csv_buffer.getvalue(),
                    file_name=file_name,
                    mime="text/csv"
                )
    except Exception as e:
        st.error(f"Error reading file: {e}")
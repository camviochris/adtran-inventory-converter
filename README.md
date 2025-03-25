# Adtran Inventory Import Tool

This Streamlit web app allows you to convert raw Adtran inventory files into a format ready for import into your provisioning system. 

**No data is stored.** Everything is handled securely in memory and discarded after download.

---

## 🔧 How It Works

1. Upload your `.csv` or `.xlsx` inventory file
2. Enter your company name (used for naming the output file)
3. Select your Adtran device type
4. Choose a location (WAREHOUSE, ITG, or enter a custom one)
5. Review the configuration preview to ensure it matches your provisioning system
6. Download the cleaned output file

---

## ⚠️ Important Notes

- If you use a **custom location**, it must exactly match what's in your system (case-sensitive, no extra spaces, etc.)
- Be sure to verify the **Device Numbers Template** shown in the preview before using the file for provisioning
- If this is a **new device type**, confirm it's supported in your provisioning platform before going live

---

## ✅ File Requirements

- Your input file must include at least:
  - A column for **Serial Number** (can be labeled `Serial`, `SN`, or `Serial Number`)
  - A column for **MAC Address** (can be labeled `MAC`, `Mac Address`, etc.)
  - Optional: **FSAN** column

---

## 📁 Output

The app will generate a `.csv` file with the following fields:

- `device_profile`
- `device_name`
- `device_numbers`
- `location`
- `status` (always set to `UNASSIGNED`)

The file name will follow this format:
```
[company]_[YYYYMMDD]_[device_name].csv
```

Example:
```
northland_20250325_SDX630.csv
```

---

## 🔗 Hosted App

> Coming soon: A link to the live app will be provided here once deployed.

---

## Contact

For questions or support, please reach out to your internal administrator or provisioning support team.
import streamlit as st
import pandas as pd
import io

# =====================================================================
# COLUMN MAP
# =====================================================================

COLUMN_MAP = {
    "Order": "order_internal_id",
    "Client": "client_name",
    "Visit": "internal_id",
    "Site": "site_internal_id",
    "Order Deadline": "end_date",
    "Responsibility": "responsibility",
    "Premises Name": "site_name",
    "Address1": "site_address_1",
    "Address2": "site_address_2",
    "Address3": "site_address_3",
    "City": None,
    "Post Code": "site_post_code",
    "Submitted Date": "submitted_date",
    "Approved Date": "approval_date",
    "Item to order": "item_to_order",
    "Actual Visit Date": "date_of_visit",
    "Actual Visit Time": "time_of_visit",
    "AM / PM": None,
    "Pass-Fail": "primary_result",
    "Pass-Fail2": None,
    "Abort Reason": "Please detail why you were unable to conduct this audit:",
    "Extra Site 1": "site_code",
    "Extra Site 2": "__MONTH__",
    "Extra Site 3": None,
    "Extra Site 4": None,
    "Extra Site 5": None,
    "What is your age (in years and months)?": "What is your age?",
    "What is the name of the restaurant/shop you made the purchase from?": "What is the name of the restaurant/shop you made the purchase from?",
    "Please state the 11-digit Order Number (this can be found on your order receipt):": "Please enter the  11-digit order number:",
    "Please state the name of the product you purchased (brand and size):": ["Please give details of the alcohol that you purchased:", "Please give details of the cigarettes that you purchased:", "Please give details of the e-cigarette that you purchased:", "Please give details of the CBD product that you purchased:"],
    "Did the rider ask for your ID?": "Did the rider ask for your ID?",
    "Did the rider check your ID?": "Did the rider check your ID?",
    "Did the rider ask for your date of birth?": "Did the rider ask for your date of birth?",
    "Did the rider hand you their phone to type in your date of birth?": "Did the rider hand you their phone to type in your date of birth?",
    "Did the rider hand over the age restricted product?": ["Did the rider hand over the alcohol?", "Did the rider hand over the cigarettes?", "Did the rider hand over the e-cigs?", "Did the rider hand over the CBD?"],
    "Anything else important to note from your interaction with the rider?": "Anything else important to note from your interaction with the rider?",
    "Deliveroo operates a contactless delivery process: Did the rider leave the delivery on the doorstep?": None,
    "If no, then did the rider hand you the delivery?": None,
    "What type of kit is the rider wearing?": "What type of kit is the rider wearing?",
    "If Deliveroo, which items are branded:": "If Deliveroo, which items are branded:",
    "If other, please provide details:": "If other, please provide details:",
    "What mode of transport was the courier using?": "What mode of transport was the rider using?",
    "Did the courier bring your delivery in a thermal bag?": "Did the rider bring your delivery in a thermal bag?",
    "Was there an age verification sticker on your order?": "Was there an age verification sticker on your order?",
    "Did the courier refer to the sticker?": "Did the courier refer to the sticker?",
    "Please use this space to explain anything unusual about your visit or to clarify any detail of your report:": "Please use this space to explain anything unusual about your visit or to clarify any detail of your report:",
    "Has the same rider delivered an age-restricted product to you and asked you for ID within the last month?": "Has the same rider delivered an age-restricted product to you and asked you for ID within the last month?",
    "Please describe the doorstep transaction:": "Please describe the doorstep transaction:",
    "Please confirm below whether or not you were asked for ID:": "Please confirm below whether or not you were asked for ID:"
}

# =====================================================================
# STREAMLIT UI
# =====================================================================

st.title("Deliveroo Report Mapper")

st.write("""
          1. Export the previous month's data
          2. Drop the file in the below box, it should then give you the output file in your downloads
          3. Standard bits - paste over new data
          4. Copy and paste over values etc!!!
          5. Done.
          """)

uploaded = st.file_uploader("Upload audits_basic_data_export.csv", type=["csv"])

# =====================================================================
# PROCESS WHEN FILE IS UPLOADED
# =====================================================================

if uploaded:

    # -----------------------------------------
    # LOAD RAW EXPORT
    # -----------------------------------------
    df = pd.read_csv(uploaded, dtype=str).fillna("")

    # -----------------------------------------
    # ROW FILTER
    # -----------------------------------------
    df = df[df["site_internal_id"] != "SITE224854"].copy()

    # -----------------------------------------
    # DATE & TIME PARSING
    # -----------------------------------------
    df["date_of_visit"] = pd.to_datetime(df["date_of_visit"], dayfirst=True, errors="coerce")
    df["time_of_visit"] = pd.to_datetime(df["time_of_visit"], format="%H:%M", errors="coerce")

    # -----------------------------------------
    # MONTH NAME EXTRACTION
    # -----------------------------------------
    df["__MONTH__"] = df["date_of_visit"].dt.month_name().fillna("")

    # -----------------------------------------
    # CONVERT DATES BACK TO STRINGS
    # -----------------------------------------
    df["date_of_visit"] = df["date_of_visit"].dt.strftime("%Y-%m-%d").fillna("")
    df["time_of_visit"] = df["time_of_visit"].dt.strftime("%H:%M:%S").fillna("")

    # -----------------------------------------
    # SORTER
    # -----------------------------------------
    df = df.sort_values(by="primary_result", ascending=False)

    # =====================================================================
    # GENERIC MAPPING FUNCTION
    # =====================================================================

    def map_value(row, mapping):
        if mapping is None:
            return ""
        if mapping == "__MONTH__":
            return row.get("__MONTH__", "")
        if isinstance(mapping, list):
            for col in mapping:
                if col in row:
                    val = str(row[col]).strip()
                    if val:
                        return val
            return ""
        if mapping in row:
            return str(row[mapping]).strip()
        return ""

    # =====================================================================
    # BUILD FINAL OUTPUT DATAFRAME
    # =====================================================================

    final_df = pd.DataFrame()
    for out_col, mapping in COLUMN_MAP.items():
        final_df[out_col] = df.apply(lambda row: map_value(row, mapping), axis=1)

    # =====================================================================
    # PREPARE DOWNLOAD
    # =====================================================================

    output_bytes = io.BytesIO()
    final_df.to_csv(output_bytes, index=False, encoding="utf-8-sig")
    output_bytes.seek(0)

    st.success(f"File processed successfully! Rows: {len(final_df)}")

    st.download_button(
        "Download Deliveroo CSV",
        data=output_bytes.getvalue(),
        file_name="Deliveroo Report Data.csv",
        mime="text/csv"
    )

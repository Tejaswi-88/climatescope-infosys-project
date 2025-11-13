# ClimateScope - Bug Report

This document lists known bugs, issues, and their resolutions for the **ClimateScope** project. It is intended for internal tracking, debugging, and future improvements.

---

## 1. Summary Table

| ID  | Description | Module / Page | Severity | Status | Resolution / Fix |
|-----|-------------|---------------|---------|--------|----------------|
| B001 | Inconsistent country/location names in raw datasets | Data Preprocessing | High | Resolved | Standardized names using ISO 3 codes; ensured consistency across dataset |
| B002 | Missing continent information in datasets | Data Preprocessing | High | Resolved | Added continent column using PyCountryConvert (pc) and mapping logic |
| B003 | Missing Year, Month, Daily info | Data Preprocessing | High | Resolved | Extracted year, month, and day from `last_updated` column |
| B004 | Numerical and categorical anomalies in datasets | Data Cleaning | High | Resolved | Applied anomaly detection and cleaned data during preprocessing |
| B005 | No crop dataset available for recommendations | Data Augmentation | Medium | Resolved | Added a custom crop dataset to generate month-based crop recommendations |
| B006 | Streamlit default sizing causing UI misalignment | Dashboard / UI | Medium | Resolved | Added custom CSS and Streamlit component styling to adjust layout and alignment |
| B007 | Sidebar navigation default behavior not working properly | Dashboard / UI | Medium | Resolved | Implemented custom sidebar navigation with CSS styling and proper menu logic |
| B008 | No data displayed when filtered by month/country/continent | Dashboard / Filters | High | Open | Applied alternation by extracting month/year from `last_updated` column; used session state to preserve filters. Full verification still needed. |
| B009 | KeyError: Year when loading dataset | Data Loading | High | Open | Alternation: instead of adding a `Year` column, extracted year from `last_updated` column dynamically; ensures dataset loads without crashing. |
| B010 | Visualizations misaligned on small screens | Dashboard / Charts | Low | Open | Alternation: users can use CTRL+ / CTRL- to zoom in/out; applied minor responsive adjustments. Complete responsive solution pending. |
| B011 | Prediction results missing for some images | CV Module / ML Integration | High | Open | Alternation: trained ML model (Random Forest with Standard Scaler). Prediction data mostly matches previous years, so graphs overlap actual vs predicted. Functionally acceptable; cannot fully resolve as predictions are inherently similar to historical data. |
| B012 | CSV data not loaded due to encoding issues | Data Processing | Medium | Open | Resolved using fixed ISO3 / CTF3 encoding standards; dataset now loads reliably across all CSVs. |
| B013 | Map visualizations category handling | Dashboard / Maps | Medium | Resolved | Used Plotly choropleth maps with proper categorical handling; users can manipulate data interactively |
| B014 | Visualization library selection | Dashboard / Charts | Medium | Resolved | Compared libraries; Plotly chosen for interactivity and dynamic filtering |
| B015 | Automated dataset loading from Kaggle | Data Loading / Deployment | Medium | Open | Attempted automation via local task manager; works locally but not on deployed environment. Cloud interfaces needed for deployment automation. Since unavailable, feature not implemented. |

---

## 2. Detailed Bug Descriptions and Fixes

### **B001: Inconsistent country/location names**
- **Module/Page:** Data Preprocessing  
- **Severity:** High  
- **Problem:** Raw datasets had inconsistent country names and location names.  
- **Resolution / Fix:** Standardized all names using ISO 3 codes; ensured uniformity for filtering and visualizations.  
- **Status:** Resolved  

---

### **B002: Missing continent information**
- **Module/Page:** Data Preprocessing  
- **Severity:** High  
- **Problem:** Datasets did not include continents.  
- **Resolution / Fix:** Added a `continent` column using PyCountryConvert (pc) with mapping logic.  
- **Status:** Resolved  

---

### **B003: Missing Year, Month, Daily info**
- **Module/Page:** Data Preprocessing  
- **Severity:** High  
- **Problem:** Dataset lacked `Year`, `Month`, and daily columns.  
- **Resolution / Fix:** Extracted year, month, and day from `last_updated` column; created derived columns for filtering.  
- **Status:** Resolved  

---

### **B004: Numerical and categorical anomalies**
- **Module/Page:** Data Cleaning  
- **Severity:** High  
- **Problem:** Raw dataset had anomalies (outliers, incorrect categories).  
- **Resolution / Fix:** Applied preprocessing steps for anomaly detection and data cleaning.  
- **Status:** Resolved  

---

### **B005: No crop dataset available**
- **Module/Page:** Data Augmentation / Recommendations  
- **Severity:** Medium  
- **Problem:** Crop recommendations require a dataset, which was missing.  
- **Resolution / Fix:** Added a custom crop dataset and integrated logic for month-based recommendations.  
- **Status:** Resolved  

---

### **B006: Streamlit default sizing causing UI issues**
- **Module/Page:** Dashboard / UI  
- **Severity:** Medium  
- **Problem:** Default Streamlit sizing caused misalignment in dashboard layout.  
- **Resolution / Fix:** Added custom CSS and Streamlit layout adjustments to fix alignment.  
- **Status:** Resolved  

---

### **B007: Sidebar navigation issues**
- **Module/Page:** Dashboard / UI  
- **Severity:** Medium  
- **Problem:** Default Streamlit sidebar navigation not working properly.  
- **Resolution / Fix:** Implemented custom sidebar navigation with CSS and menu logic to improve usability.  
- **Status:** Resolved  

---

### **B008: No data displayed for filtered month/country/continent**
- **Module/Page:** Dashboard / Filters  
- **Severity:** High  
- **Problem:** Filters sometimes returned empty data.  
- **Resolution / Workaround:** 
  - Extracted month/year dynamically from `last_updated` column.  
  - Preserved filtered dataframe using Streamlit session state.  
  - Full verification/testing across all datasets is pending.  
- **Status:** Open   

---

### **B009: KeyError: Year**
- **Module/Page:** Data Loading  
- **Severity:** High  
- **Problem:** Missing `Year` column caused script to crash.  
- **Resolution / Workaround:** 
  - Did not add a `Year` column manually; instead, dynamically extracted year from `last_updated` column.  
  - Ensures dataset loads without crashing and filters work.  
- **Status:** Open  

---

### **B010: Visualizations misaligned on small screens**
- **Module/Page:** Dashboard / Charts  
- **Severity:** Low  
- **Problem:** Charts overflowed or misaligned on small screens.  
- **Resolution / Workaround:** 
  - Users can zoom in/out using CTRL+ / CTRL-.  
  - Minor responsive adjustments applied.  
  - Full adaptive layout still pending.  
- **Status:** Open  

---

### **B011: Prediction results missing / overlapping**
- **Module/Page:** CV Module / ML Integration  
- **Severity:** High  
- **Problem:** Some images did not display predictions correctly; predicted graphs overlapped actual historical data.  
- **Resolution / Workaround:** 
  - Trained ML model using Random Forest with Standard Scaler.  
  - Prediction data inherently similar to historical data; graphs overlap by design.  
  - Functionally acceptable; nothing further can be done to separate prediction vs actual.  
- **Status:** Open  

---

### **B012: CSV data encoding issues**
- **Module/Page:** Data Processing  
- **Severity:** Medium  
- **Problem:** Some CSVs had encoding issues, causing load errors.  
- **Resolution / Workaround:** 
  - Applied fixed ISO3 / CTF3 encoding standards.  
  - Dataset now loads reliably without errors.  
- **Status:** Open  

---

### **B013: Map visualization category handling**
- **Module/Page:** Dashboard / Maps  
- **Severity:** Medium  
- **Problem:** Map visualization failed for categorical data.  
- **Resolution / Fix:** Used Plotly choropleth maps with proper categorical handling; enabled dynamic user interaction.  
- **Status:** Resolved  

---

### **B014: Visualization library selection**
- **Module/Page:** Dashboard / Charts  
- **Severity:** Medium  
- **Problem:** Multiple libraries tested; some lacked interactivity.  
- **Resolution / Fix:** Plotly chosen for interactive charts, dynamic filtering, and ease of use by users.  
- **Status:** Resolved  

---

### **B015: Automated dataset loading from Kaggle**
- **Module/Page:** Data Loading / Deployment  
- **Severity:** Medium  
- **Problem:** Automating dataset download and app refresh works locally via task manager, but fails on deployed environments.  
- **Resolution / Workaround:** 
  - Local automation works.  
  - Deployment would require cloud interfaces or schedulers (not currently available).  
  - Feature not implemented in deployment.  
- **Status:** Open  

---

## 3. Notes
- **Severity:** High (blocks functionality), Medium (affects usability), Low (minor visual/UX issues).  
- **Open vs Workaround:** All open bugs either have alternations or partial solutions, but require further testing or are inherently limited by design.  

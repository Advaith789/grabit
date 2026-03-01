# 🥗 Grabit: Bridging the Gap Between Surplus and Sustenance

**Grabit** is a real-time, AI-driven marketplace designed to combat urban food waste. By connecting restaurants with surplus inventory to local consumers at deeply discounted prices, we transform potential waste into affordable, high-quality meals.

---

## Project Overview
* **Theme:** Social Good & Sustainability
* **Core Mission:** To eliminate urban food waste through "last-mile" sales and data-driven inventory management.
* **The Problem:** Overproduction leads to financial loss for businesses and an environmental crisis (methane emissions), while budget-conscious consumers struggle to access quality nutrition.

---

## ⚙️ Technical Architecture

Grabit moves beyond simple API wrappers to a multi-layered automated pipeline.

### **The Stack**
* **Frontend:** **Angular** – A seamless, reactive dashboard for both Restaurants (to post inventory) and Users (to manage preferences).
* **Backend:** **PostgreSQL on GCP (Cloud SQL)** – Optimized for storing complex user-to-cuisine mapping and historical waste logs.
* **Agentic AI Pipeline:** Developed in Google Colab & VS Code.

### **The Innovation: AI as a Structural Parser**
Instead of using GenAI as a "chatbot," Grabit utilizes it as a **Structural Parser**:
1.  **Data Extraction:** The AI parses unstructured restaurant "shouts" (e.g., *"Got 5 veg plates left, 50% off until 10pm"*).
2.  **Entity Identification:** It identifies the "What, How Much, and When," passing structured data to our custom backend.
3.  **Smart-Matching Engine:** Custom Python logic performs a **"Pref-Join"** between real-time AI entities and the PostgreSQL user-base.
4.  **Push System:** Users don't search for food; the food (via AI matching) finds them based on their pre-set "Food DNA" (Cuisine + Restaurant preferences).

---

## Key Features

* **Real-Time Notifications:** Automated alerts triggered by the matching engine.
* **Waste Visualization:** A dedicated suite showing restaurants their "Total Loss Occurred," forcing a data-driven realization of their environmental footprint.
* **Lean Manufacturing Integration:** Using data to help restaurants adjust their supply chain to prevent loss before it happens.

---

## Sustainability & Social Impact

* **Carbon Reduction:** Lowering the daily CO2 footprint of participating local businesses.
* **Nutrition Accessibility:** Providing high-protein meals to students and low-income users at **40-70% discounts**.
* **Operational Strategy:** Shifting the industry from reactive disposal to proactive inventory management.

---

## Future Roadmap

1.  **Predictive Waste Analytics:** Moving from reactive to proactive by analyzing "Loss Occurred" trends to provide Demand Forecasting reports.
2.  **Dynamic Pricing Engine:** An automated "Price-Decay" algorithm where discounts increase (e.g., 40% → 70%) as the pickup deadline approaches.
3.  **In-App Booking:** Integrated payment gateways to allow users to "Claim" their meal instantly, removing availability uncertainty.

---

**Grabit: Bridging the Gap Between Surplus and Sustenance**

**Theme:** Social Good & Sustainability
Grabit is a real-time, AI-driven marketplace designed to combat urban food waste by connecting restaurants with surplus inventory to local consumers at discounted prices.
 Problem Statement: Every day, perfectly edible food is discarded by restaurants due to overproduction. This isn't just a financial loss; it’s a sustainability crisis.
**Who it affects:** Local businesses (lost revenue) and budget-conscious consumers (limited access to quality food).
**Why it matters:** Food waste is a leading contributor to methane emissions. By facilitating the "last-mile" sale of leftovers, we turn potential waste into affordable meals.
**Technical Architecture**
We moved beyond simple API wrappers to build a multi-layered automated pipeline.
**Frontend:** Angular – a seamless dashboard for both Restaurants (to post) and Users (to manage preferences).
**Backend:** PostgreSQL on GCP (Cloud SQL) –  For storing complex user-to-cuisine mapping and historical waste logs.
**Agentic AI Pipeline:** Developed in Google Colab & VS Code.
**Depth:** Instead of a basic chatbot, our Agent acts as a Data Extractor. It parses unstructured restaurant "shouts" (e.g., "Got 5 veg plates left, 50% off until 10pm"), identifies key entities, and triggers the matching logic.
**Smart-Matching Engine:** Custom Python logic that performs a "Pref-Join" between real-time AI entities and the PostgreSQL user-base to trigger automated notifications.
**Innovation & Originality**
**While many apps use GenAI for chat, Grabit uses it as a Structural Parser:**
We don't use AI to "talk" to the user; we use it to transform data. The AI extracts the "What, How Much, and When," passing structured data to our custom backend logic.
Unlike "search-and-find" apps, Grabit is a Push System. Users don't have to look for food; the food (via AI matching) finds them based on their pre-set DNA (Cuisine + Restaurant preferences).
A dedicated visualization suite that shows restaurants the "Total Loss Occurred," forcing a data-driven realization of their environmental footprint.
**Social Impact & Sustainability Goals**
Reduce daily CO2 footprint per participating restaurant.
Provide high-protein, quality meals to students and low-income users at a 40-70% discount.
Use the Waste Visualization data to help restaurants implement "Lean Manufacturing" principles and adjusting their supply chain to prevent the loss before it happens.
**Future Roadmap**
Predictive Waste Analytics: Moving from reactive to proactive. By analyzing "Loss Occurred" trends, Grabit will provide restaurants with Demand Forecasting reports, suggesting prep-volume adjustments to prevent waste before it happens.
Dynamic Pricing Engine: Implement an automated "Price-Decay" algorithm. As the pickup deadline approaches, the AI will dynamically adjust the discount (e.g., 40% off at 8 PM, 70% off at 9:30 PM) to ensure 100% inventory clearance.
Online In-App Booking: Integrated payment gateways to allow users to "Claim" their meal instantly, removing the uncertainty of availability upon arrival.
Conclusion
Grabit isn't just an app; it’s an Operational Strategy. By combining Angular’s reactive interface, PostgreSQL’s reliable data architecture on GCP, and the analytical power of Agentic AI, we are turning a massive environmental problem into a community-driven solution.



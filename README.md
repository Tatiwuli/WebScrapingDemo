# E-commerce Analytics Platform for Product Review Analysis

## ⚡ **Project Description & Purpose**

**Experience:** Software Developer Internship at a Consulting Firm, National Taiwan University

In Taiwan, online forums like Mobile01 are popular platforms where users share product experiences and recommendations. While e-commerce platforms provide built-in access to customer reviews, companies struggle to efficiently gather insights from forums. A business department of one of our clients spent **4+ hours per report** manually searching for product reviews, organizing data in spreadsheets, and analyzing them for the **executive board**. When they want qualitative data, they would spent 450 hours and USD$600 for user interviews.

This process was optimized when my team and I developed a **Business Intelligence platform** that scrapes product reviews from online forums and generates **data analysis reports** using **Python, OpenAI, and Streamlit**.

---

## 🤔 **How Does the Platform Work?**

### **Input:**
- `website_url`: The URL of the online forum or website to scrape.
- `keyword`: The product name, brand, and model (if available).
- `time_range`: The publication date range for filtering relevant forum posts.

### **Output:**
- A structured report summarizing **positive and negative perspectives** on the product.

### **Process:**
1. **Checks the knowledge base** – Retrieves stored HTML tags for the website. If unavailable, the system triggers agents to inspect the site and save the tags.
2. **Extracts relevant posts** – Searches for the keyword, sorts results by date, and retrieves posts published within the specified time range.
3. **Filters and summarizes content** – The **Post Summarizer LLM** analyzes each post, filtering out irrelevant content based on the keyword and target audience. Relevant posts are then passed to the **Product Summarizer LLM**.
4. **Generates the final report** – The **Product Summarizer LLM** compiles all relevant summaries into a structured **data analysis report**, displayed on **Streamlit**.

---

## 🤖 **How the Agents Work**

Each agent is powered by an **LLM with a specific role, background, and task**. Their primary function is to **inspect HTML content**, identify the necessary elements for scraping, and validate them using **Selenium**. Once the correct HTML tags are identified, they are stored in the **knowledge base** for future reference.

### **Agent Roles & Responsibilities**
- **SearchAgent** – Identifies the selectors that enable Selenium to perform searches.
- **SortResultsAgent** – Finds the selectors that allow sorting results by date.
- **ExtractResultsAgent** – Locates the selectors that allow Selenium to extract post content.
- **ChangePageAgent** – Determines the selectors for navigating between pages of search results.

### **Feedback Mechanism**
All agents operate under a **feedback loop** to ensure accuracy:

1. **Initial Attempt:** The agent inspects the website and identifies HTML tags.
2. **Validation with Selenium:** The extracted tags are tested to perform the intended action (search, sort, extract, or paginate).
3. **Error Handling & Refinement:** If an action fails, the **error message from Selenium** is stored in temporary memory. The agent then **updates its prompt**, incorporating the failure information to refine its selection.
4. **Retry Process:** The agent reattempts the process with the refined approach. This continues for up to **three retries** until a valid set of HTML tags is identified.
5. **Knowledge Base Update:** Once successful, the correct HTML tags are stored in the **knowledge base**, allowing the system to bypass inspection for future scrapes of the same website.

---
## 💻 Demo 
### User Interface

![End Result](https://github.com/Tatiwuli/WebScrapingDemo/blob/main/user-interface-demo.gif)


**Check out the Notion page for** 

✅ Screen recordings of Selenium scraping data autonomously  
✅ Terminal output screenshots showcasing each step of the process  

🔗 [View the Full Demo on Notion](https://cooing-parsley-1bb.notion.site/Web-Scraping-Project-Demo-1aaecbc620b480998f73d026917cfd6e?pvs=4)



## 👩🏻‍💻 **My Contributions**
- **Ideated and designed** the agent framework and feedback mechanism with another Software Engineer.
- **Engineered LLM prompts** for the HTML inspection agents.
- **Developed agent scripts (HTML inspection), scraping tools, and the `run_scraper` file** to manage the HTML inspection and scraping workflow.
- **Enhanced Streamlit UI/UX** by participating in design-thinking sessions with the UX team to improve the client experience.

---

## 🥳 **Impact**
This platform improved **product review collection efficiency by 50%** while achieving **95% data accuracy** in extracted post reviews, enabling deeper consumer insights with greater efficiency.

---

## 🚲 **Next Steps**
To scale this tool for more companies, the following improvements are needed:

### **Enhancing User Experience**
- Implement a **more engaging loading interface** during HTML inspection and scraping:  
  - Display **real-time agent progress** on Streamlit.  
  - Show **initial summarized results** from the Summarizers before the full report is generated.

### **Optimizing Performance**
- **Increase HTML inspection speed** by making sorting, extracting results, and pagination **asynchronous**.  
  - The **Inspection phase** focuses only on identifying and validating HTML tags, meaning the **ExtractResults and ChangePage stages** do not need to wait for sorting to complete.  
  - Since these three stages operate on the same webpage, they can run **concurrently**, reducing processing time.

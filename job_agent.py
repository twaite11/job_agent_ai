import os
import smtplib
from email.mime.text import MIMEText
from typing import List, Dict
import requests
from bs4 import BeautifulSoup

from langchain_community.llms import OpenAI
from langchain.agents import initialize_agent, AgentType, Tool
from langchain.memory import ConversationBufferMemory
from dotenv import load_dotenv

#------------------------------------------------------------------------------------------------------------------------------------------
# The AI Job Search Agent is an autonomous and goal-driven system designed to automate the tedious process of searching for new job opportunities. 
# Instead of manually checking various job boards, this intelligent agent 
# leverages the power of large language models (LLMs) and specialized tools to find relevant 
# job postings and deliver them directly to your inbox. This project serves as a practical 
# demonstration of building a functional agentic AI application.
#--------------------------------------------------------------------------------------------------------------------------------------

# load .env to keep sensitive stuff safe and sound.
load_dotenv()

class EmailTool:
    """A tool to send emails using SMTP."""
    def __init__(self, sender_email: str, sender_password: str, smtp_server: str = "smtp.gmail.com", smtp_port: int = 587):
        self.sender_email = sender_email
        self.sender_password = sender_password
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
    
    def send_email(self, to_email: str, subject: str, body: str) -> str:
        """Sends an email to a specified recipient with a given subject and body."""
        try:
            msg = MIMEText(body)
            msg['Subject'] = subject
            msg['From'] = self.sender_email
            msg['To'] = to_email

            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()  
                server.login(self.sender_email, self.sender_password)
                server.send_message(msg)
            return f"Email successfully sent to {to_email}."
        except Exception as e:
            return f"Failed to send email. Error: {e}"

@tool
def send_job_email(job_details: str, recipient_email: str) -> str:
    """Sends a summary of job postings via email.
    
    The input must be a JSON string with 'recipient_email' and 'job_details' keys.
    The job_details should be a formatted string containing all the job listings."""
    
    # grabbing email login from the secure .env file.
    email_tool = EmailTool(
        sender_email=os.getenv("EMAIL_ADDRESS"),
        sender_password=os.getenv("EMAIL_PASSWORD")
    )
    
    subject = "Your Daily AI Engineering Job Postings"
    body = f"Hello,\n\nHere are the new AI engineering job postings I found for you. Hope these help you land that dream role!\n\n{job_details}\n\nBest regards,\nYour Job Agent"
    
    return email_tool.send_email(recipient_email, subject, body)

@tool
def get_job_postings(query: str) -> List[Dict]:
    """Searches for recent job postings using a search API and returns a structured list of results."""
    
    # SerpApi key to search for jobs.
    serpapi_key = os.getenv("SERPAPI_API_KEY")
    if not serpapi_key:
        return "Error: SERPAPI_API_KEY not set. Cannot perform search."

    search_url = "https://serpapi.com/search.json"
    params = {
        "engine": "google_jobs",
        "q": query,
        "api_key": serpapi_key,
    }
    
    response = requests.get(search_url, params=params)
    data = response.json()
    
    jobs = []
    if 'jobs_results' in data:
        # clean the data assuming we found jobs
        for job in data['jobs_results']:
            jobs.append({
                "title": job.get("title"),
                "company": job.get("company_name"),
                "location": job.get("location"),
                "link": job.get("related_links", [{}])[0].get("link") if job.get("related_links") else 'No link available'
            })
    
    return jobs

# --- Agent and Tool Initialization ---
# create our agent
llm = OpenAI(temperature=0)  # using OpenAI
tools = [
    # initilizae tool for searching the web
    Tool(
        name="get_job_postings",
        func=get_job_postings.run,
        description="Useful for when you need to find new AI engineering jobs. The input should be a precise job query, e.g., 'AI engineer jobs in New York'."
    ),
    # initialize tool for sending emails 
    # needs input to see if the email sent successfully.
    Tool(
        name="send_job_email",
        func=send_job_email.run,
        description="Useful for when you need to send an email with job postings. The input should be a JSON string with 'recipient_email' and a formatted 'job_details' string."
    )
]

# add memeory for agent to learn from / history
memory = ConversationBufferMemory(memory_key="chat_history")

agent_chain = initialize_agent(
    tools, 
    llm, 
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, 
    verbose=True,
    memory=memory,
)

if __name__ == "__main__":
    print("Agentic Job Finder is running. Type 'exit' to quit.")
    # loop until we decide to exit
    while True:
        user_input = input("Enter your request: ")
        if user_input.lower() == 'exit':
            break
        
        try:
            # agent decide how to handle the input
            response = agent_chain.run(user_input)
            print("Agent's response:")
            print(response)
        except Exception as e:
            # in case something goes wrong, catch the error and print it.
            print(f"An error occurred: {e}")

import os
import requests
from bs4 import BeautifulSoup
import streamlit as st
from langchain.llms import AzureOpenAI
from langchain.prompts import PromptTemplate

os.environ["OPENAI_API_TYPE"] = "azure"
os.environ["OPENAI_API_VERSION"] = "2023-08-01-preview"
os.environ["OPENAI_API_BASE"] = st.secrets["azureopenai"]["AZURE_OPENAI_ENDPOINT"]
os.environ["OPENAI_API_KEY"] = st.secrets["azureopenai"]["AZURE_OPENAI_KEY"]
DEPLOYMENT_NAME = st.secrets["azureopenai"]["AZURE_OPENAI_DEPLOYMENT_NAME"]


def scrape_text(url):
    '''
    Scrape text from url
    '''
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        text = ' '.join([p.get_text() for p in soup.find_all('p')])
        return text
    except Exception as e:
        st.error(f"Error scraping URL: {e}")
        return None


def generate_topic_brand_voice(combined_text, tone, formality, enthusiasm, user_topic):
    '''
    Generate text about a given user topic with a specific tone, formality, and enthusiam, having
    as base the scraped texts from the provided URLs
    '''

    template = """Create a brand voice about the following topic: 
    {user_topic}
    
    with the following characteristics: Tone: {tone}, Formality: {formality}, Enthusiasm: {enthusiasm}.
    Based on this text: 
    {combined_text}
    """

    prompt = PromptTemplate(
        input_variables=["combined_text", "tone",
                         "formality", "enthusiasm", "user_topic"],
        template=template
    )

    llm = AzureOpenAI(deployment_name=DEPLOYMENT_NAME,
                      model_name="gpt-35-turbo",
                      temperature=0.5,
                      max_tokens=600,
                      top_p=1,
                      frequency_penalty=0,
                      presence_penalty=0)

    return llm(prompt.format(combined_text=combined_text, tone=tone, formality=formality, enthusiasm=enthusiasm, user_topic=user_topic))


def app():
    '''
    The app with the required UI elements and logic
    '''
    st.title("Brand Voice Topic Generator")

    # Input URL(s)
    urls = st.text_area(
        "Enter one or more URLs (separated by commas) to scrape text from")

    # Selection buttons
    tone = st.selectbox(
        "Select Tone", ["funny", "neutral", "serious"], index=1)
    formality = st.selectbox("Select Formality", [
                             "casual", "neutral", "formal"], index=1)
    enthusiasm = st.selectbox("Select Enthusiasm", [
                              "enthusiastic", "neutral", "practical"], index=1)

    # Topic
    user_topic = st.text_input(
        "Write 1-2 sentences about the topic you want to generate")

    # Generate topic
    generate_voice = st.button("Generate topic with brand voice")

    if generate_voice:
        # Scrape the text from the provided URLs
        url_list = [url.strip() for url in urls.split(',')]
        text_list = []

        for url in url_list:
            text = scrape_text(url)
            if text:
                text_list.append(text)

        # Combine the text and send it to the LLM to generate the topic in the brand voice
        combined_text = ' '.join(text_list)
        # st.write(combined_text)

        if user_topic:
            topic_brand_voice = generate_topic_brand_voice(
                combined_text, tone, formality, enthusiasm, user_topic)
            # Display the generated topic in the brand voice
            st.write(topic_brand_voice)
        else:
            st.warning("Please enter a sentence.")


if __name__ == "__main__":
    # Run the Streamlit app
    app()

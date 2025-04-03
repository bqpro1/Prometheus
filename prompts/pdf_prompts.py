"""
PDF-related prompts for the Odysseus agent.
These prompts define how the agent handles PDF files and PDF links on webpages.
"""

# Basic role description
role = "You are a software engineer working at a startup"

# Prompt to determine if a page is a PDF file
is_pdf = """You are on a page under the address: {current_url}. 
This the raw html of the page: 

```html
{page_html}
```

Think step by step and answer the following question: Is it a PDF file? Respond with json:{json_format}Insert 1 if it is a PDF file, 0 otherwise."""

# Prompt to determine if a page contains full information or just an abstract
full_info = """You are on a page under the address: {current_url}. 
This the raw html of the page: 

```html
{page_html}
```

Decide if the page is just a page with abstract of article or page with the full information about the topic. Respond with json:{json_format}Insert 1 if it is a page with the full information about the topic, 0 otherwise."""

# Prompt to extract PDF links from a webpage
extract_pdf_link = """Your task is to find a specyfic elements of a given website. You have to find the elements in a page source and write a proper xpath for each of them. You use selenium library for Python to interact with the website. You should also write python code using selenium to find the elements. Selenium session is already started and the page source is already loaded. Session is stored in a variable called `driver`. You use new version of selenium library, so you can use `driver.find_element(By.XPATH, xpath)` method to find the elements. You can also use `driver.page_source` to access the page source.
Your response should be a json object with the following structure:{json_format}In the code field create a variable called `pdf_link` and assign the link to the pdf file to it.
This the source code of a website:
```html
{page_html}
```
Find the following elements:
- Link to a pdf file.
Please be careful with the correctness of the Python code! Make sure that the code is correct and that it works properly."""

# Prompt to analyze the content of a PDF file
read_pdf = """This is a text from a PDF file: 

{pdf_content}

Think step by step about what you have read and formulate a reflection on the content of the article. Find a balance between creativity and reliability in reporting PDF content. Take into consideration most important claims from the article. You can use LaTeX syntax or markdown syntax to format your reflection and most important claims. If there are some mathematical formulas in the text, use LaTeX syntax to format them as LaTeX formulas.
Use double $ sign at the beginning and at the end of the formula to format it as LaTeX formula. For example: $$x^2$$
 If you want to insert an inline formula, use single $ sign at the beginning and at the end of the formula. For example: $x^2$"""

# JSON response format for is_pdf prompt
json_is_pdf = """
```json
 {
 "is_pdf": 0 | 1
}
```
"""

# JSON response format for full_info prompt
json_page2pdf = """
```json
 {
 "full_info": 0 | 1
}
```
"""

# JSON response format for extract_pdf_link prompt
json_extract_pdf_link = """
```json
{
"pdf": "xpath"
"element_tag": "html tag"
"ccs_class": "classname"
"id": "id"
"code": "python code"}```
"""

# Export all prompts as a dictionary for backwards compatibility with JSON loading
prompts = {
    "role": role,
    "is_pdf": is_pdf,
    "full_info": full_info,
    "extract_pdf_link": extract_pdf_link,
    "read_pdf": read_pdf,
    "json_is_pdf": json_is_pdf,
    "json_page2pdf": json_page2pdf,
    "json_extract_pdf_link": json_extract_pdf_link
} 
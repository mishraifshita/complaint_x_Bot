import pandas as pd
from langchain_core.documents import Document

def dataconverter():

    Query_data = pd.read_csv(r"data/insurance_data.csv")

    data = Query_data[["Query", "Answer"]]

    query_list = []

    ## Itrate over the rows of the DataFrame

    for index, row in data.iterrows():
        object = {
             "Query": row["Query"],
             "Answer": row["Answer"]
        }

    ## Append the object to the product list
    query_list.append(object)
    docs = []
    for entry in query_list:
        metadata = {"Query": entry["Query"]}
        doc = Document(page_content= entry['Answer'], metadata=metadata)
        docs.append(doc)
    return docs




from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.prompts import base
from pydantic import Field

"""
MCP Servers are essentially composed of
tools, resources and prompts.

    -Tools: These are functions that perform specific actions. 
    They can be called by the agent to interact with the environment or perform tasks;

    - Resources: These are data endpoints that the agent can query to retrieve information. 
    They can be thought of as APIs that provide access to data or services;

    - Prompts: These are templates that guide the agent in generating responses. 
    They can be used to structure the agent's output or to provide context for its responses.
"""

mcp = FastMCP("DocumentMCP", log_level="ERROR")


docs = {
    "deposition.md": "This deposition covers the testimony of Angela Smith, P.E.",
    "report.pdf": "The report details the state of a 20m condenser tower.",
    "financials.docx": "These financials outline the project's budget and expenditures.",
    "outlook.pdf": "This document presents the projected future performance of the system.",
    "plan.md": "The plan outlines the steps for the project's implementation.",
    "spec.txt": "These specifications define the technical requirements for the equipment.",
}


# Tools


@mcp.tool(
    name="read_doc_contents",
    description="Reads the contents of a document given its name.",
)
def read_doc_contents(
    doc_id: str = Field(description="The ID of the document to read"),
):
    if doc_id not in docs:
        raise ValueError(f"Document with ID '{doc_id}' not found.")
    return docs[doc_id]


@mcp.tool(
    name="edit_documents",
    description="Edit a document by replacing its content with new content.",
)
def edit_doc_contents(
    doc_id: str = Field(description="The ID of the document to edit"),
    old_content: str = Field(description="The existing content of the document"),
    new_content: str = Field(
        description="The new content to replace the existing document content"
    ),
):
    if doc_id not in docs:
        raise ValueError(f"Document with ID '{doc_id}' not found.")
    docs[doc_id] = docs[doc_id].replace(old_content, new_content)
    return f"Document '{doc_id}' has been updated."


# Resources


@mcp.resource(
    "docs://documents",
    mime_type="application/json",
)
def list_docs() -> list[str]:
    return list(docs.keys())


@mcp.resource(
    "docs://documents/{doc_id}",
    mime_type="text/plain",
)
def get_doc_content(
    doc_id: str = Field(description="The ID of the document to edit"),
) -> str:
    if doc_id not in docs:
        raise ValueError(f"Document with ID '{doc_id}' not found.")
    return docs[doc_id]


# Prompts


@mcp.prompt(
    name="format",
    description="Rewrite a document in markdown format.",
)
def rewrite_doc_markdown(
    doc_id: str = Field(description="The ID of the document to rewrite"),
) -> list[base.Message]:
    prompt = f"""
    Your goal is to reformat a document to be written in markdown syntax.
    
    The id of the document you neet to reformat is:
    <document_id>
    {doc_id}
    </document_id>

    Add in headers, bullet points, or any other markdown syntax you think is appropriate to make the document easier to read.
    Use the 'edit_doc_contents' tool to edit the document.
    """

    return [base.UserMessage(prompt)]


@mcp.prompt(
    name="summarize",
    description="Summarize the content of a document.",
)
def summarize_doc(
    doc_id: str = Field(description="The ID of the document to summarize"),
) -> list[base.Message]:
    prompt = f"""
    Your goal is to summarize the content of a document.
    
    The id of the document you need to summarize is:
    <document_id>
    {doc_id}
    </document_id>
    """

    return [base.UserMessage(prompt)]


if __name__ == "__main__":
    mcp.run(transport="stdio")

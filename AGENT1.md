# Agent Instructions for Jules

## Data Handling Protocol
* **No Simulations:** Under no circumstances should you simulate or "mock" a dataset if a URL is provided.
* **External Fetching:** Use `curl`, `wget`, or the `requests` library to fetch data from provided Open Access links.
* **Loading Procedure:** Always attempt to load the fetched data into a Pandas DataFrame named `df` immediately after download.
* **Error Reporting:** If a link is broken or restricted, report the specific HTTP error code instead of falling back to a simulated dataset.

"""Flask entrypoint for Universal Medical AI Agent. No clinical conclusions are generated without evidence."""
import os
import requests
from flask import Flask, jsonify, render_template, request

app = Flask(__name__)
EPMC_URL = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"

@app.get("/")
def home():
    return render_template("index.html")

@app.get("/api/health")
def health():
    return jsonify(status="ok", service="Universal Medical AI Agent")

@app.post("/api/search_pmc")
def search_pmc():
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify(success=False, message="Invalid JSON body"), 400
    query = payload.get("query", "")
    if not isinstance(query, str) or not 2 <= len(query.strip()) <= 300:
        return jsonify(success=False, message="Query must contain 2–300 characters"), 400
    try:
        limit = int(payload.get("limit", 10))
    except (TypeError, ValueError):
        return jsonify(success=False, message="Invalid limit"), 400
    if not 1 <= limit <= 20:
        return jsonify(success=False, message="Limit must be 1–20"), 400
    try:
        response = requests.get(EPMC_URL, params={"query": query.strip(), "format": "json", "pageSize": limit, "resultType": "core"}, timeout=12)
        response.raise_for_status()
        records = response.json().get("resultList", {}).get("result", [])
    except (requests.RequestException, ValueError):
        return jsonify(success=False, message="Scientific search temporarily unavailable"), 502
    results = []
    for record in records:
        pmid = record.get("pmid")
        pmcid = record.get("pmcid")
        doi = record.get("doi")
        if pmid:
            url = "https://europepmc.org/article/MED/" + str(pmid)
        elif pmcid:
            url = "https://europepmc.org/article/PMC/" + str(pmcid)
        elif doi:
            from urllib.parse import quote
            url = "https://doi.org/" + quote(str(doi), safe="/")
        else:
            url = "https://europepmc.org/"
        results.append({"title": record.get("title") or "Untitled", "authors": record.get("authorString") or "", "journal": record.get("journalTitle") or "", "year": record.get("pubYear") or "", "url": url})
    return jsonify(success=True, data=results, source="Europe PMC")

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=int(os.environ.get("PORT", "8000")))

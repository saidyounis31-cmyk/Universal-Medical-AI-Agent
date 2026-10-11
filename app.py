from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

# الصفحة الرئيسية
@app.route('/')
def home():
    return render_template('index.html')

# محرك البحث المباشر في المكتبة الطبية المحكمة Europe PMC
@app.route('/api/search_pmc', methods=['POST'])
def search_pmc():
    data = request.json or {}
    query = data.get('query', 'Nigella sativa')
    limit = data.get('limit', 10)
    
    url = f"https://www.ebi.ac.uk/europepmc/webservices/rest/search?query={query}&format=json&pageSize={limit}"
    
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            results = response.json().get('resultList', {}).get('result', [])
            formatted = []
            for item in results:
                formatted.append({
                    'title': item.get('title', 'بدون عنوان'),
                    'authors': item.get('authorString', 'غير محدد'),
                    'journal': item.get('journalTitle', 'مجلة علمية'),
                    'year': item.get('pubYear', ''),
                    'pmid': item.get('pmid', ''),
                    'doi': item.get('doi', ''),
                    'url': f"https://europepmc.org/article/MED/{item.get('pmid')}" if item.get('pmid') else "#"
                })
            return jsonify({'success': True, 'data': formatted})
        return jsonify({'success': False, 'message': 'تعذر جلب البيانات من المصدر'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

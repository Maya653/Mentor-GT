import requests
from flask import current_app
from typing import Dict, List, Optional

class APIExternaService:
    """Servicio para interactuar con APIs externas de bases de datos académicas"""
    
    def __init__(self):
        self.google_scholar_api = current_app.config.get('GOOGLE_SCHOLAR_API', '')
        self.scopus_api_key = current_app.config.get('SCOPUS_API_KEY', '')
        self.orcid_client_id = current_app.config.get('ORCID_CLIENT_ID', '')
        self.pubmed_api_key = current_app.config.get('PUBMED_API_KEY', '')
    
    def obtener_publicaciones_google_scholar(self, scholar_id: str) -> List[Dict]:
        """Obtiene publicaciones de Google Scholar"""
        if not self.google_scholar_api or not scholar_id:
            return []
        
        try:
            # Nota: Google Scholar no tiene API oficial, esto es un placeholder
            # En producción se necesitaría usar scraping o servicios de terceros
            url = f"https://scholar.google.com/citations?user={scholar_id}"
            # Implementación real requeriría scraping o API de terceros
            return []
        except Exception as e:
            print(f"Error obteniendo publicaciones de Google Scholar: {e}")
            return []
    
    def obtener_publicaciones_scopus(self, scopus_id: str) -> List[Dict]:
        """Obtiene publicaciones de Scopus"""
        if not self.scopus_api_key or not scopus_id:
            return []
        
        try:
            url = f"https://api.elsevier.com/content/search/author"
            headers = {
                'Accept': 'application/json',
                'X-ELS-APIKey': self.scopus_api_key
            }
            params = {
                'query': f'AU-ID({scopus_id})',
                'view': 'STANDARD'
            }
            
            response = requests.get(url, headers=headers, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                # Procesar respuesta de Scopus
                return self._procesar_respuesta_scopus(data)
            return []
        except Exception as e:
            print(f"Error obteniendo publicaciones de Scopus: {e}")
            return []
    
    def obtener_publicaciones_orcid(self, orcid_id: str) -> List[Dict]:
        """Obtiene publicaciones de ORCID"""
        if not self.orcid_client_id or not orcid_id:
            return []
        
        try:
            url = f"https://pub.orcid.org/v3.0/{orcid_id}/works"
            headers = {
                'Accept': 'application/json'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                return self._procesar_respuesta_orcid(data)
            return []
        except Exception as e:
            print(f"Error obteniendo publicaciones de ORCID: {e}")
            return []
    
    def obtener_publicaciones_pubmed(self, pubmed_query: str) -> List[Dict]:
        """Obtiene publicaciones de PubMed"""
        if not pubmed_query:
            return []
        
        try:
            url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
            params = {
                'db': 'pubmed',
                'term': pubmed_query,
                'retmode': 'json',
                'retmax': 100
            }
            
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                pmids = data.get('esearchresult', {}).get('idlist', [])
                return self._obtener_detalles_pubmed(pmids)
            return []
        except Exception as e:
            print(f"Error obteniendo publicaciones de PubMed: {e}")
            return []
    
    def _procesar_respuesta_scopus(self, data: Dict) -> List[Dict]:
        """Procesa la respuesta de Scopus"""
        publicaciones = []
        # Implementar procesamiento según estructura de respuesta de Scopus
        return publicaciones
    
    def _procesar_respuesta_orcid(self, data: Dict) -> List[Dict]:
        """Procesa la respuesta de ORCID"""
        publicaciones = []
        works = data.get('group', [])
        for work in works:
            work_summary = work.get('work-summary', [{}])[0]
            titulo = work_summary.get('title', {}).get('title', {}).get('value', '')
            if titulo:
                publicaciones.append({
                    'titulo': titulo,
                    'doi': work_summary.get('external-ids', {}).get('external-id', [{}])[0].get('external-id-value', ''),
                    'año': work_summary.get('publication-date', {}).get('year', {}).get('value', ''),
                    'tipo': 'articulo'
                })
        return publicaciones
    
    def _obtener_detalles_pubmed(self, pmids: List[str]) -> List[Dict]:
        """Obtiene detalles de publicaciones de PubMed por sus IDs"""
        if not pmids:
            return []
        
        try:
            url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
            params = {
                'db': 'pubmed',
                'id': ','.join(pmids),
                'retmode': 'xml'
            }
            
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                # Procesar XML de PubMed
                return self._procesar_xml_pubmed(response.text)
            return []
        except Exception as e:
            print(f"Error obteniendo detalles de PubMed: {e}")
            return []
    
    def _procesar_xml_pubmed(self, xml_data: str) -> List[Dict]:
        """Procesa XML de PubMed"""
        publicaciones = []
        # Implementar procesamiento XML
        # Por ahora retornar lista vacía
        return publicaciones


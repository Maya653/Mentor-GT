import requests
import os
from xml.etree import ElementTree as ET
from dotenv import load_dotenv

load_dotenv()

# API Key de Scopus (esta sí va en .env porque es secreta)
SCOPUS_API_KEY = os.getenv("SCOPUS_API_KEY")


class APIExternaService:
    """Servicio para interactuar con APIs externas de bases de datos académicas"""
    
    def __init__(self, docente=None):
        """
        Inicializa el servicio con los IDs del docente
        
        Args:
            docente: Objeto Docente con los campos orcid, scopus_author_id, pubmed_query
        """
        self.orcid_id = docente.orcid if docente and docente.orcid else None
        self.scopus_author_id = docente.scopus_author_id if docente and docente.scopus_author_id else None
        self.pubmed_query = docente.pubmed_query if docente and docente.pubmed_query else None
        self.scopus_api_key = SCOPUS_API_KEY
    
    # ==========================================
    # 1. ORCID API
    # ==========================================
    def obtener_publicaciones_orcid(self):
        """Obtiene publicaciones de ORCID"""
        if not self.orcid_id:
            raise ValueError("No tienes configurado tu ORCID ID. Agrégalo en tu perfil.")
        
        url = f"https://pub.orcid.org/v3.0/{self.orcid_id}/works"
        headers = {"Accept": "application/json"}
        
        r = requests.get(url, headers=headers, timeout=30)
        if r.status_code == 404:
            raise ValueError(f"ORCID ID no encontrado: {self.orcid_id}")
        if r.status_code != 200:
            raise ValueError(f"Error al conectar con ORCID (código {r.status_code})")
        
        data = r.json()
        works = []
        
        for group in data.get("group", []):
            summary = group.get("work-summary", [{}])[0]
            
            title = summary.get("title", {}).get("title", {}).get("value", "Sin título")
            pub_type = summary.get("type", "Sin tipo")
            pub_year = summary.get("publication-date", {}).get("year", {}).get("value", None)
            
            try:
                pub_year = int(pub_year) if pub_year else None
            except:
                pub_year = None
            
            external_ids = summary.get("external-ids", {}).get("external-id", [])
            
            doi = None
            for ext in external_ids:
                if ext.get("external-id-type") == "doi":
                    doi = ext.get("external-id-value")
            
            revista = ""
            journal_title = summary.get("journal-title")
            if journal_title:
                revista = journal_title.get("value", "")
            
            works.append({
                "titulo": title,
                "año": pub_year,
                "tipo": pub_type,
                "doi": doi,
                "revista": revista,
                "fuente": "ORCID"
            })
        
        return works
    
    # ==========================================
    # 2. SCOPUS API
    # ==========================================
    def obtener_publicaciones_scopus(self):
        """Obtiene publicaciones de Scopus"""
        if not self.scopus_author_id:
            raise ValueError("No tienes configurado tu Scopus Author ID. Agrégalo en tu perfil.")
        
        if not self.scopus_api_key:
            raise ValueError("API Key de Scopus no configurada en el servidor")
        
        url = f"https://api.elsevier.com/content/search/scopus?query=AU-ID({self.scopus_author_id})"
        
        headers = {
            "X-ELS-APIKey": self.scopus_api_key,
            "Accept": "application/json"
        }
        
        r = requests.get(url, headers=headers, timeout=30)
        
        if r.status_code == 401:
            raise ValueError("Error de autenticación con Scopus")
        if r.status_code != 200:
            raise ValueError(f"Error al conectar con Scopus (código {r.status_code})")
        
        data = r.json()
        items = data.get("search-results", {}).get("entry", [])
        works = []
        
        for item in items:
            title = item.get("dc:title", "Sin título")
            year_str = item.get("prism:coverDate", "")[:4]
            doi = item.get("prism:doi", None)
            revista = item.get("prism:publicationName", "")
            autores = item.get("dc:creator", "")
            
            try:
                year = int(year_str) if year_str else None
            except:
                year = None
            
            works.append({
                "titulo": title,
                "año": year,
                "doi": doi,
                "revista": revista,
                "autores": autores,
                "fuente": "Scopus"
            })
        
        return works
    
    # ==========================================
    # 3. PUBMED API
    # ==========================================
    def obtener_publicaciones_pubmed(self):
        """Obtiene publicaciones de PubMed"""
        if not self.pubmed_query:
            raise ValueError("No tienes configurada tu búsqueda de PubMed. Agrégala en tu perfil.")
        
        # 1. Buscar PMIDs del autor
        search_url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term={self.pubmed_query}&retmode=json"
        
        r = requests.get(search_url, timeout=30)
        if r.status_code != 200:
            raise ValueError(f"Error al conectar con PubMed (código {r.status_code})")
        
        pmids = r.json().get("esearchresult", {}).get("idlist", [])
        if not pmids:
            return []
        
        # 2. Obtener detalles de los artículos
        fetch_url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id={','.join(pmids)}&retmode=xml"
        
        r2 = requests.get(fetch_url, timeout=30)
        if r2.status_code != 200:
            raise ValueError("Error al obtener detalles de PubMed")
        
        root = ET.fromstring(r2.text)
        
        works = []
        for article in root.findall(".//PubmedArticle"):
            title = article.findtext(".//ArticleTitle", "Sin título")
            year_str = article.findtext(".//PubDate/Year", "")
            revista = article.findtext(".//Journal/Title", "")
            
            doi = None
            for aid in article.findall(".//ArticleId"):
                if aid.get("IdType") == "doi":
                    doi = aid.text
                    break
            
            try:
                year = int(year_str) if year_str else None
            except:
                year = None
            
            works.append({
                "titulo": title,
                "año": year,
                "doi": doi,
                "revista": revista,
                "fuente": "PubMed"
            })
        
        return works
    
    # ==========================================
    # OBTENER TODAS
    # ==========================================
    def obtener_todas_publicaciones(self):
        """Obtiene publicaciones de todas las fuentes configuradas"""
        resultados = {
            'orcid': [],
            'scopus': [],
            'pubmed': [],
            'errores': []
        }
        
        # ORCID
        if self.orcid_id:
            try:
                resultados['orcid'] = self.obtener_publicaciones_orcid()
            except Exception as e:
                resultados['errores'].append(f"ORCID: {str(e)}")
        
        # Scopus
        if self.scopus_author_id and self.scopus_api_key:
            try:
                resultados['scopus'] = self.obtener_publicaciones_scopus()
            except Exception as e:
                resultados['errores'].append(f"Scopus: {str(e)}")
        
        # PubMed
        if self.pubmed_query:
            try:
                resultados['pubmed'] = self.obtener_publicaciones_pubmed()
            except Exception as e:
                resultados['errores'].append(f"PubMed: {str(e)}")
        
        return resultados

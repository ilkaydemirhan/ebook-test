import streamlit as st
import requests

# 1. Google Books API Arama Fonksiyonu
def search_google_books(query):
    url = f"https://www.googleapis.com/books/v1/volumes?q={query}&maxResults=3"
    try:
        response = requests.get(url, timeout=5)
        results = []
        if response.status_code == 200:
            data = response.json()
            for item in data.get("items", []):
                info = item.get("volumeInfo", {})
                results.append({
                    "title": info.get("title", "Başlık Belirtilmemiş"),
                    "author": ", ".join(info.get("authors", ["Bilinmeyen Yazar"])),
                    "page_count": info.get("pageCount", "Bilinmiyor"),
                    "source": "Google Books"
                })
        return results
    except Exception:
        return []

# 2. Open Library API Arama Fonksiyonu
def search_open_library(query):
    url = f"https://openlibrary.org/search.json?q={query}&limit=3"
    try:
        response = requests.get(url, timeout=5)
        results = []
        if response.status_code == 200:
            data = response.json()
            for item in data.get("docs", []):
                authors = item.get("author_name", ["Bilinmeyen Yazar"])
                results.append({
                    "title": item.get("title", "Başlık Belirtilmemiş"),
                    "author": ", ".join(authors) if isinstance(authors, list) else authors,
                    "page_count": item.get("number_of_pages_median", "Bilinmiyor"),
                    "source": "Open Library"
                })
        return results
    except Exception:
        return []

# 3. Project Gutenberg (Gutendex API) Arama Fonksiyonu
def search_gutenberg(query):
    url = f"https://gutendex.com/books/?search={query}"
    try:
        response = requests.get(url, timeout=5)
        results = []
        if response.status_code == 200:
            data = response.json()
            for item in data.get("results", [])[:3]:
                authors = [a.get("name", "") for a in item.get("authors", [])]
                results.append({
                    "title": item.get("title", "Başlık Belirtilmemiş"),
                    "author": ", ".join(authors) if authors else "Bilinmeyen Yazar",
                    "page_count": "Bilinmiyor (Gutenberg metin bazlıdır)",
                    "source": "Project Gutenberg"
                })
        return results
    except Exception:
        return []

# --- STREAMLIT ARAYÜZÜ ---
st.set_page_config(page_title="E-Kitap Arama Motoru", page_icon="📚")
st.title("📚 Küresel E-Kitap Arama Motoru")
st.caption("Google Books, Open Library ve Project Gutenberg üzerinde eş zamanlı arama yapın.")

query = st.text_input("Aramak istediğiniz kitap adı, yazar veya konuyu yazın (Türkçe, Arapça, İngilizce):")

if query:
    with st.spinner("Tüm kütüphaneler taranıyor..."):
        # Üç kaynaktan verileri çekip birleştirme
        google_results = search_google_books(query)
        openlib_results = search_open_library(query)
        gutenberg_results = search_gutenberg(query)
        
        all_results = google_results + openlib_results + gutenberg_results

    st.subheader(f"Arama Sonuçları ({len(all_results)} sonuç bulundu)")
    
    if all_results:
        for book in all_results:
            with st.container():
                st.markdown(f"### 📖 {book['title']}")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.write(f"**Yazar:** {book['author']}")
                with col2:
                    st.write(f"**Sayfa Sayısı:** {book['page_count']}")
                with col3:
                    st.write(f"**Kaynak:** `{book['source']}`")
                st.divider()
    else:
        st.warning("Hiçbir kütüphanede eşleşen sonuç bulunamadı.")

import streamlit as st
import requests

# 1. Google Books API
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
                    "link": info.get("previewLink") or info.get("infoLink"),
                    "link_text": "📖 Google Books'ta Oku / İncele",
                    "source": "Google Books"
                })
        return results
    except Exception:
        return []

# 2. Open Library API
def search_open_library(query):
    url = f"https://openlibrary.org/search.json?q={query}&limit=3"
    try:
        response = requests.get(url, timeout=5)
        results = []
        if response.status_code == 200:
            data = response.json()
            for item in data.get("docs", []):
                authors = item.get("author_name", ["Bilinmeyen Yazar"])
                key = item.get("key", "")
                link = f"https://openlibrary.org{key}" if key else None
                results.append({
                    "title": item.get("title", "Başlık Belirtilmemiş"),
                    "author": ", ".join(authors) if isinstance(authors, list) else authors,
                    "page_count": item.get("number_of_pages_median", "Bilinmiyor"),
                    "link": link,
                    "link_text": "📖 Open Library'de Oku",
                    "source": "Open Library"
                })
        return results
    except Exception:
        return []

# 3. Project Gutenberg (Gutendex API)
def search_gutenberg(query):
    url = f"https://gutendex.com/books/?search={query}"
    try:
        response = requests.get(url, timeout=5)
        results = []
        if response.status_code == 200:
            data = response.json()
            for item in data.get("results", [])[:3]:
                authors = [a.get("name", "") for a in item.get("authors", [])]
                formats = item.get("formats", {})
                
                # İndirme bağlantılarını öncelik sırasına göre seçme (EPUB, HTML, Text)
                download_link = (
                    formats.get("application/epub+zip") or 
                    formats.get("text/html") or 
                    formats.get("text/plain; charset=us-ascii")
                )
                
                results.append({
                    "title": item.get("title", "Başlık Belirtilmemiş"),
                    "author": ", ".join(authors) if authors else "Bilinmeyen Yazar",
                    "page_count": "Bilinmiyor (Düz Metin)",
                    "link": download_link,
                    "link_text": "⬇️ Ücretsiz İndir (EPUB / HTML)",
                    "source": "Project Gutenberg"
                })
        return results
    except Exception:
        return []

# --- STREAMLIT ARAYÜZÜ ---
st.set_page_config(page_title="E-Kitap Arama Motoru", page_icon="📚")
st.title("📚 Küresel E-Kitap Arama Motoru")
st.caption("Google Books, Open Library ve Project Gutenberg üzerinde arama yapın ve indirin.")

query = st.text_input("Kitap adı, yazar veya konu girin (TR, AR, EN):")

if query:
    with st.spinner("Kütüphaneler taranıyor..."):
        all_results = (
            search_google_books(query) + 
            search_open_library(query) + 
            search_gutenberg(query)
        )

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
                
                # Okuma / İndirme Bağlantısı
                if book['link']:
                    st.link_button(book['link_text'], book['link'])
                else:
                    st.caption("⚠️ Bu kitap için doğrudan erişim bağlantısı bulunamadı.")
                
                st.divider()
    else:
        st.warning("Eşleşen bir sonuç bulunamadı.")

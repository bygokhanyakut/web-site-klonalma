import os
import requests
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
import curses
import time

def download_file(url, folder, stdscr):
    """Belirtilen URL'den dosya indir ve belirtilen klasöre kaydet, ilerleme çubuğu ile."""
    try:
        local_filename = os.path.join(folder, os.path.basename(url))
        with requests.get(url, stream=True) as r:
            r.raise_for_status()  # HTTP hatalarını kontrol et
            total_size = int(r.headers.get('content-length', 0))
            with open(local_filename, 'wb') as f:
                downloaded = 0
                # İlerleme çubuğunu göster
                while True:
                    chunk = r.raw.read(8192)
                    if not chunk:
                        break
                    f.write(chunk)
                    downloaded += len(chunk)
                    progress = int(downloaded / total_size * 100) if total_size else 100
                    
                    # Curses ile ilerlemeyi güncelle
                    stdscr.addstr(8, (curses.COLS - 30) // 2, f"İndiriliyor: {os.path.basename(url)}: [{progress}%]", curses.color_pair(2) | curses.A_BOLD)
                    stdscr.addstr(9, (curses.COLS - 30) // 2, "#" * (progress // 2) + "-" * (50 - progress // 2))
                    stdscr.refresh()
                    time.sleep(0.1)  # Demo için gecikme simülasyonu

        return local_filename
    except Exception as e:
        return f"Hata: {e}"

def clone_website(url, stdscr):
    """Belirtilen web sitesini klonla ve içeriği yerel olarak kaydet."""
    parsed_url = urlparse(url)
    base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
    
    folder_name = parsed_url.netloc.replace('.', '_')
    os.makedirs(folder_name, exist_ok=True)

    css_folder = os.path.join(folder_name, 'css')
    js_folder = os.path.join(folder_name, 'js')
    os.makedirs(css_folder, exist_ok=True)
    os.makedirs(js_folder, exist_ok=True)

    try:
        response = requests.get(url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        # CSS ve JavaScript dosyalarını indir
        for link in soup.find_all(['link', 'script']):
            if link.name == 'link' and link.get('href'):
                href = link['href']
                full_url = urljoin(base_url, href)
                local_css_path = download_file(full_url, css_folder, stdscr)
                if not local_css_path.startswith("Hata"):
                    link['href'] = os.path.join('css', os.path.basename(local_css_path))  # Bağlantıyı güncelle
            elif link.name == 'script' and link.get('src'):
                src = link['src']
                full_url = urljoin(base_url, src)
                local_js_path = download_file(full_url, js_folder, stdscr)
                if not local_js_path.startswith("Hata"):
                    link['src'] = os.path.join('js', os.path.basename(local_js_path))  # Bağlantıyı güncelle

        # Ana sayfayı kaydet
        html_file_path = os.path.join(folder_name, 'index.html')
        with open(html_file_path, 'w', encoding='utf-8') as f:
            f.write(str(soup))  # Güncellenmiş HTML içeriğini yaz

        return f"Klonlama tamamlandı! İçerikler '{folder_name}' klasöründe kaydedildi."
        
    except requests.exceptions.RequestException as e:
        return f"HTTP Hatası: {str(e)}"
    except Exception as e:
        return f"Beklenmeyen hata: {str(e)}"

def draw_header(stdscr):
    """Başlığı çiz ve ortala."""
    header_text = "== WEB SİTESİ KLONLAMA ARACI == "
    y, x = stdscr.getmaxyx()  # Terminal boyutunu al
    stdscr.addstr(1, (x - len(header_text)) // 2, header_text, curses.color_pair(1) | curses.A_BOLD | curses.A_UNDERLINE)

def draw_social_media(stdscr):
    """Sosyal medya bağlantılarını çiz ve ortala."""
    stdscr.addstr(10, (curses.COLS - len("Sosyal Medya Hesaplarım:")) // 2, "Sosyal Medya Hesaplarım:", curses.color_pair(3) | curses.A_BOLD)
    social_links = [
        ("Instagram:", "https://instagram.com/Gokhan_yakut_04"),
        ("Twitter:", "https://twitter.com/bygokhanYakut"),
        ("YouTube:", "https://www.youtube.com/@byGokhanYakut"),
        ("WhatsApp:", "https://wa.me/+447833319922"),
        ("GitHub:", "https://github.com/bygokhanyakut"),
    ]
    
    for idx, (platform, link) in enumerate(social_links):
        link_text = f"{platform} {link}"
        stdscr.addstr(11 + idx, (curses.COLS - len(link_text)) // 2, link_text, curses.color_pair(5) | curses.A_BOLD | curses.A_UNDERLINE)

def draw_footer(stdscr):
    """Alt bilgiyi çiz ve ortala."""
    footer_text = "Bu web sitesi Gokhan Yakut tarafından yazılmıştır. Siber güvenlik & Yazılım Geliştiricisi."
    y, x = stdscr.getmaxyx()  # Terminal boyutunu al
    stdscr.addstr(y - 2, (x - len(footer_text)) // 2, footer_text, curses.color_pair(6) | curses.A_BOLD)

def draw_kurdish_footer(stdscr):
    """Kürtçe alt bilgiyi çiz ve ortala."""
    footer_text_kurdish = "Ev malper ji aliyê Gökhan Yakut ve hatiye nivîsandin. Pêşvebirê Ewlekariya Sîber û Nermalavê."
    y, x = stdscr.getmaxyx()  # Terminal boyutunu al
    stdscr.addstr(y - 1, (x - len(footer_text_kurdish)) // 2, footer_text_kurdish, curses.color_pair(6) | curses.A_BOLD)

def main(stdscr):
    curses.curs_set(0)  # İmleci gizle
    stdscr.clear()
    
    # Renk tanımlamaları
    curses.start_color()
    curses.init_pair(1, curses.COLOR_YELLOW, curses.COLOR_BLACK)  # Başlık rengi
    curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_BLACK)   # Metin rengi
    curses.init_pair(3, curses.COLOR_CYAN, curses.COLOR_BLACK)    # Sosyal medya başlık rengi
    curses.init_pair(4, curses.COLOR_GREEN, curses.COLOR_BLACK)    # Bekleme mesajı rengi
    curses.init_pair(5, curses.COLOR_MAGENTA, curses.COLOR_BLACK)   # Bağlantı rengi
    curses.init_pair(6, curses.COLOR_BLUE, curses.COLOR_BLACK)      # Önemli mesaj rengi
    curses.init_pair(7, curses.COLOR_RED, curses.COLOR_BLACK)       # Hata mesajı rengi

    draw_header(stdscr)
    stdscr.addstr(4, (curses.COLS - len("Klonlamak istediğiniz URL'yi girin:")) // 2, "Klonlamak istediğiniz URL'yi girin:", curses.color_pair(2) | curses.A_BOLD)

    # URL için kullanıcıdan giriş al
    stdscr.addstr(6, (curses.COLS - len("URL: ")) // 2, "URL: ", curses.color_pair(2) | curses.A_BOLD)
    curses.echo()
    url = stdscr.getstr(6, (curses.COLS - len("URL: ")) // 2 + 5, 50).decode('utf-8')
    curses.noecho()
    
    # Bekleme mesajını göster
    stdscr.clear()
    draw_header(stdscr)
    stdscr.addstr(4, (curses.COLS - len("Lütfen bekleyin, web sitesi klonlanıyor...")) // 2, "Lütfen bekleyin, web sitesi klonlanıyor...", curses.color_pair(4) | curses.A_BOLD | curses.A_UNDERLINE)
    stdscr.refresh()
    time.sleep(2)  # Bekleme süresi (2 saniye)

    result = clone_website(url, stdscr)

    # Sonuçları göster
    stdscr.clear()
    draw_header(stdscr)
    if "Hata" in result:
        stdscr.addstr(6, (curses.COLS - len(result)) // 2, result, curses.color_pair(7) | curses.A_BOLD)  # Hata mesajı
    else:
        stdscr.addstr(6, (curses.COLS - len(result)) // 2, result, curses.color_pair(2) | curses.A_BOLD)  # Başarı mesajı

    draw_social_media(stdscr)
    draw_footer(stdscr)
    draw_kurdish_footer(stdscr)

    stdscr.refresh()
    stdscr.getch()  # Kullanıcıdan bir tuşa basmasını bekle

if __name__ == "__main__":
    curses.wrapper(main)

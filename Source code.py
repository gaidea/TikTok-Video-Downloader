import customtkinter as ctk
import requests
import os
import random
from PIL import Image, ImageTk
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

root = ctk.CTk()
root.geometry("500x550")
root.title("TikTok Video Downloader")
root.resizable(False, False)
root.attributes("-alpha", 0.95)
root.overrideredirect(True)
root.configure(bg="black")

def start_move(event):
    root.x = event.x
    root.y = event.y

def stop_move(event):
    root.x = None
    root.y = None

def do_move(event):
    x = root.winfo_x() + (event.x - root.x)
    y = root.winfo_y() + (event.y - root.y)
    root.geometry(f"+{x}+{y}")

root.bind("<ButtonPress-1>", start_move)
root.bind("<ButtonRelease-1>", stop_move)
root.bind("<B1-Motion>", do_move)

background_path = "https://raw.githubusercontent.com/gaidea/TikTok-Video-Downloader/refs/heads/main/tiktok_logo.ico"
if os.path.exists(background_path):
    bg_image = Image.open(background_path)
    bg_image = bg_image.resize((120, 120), Image.Resampling.LANCZOS)
    bg_photo = ImageTk.PhotoImage(bg_image)
    bg_label = ctk.CTkLabel(root, image=bg_photo, text="")
    bg_label.place(relx=0.5, rely=0.15, anchor="center")

def close_app():
    root.destroy()

close_button = ctk.CTkButton(root, text="×", fg_color="red", text_color="white",
                             font=("Arial", 16, "bold"), corner_radius=20, command=close_app, width=40)
close_button.place(x=450, y=10)

label = ctk.CTkLabel(root, text="TikTok Video Downloader", font=("Arial", 22, "bold"), text_color="white")
label.pack(pady=60)

keyword_entry = ctk.CTkEntry(root, placeholder_text="Enter keyword", width=300, corner_radius=20)
keyword_entry.pack(pady=10)

video_count_entry = ctk.CTkEntry(root, placeholder_text="Number of videos to download?", width=300, corner_radius=20)
video_count_entry.pack(pady=10)

filter_var = ctk.StringVar(value="latest")
filter_frame = ctk.CTkFrame(root, corner_radius=20)
filter_frame.pack(pady=10)
latest_filter = ctk.CTkRadioButton(filter_frame, text="Latest", variable=filter_var, value="latest",
                                   corner_radius=15, font=("Arial", 14))
latest_filter.pack(side="left", padx=10)
popular_filter = ctk.CTkRadioButton(filter_frame, text="Popular", variable=filter_var, value="popular",
                                    corner_radius=15, font=("Arial", 14))
popular_filter.pack(side="left", padx=10)

progress_bar = ctk.CTkProgressBar(root, width=300, corner_radius=20)
progress_bar.pack(pady=20)
progress_bar.set(0)

def update_progress(value):
    progress_bar.set(value / 100)
    root.update_idletasks()

def download_video(url, filename):
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        os.makedirs("downloads", exist_ok=True)
        file_path = os.path.join("downloads", filename)
        with open(file_path, "wb") as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
        print(f"✅ Video downloaded successfully: {file_path}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Download error: {e}")

def download_tiktok_videos():
    try:
        num_videos = int(video_count_entry.get())
        search_keyword = keyword_entry.get().replace(" ", "%20")
        filter_option = filter_var.get()
    except ValueError:
        print("❌ Please enter a valid number!")
        return
    
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-blink-features=AutomationControlled")
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    try:
        search_url = f"https://www.tiktok.com/search?q={search_keyword}{'&sort=popularity' if filter_option == 'popular' else '&sort=latest'}"
        driver.get(search_url)
        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR, "a[href*='/video/']")))
        
        videos = driver.find_elements(By.CSS_SELECTOR, "a[href*='/video/']")
        video_links = [video.get_attribute("href") for video in videos]
        if not video_links:
            print("❌ No videos found!")
            return
        
        for i in range(min(num_videos, len(video_links))):
            update_progress((i + 1) / num_videos * 100)
            video_link = random.choice(video_links)
            print(f"🎬 {i+1}. Video: {video_link}")
            
            driver.get("https://snaptik.app/")
            WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.ID, "url")))
            
            input_box = driver.find_element(By.ID, "url")
            input_box.send_keys(video_link)
            input_box.send_keys(Keys.RETURN)
            
            try:
                WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR, "a.download-link, .download a")))
                download_button = driver.find_element(By.CSS_SELECTOR, "a.download-link, .download a")
                download_url = download_button.get_attribute("href")
                print(f"✅ Download Link: {download_url}")
                
                download_video(download_url, f"tiktok_edit_{i+1}.mp4")
            except Exception as e:
                print(f"⚠ Download error: {e}")
        
        update_progress(100)
        
    finally:
        driver.quit()
        update_progress(0)

download_button = ctk.CTkButton(root, text="Download Videos", fg_color="#1abc9c", hover_color="#16a085",
                                font=("Arial", 16, "bold"), corner_radius=20, command=download_tiktok_videos)
download_button.pack(pady=20)

root.mainloop()

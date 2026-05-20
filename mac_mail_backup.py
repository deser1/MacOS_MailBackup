import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import imaplib
import email
from email.policy import default
import os
import threading
import shutil
from datetime import datetime

class MailBackupApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Kopia Zapasowa E-mail (macOS -> QNAP)")
        self.root.geometry("600x550")
        self.root.configure(padx=10, pady=10)

        # --- Zakładki (Tabs) ---
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill="both", expand=True, pady=5)

        # Tab 1: IMAP
        self.tab_imap = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_imap, text="Kopia IMAP (Zalecane)")

        frame_server = tk.LabelFrame(self.tab_imap, text="Dane konta pocztowego", padx=10, pady=10)
        frame_server.pack(fill="x", pady=10, padx=10)

        tk.Label(frame_server, text="Serwer IMAP:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.server_entry = tk.Entry(frame_server, width=35)
        self.server_entry.grid(row=0, column=1, padx=5, pady=5)
        self.server_entry.insert(0, "imap.gmail.com")

        tk.Label(frame_server, text="Adres e-mail:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.email_entry = tk.Entry(frame_server, width=35)
        self.email_entry.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(frame_server, text="Hasło (np. aplikacji):").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.password_entry = tk.Entry(frame_server, width=35, show="*")
        self.password_entry.grid(row=2, column=1, padx=5, pady=5)

        # Tab 2: Local Files
        self.tab_local = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_local, text="Pliki Lokalne (Apple Mail)")

        frame_local = tk.LabelFrame(self.tab_local, text="Wybierz folder źródłowy", padx=10, pady=10)
        frame_local.pack(fill="x", pady=10, padx=10)

        tk.Label(frame_local, text="Katalog Mail:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.source_var = tk.StringVar()
        self.source_var.set(os.path.expanduser("~/Library/Mail"))
        self.source_entry = tk.Entry(frame_local, textvariable=self.source_var, width=25)
        self.source_entry.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        tk.Button(frame_local, text="Przeglądaj...", command=self.browse_source).grid(row=0, column=2, sticky="e")

        tk.Label(frame_local, text="UWAGA: Wyszukiwanie lokalne może trwać bardzo długo.\nMoże być wymagane nadanie uprawnień 'Pełny dostęp do dysku'.",
                 fg="red", justify="left", font=("Arial", 8)).grid(row=1, column=0, columnspan=3, pady=5)

        # --- Wspólne Ustawienia (Common Settings) ---
        frame_settings = tk.LabelFrame(root, text="Ustawienia docelowe i filtry", padx=10, pady=10)
        frame_settings.pack(fill="x", pady=5)

        tk.Label(frame_settings, text="Filtruj domenę (np. @example.com):").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.domain_entry = tk.Entry(frame_settings, width=35)
        self.domain_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(frame_settings, text="Folder docelowy (QNAP):").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.dest_var = tk.StringVar()
        self.dest_entry = tk.Entry(frame_settings, textvariable=self.dest_var, width=25)
        self.dest_entry.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        tk.Button(frame_settings, text="Przeglądaj...", command=self.browse_dest).grid(row=1, column=2, sticky="e")

        # --- Pasek Postępu i Status ---
        self.status_var = tk.StringVar()
        self.status_var.set("Gotowy do rozpoczęcia.")
        tk.Label(root, textvariable=self.status_var, fg="#333333", font=("Arial", 10, "italic")).pack(pady=5)

        self.progress = ttk.Progressbar(root, orient="horizontal", length=550, mode="determinate")
        self.progress.pack(pady=5)

        # --- Przycisk Start ---
        self.start_btn = tk.Button(root, text="Uruchom Kopię Zapasową", command=self.start_backup_thread,
                                   bg="#007BFF", fg="black", font=("Arial", 12, "bold"), pady=5)
        self.start_btn.pack(pady=10)

    def browse_source(self):
        folder = filedialog.askdirectory(initialdir=os.path.expanduser("~/Library/Mail"), title="Wybierz folder źródłowy")
        if folder:
            self.source_var.set(folder)

    def browse_dest(self):
        folder = filedialog.askdirectory(initialdir="/Volumes", title="Wybierz zamontowany folder QNAP")
        if folder:
            self.dest_var.set(folder)

    def start_backup_thread(self):
        if not self.dest_var.get():
            messagebox.showerror("Błąd", "Wybierz folder docelowy na QNAP.")
            return

        active_tab = self.notebook.index(self.notebook.select())

        if active_tab == 0:  # IMAP
            if not self.email_entry.get() or not self.password_entry.get():
                messagebox.showerror("Błąd", "Wypełnij dane logowania IMAP (E-mail i Hasło).")
                return
            target_func = self.perform_imap_backup
        else:  # Local Files
            if not self.source_var.get() or not os.path.exists(self.source_var.get()):
                messagebox.showerror("Błąd", "Wskazany folder źródłowy nie istnieje.")
                return
            target_func = self.perform_local_backup

        self.start_btn.config(state=tk.DISABLED)
        self.progress['value'] = 0

        thread = threading.Thread(target=target_func)
        thread.daemon = True
        thread.start()

    def perform_imap_backup(self):
        mail = None
        try:
            mail = imaplib.IMAP4_SSL(self.server_entry.get())
            mail.login(self.email_entry.get(), self.password_entry.get())
            mail.select("inbox")

            domain = self.domain_entry.get().strip()
            if domain:
                search_criteria = f'(FROM "{domain}")'
            else:
                search_criteria = 'ALL'

            self.status_var.set(f"IMAP: Wyszukiwanie wiadomości wg kryteriów: {search_criteria}...")
            status, messages = mail.search(None, search_criteria)

            if status != "OK":
                raise Exception("Nie udało się przeszukać skrzynki pocztowej.")

            email_ids = messages[0].split()
            total_emails = len(email_ids)

            if total_emails == 0:
                self.status_var.set("IMAP: Brak wiadomości spełniających kryteria.")
                self.root.after(0, lambda: self.start_btn.config(state=tk.NORMAL))
                return

            self.progress['maximum'] = total_emails
            dest_dir = self.dest_var.get()

            for i, e_id in enumerate(email_ids):
                status, msg_data = mail.fetch(e_id, '(RFC822)')
                if status == "OK":
                    raw_email = msg_data[0][1]
                    msg = email.message_from_bytes(raw_email)

                    subject = str(msg.get("Subject", "Brak_Tematu"))
                    safe_subject = "".join([c for c in subject if c.isalpha() or c.isdigit() or c in ' -_']).rstrip()
                    date_str = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"imap_{date_str}_{safe_subject[:30]}_{i}.eml"
                    filepath = os.path.join(dest_dir, filename)

                    with open(filepath, "wb") as f:
                        f.write(raw_email)

                self.progress['value'] = i + 1
                self.status_var.set(f"IMAP: Zapisano {i+1} z {total_emails} wiadomości...")
                self.root.update_idletasks()

            self.status_var.set("Kopia IMAP zakończona sukcesem!")
            messagebox.showinfo("Sukces", f"Pomyślnie zapisano {total_emails} wiadomości przez IMAP.")

        except imaplib.IMAP4.error as e:
            self.status_var.set("Błąd logowania IMAP. Sprawdź e-mail/hasło.")
            messagebox.showerror("Błąd autoryzacji", f"Nie można zalogować się do IMAP:\n{str(e)}")
        except Exception as e:
            self.status_var.set("Wystąpił błąd podczas kopii IMAP!")
            messagebox.showerror("Błąd", str(e))
        finally:
            if mail:
                try:
                    mail.logout()
                except:
                    pass
            self.root.after(0, lambda: self.start_btn.config(state=tk.NORMAL))

    def perform_local_backup(self):
        try:
            self.status_var.set("Lokalnie: Skanowanie struktury plików (to może potrwać)...")
            self.root.update_idletasks()

            source_dir = self.source_var.get()
            dest_dir = self.dest_var.get()
            domain = self.domain_entry.get().strip().lower()

            email_files = []
            # Szukamy plików z rozszerzeniami eml oraz emlx
            for root_dir, dirs, files in os.walk(source_dir):
                for file in files:
                    if file.lower().endswith(('.eml', '.emlx')):
                        email_files.append(os.path.join(root_dir, file))

            total_files = len(email_files)
            if total_files == 0:
                self.status_var.set("Lokalnie: Nie znaleziono plików .eml lub .emlx we wskazanym folderze.")
                self.root.after(0, lambda: self.start_btn.config(state=tk.NORMAL))
                return

            self.progress['maximum'] = total_files
            saved_count = 0

            self.status_var.set(f"Znaleziono {total_files} plików e-mail. Rozpoczynam sprawdzanie nadawców...")
            self.root.update_idletasks()

            for i, filepath in enumerate(email_files):
                try:
                    with open(filepath, 'rb') as f:
                        # Czytamy plik do analizy nagłówków
                        msg = email.message_from_binary_file(f, policy=default)

                    from_header = str(msg.get("From", "")).lower()

                    # Sprawdzamy czy domena z filtra znajduje się w nadawcy
                    if domain == "" or domain in from_header:
                        subject = str(msg.get("Subject", "Brak_Tematu"))
                        safe_subject = "".join([c for c in subject if c.isalpha() or c.isdigit() or c in ' -_']).rstrip()
                        date_str = datetime.now().strftime("%Y%m%d_%H%M%S")
                        filename = f"local_{date_str}_{safe_subject[:30]}_{saved_count}.eml"
                        dest_path = os.path.join(dest_dir, filename)

                        # Kopiujemy plik
                        shutil.copy2(filepath, dest_path)
                        saved_count += 1

                except Exception:
                    # Ignorujemy pliki, których nie można odczytać (np. brak uprawnień systemowych)
                    pass

                # Aktualizacja GUI co 10 plików, aby nie zamrozić interfejsu przy tysiącach plików
                if i % 10 == 0 or i == total_files - 1:
                    self.progress['value'] = i + 1
                    self.status_var.set(f"Lokalnie: Przeskanowano {i+1} z {total_files} plików. Skopiowano: {saved_count}")
                    self.root.update_idletasks()

            self.status_var.set(f"Kopia lokalna zakończona! Skopiowano {saved_count} wiadomości.")
            messagebox.showinfo("Sukces", f"Przeskanowano plików: {total_files}\nZapisano pasujących wiadomości: {saved_count}")

        except Exception as e:
            self.status_var.set("Wystąpił błąd podczas kopii lokalnej!")
            messagebox.showerror("Błąd", str(e))
        finally:
            self.root.after(0, lambda: self.start_btn.config(state=tk.NORMAL))

if __name__ == "__main__":
    root = tk.Tk()
    app = MailBackupApp(root)
    root.mainloop()

# ============================================
# SECURE VAULT - Coffre-fort sécurisé
# Cryptographie - 8INF874
# Équipe 5 : Maha El Allem & Oum El Kheir Righi
# ============================================

import customtkinter as ctk
from tkinter import messagebox
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Protocol.KDF import PBKDF2
from PIL import Image
import base64, json, os, random, string, hashlib, time
from datetime import datetime

# ==================== CONFIGURATION ====================
ctk.set_appearance_mode("dark")
GREEN = "#73D74C"
RED = "#ef4444"
BG = "#0a0a0a"
CARD = "#1a1a1a"
CARD_LIGHT = "#262626"
VAULT_FILE = "vault.json"
HASH_FILE = "master.hash"
PERF_LOG = "performance.log"

# ==================== FONCTIONS CRYPTO ====================

def hash_master_password(password):
    """SHA-256 pour l'authentification - Résiste aux collisions"""
    return hashlib.sha256(password.encode()).hexdigest()

def derive_key(master_password, salt):
    """
    PBKDF2 - Dérivation de clé avec 100 000 itérations
    Résistance : Force brute (calcul coûteux)
    Résistance : Rainbow tables (sel unique)
    """
    return PBKDF2(master_password, salt, dkLen=32, count=100000)

def encrypt_password(master_password, plaintext):
    """
    AES-256-GCM - Chiffrement authentifié
    Confidentialité : AES-256 (clé 256 bits)
    Intégrité : GCM avec tag 128 bits
    """
    salt = get_random_bytes(16)      # Anti-rainbow tables
    nonce = get_random_bytes(12)     # Anti-replay attack
    key = derive_key(master_password, salt)
    
    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
    ciphertext, tag = cipher.encrypt_and_digest(plaintext.encode())
    
    return {
        "salt": base64.b64encode(salt).decode(),
        "nonce": base64.b64encode(nonce).decode(),
        "ciphertext": base64.b64encode(ciphertext).decode(),
        "tag": base64.b64encode(tag).decode(),
        "timestamp": datetime.now().isoformat()
    }

def decrypt_password(master_password, encrypted_data):
    """
    Déchiffrement avec vérification du tag
    Si tag invalide -> donnée corrompue ou modifiée
    """
    salt = base64.b64decode(encrypted_data["salt"])
    nonce = base64.b64decode(encrypted_data["nonce"])
    ciphertext = base64.b64decode(encrypted_data["ciphertext"])
    tag = base64.b64decode(encrypted_data["tag"])
    
    key = derive_key(master_password, salt)
    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
    
    plaintext = cipher.decrypt_and_verify(ciphertext, tag)
    return plaintext.decode()

def generate_password(length=16):
    """Générateur de mots de passe robustes (94 caractères possibles)"""
    chars = string.ascii_letters + string.digits + string.punctuation
    # string.punctuation = !"#$%&'()*+,-./:;<=>?@[\]^_`{|}~ (32 symboles)
    return ''.join(random.choice(chars) for _ in range(length))

# ==================== TESTS DE PERFORMANCE ====================

def test_performance():
    """
    Tests de performance pour démonstration
    Mesure les temps de chiffrement/déchiffrement
    """
    master = "test_password"
    data_sizes = [100, 1000, 10000]  # bytes
    
    results = []
    
    for size in data_sizes:
        test_data = "X" * size
        
        # Chiffrement
        start = time.time()
        encrypted = encrypt_password(master, test_data)
        enc_time = (time.time() - start) * 1000
        
        # Déchiffrement
        start = time.time()
        decrypted = decrypt_password(master, encrypted)
        dec_time = (time.time() - start) * 1000
        
        results.append({
            "size": size,
            "encrypt_ms": enc_time,
            "decrypt_ms": dec_time
        })
    
    # Log des performances
    with open(PERF_LOG, "w") as f:
        f.write(f"=== PERFORMANCE TEST ===\n")
        f.write(f"Date : {datetime.now()}\n\n")
        for r in results:
            f.write(f"Taille : {r['size']} bytes\n")
            f.write(f"Chiffrement : {r['encrypt_ms']:.2f} ms\n")
            f.write(f"Déchiffrement : {r['decrypt_ms']:.2f} ms\n\n")
    
    return results

# ==================== GESTION DU COFFRE ====================

def load_vault():
    if not os.path.exists(VAULT_FILE):
        return {}
    with open(VAULT_FILE, "r") as f:
        return json.load(f)

def save_vault(data):
    with open(VAULT_FILE, "w") as f:
        json.dump(data, f, indent=2)

def is_first_use():
    return not os.path.exists(HASH_FILE)

def get_vault_stats():
    """Statistiques du coffre"""
    vault = load_vault()
    total = sum(len(entries) for entries in vault.values())
    return {
        "total_passwords": total,
        "total_sites": len(vault),
        "last_backup": datetime.now().isoformat()
    }

# ==================== INTERFACE ====================

class App:
    def __init__(self):
        self.master = None
        self.logo_img = None
        self.bg_logo_label = None
        self.perf_results = None
        
        self.window = ctk.CTk()
        self.window.title("Secure Vault - Projet de Cryptographie 8INF874")
        self.window.geometry("1300x800")
        self.window.configure(fg_color=BG)
        
        # Charger logo
        for f in ["lo.png", "logo.png", "image.png"]:
            if os.path.exists(f):
                try:
                    self.logo_img = Image.open(f)
                    print("✅ Logo chargé")
                    break
                except:
                    pass
        
        # Ajouter fond d'écran avec logo
        self.add_background()
        
        # Exécuter les tests de performance au démarrage
        self.perf_results = test_performance()
        
        if is_first_use(): self.setup_screen()
        else: self.login_screen()
        self.window.mainloop()
    
    def add_background(self):
        """Ajoute le logo en arrière-plan"""
        if self.logo_img is None:
            print("Pas de logo pour le fond")
            return
        try:
            self.window.update_idletasks()
            w, h = self.window.winfo_width(), self.window.winfo_height()
            if w < 100: w, h = 1300, 800
            
            taille = min(w, h) - 100
            if taille < 100: taille = 500
                
            img = self.logo_img.resize((taille, taille), Image.Resampling.LANCZOS)
            bg = ctk.CTkImage(img, img, size=(taille, taille))
            self.bg_logo_label = ctk.CTkLabel(self.window, image=bg, text="")
            self.bg_logo_label.place(relx=0.5, rely=0.5, anchor="center")
            self.bg_logo_label.lower()
            print(f"✅ Fond ajouté (taille {taille})")
        except Exception as e:
            print(f"Fond logo erreur: {e}")
    
    def get_logo(self, size):
        if self.logo_img:
            try:
                img = self.logo_img.resize(size, Image.Resampling.LANCZOS)
                return ctk.CTkImage(img, img, size=size)
            except:
                pass
        return None
    
    def clear(self):
        for w in self.window.winfo_children():
            if w != self.bg_logo_label:
                w.destroy()
    
    def setup_screen(self):
        self.clear()
        f = ctk.CTkFrame(self.window, width=500, height=550, fg_color=CARD, corner_radius=20, border_width=1, border_color=GREEN)
        f.pack(expand=True)
        f.pack_propagate(False)
        
        logo = self.get_logo((110,110))
        if logo: ctk.CTkLabel(f, text="", image=logo).pack(pady=30)
        ctk.CTkLabel(f, text="SECURE VAULT", font=("Arial",28,"bold"), text_color=GREEN).pack()
        ctk.CTkLabel(f, text="Créez votre coffre-fort", font=("Arial",12), text_color="gray").pack(pady=(0,30))
        
        for txt in ["MOT DE PASSE MAÎTRE", "CONFIRMATION"]:
            ctk.CTkLabel(f, text=txt, font=("Arial",13,"bold")).pack(anchor="w", padx=50, pady=(15,5))
            e = ctk.CTkEntry(f, show="*", height=45, corner_radius=10, fg_color="#2a2a2a", border_color=GREEN)
            e.pack(fill="x", padx=50, pady=5)
            if txt == "MOT DE PASSE MAÎTRE": self.setup_master = e
            else: self.setup_confirm = e
        
        ctk.CTkButton(f, text="CRÉER LE COFFRE", command=self.create, height=50,
                     fg_color=GREEN, text_color="black", font=("Arial",14,"bold")).pack(pady=30, padx=50, fill="x")
    
    def create(self):
        if self.setup_master.get() != self.setup_confirm.get():
            messagebox.showerror("Erreur", "Les mots de passe ne correspondent pas")
            return
        if len(self.setup_master.get()) < 4:
            messagebox.showerror("Erreur", "Mot de passe trop court")
            return
        
        # ✅ MESSAGE D'AVERTISSEMENT
        result = messagebox.askyesno(
            "⚠️ ATTENTION - MOT DE PASSE MAÎTRE",
            "🔐 CONSERVEZ PRÉCIEUSEMENT CE MOT DE PASSE !\n\n"
            "• Il est stocké sous forme de hash (SHA-256)\n"
            "• Il n'est PAS récupérable si vous l'oubliez\n"
            "• Il protège TOUS vos mots de passe\n"
            "• Sans lui, vos données sont perdues à jamais\n\n"
            "✅ Avez-vous bien noté votre mot de passe ?"
        )
        
        if not result:
            return
        
        open(HASH_FILE, "w").write(hash_master_password(self.setup_master.get()))
        self.master = self.setup_master.get()
        messagebox.showinfo("Succès", "✅ Coffre créé avec succès !\n\n⚠️ N'oubliez pas votre mot de passe maître !")
        self.main_screen()
    
    def login_screen(self):
        self.clear()
        f = ctk.CTkFrame(self.window, width=450, height=450, fg_color=CARD, corner_radius=20, border_width=1, border_color=GREEN)
        f.pack(expand=True)
        f.pack_propagate(False)
        
        logo = self.get_logo((150,150))
        if logo: ctk.CTkLabel(f, text="", image=logo).pack(pady=30)
        ctk.CTkLabel(f, text="SECURE VAULT", font=("Arial",28,"bold"), text_color=GREEN).pack()
        ctk.CTkLabel(f, text="Déverrouillez votre coffre", font=("Arial",12), text_color="gray").pack(pady=(0,30))
        
        ctk.CTkLabel(f, text="MOT DE PASSE MAÎTRE", font=("Arial",13,"bold")).pack(anchor="w", padx=50, pady=(15,5))
        self.login_entry = ctk.CTkEntry(f, show="*", height=45, corner_radius=10, fg_color="#2a2a2a", border_color=GREEN)
        self.login_entry.pack(fill="x", padx=50, pady=5)
        self.login_entry.bind("<Return>", lambda e: self.login())
        ctk.CTkButton(f, text="DÉVERROUILLER", command=self.login, height=50,
                     fg_color=GREEN, text_color="black", font=("Arial",14,"bold")).pack(pady=30, padx=50, fill="x")
    
    def login(self):
        if not os.path.exists(HASH_FILE):
            messagebox.showerror("Erreur", "Aucun coffre trouvé")
            return
        if hash_master_password(self.login_entry.get()) == open(HASH_FILE).read():
            self.master = self.login_entry.get()
            self.main_screen()
        else:
            messagebox.showerror("Erreur", "Mot de passe incorrect")
    
    def main_screen(self):
        self.clear()
        
        # Sidebar
        side = ctk.CTkScrollableFrame(self.window, width=340, fg_color=CARD, corner_radius=15, border_width=1, border_color=GREEN)
        side.pack(side="left", fill="y", padx=10, pady=10)
        
        logo = self.get_logo((180,180))
        if logo: ctk.CTkLabel(side, text="", image=logo).pack(pady=20)
        ctk.CTkLabel(side, text="SECURE VAULT", font=("Arial",20,"bold"), text_color=GREEN).pack()
        ctk.CTkLabel(side, text="Coffre-fort sécurisé", font=("Arial",11), text_color="gray").pack()
        ctk.CTkFrame(side, height=1, fg_color=GREEN).pack(fill="x", padx=20, pady=10)
        
        # Algorithmes
        ctk.CTkLabel(side, text="ALGORITHMES", font=("Arial",13,"bold"), text_color=GREEN).pack(anchor="w", padx=20, pady=(10,5))
        for algo, desc in [("AES-256-GCM","Chiffrement + Intégrité"), ("PBKDF2","Dérivation (100k itérations)"), ("SHA-256","Hachage")]:
            c = ctk.CTkFrame(side, fg_color=CARD_LIGHT, corner_radius=8)
            c.pack(fill="x", padx=15, pady=3)
            ctk.CTkLabel(c, text=algo, font=("Arial",12,"bold"), text_color=GREEN).pack(anchor="w", padx=10, pady=(5,0))
            ctk.CTkLabel(c, text=desc, font=("Arial",10), text_color="gray").pack(anchor="w", padx=10, pady=(0,5))
        
        # Résistance
        ctk.CTkLabel(side, text="RÉSISTANCE AUX ATTAQUES", font=("Arial",13,"bold"), text_color=GREEN).pack(anchor="w", padx=20, pady=(15,5))
        for att, defs in [("Force brute","100k itérations PBKDF2"), ("Dictionnaire","Sel unique 16 bytes"), ("Rainbow tables","Sel + SHA-256"), ("Replay attack","Nonce 12 bytes"), ("Corruption","Tag GCM 128 bits")]:
            c = ctk.CTkFrame(side, fg_color=CARD_LIGHT, corner_radius=8)
            c.pack(fill="x", padx=15, pady=3)
            ctk.CTkLabel(c, text=f" {att}", font=("Arial",10,"bold"), text_color=GREEN).pack(anchor="w", padx=10, pady=(5,0))
            ctk.CTkLabel(c, text=f"🛡️ {defs}", font=("Arial",9), text_color="gray").pack(anchor="w", padx=10, pady=(0,5))
        
       
        
        ctk.CTkLabel(side, text=datetime.now().strftime("%d/%m/%Y %H:%M"), font=("Arial",9), text_color="gray").pack(pady=15)
        
        # Main area
        main = ctk.CTkFrame(self.window, fg_color="transparent")
        main.pack(side="left", fill="both", expand=True, padx=(0,10), pady=10)
        
        ctk.CTkLabel(main, text="MON COFFRE FORT", font=("Arial",28,"bold")).pack(anchor="w", padx=25, pady=(15,0))
        
        # Stats
        vault = load_vault()
        total = sum(len(e) for e in vault.values())
        stats = ctk.CTkFrame(main, fg_color="transparent")
        stats.pack(fill="x", padx=20, pady=15)
        for icon, title, val in [("🔒","MOTS DE PASSE",total), ("🌐","SITES",len(vault)), ("💾","DERNIÈRE",datetime.now().strftime("%d/%m/%Y"))]:
            c = ctk.CTkFrame(stats, fg_color=CARD_LIGHT, width=200, height=100, corner_radius=12, border_width=1, border_color=GREEN)
            c.pack(side="left", padx=8)
            c.pack_propagate(False)
            ctk.CTkLabel(c, text=icon, font=("Arial",28)).pack(pady=(10,0))
            ctk.CTkLabel(c, text=title, font=("Arial",10), text_color="gray").pack()
            ctk.CTkLabel(c, text=str(val), font=("Arial",24,"bold"), text_color=GREEN).pack()
        
        # Boutons
        btn_frame = ctk.CTkFrame(main, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=10)
        for txt, cmd in [("➕ AJOUTER",self.add_dialog), ("🔑 GÉNÉRATEUR",self.gen_dialog), ("📊 ANALYSE",self.analysis_dialog)]:
            ctk.CTkButton(btn_frame, text=txt, command=cmd, width=130, height=40,
                         fg_color="transparent", border_width=2, border_color=GREEN, text_color=GREEN,
                         font=("Arial",12,"bold")).pack(side="left", padx=6)
        ctk.CTkButton(btn_frame, text="🚪 QUITTER", command=self.window.destroy, width=130, height=40,
                     fg_color="transparent", border_width=2, border_color=RED, text_color=RED,
                     font=("Arial",12,"bold")).pack(side="left", padx=6)
        
        # Recherche
        search = ctk.CTkFrame(main, fg_color=CARD_LIGHT, corner_radius=10, border_width=1, border_color=GREEN)
        search.pack(fill="x", padx=20, pady=10)
        self.search_entry = ctk.CTkEntry(search, placeholder_text="Rechercher...", height=38, corner_radius=8, fg_color="#2a2a2a")
        self.search_entry.pack(side="left", padx=10, pady=8, fill="x", expand=True)
        self.search_entry.bind("<KeyRelease>", lambda e: self.refresh())
        ctk.CTkButton(search, text="🔍", width=50, height=38, fg_color=GREEN, text_color="black",
                     command=self.refresh).pack(side="right", padx=10, pady=8)
        
        # Liste des mots de passe
        self.list_frame = ctk.CTkScrollableFrame(main, fg_color=CARD, corner_radius=12, border_width=1, border_color=GREEN)
        self.list_frame.pack(fill="both", expand=True, padx=20, pady=(0,20))
        self.refresh()
    
    def refresh(self):
        for w in self.list_frame.winfo_children(): w.destroy()
        vault = load_vault()
        search = self.search_entry.get().lower() if hasattr(self, 'search_entry') else ""
        
        for site, entries in vault.items():
            if search and search not in site.lower(): continue
            site_frame = ctk.CTkFrame(self.list_frame, fg_color=CARD_LIGHT, corner_radius=8)
            site_frame.pack(fill="x", pady=(5,2), padx=5)
            ctk.CTkLabel(site_frame, text=f"📁 {site.upper()}", font=("Arial",13,"bold"), text_color=GREEN).pack(anchor="w", padx=15, pady=8)
            
            for idx, e in enumerate(entries):
                try:
                    pwd = decrypt_password(self.master, e["password"])
                    row = ctk.CTkFrame(self.list_frame, fg_color="transparent")
                    row.pack(fill="x", pady=2, padx=15)
                    
                    ctk.CTkLabel(row, text=f"👤 {e['username']}", width=180, anchor="w").pack(side="left", padx=10, pady=6)
                    
                    pwd_var = ctk.StringVar(value="••••••••••••••")
                    ctk.CTkLabel(row, textvariable=pwd_var, width=160, font=("Courier",11)).pack(side="left", padx=10)
                    
                    def make_show(var, pwd_data, username, site_name, idx_entry):
                        def show():
                            try:
                                decrypted = decrypt_password(self.master, pwd_data)
                                if var.get() == "••••••••••••••":
                                    var.set(decrypted)
                                else:
                                    var.set("••••••••••••••")
                            except Exception as err:
                                messagebox.showerror(
                                    "Erreur d'intégrité",
                                    f"❌ Données corrompues pour '{username}'\n\n"
                                    f"Le tag GCM ne correspond pas.\n"
                                    f"Le fichier vault.json a probablement été modifié manuellement."
                                )
                                v = load_vault()
                                v[site_name].pop(idx_entry)
                                if not v[site_name]: del v[site_name]
                                save_vault(v)
                                self.refresh()
                        return show
                    
                    ctk.CTkButton(row, text="👁", width=45, height=28, fg_color="transparent", border_width=1,
                                 border_color=GREEN, text_color=GREEN,
                                 command=make_show(pwd_var, e["password"], e['username'], site, idx)).pack(side="left", padx=3)
                    
                    def make_copy(t): return lambda: (self.window.clipboard_append(t), messagebox.showinfo("Copié", "Mot de passe copié"))
                    ctk.CTkButton(row, text="📋", width=45, height=28, fg_color="transparent", border_width=1,
                                 border_color=GREEN, text_color=GREEN, command=make_copy(pwd)).pack(side="left", padx=3)
                    
                    def make_del(s, i):
                        def delete():
                            if messagebox.askyesno("Supprimer", f"Supprimer {s} ?"):
                                v = load_vault()
                                v[s].pop(i)
                                if not v[s]: del v[s]
                                save_vault(v)
                                self.refresh()
                        return delete
                    ctk.CTkButton(row, text="🗑", width=45, height=28, fg_color="transparent", border_width=1,
                                 border_color=RED, text_color=RED, command=make_del(site, idx)).pack(side="right", padx=10)
                    
                except Exception as err:
                    error_frame = ctk.CTkFrame(self.list_frame, fg_color="#3c1a1a", corner_radius=8)
                    error_frame.pack(fill="x", pady=2, padx=15)
                    ctk.CTkLabel(
                        error_frame,
                        text=f"⚠️ {e['username']} - Données corrompues (tag invalide)",
                        text_color="#ff8888"
                    ).pack(side="left", padx=15, pady=8)
    
    def add_dialog(self):
        d = ctk.CTkToplevel(self.window)
        d.title("Ajouter")
        d.geometry("450x420")
        d.grab_set()
        d.update_idletasks()
        x = (d.winfo_screenwidth() - 450) // 2
        y = (d.winfo_screenheight() - 420) // 2
        d.geometry(f"450x420+{x}+{y}")
        
        f = ctk.CTkFrame(d, fg_color=CARD, corner_radius=15, border_width=1, border_color=GREEN)
        f.pack(pady=20, padx=20, fill="both", expand=True)
        ctk.CTkLabel(f, text="NOUVEAU MOT DE PASSE", font=("Arial",18,"bold"), text_color=GREEN).pack(pady=15)
        
        entries = {}
        for txt in ["Site / Service", "Nom d'utilisateur"]:
            ctk.CTkLabel(f, text=txt, font=("Arial",12,"bold")).pack(anchor="w", padx=20, pady=(10,0))
            e = ctk.CTkEntry(f, height=38, corner_radius=8, fg_color="#2a2a2a", border_color=GREEN)
            e.pack(fill="x", padx=20, pady=5)
            entries[txt] = e
        
        ctk.CTkLabel(f, text="Mot de passe", font=("Arial",12,"bold")).pack(anchor="w", padx=20, pady=(10,0))
        pwd_frame = ctk.CTkFrame(f, fg_color="transparent")
        pwd_frame.pack(fill="x", padx=20, pady=5)
        pwd_e = ctk.CTkEntry(pwd_frame, height=38, corner_radius=8, fg_color="#2a2a2a", border_color=GREEN)
        pwd_e.pack(side="left", fill="x", expand=True, padx=(0,5))
        ctk.CTkButton(pwd_frame, text="🔑", width=50, height=38, fg_color=GREEN, text_color="black",
                     command=lambda: (pwd_e.delete(0,"end"), pwd_e.insert(0, generate_password()))).pack(side="left")
        
        def save_entry():
            if not entries["Site / Service"].get() or not entries["Nom d'utilisateur"].get() or not pwd_e.get():
                messagebox.showerror("Erreur", "Tous les champs sont obligatoires")
                return
            v = load_vault()
            site = entries["Site / Service"].get()
            if site not in v: v[site] = []
            v[site].append({"username": entries["Nom d'utilisateur"].get(), "password": encrypt_password(self.master, pwd_e.get())})
            save_vault(v)
            self.refresh()
            d.destroy()
        
        ctk.CTkButton(f, text="💾 SAUVEGARDER", command=save_entry, height=40, fg_color=GREEN, text_color="black").pack(pady=20, padx=20, fill="x")
        ctk.CTkButton(f, text="ANNULER", command=d.destroy, height=35, fg_color="transparent", border_width=1, border_color=RED, text_color=RED).pack(pady=(0,15), padx=20, fill="x")
    
    def gen_dialog(self):
        d = ctk.CTkToplevel(self.window)
        d.title("Générateur")
        d.geometry("450x400")
        d.grab_set()
        d.update_idletasks()
        x = (d.winfo_screenwidth() - 450) // 2
        y = (d.winfo_screenheight() - 400) // 2
        d.geometry(f"450x400+{x}+{y}")
        
        f = ctk.CTkFrame(d, fg_color=CARD, corner_radius=15, border_width=1, border_color=GREEN)
        f.pack(pady=20, padx=20, fill="both", expand=True)
        ctk.CTkLabel(f, text="GÉNÉRATEUR", font=("Arial",20,"bold"), text_color=GREEN).pack(pady=15)
        
        pwd = ctk.CTkEntry(f, font=("Courier",18), height=50, corner_radius=8, fg_color="#2a2a2a")
        pwd.pack(fill="x", padx=20, pady=20)
        
        lbl = ctk.CTkLabel(f, text="Longueur : 16", font=("Arial",11))
        lbl.pack()
        
        def update(v):
            pwd.delete(0,"end")
            pwd.insert(0, generate_password(int(v)))
            lbl.configure(text=f"Longueur : {int(v)}")
        
        s = ctk.CTkSlider(f, from_=8, to=32, number_of_steps=24, command=update)
        s.set(16)
        s.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkButton(f, text="📋 COPIER", command=lambda: (self.window.clipboard_append(pwd.get()), messagebox.showinfo("Copié", "Mot de passe copié")),
                     height=40, fg_color=GREEN, text_color="black").pack(pady=15, padx=20, fill="x")
        pwd.insert(0, generate_password(16))
    
    def analysis_dialog(self):
        d = ctk.CTkToplevel(self.window)
        d.title("Analyse")
        d.geometry("650x520")
        d.grab_set()
        d.update_idletasks()
        x = (d.winfo_screenwidth() - 650) // 2
        y = (d.winfo_screenheight() - 520) // 2
        d.geometry(f"650x520+{x}+{y}")
        
        f = ctk.CTkFrame(d, fg_color=CARD, corner_radius=15, border_width=1, border_color=GREEN)
        f.pack(pady=20, padx=20, fill="both", expand=True)
        ctk.CTkLabel(f, text="ANALYSE DE SÉCURITÉ", font=("Arial",20,"bold"), text_color=GREEN).pack(pady=15)
        
        tab = ctk.CTkTabview(f, width=580, height=420)
        tab.pack(padx=20, pady=10)
        t1, t2, t3 = tab.add("🛡️ RÉSISTANCE"), tab.add("⚡ PERFORMANCES"), tab.add("⚠️ LIMITES")
        
        # Résistance
        ctk.CTkLabel(t1, text="RÉSISTANCE AUX ATTAQUES", font=("Arial",15,"bold"), text_color=GREEN).pack(pady=10)
        for a,d in [("Force brute","100k itérations PBKDF2 (0.1s/tentative)"), ("Dictionnaire","Sel unique de 16 bytes"), ("Rainbow tables","Sel + SHA-256"), ("Replay attack","Nonce unique 12 bytes"), ("Corruption","Tag GCM 128 bits")]:
            r = ctk.CTkFrame(t1, fg_color="#2a2a2a", corner_radius=8)
            r.pack(fill="x", padx=20, pady=4)
            ctk.CTkLabel(r, text=f"⚔️ {a}", font=("Arial",11,"bold"), width=140, text_color=GREEN).pack(side="left", padx=15, pady=6)
            ctk.CTkLabel(r, text=f"🛡️ {d}", font=("Arial",10), text_color="gray").pack(side="left", padx=15, pady=6)
        
        # Performances
        if self.perf_results:
            ctk.CTkLabel(t2, text="TESTS DE PERFORMANCE", font=("Arial",15,"bold"), text_color=GREEN).pack(pady=10)
            for r in self.perf_results:
                frame = ctk.CTkFrame(t2, fg_color="#2a2a2a", corner_radius=8)
                frame.pack(fill="x", padx=20, pady=5)
                ctk.CTkLabel(frame, text=f"📊 {r['size']} bytes", font=("Arial",12,"bold")).pack(anchor="w", padx=15, pady=5)
                ctk.CTkLabel(frame, text=f"⏱️ Chiffrement : {r['encrypt_ms']:.2f} ms", font=("Arial",11)).pack(anchor="w", padx=15)
                ctk.CTkLabel(frame, text=f"⏱️ Déchiffrement : {r['decrypt_ms']:.2f} ms", font=("Arial",11)).pack(anchor="w", padx=15, pady=(0,5))
        
        ctk.CTkLabel(t2, text="📊 AES-GCM est 2x plus rapide que AES-CBC+HMAC (1 passage au lieu de 2)", font=("Arial",11), text_color="gray").pack(pady=15)
        
        # Limites
        ctk.CTkLabel(t3, text="LIMITES IDENTIFIÉES", font=("Arial",15,"bold"), text_color=RED).pack(pady=10)
        for l,d in [("Authentification mono-facteur","Un seul mot de passe protège tout"), ("Perte irrécupérable","Master perdu = données perdues"), ("Machine compromise","Keylogger peut capturer le master")]:
            r = ctk.CTkFrame(t3, fg_color="#2a2a2a", corner_radius=8)
            r.pack(fill="x", padx=20, pady=4)
            ctk.CTkLabel(r, text=f"⚠️ {l}", font=("Arial",11,"bold"), width=220, text_color=RED).pack(side="left", padx=15, pady=6)
            ctk.CTkLabel(r, text=d, font=("Arial",10), text_color="gray").pack(side="left", padx=15, pady=6)
        ctk.CTkLabel(t3, text="🔧 Améliorations possibles : Argon2id, 2FA (TOTP), sauvegarde cloud chiffrée", font=("Arial",11), text_color="#3498db").pack(pady=15)
        
        ctk.CTkButton(f, text="FERMER", command=d.destroy, height=38, fg_color=GREEN, text_color="black").pack(pady=15, padx=20, fill="x")

App()

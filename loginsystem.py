import csv
import smtplib
import random
import string
import os
from tkinter import *
from tkinter import messagebox
import customtkinter 
from customtkinter import CTkButton
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart 
from PIL import Image, ImageTk
import customtkinter as ctk
import tkinter as tk
from ExpiryTracker import SmartGroceryTrackerUI

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Smart Grocery Expiry Tracker")
        self.geometry("600x400")
        self.resizable(False, False)
        ctk.set_appearance_mode("Dark")  

        self.image = customtkinter.CTkImage(light_image=Image.open("Tracker.png"),
                                            dark_image=Image.open("Tracker.png"), size=(600, 400))
        self.img_label = customtkinter.CTkLabel(master=self, image=self.image, text="")
        self.img_label.pack(side="left", padx=0, pady=0)

        self.overlay_button = ctk.CTkButton(master=self.img_label, text="Start Your App", bg_color= "#599fcc",
                                            font=("San Serif",18,"bold"), command=self.open_signup, 
                                            corner_radius=10, hover_color="green", text_color="white")
        self.overlay_button.place(relx=0.8, rely=0.48, anchor="center")
        
    def change_mode(self, mode):
        ctk.set_appearance_mode(mode)
           
    def show_signup(self):
        self.signin_frame.pack_forget()
        self.signup_frame.pack(fill="both", expand=True)    

    def show_signin(self):
        self.signup_frame.pack_forget()
        self.signin_frame.pack(fill="both", expand=True)

    def open_signup(self):
        for widget in self.winfo_children():
            widget.destroy()
        signup_frame = Signup(self)
        signup_frame.pack(fill="both", expand=True)
        
class Signup(ctk.CTkFrame):
    FILE_NAME = "users.csv"
    SENDER_EMAIL = "smartgrocerytracker@gmail.com"
    SENDER_PASSWORD = "gyaa oicw mfbj ypve" 
    SMTP_SERVER = "smtp.gmail.com"
    SMTP_PORT = 587


    def __init__(self, master):
        super().__init__(master)
        self.master = master

        self.container = customtkinter.CTkFrame(master=self, corner_radius=15, fg_color="#0f2440")
        self.container.pack(side="top", fill="both", expand=True, padx=20, pady=20)

        self.title_label = customtkinter.CTkLabel(master=self.container, text="Sign Up", font=("Sans Serif", 24, "bold"))
        self.image = customtkinter.CTkImage(light_image=Image.open("icon.png"),
                                dark_image=Image.open("icon.png"),
                                size=(270, 400)) 

        self.img_label = customtkinter.CTkLabel(master=self.container, image=self.image, text="")
        self.img_label.pack(side="left", padx=0, pady=0)

        self.frame = customtkinter.CTkFrame(master=self.container, corner_radius=15, fg_color="#0f2440")
        self.frame.pack(side="right", padx=20, pady=20, fill="both", expand=True)

        ctk.CTkLabel(self.frame, text="Sign Up", font=("Sans Serif", 28, "bold"), text_color="white").pack(pady=12)

        self.email_entry = customtkinter.CTkEntry(master=self.frame, placeholder_text="Email")
        self.email_entry.pack(pady=5, padx=15)

        self.username_entry = customtkinter.CTkEntry(master=self.frame, placeholder_text="Username")
        self.username_entry.pack(pady=5, padx=10)

        self.password_entry = customtkinter.CTkEntry(master=self.frame, placeholder_text="Password", show="*")
        self.password_entry.pack(pady=5, padx=10)

        self.confirm_password_entry = customtkinter.CTkEntry(master=self.frame, placeholder_text="Confirm Password", show="*")
        self.confirm_password_entry.pack(pady=5, padx=10)

        ctk.CTkButton(master=self.frame, text="Sign Up", font=("San Serif",14,"bold"), width=70, command=self.signup).pack(pady=10)

        ctk.CTkLabel(master=self.frame, text="Already have an account?", text_color="white").pack()

        self.overlay_button = ctk.CTkButton(master=self.frame, text="Go to Sign In", width=100,
                                            font=("San serif",14,"bold"), command=self.open_signin, 
                                            corner_radius=10, hover_color="green", text_color="white")
        self.overlay_button.place(relx=0.5, rely=0.93, anchor="center")

    def initialize_csv_file(self):
        if not os.path.exists(Signup.FILE_NAME):
            with open(Signup.FILE_NAME, mode="w", newline="") as file:
                writer = csv.writer(file)
                writer.writerow(["email", "username", "password"])
    def signup(self):
        self.email = self.email_entry.get()
        self.username = self.username_entry.get()
        self.password = self.password_entry.get()
        self.confirm_password = self.confirm_password_entry.get()

        self.initialize_csv_file()
        def __init__(self, parent):
            super().__init__(parent)

            self.email_entry = ctk.Entry(self)
            self.email_entry.pack()

            self.email = self.email_entry.get() 

        if self.email == "" or self.username == "" or self.password == "" or self.confirm_password == "":
            messagebox.showerror("😱 Attention!", "⚠️ Please make sure all fields are filled in! ✍️")
            return
        
        if os.path.exists(Signup.FILE_NAME):
            with open(Signup.FILE_NAME, mode="r", newline="") as file:
                reader = csv.reader(file)
                next(reader, None)
                for row in reader:
                    if row[0] == self.email_entry.get():
                        messagebox.showerror("😕 User Exists", "🔑 An account with this information already exists. Please sign in to continue.")
                        return
                    
        if self.password != self.confirm_password:
            messagebox.showerror("🔒 Password Mismatch", "The passwords entered do not match. Please verify and try again.")
            return
        
        with open(Signup.FILE_NAME, mode="a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow([self.email_entry.get(), self.username_entry.get(), self.password_entry.get()])
            messagebox.showinfo("✅ Registration Complete 🎉", "Your account has been created successfully! Welcome to SMART GROCERY EXPIRY TRACKER 🛒🥳")
            return

    def open_signin(self):
        for widget in self.winfo_children():
            widget.destroy()
        signup_frame = Signin(self)
        signup_frame.pack(fill="both", expand=True)
    
class Signin(ctk.CTkFrame):
    FILE_NAME = "users.csv"
    SENDER_EMAIL = "smartgrocerytracker@gmail.com"
    SENDER_PASSWORD = "gyaa oicw mfbj ypve" 
    SMTP_SERVER = "smtp.gmail.com"
    SMTP_PORT = 587
    def __init__(self, parent):
        super().__init__(parent)

        self.container = customtkinter.CTkFrame(master=self, corner_radius=15, fg_color="#0f2440")
        self.container.pack(side="top", fill="both", expand=True, padx=20, pady=20)

        self.image = customtkinter.CTkImage( dark_image=Image.open("icon.png"),
                                    size=(270, 400))

        self.img_label = customtkinter.CTkLabel(master=self.container, image=self.image, text="")
        self.img_label.pack(side="left", padx=0, pady=0)

        self.frame = customtkinter.CTkFrame(master=self.container, corner_radius=15, fg_color="#0f2440")
        self.frame.pack(side="right", padx=20, pady=20, fill="both", expand=True)

        self.my_label = customtkinter.CTkLabel(master=self.frame, text="Sign In",  font=("Sans Serif", 28, "bold"), text_color="white")
        self.my_label.pack(pady=10, padx=10)
        

        self.email_entry = customtkinter.CTkEntry(master=self.frame, placeholder_text="Email")
        self.email_entry.pack(pady=10, padx=15)

        self.password_entry = customtkinter.CTkEntry(master=self.frame, placeholder_text="Password", show="*")
        self.password_entry.pack(pady=10, padx=10)

        self.my_text = customtkinter.CTkLabel(master=self.frame, text="Forgot Password?", text_color="white")
        self.my_text.place(relx=0.2, rely=0.67, anchor=CENTER)

        self.overlay_button = ctk.CTkButton(master=self.frame, text="Forgot Password", width=100, 
                                            font=("San Serif",14,), command=self.forgot_password, 
                                            corner_radius=10, hover_color="green", text_color="white")
        self.overlay_button.place(relx=0.73, rely=0.67, anchor="center")

            
        self.overlay_button = ctk.CTkButton(master=self.frame, text="Login", 
                                            font=("San Serif",14,"bold"), command=self.login, 
                                            corner_radius=10, hover_color="green", text_color="white", width=70)
        self.overlay_button.place(relx=0.5, rely=0.52, anchor="center")

        self.overlay_button = ctk.CTkButton(master=self.img_label, text="Back", width=70,fg_color="blue",bg_color="white",
                                            font=("Times New Roman",18,"bold"), command=self.open_signup, 
                                            corner_radius=10, hover_color="green", text_color="white")
        self.overlay_button.place(relx=0.1, rely=0.03, anchor="center")
    def generate_temp_password(self):
        return ''.join(random.choices(string.ascii_letters + string.digits, k=8))

    def send_email(receiver_email, subject, body):
        try:
            msg = MIMEMultipart()
            msg["From"] = Signup.SENDER_EMAIL
            msg["To"] = receiver_email
            msg["Subject"] = subject
            msg.attach(MIMEText(body, "plain"))

            server = smtplib.SMTP(Signup.SMTP_SERVER, Signup.SMTP_PORT)
            server.starttls()
            server.login(Signup.SENDER_EMAIL, Signup.SENDER_PASSWORD)
            server.sendmail(Signup.SENDER_EMAIL, receiver_email, msg.as_string())
            server.quit()
            # messagebox.showinfo("Success", "An email has been sent to reset your password.")
        except smtplib.SMTPAuthenticationError:
            messagebox.showerror("Error", "Authentication failed. Check your email credentials.")
        except Exception as e:
            messagebox.showerror("Error", f"Error: {e}")
  
    def initialize_csv_file(self):
        if not os.path.exists(Signup.FILE_NAME):
            with open(Signup.FILE_NAME, mode="w", newline="") as file:
                writer = csv.writer(file)
                writer.writerow(["email", "username", "password"]) 

    def forgot_password(self):
        email = self.email_entry.get()
        
        if not os.path.exists(Signup.FILE_NAME):
            messagebox.showerror("Error", "User database not found. Please try again.")
            return
        
        users = []
        found = False
    
        with open(Signup.FILE_NAME, mode="r", newline="") as file:
            reader = csv.reader(file)
            headers = next(reader, None) 

            for row in reader:
                if len(row) >= 3 and row[0] == email:
                    temp_password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
                    
                    row[2] = temp_password
                    found = True
                    
                    try:
                        msg = MIMEMultipart()
                        msg["From"] = Signup.SENDER_EMAIL
                        msg["To"] = email
                        msg["Subject"] = "Password Reset"
                        body = f"Greeting, {row[1]}!\n\nYour new password is: {temp_password}. Please use this password to log in and update it for security reasons.\n\nBest regards,\nSMART GROCERY EXPIRY TRACKER"
                        msg.attach(MIMEText(body, "plain"))

                        server = smtplib.SMTP(Signup.SMTP_SERVER, Signup.SMTP_PORT)
                        server.starttls()
                        server.login(Signup.SENDER_EMAIL, Signup.SENDER_PASSWORD)
                        server.sendmail(Signup.SENDER_EMAIL, email, msg.as_string())
                        server.quit()
                        messagebox.showinfo("📧 The New Password Sent", "Your temporary password has been emailed! Please check your inbox and use it to log in. 📬 ")

                    except Exception as e:
                        messagebox.showerror("Error", f"Failed to send email: {e}")
                        
                users.append(row)
    
        if found:
            with open(Signup.FILE_NAME, mode="w", newline="") as file:
                writer = csv.writer(file)
                if headers:  
                    writer.writerow(headers)
                writer.writerows(users)  
        else:
            messagebox.showerror("❌ Email Not Found", "We couldn't locate that email address. Please verify and try again. 📧")

    def login(self):
        email = self.email_entry.get().strip()
        password = self.password_entry.get().strip()

        if email == "" or password == "":
            messagebox.showerror("⚠️ Missing Info", "📧🔒 Please enter your email and password to continue.")
            return

        with open(Signup.FILE_NAME, mode="r", newline="") as file:
            reader = csv.reader(file)
            next(reader, None) 

            for row in reader:
                if row[0].strip() == email and row[2].strip() == password:
                    messagebox.showinfo(
                        "🎉 Welcome Aboard! 🛒",
                        f"Hey {row[1]}! 👋\n\n"
                        "Welcome to Smart Grocery Expiry Tracker! 🥳\n"
                        "Let’s keep your pantry fresh and organized. ✅"
                    )

                    self.master.master.switch_to_expiry_tracker()  
                    return
                   
            messagebox.showerror("❗Error", "🚫Invalid email or password. Please try again 🔁")
            
    def open_signup(self):
        for widget in self.winfo_children():
            widget.destroy()
        signup_frame = Signup(self)
        signup_frame.pack(fill="both", expand=True)

# if __name__ == "__main__":
#     app = App()
#     app.mainloop()
    

from bs4 import BeautifulSoup
import os, requests, time, os, smtplib, schedule
from replit import db
from email.mime.multipart import MIMEMultipart 
from email.mime.text import MIMEText

# <div class="css-wi7uht">
# text: <span class="css-19l40in">
# date: <span class="css-1jm4vlb">

def scrape():
  url = "https://replit.com/community-hub"
  res = requests.get(url)
  soup = BeautifulSoup(res.text, 'html.parser')
  event = soup.find_all("div", class_="css-wi7uht")
  keys = db.keys()
  for e in event:
    present = False
    desc = e.find(class_="css-19l40in")
    date = e.find(class_="css-1jm4vlb")
    link = e.find("a")["href"]
    if desc == None or date == None:
      continue
    desc = desc.text
    date = date.text
    if "Replit Reps" in desc:
      break
    if "Machine Learning" in desc:
      for key in keys:
        if date == key:
          print("Already present, skipping...")
          present = True
      if present == False:
        db[date] = {"date": date, "description": desc, "link": link, "sent": False}
        print(f"{desc} added to db")
      else:
        continue

def sendMail(desc,date,link):
  template = ""
  with open("email_template.html", "r") as f:
    template = f.read()
  template = template.replace("{date}", date)
  template = template.replace("{desc}", desc)
  template = template.replace("{link}", link)
  server = os.environ.get("SMTP_SERVER")
  port = 587
  s = smtplib.SMTP(host = server, port = port)
  s.starttls()
  username = os.environ['mailUsername']
  password = os.environ['mailPassword']
  s.login(username, password)
  msg = MIMEMultipart()
  msg['To'] = os.environ['emailTo']
  msg['From'] = os.environ['emailFrom']
  msg['Subject'] = "New Replit Event!"
  msg.attach(MIMEText(template, 'html'))
  s.send_message(msg)
  del msg

def scrape_and_send():
  scrape()
  keys = db.keys()
  for key in keys:
    if db[key]["sent"] == False:
      sendMail(db[key]["description"], db[key]["date"], db[key]["link"])
      db[key]["sent"] = True
      
schedule.every().day.at("17:00").do(scrape_and_send)

if __name__ == "__main__":
  schedule.run_pending()
  time.sleep(5)
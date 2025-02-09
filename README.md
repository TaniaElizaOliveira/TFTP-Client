# 📡 TFTP Client - File Transfer Protocol Implementation
> A simple implementation of a TFTP (Trivial File Transfer Protocol) client for file transfer operations.

---

## 📌 Project Description
This project is an implementation of a **TFTP Client**, allowing basic file transfer operations (**GET** and **PUT**) between a local machine and a TFTP server. The project was developed in Python, using **sockets** for network communication.

---

## 🚀 Features
- ✅ Download files from a TFTP server (**GET**)
- ✅ Upload files to a TFTP server (**PUT**)
- ✅ Supports **octet** (binary) transfer mode
- ✅ Handles **error codes** and retransmissions
- ✅ Timeout handling for unreliable networks
- ✅ Uses **structured packet processing** (RFC 1350)

---

## 🛠️ Installation & Setup
### 1️⃣ Clone the Repository
```sh
git clone https://github.com/seu-usuario/TFTP-Client.git
cd TFTP-Client
```

### 2️⃣ Set Up a Virtual Environment (Recommended)
```sh
python3 -m venv venv
source venv/bin/activate  # On Linux/macOS
venv\Scripts\activate     # On Windows
```


---

## 📌 Usage

### 1️⃣ Start a TFTP Server (if needed)
To test locally, you need a TFTP server running. You can install `tftpd-hpa`:
```sh
sudo apt install tftpd-hpa -y
```
Then, configure your TFTP directory (e.g., `/var/lib/tftpboot`) and restart the service:
```sh
sudo systemctl restart tftpd-hpa
```

### 2️⃣ Configure TFTP Server
Edit the configuration file:
```sh
sudo nano /etc/default/tftpd-hpa
```
Ensure it contains:
```ini
TFTP_USERNAME="tftp"
TFTP_DIRECTORY="/var/lib/tftpboot"
TFTP_ADDRESS=":69"
TFTP_OPTIONS="--secure"
```
Save the file and restart the service:
```sh
sudo systemctl restart tftpd-hpa
```

### 3️⃣ Check Permissions
Ensure that the TFTP directory and files have the correct permissions:
```sh
sudo chmod -R 777 /var/lib/tftpboot
sudo chown -R tftp:tftp /var/lib/tftpboot
```

### 4️⃣ Run the TFTP Client
```sh
python src/client.py
```

### 5️⃣ Perform a File Transfer
#### 📥 Download a file from the server:
```sh
Operation (get/put): get
TFTP Server Address: 127.0.0.1
Source file: testfile.txt
Destination file: testfile_local.txt
```
#### 📤 Upload a file to the server:
```sh
Operation (get/put): put
TFTP Server Address: 127.0.0.1
Local file: testfile.txt
Destination file: serverfile.txt
```

---

## 🔍 Project Structure
```
📂 TFTP-Client
 ├── 📂 src          # Source code
 │   ├── client.py   # TFTP client implementation
 │   ├── tftp.py     # TFTP protocol packet handling
 │   ├── __init__.py # Init file for Python package
 ├── 📂 docs         # Documentation
 ├── 📂 diagrams     # Architecture and flow diagrams
 ├── 📜 README.md    # This file
 ├── 📜 requirements.txt # Python dependencies
 ├── 📜 .gitignore   # Git ignored files
```



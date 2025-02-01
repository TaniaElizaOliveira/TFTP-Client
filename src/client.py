#!/usr/bin/env python3
import sys
from socket import AF_INET, SOCK_DGRAM, socket
from tftp import (
    get_file, put_file, read_file_content,
    TFTPValueError, ProtocolError, Err
)

def tftp_client():
    print("\n==== 🖧 TFTP Client Simulation ====")
    
    while True:  # Permite repetir em caso de erro
        try:
            # 📌 Coletar entrada do usuário
            operation = input("\n📌 Operation (get/put): ").strip().lower()
            if operation not in ["get", "put"]:
                print("❌ Invalid operation. Use 'get' or 'put'.")
                continue  # Volta para o início do loop

            server = input("🌐 TFTP Server Address: ").strip()
            source_file = input("📄 Source file (local or remote): ").strip()
            dest_file = input("📂 Destination file (leave empty to use the same name): ").strip() or source_file

            server_address = (server, 69)  # Porta padrão do TFTP

            with socket(AF_INET, SOCK_DGRAM) as sock:
                sock.settimeout(5)

                if operation == "get":
                    print(f"\n📥 Downloading file '{source_file}' from server {server}...")
                    get_file(server_address, source_file, dest_file)  # ✅ Agora passa o nome correto
                    print(f"✅ File '{source_file}' successfully downloaded as '{dest_file}'.")

                elif operation == "put":
                    print("\n📄 Would you like to preview the file before sending? (yes/no)")
                    preview = input("> ").strip().lower()
                    
                    if preview == "yes":
                        try:
                            read_file_content(source_file)  # Exibir conteúdo do arquivo antes do upload
                        except FileNotFoundError:
                            print(f"❌ File '{source_file}' not found. Cannot preview.")
                            continue

                    print(f"\n📤 Uploading file '{source_file}' to server {server}...")
                    put_file(server_address, source_file, dest_file)
                    print(f"✅ File '{source_file}' successfully uploaded as '{dest_file}'.")

            break  # Sai do loop se tudo ocorrer bem

        except FileNotFoundError:
            print(f"❌ Error: File '{source_file}' not found.")
        except TFTPValueError as e:
            print(f"❌ TFTP Error: {e}")
        except ProtocolError as e:
            print(f"❌ Protocol Error: {e}")
        except Err as e:
            print(f"❌ {e}")
        except OSError as e:
            print(f"❌ Network error: {e}")
        except Exception as e:
            print(f"❌ Unexpected error: {e}")

        print("\n🔄 Would you like to try again? (yes/no)")
        retry = input("> ").strip().lower()
        if retry != "yes":
            print("👋 Exiting TFTP client.")
            break

if __name__ == "__main__":
    tftp_client()

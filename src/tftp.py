import struct
import string
from socket import socket, AF_INET, SOCK_DGRAM

############################
# CONSTANTES
############################

MAX_DATA_LEN = 512  # bytes
DEFAULT_MODE = 'octet'  # Transfer mode (e.g., 'octet', 'netascii', etc.)
INACTIVITY_TIMEOUT = 10.0  # Timeout padrão de inatividade (segundos)
DEFAULT_BUFFER_SIZE = 8192  # Tamanho do buffer para recebimento de pacotes
MAX_RETRIES = 5  # Número máximo de tentativas de retransmissão

# OpCodes do TFTP
RRQ = 1  # Read Request
WRQ = 2  # Write Request
DAT = 3  # Data Transfer
ACK = 4  # Acknowledge
ERR = 5  # Error Packet

# Códigos de erro do TFTP
ERR_NOT_DEFINED = 0
ERR_FILE_NOT_FOUND = 1
ERR_ACCESS_VIOLATION = 2
ERR_DISK_FULL = 3
ERR_ILLEGAL_OPERATION = 4
ERR_UNKNOWN_TRANSFER_ID = 5
ERR_FILE_ALREADY_EXISTS = 6
ERR_NO_SUCH_USER = 7

# Mensagens de erro associadas aos códigos de erro
ERROR_MESSAGES = {
    ERR_NOT_DEFINED: "Not defined, see error message (if any).",
    ERR_FILE_NOT_FOUND: "File not found.",
    ERR_ACCESS_VIOLATION: "Access violation.",
    ERR_DISK_FULL: "Disk full or allocation exceeded.",
    ERR_ILLEGAL_OPERATION: "Illegal TFTP operation.",
    ERR_UNKNOWN_TRANSFER_ID: "Unknown transfer ID.",
    ERR_FILE_ALREADY_EXISTS: "File already exists.",
    ERR_NO_SUCH_USER: "No such user.",
}

INET4Address = tuple[str, int]

############################
# PACKET PACKING AND UNPACKING
############################

def pack_rrq(filename: str, mode=DEFAULT_MODE) -> bytes:
    return _pack_rq(RRQ, filename, mode)

def pack_wrq(filename: str, mode=DEFAULT_MODE) -> bytes:
    return _pack_rq(WRQ, filename, mode)

def _pack_rq(opcode: int, filename: str, mode=DEFAULT_MODE) -> bytes:
    if not is_ascii_printable(filename):
        raise TFTPValueError(f"Invalid filename: {filename}. Not ASCII printable")
    filename_bytes = filename.encode() + b"\x00"
    mode_bytes = mode.encode() + b"\x00"
    return struct.pack(f"!H{len(filename_bytes)}s{len(mode_bytes)}s", opcode, filename_bytes, mode_bytes)

def unpack_opcode(packet: bytes) -> int:
    opcode, *_ = struct.unpack("!H", packet[:2])
    if opcode not in (RRQ, WRQ, DAT, ACK, ERR):
        raise TFTPValueError(f"Invalid opcode: {opcode}")
    return opcode

def pack_dat(block_number: int, data: bytes) -> bytes:
    if len(data) > MAX_DATA_LEN:
        raise TFTPValueError(f"Data length exceeds {MAX_DATA_LEN} bytes")
    return struct.pack(f"!HH{len(data)}s", DAT, block_number, data)

def unpack_dat(packet: bytes) -> tuple[int, bytes]:
    opcode, block_number = struct.unpack("!HH", packet[:4])
    if opcode != DAT:
        raise TFTPValueError(f"Invalid opcode: {opcode}")
    return block_number, packet[4:]

def pack_ack(block_number: int) -> bytes:
    return struct.pack("!HH", ACK, block_number)

def unpack_ack(packet: bytes) -> int:
    if len(packet) != 4:
        raise TFTPValueError(f"Invalid packet length: {len(packet)}")
    opcode, block_number = struct.unpack("!HH", packet)
    if opcode != ACK:
        raise TFTPValueError(f"Invalid opcode: {opcode}")
    return block_number

def pack_err(error_num: int, error_msg: str) -> bytes:
    if not is_ascii_printable(error_msg):
        raise TFTPValueError(f"Invalid error message: {error_msg}. Not ASCII printable")
    return struct.pack(f"!HH{len(error_msg.encode())+1}s", ERR, error_num, error_msg.encode() + b"\x00")

def unpack_err(packet: bytes) -> tuple[int, str]:
    opcode, error_num = struct.unpack("!HH", packet[:4])
    if opcode != ERR:
        raise TFTPValueError(f"Invalid opcode: {opcode}")
    return error_num, packet[4:].decode().rstrip("\x00")

############################
# TFTP FILE TRANSFER FUNCTIONS
############################

def get_file(server_addr: INET4Address, filename: str, dest_file: str):
    """Receives a file from the TFTP server and saves it as `dest_file`."""
    with socket(AF_INET, SOCK_DGRAM) as sock:
        sock.settimeout(INACTIVITY_TIMEOUT)
        
        # 🚀 Aqui, garantimos que o arquivo será salvo com o nome correto!
        with open(dest_file, "wb") as out_file:
            sock.sendto(pack_rrq(filename), server_addr)
            next_block_number = 1
            
            while True:
                packet, _ = sock.recvfrom(DEFAULT_BUFFER_SIZE)
                opcode = unpack_opcode(packet)

                if opcode == DAT:
                    block_number, data = unpack_dat(packet)
                    if block_number == next_block_number:
                        out_file.write(data)  # ✅ Escrevendo no `dest_file`
                        sock.sendto(pack_ack(block_number), server_addr)
                        next_block_number += 1
                    if len(data) < MAX_DATA_LEN:
                        print(f"✅ File '{filename}' successfully downloaded as '{dest_file}'.")
                        return

                elif opcode == ERR:
                    error_code, error_msg = unpack_err(packet)
                    raise Err(error_code, error_msg)

    """Recebe um arquivo do servidor TFTP, garantindo retransmissão de pacotes perdidos."""
    with socket(AF_INET, SOCK_DGRAM) as sock:
        sock.settimeout(INACTIVITY_TIMEOUT)
        with open(filename, "wb") as out_file:
            sock.sendto(pack_rrq(filename), server_addr)
            next_block_number = 1
            retries = 0

            while True:
                try:
                    packet, _ = sock.recvfrom(DEFAULT_BUFFER_SIZE)
                    opcode = unpack_opcode(packet)

                    if opcode == DAT:
                        block_number, data = unpack_dat(packet)

                        if block_number == next_block_number:
                            out_file.write(data)
                            sock.sendto(pack_ack(block_number), server_addr)
                            next_block_number += 1
                            retries = 0  # Reseta o contador de tentativas
                        elif block_number < next_block_number:
                            # Se receber um bloco repetido, reenvia o último ACK
                            sock.sendto(pack_ack(block_number), server_addr)

                        if len(data) < MAX_DATA_LEN:
                            return

                    elif opcode == ERR:
                        error_code, error_msg = unpack_err(packet)
                        raise Err(error_code, error_msg)

                except TimeoutError:
                    retries += 1
                    if retries > MAX_RETRIES:
                        raise TFTPValueError("❌ Max retries exceeded, aborting transfer.")
                    print(f"⚠️ Timeout! Resending last ACK ({next_block_number - 1})...")
                    sock.sendto(pack_ack(next_block_number - 1), server_addr)

    """Recebe um arquivo do servidor TFTP."""
    with socket(AF_INET, SOCK_DGRAM) as sock:
        sock.settimeout(INACTIVITY_TIMEOUT)
        with open(filename, "wb") as out_file:
            sock.sendto(pack_rrq(filename), server_addr)
            next_block_number = 1

            while True:
                packet, _ = sock.recvfrom(DEFAULT_BUFFER_SIZE)
                opcode = unpack_opcode(packet)

                if opcode == DAT:
                    block_number, data = unpack_dat(packet)
                    if block_number == next_block_number:
                        out_file.write(data)
                        sock.sendto(pack_ack(block_number), server_addr)
                        next_block_number += 1
                    if len(data) < MAX_DATA_LEN:
                        return

                elif opcode == ERR:
                    error_code, error_msg = unpack_err(packet)
                    raise Err(error_code, error_msg)

def put_file(server_addr: INET4Address, local_file: str, remote_file: str):
    """Envia um arquivo para o servidor TFTP, com retransmissão se necessário."""
    with socket(AF_INET, SOCK_DGRAM) as sock:
        sock.settimeout(INACTIVITY_TIMEOUT)

        with open(local_file, "rb") as in_file:
            sock.sendto(pack_wrq(remote_file), server_addr)
            next_block_number = 0

            while True:
                for attempt in range(MAX_RETRIES):
                    try:
                        packet, _ = sock.recvfrom(DEFAULT_BUFFER_SIZE)
                        opcode = unpack_opcode(packet)

                        if opcode == ACK:
                            block_number = unpack_ack(packet)
                            if block_number == next_block_number:
                                data = in_file.read(MAX_DATA_LEN)
                                if not data:
                                    return
                                next_block_number += 1
                                sock.sendto(pack_dat(next_block_number, data), server_addr)
                            break  # Sai do loop de tentativas se o ACK for recebido corretamente
                    except TimeoutError:
                        print(f"⚠️ Timeout! Retrying block {next_block_number} ({attempt+1}/{MAX_RETRIES})...")
                else:
                    raise TFTPValueError("❌ Max retries exceeded, aborting transfer.")

    """Envia um arquivo para o servidor TFTP."""
    with socket(AF_INET, SOCK_DGRAM) as sock:
        sock.settimeout(INACTIVITY_TIMEOUT)

        with open(local_file, "rb") as in_file:
            sock.sendto(pack_wrq(remote_file), server_addr)
            next_block_number = 0

            while True:
                packet, _ = sock.recvfrom(DEFAULT_BUFFER_SIZE)
                opcode = unpack_opcode(packet)

                if opcode == ACK:
                    block_number = unpack_ack(packet)
                    if block_number == next_block_number:
                        data = in_file.read(MAX_DATA_LEN)
                        if not data:
                            return
                        next_block_number += 1
                        sock.sendto(pack_dat(next_block_number, data), server_addr)

                elif opcode == ERR:
                    error_code, error_msg = unpack_err(packet)
                    raise Err(error_code, error_msg)

def read_file_content(file_path: str):
    """Lê e imprime o conteúdo de um arquivo local antes de enviá-lo via TFTP."""
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            print("\n==== File Content Preview ====\n")
            print(file.read())
            print("\n==============================")
    except FileNotFoundError:
        print(f"❌ Error: File '{file_path}' not found.")
    except Exception as e:
        print(f"❌ Error reading file: {e}")

############################
# ERRORS AND EXCEPTIONS
############################

class TFTPValueError(ValueError):
    pass

class ProtocolError(Exception):
    pass

class Err(Exception):
    def __init__(self, code, msg):
        super().__init__(f"TFTP Error {code}: {msg}")
        self.code = code
        self.msg = msg

############################
# COMMON UTILITIES
############################

def is_ascii_printable(txt: str) -> bool:
    return set(txt).issubset(set(string.printable))

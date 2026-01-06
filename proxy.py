import socket
import threading
import select
import logging
import struct
import socketserver

logger = logging.getLogger(__name__)

class ThreadingTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    daemon_threads = True
    allow_reuse_address = True

class SocksProxy:
    def __init__(self, port, ssh_transport):
        self.port = port
        self.ssh_transport = ssh_transport
        self.server = None
        self.server_thread = None

    def start(self):
        class SocksHandler(socketserver.BaseRequestHandler):
            transport = self.ssh_transport

            def handle(self):
                try:
                    # SOCKS5 Initial Handshake
                    # Client sends: VER(1) | NMETHODS(1) | METHODS(N)
                    header = self.request.recv(2)
                    if not header or header[0] != 5:
                        return

                    nmethods = header[1]
                    _ = self.request.recv(nmethods) # Consume methods
                    
                    # Respond: VER(5) | METHOD(00 - No Auth)
                    self.request.sendall(b"\x05\x00")

                    # Request Details
                    # Client sends: VER(1) | CMD(1) | RSV(1) | ATYP(1) | ADDR | PORT
                    details = self.request.recv(4)
                    if not details or len(details) < 4:
                        return

                    ver, cmd, rsv, atyp = details

                    if cmd != 1: # Only CONNECT supported
                        self.request.sendall(b"\x05\x07\x00\x01\x00\x00\x00\x00\x00\x00") # Command not supported
                        return

                    # Parse Destination Address
                    if atyp == 1: # IPv4
                        addr_bytes = self.request.recv(4)
                        dest_addr = socket.inet_ntoa(addr_bytes)
                    elif atyp == 3: # Domain
                        addr_len = ord(self.request.recv(1))
                        dest_addr = self.request.recv(addr_len).decode()
                    elif atyp == 4: # IPv6
                        # Not supported in this basic impl
                        self.request.sendall(b"\x05\x08\x00\x01\x00\x00\x00\x00\x00\x00")
                        return
                    else:
                        return

                    # Parse Port
                    port_bytes = self.request.recv(2)
                    dest_port = struct.unpack('>H', port_bytes)[0]

                    # Establish SSH Tunnel
                    try:
                        remote_channel = self.transport.open_channel(
                            "direct-tcpip", (dest_addr, dest_port), self.request.getpeername()
                        )
                    except Exception as e:
                        logger.error(f"SSH Tunnel failed to {dest_addr}:{dest_port} - {e}")
                        self.request.sendall(b"\x05\x04\x00\x01\x00\x00\x00\x00\x00\x00") # Host unreachable
                        return

                    # Send Success response
                    # BND.ADDR (0.0.0.0), BND.PORT (0)
                    self.request.sendall(b"\x05\x00\x00\x01\x00\x00\x00\x00\x00\x00")

                    # Start Forwarding
                    self._forward(self.request, remote_channel)

                except Exception as e:
                    # logger.debug(f"SOCKS handler error: {e}")
                    pass
                finally:
                    try: self.request.close()
                    except: pass

            def _forward(self, client, remote):
                try:
                    while True:
                        r, w, x = select.select([client, remote], [], [], 60)
                        if client in r:
                            data = client.recv(32768)
                            if not data: break
                            remote.sendall(data)
                        if remote in r:
                            data = remote.recv(32768)
                            if not data: break
                            client.sendall(data)
                except:
                    pass
                finally:
                    try: remote.close()
                    except: pass

        self.server = ThreadingTCPServer(('127.0.0.1', self.port), SocksHandler)
        self.server_thread = threading.Thread(target=self.server.serve_forever)
        self.server_thread.daemon = True
        self.server_thread.start()
        logger.info(f"SOCKS5 Proxy server running on 127.0.0.1:{self.port}")

    def stop(self):
        if self.server:
            self.server.shutdown()
            self.server.server_close()
            self.server = None
        logger.info("SOCKS5 Proxy stopped")
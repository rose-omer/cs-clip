import socket
import threading
import time

import pytest

from render import Console


def test_console_sends_commands_and_drains_output(tmp_path):
    server = socket.socket()
    server.bind(("127.0.0.1", 0))
    server.listen(1)
    port = server.getsockname()[1]
    received = []

    def fake_cs2():
        conn, _ = server.accept()
        conn.sendall(b"x" * 2_000_000)  # okunmazsa tampon dolar
        buf = b""
        while b"demo_pause\n" not in buf:
            buf += conn.recv(1024)
        received.append(buf.decode())
        conn.close()

    t = threading.Thread(target=fake_cs2, daemon=True)
    t.start()
    log = tmp_path / "konsol.log"
    con = Console(port, log_path=log)
    con.send("playdemo cs-klip/mac1", "demo_pause")
    t.join(timeout=10)
    assert received and "playdemo cs-klip/mac1\ndemo_pause\n" in received[0]
    for _ in range(50):
        if log.stat().st_size >= 2_000_000:
            break
        time.sleep(0.1)
    assert log.stat().st_size == 2_000_000
    server.close()


def test_console_reports_missing_cs2():
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()  # port boş: bağlantı reddedilir
    with pytest.raises(SystemExit, match="netconport"):
        Console(port)

import uuid
from database import koneksi
from qr_utils import buat_qr

class Registrasi:
    def daftar_kendaraan(self):
        print("\n=== Registrasi Kendaraan ===")
        nama = input("Nama pemilik: ").strip()
        email = input("Email pemilik: ").strip().lower()
        plat = input("Nomor polisi: ").strip().upper()
        jenis = input("Jenis (Motor/Mobil): ").strip().capitalize()

        if not nama or not email or not plat:
            print("Semua data wajib diisi.")
            return
        if jenis not in ("Motor", "Mobil"):
            print("Jenis kendaraan harus Motor atau Mobil.")
            return

        id_qr = "SP-" + uuid.uuid4().hex[:12].upper()
        try:
            with koneksi() as conn:
                pemilik = conn.execute(
                    "SELECT id FROM pengguna WHERE email = ?", (email,)
                ).fetchone()
                if pemilik:
                    pengguna_id = pemilik["id"]
                    conn.execute(
                        "UPDATE pengguna SET nama = ? WHERE id = ?",
                        (nama, pengguna_id)
                    )
                else:
                    cur = conn.execute(
                        "INSERT INTO pengguna(nama, email) VALUES (?, ?)",
                        (nama, email)
                    )
                    pengguna_id = cur.lastrowid

                conn.execute("""
                    INSERT INTO kendaraan(id_qr, pengguna_id, nomor_polisi, jenis)
                    VALUES (?, ?, ?, ?)
                """, (id_qr, pengguna_id, plat, jenis))

            path = buat_qr(id_qr, plat, jenis)
            print("\nRegistrasi berhasil.")
            print(f"ID QR        : {id_qr}")
            print(f"Nomor polisi : {plat}")
            print(f"File QR      : {path}")
            print("QR yang sama berlaku di semua mall dalam sistem.")
        except Exception as e:
            print(f"Registrasi gagal: {e}")

    @staticmethod
    def validasi_kendaraan_qr(data):
        """QR hanya boleh dipakai jika ID, plat, dan jenis cocok dengan database."""
        with koneksi() as conn:
            row = conn.execute(
                "SELECT * FROM kendaraan WHERE id_qr = ?",
                (data["vehicle_id"],)
            ).fetchone()
        if not row:
            return None
        if row["nomor_polisi"] != data["plate"].upper():
            return None
        if row["jenis"] != data["type"]:
            return None
        return row

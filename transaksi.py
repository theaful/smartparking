from datetime import datetime
import math
from config import TARIF
from database import koneksi

FMT = "%Y-%m-%d %H:%M:%S"

class TransaksiParkir:
    @staticmethod
    def mulai_parkir(id_qr, mall_id):
        with koneksi() as conn:
            aktif = conn.execute("""
                SELECT id FROM transaksi
                WHERE id_qr = ? AND status IN ('Berlangsung', 'Menunggu Pembayaran')
                LIMIT 1
            """, (id_qr,)).fetchone()
            if aktif:
                print("Kendaraan masih memiliki transaksi parkir aktif.")
                return False

            conn.execute("""
                INSERT INTO transaksi(id_qr, mall_masuk_id, waktu_masuk, status)
                VALUES (?, ?, ?, 'Berlangsung')
            """, (id_qr, mall_id, datetime.now().strftime(FMT)))
        print("Kendaraan berhasil tercatat masuk.")
        return True

    @staticmethod
    def hitung_tagihan(id_qr, mall_keluar_id):
        with koneksi() as conn:
            trx = conn.execute("""
                SELECT t.*, k.jenis
                FROM transaksi t JOIN kendaraan k ON t.id_qr = k.id_qr
                WHERE t.id_qr = ? AND t.status = 'Berlangsung'
                ORDER BY t.id DESC LIMIT 1
            """, (id_qr,)).fetchone()

            if not trx:
                print("Tidak ada transaksi parkir aktif untuk kendaraan ini.")
                return None

            if trx["mall_masuk_id"] != mall_keluar_id:
                print("Lokasi keluar berbeda dengan lokasi masuk.")
                print("Untuk versi ini, kendaraan harus keluar di mall tempat masuk.")
                return None

            sekarang = datetime.now()
            masuk = datetime.strptime(trx["waktu_masuk"], FMT)
            durasi_detik = max(0, (sekarang - masuk).total_seconds())
            jam = max(1, math.ceil(durasi_detik / 3600))
            biaya = jam * TARIF[trx["jenis"]]
            conn.execute("""
                UPDATE transaksi
                SET waktu_keluar = ?, durasi_jam = ?, biaya = ?,
                    mall_keluar_id = ?, status = 'Menunggu Pembayaran'
                WHERE id = ?
            """, (sekarang.strftime(FMT), jam, biaya, mall_keluar_id, trx["id"]))
            return {"id": trx["id"], "biaya": biaya, "jam": jam}

    @staticmethod
    def selesaikan_pembayaran(transaksi_id, metode):
        with koneksi() as conn:
            conn.execute("""
                UPDATE transaksi
                SET metode_pembayaran = ?, status = 'Lunas'
                WHERE id = ? AND status = 'Menunggu Pembayaran'
            """, (metode, transaksi_id))

    @staticmethod
    def batalkan_tagihan(transaksi_id):
        # Bila simulasi pembayaran gagal, transaksi dapat dihitung ulang saat dicoba lagi.
        with koneksi() as conn:
            conn.execute("""
                UPDATE transaksi
                SET waktu_keluar = NULL, durasi_jam = NULL, biaya = NULL,
                    mall_keluar_id = NULL, status = 'Berlangsung'
                WHERE id = ? AND status = 'Menunggu Pembayaran'
            """, (transaksi_id,))

    @staticmethod
    def riwayat(id_qr=None, mall_id=None):
        sql = """
            SELECT t.*, k.nomor_polisi, k.jenis,
                   mi.nama AS mall_masuk, mo.nama AS mall_keluar
            FROM transaksi t
            JOIN kendaraan k ON t.id_qr = k.id_qr
            JOIN mall mi ON t.mall_masuk_id = mi.id
            LEFT JOIN mall mo ON t.mall_keluar_id = mo.id
            WHERE 1=1
        """
        params = []
        if id_qr:
            sql += " AND t.id_qr = ?"
            params.append(id_qr)
        if mall_id:
            sql += " AND t.mall_masuk_id = ?"
            params.append(mall_id)
        sql += " ORDER BY t.id DESC"
        with koneksi() as conn:
            return conn.execute(sql, params).fetchall()

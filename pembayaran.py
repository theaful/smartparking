from abc import ABC, abstractmethod

class MetodePembayaran(ABC):
    @abstractmethod
    def bayar(self, nominal):
        pass

class PembayaranQRIS(MetodePembayaran):
    def bayar(self, nominal):
        print(f"Simulasi pembayaran QRIS sebesar Rp{nominal:,}".replace(",", "."))
        return input("Konfirmasi pembayaran berhasil? (y/n): ").strip().lower() == "y"

class PembayaranEMoney(MetodePembayaran):
    def bayar(self, nominal):
        print(f"Simulasi pembayaran E-Money sebesar Rp{nominal:,}".replace(",", "."))
        return input("Konfirmasi pembayaran berhasil? (y/n): ").strip().lower() == "y"

"""
KOMPAS 100 Index Constituents — Updated May 2026
Using Indonesian Industry Naming (IDX Standard).
"""

# 1. Start with LQ45 (45 tickers)
from app.constants.lq45_tickers import LQ45_TICKERS

KOMPAS100_TICKERS: list[dict] = list(LQ45_TICKERS)

# 2. Add the 55 Non-LQ45 tickers provided by the user
NON_LQ45_ADDITIONS: list[dict] = [
    # Perbankan & Finance (Non-LQ45)
    {"ticker": "ARTO.JK", "name": "Bank Jago", "sector": "Keuangan"},
    {"ticker": "BRIS.JK", "name": "Bank Syariah Indonesia", "sector": "Keuangan"},
    {"ticker": "BDMN.JK", "name": "Bank Danamon Indonesia", "sector": "Keuangan"},
    {"ticker": "PNBN.JK", "name": "Bank Pan Indonesia", "sector": "Keuangan"},
    {"ticker": "BJBR.JK", "name": "Bank Pembangunan Daerah Jabar", "sector": "Keuangan"},
    {"ticker": "BJTM.JK", "name": "Bank Pembangunan Daerah Jatim", "sector": "Keuangan"},
    {"ticker": "BTPS.JK", "name": "Bank BTPN Syariah", "sector": "Keuangan"},
    {"ticker": "AGRO.JK", "name": "Bank Raya Indonesia", "sector": "Keuangan"},
    {"ticker": "BNII.JK", "name": "Bank Maybank Indonesia", "sector": "Keuangan"},
    {"ticker": "ADMF.JK", "name": "Adira Dinamika Multi Finance", "sector": "Keuangan"},
    {"ticker": "CFIN.JK", "name": "Clipan Finance Indonesia", "sector": "Keuangan"},

    # Energi & Mining (Non-LQ45)
    {"ticker": "HRUM.JK", "name": "Harum Energy", "sector": "Energi"},
    {"ticker": "TINS.JK", "name": "Timah", "sector": "Barang Baku"},
    {"ticker": "NCKL.JK", "name": "Trimegah Bangun Persada", "sector": "Barang Baku"},
    {"ticker": "ENRG.JK", "name": "Energi Mega Persada", "sector": "Energi"},
    {"ticker": "DSSA.JK", "name": "Dian Swastatika Sentosa", "sector": "Energi"},
    {"ticker": "BREN.JK", "name": "Barito Renewables Energy", "sector": "Energi"},
    {"ticker": "TPIA.JK", "name": "Chandra Asri Pacific", "sector": "Barang Baku"},
    {"ticker": "RMKE.JK", "name": "RMK Energy", "sector": "Energi"},

    # Properti & Konstruksi (Non-LQ45)
    {"ticker": "BSDE.JK", "name": "Bumi Serpong Damai", "sector": "Properti & Real Estat"},
    {"ticker": "PWON.JK", "name": "Pakuwon Jati", "sector": "Properti & Real Estat"},
    {"ticker": "SMRA.JK", "name": "Summarecon Agung", "sector": "Properti & Real Estat"},
    {"ticker": "CTRA.JK", "name": "Ciputra Development", "sector": "Properti & Real Estat"},
    {"ticker": "INTP.JK", "name": "Indocement Tunggal Prakarsa", "sector": "Barang Baku"},
    {"ticker": "SMBR.JK", "name": "Semen Baturaja", "sector": "Barang Baku"},
    {"ticker": "JSMR.JK", "name": "Jasa Marga", "sector": "Infrastruktur"},
    {"ticker": "ADHI.JK", "name": "Adhi Karya", "sector": "Perindustrian"},
    {"ticker": "PTPP.JK", "name": "PP (Persero)", "sector": "Perindustrian"},
    {"ticker": "DGIK.JK", "name": "Nusa Konstruksi Enjiniring", "sector": "Perindustrian"},

    # Consumer & Retail (Non-LQ45)
    {"ticker": "MYOR.JK", "name": "Mayora Indah", "sector": "Barang Konsumsi Primer"},
    {"ticker": "ROTI.JK", "name": "Nippon Indosari Corpindo", "sector": "Barang Konsumsi Primer"},
    {"ticker": "SIDO.JK", "name": "Industri Jamu Sido Muncul", "sector": "Barang Konsumsi Primer"},
    {"ticker": "WIIM.JK", "name": "Wismilak Inti Makmur", "sector": "Barang Konsumsi Primer"},
    {"ticker": "ERAA.JK", "name": "Erajaya Swasembada", "sector": "Barang Konsumsi Sekunder"},
    {"ticker": "MAPA.JK", "name": "Map Aktif Adiperkasa", "sector": "Barang Konsumsi Sekunder"},
    {"ticker": "ACES.JK", "name": "Aspirasi Hidup Indonesia", "sector": "Barang Konsumsi Sekunder"},
    {"ticker": "RALS.JK", "name": "Ramayana Lestari Sentosa", "sector": "Barang Konsumsi Sekunder"},
    {"ticker": "LPPF.JK", "name": "Matahari Department Store", "sector": "Barang Konsumsi Sekunder"},

    # Kesehatan (Non-LQ45)
    {"ticker": "HEAL.JK", "name": "Medikaloka Hermina", "sector": "Kesehatan"},
    {"ticker": "MIKA.JK", "name": "Mitra Keluarga Karyasehat", "sector": "Kesehatan"},
    {"ticker": "SILO.JK", "name": "Siloam International Hospitals", "sector": "Kesehatan"},
    {"ticker": "PRDA.JK", "name": "Prodia Widyahusada", "sector": "Kesehatan"},
    {"ticker": "TSPC.JK", "name": "Tempo Scan Pacific", "sector": "Kesehatan"},

    # Teknologi & Logistik (Non-LQ45)
    {"ticker": "BUKA.JK", "name": "Bukalapak.com", "sector": "Infrastruktur"},
    {"ticker": "BELI.JK", "name": "Global Digital Niaga", "sector": "Infrastruktur"},
    {"ticker": "MTEL.JK", "name": "Dayamitra Telekomunikasi", "sector": "Infrastruktur"},
    {"ticker": "TBIG.JK", "name": "Tower Bersama Infrastructure", "sector": "Infrastruktur"},
    {"ticker": "EDGE.JK", "name": "Indointernet", "sector": "Infrastruktur"},
    {"ticker": "SMDR.JK", "name": "Samudera Indonesia", "sector": "Transportasi & Logistik"},
    {"ticker": "TMAS.JK", "name": "Temas", "sector": "Transportasi & Logistik"},
    {"ticker": "ASSA.JK", "name": "Adi Sarana Armada", "sector": "Transportasi & Logistik"},
    {"ticker": "BIRD.JK", "name": "Blue Bird", "sector": "Transportasi & Logistik"},

    # Agrikultur (Non-LQ45)
    {"ticker": "DSNG.JK", "name": "Dharma Satya Nusantara", "sector": "Barang Konsumsi Primer"},
    {"ticker": "TAPG.JK", "name": "Triputra Agro Persada", "sector": "Barang Konsumsi Primer"},
    {"ticker": "AALI.JK", "name": "Astra Agro Lestari", "sector": "Barang Konsumsi Primer"},
]

# Ensure no duplicates from LQ45
_seen = {t["ticker"] for t in KOMPAS100_TICKERS}
for stock in NON_LQ45_ADDITIONS:
    if stock["ticker"] not in _seen:
        KOMPAS100_TICKERS.append(stock)
        _seen.add(stock["ticker"])

KOMPAS100_TICKER_SYMBOLS: list[str] = [t["ticker"] for t in KOMPAS100_TICKERS]
KOMPAS100_TICKER_META: dict[str, dict] = {t["ticker"]: t for t in KOMPAS100_TICKERS}

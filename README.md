# 🛒 Smart Shopping Cart for Enhanced Retail Experience

An IoT and embedded-system-based smart shopping cart that simplifies in-store shopping by automating billing, reducing checkout lines, and offering real-time inventory management — all while enhancing the customer experience.

---

## 🎯 Project Objective

To design and implement a smart cart that:
- Automatically detects products via RFID
- Calculates total bill in real time
- Displays items and price on an LCD
- Sends data to a central database or store system
- Minimizes human intervention in billing

---

## 🧠 System Features

- 📶 **RFID-based product detection**
- 💵 **Automated billing system**
- 🖥️ **LCD display for item name & price**
- 📡 **Wi-Fi module (ESP8266/NodeMCU) for data sync**
- 🔋 **Low-power embedded design**
- 🛒 **Cart ID system for multiple users**

---

## ⚙️ Hardware Components

| Component           | Description                        |
|--------------------|------------------------------------|
| Microcontroller     | NodeMCU / Arduino Uno              |
| RFID Module         | MFRC522 or RC522                   |
| LCD Display         | 16x2 or 20x4                       |
| Buzzer              | For item scan/beep feedback        |
| Wi-Fi Module        | Built-in ESP8266 (if NodeMCU used) |
| Power Supply        | Rechargeable battery/USB power     |

---

## 🔌 Working Principle

1. Product with RFID tag is placed in the cart
2. RFID reader scans the tag
3. Item name & price displayed on LCD
4. Buzzer confirms item detection
5. Total bill updated in real time
6. Final bill can be sent to billing counter or mobile app

---

## 🚀 Future Enhancements
- QR-code scanner integration
- Mobile app for real-time billing
- Cart weight sensor to prevent theft
- Voice output module for accessibility

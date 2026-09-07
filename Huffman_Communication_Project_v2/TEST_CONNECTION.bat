@echo off
echo ============================================================
echo HUFFMAN PROJECT - NETWORK DIAGNOSTIC TOOL
echo ============================================================
echo.
echo STEP 1: Check your IP address
echo Run: ipconfig
echo Look for "IPv4 Address" under Wireless LAN adapter Wi-Fi
echo.
echo STEP 2: On RECEIVER laptop (the one that should LISTEN)
echo   a) Run: python receiver_gui.py
echo   b) Verify GUI shows: "LINK: LISTENING" and "STATE: LISTENING"
echo   c) Open NEW cmd and run: netstat -ano | findstr :5000
echo      MUST see: TCP    0.0.0.0:5000           0.0.0.0:0              LISTENING
echo.
echo STEP 3: On SENDER laptop (the one that sends message)
echo   a) Run: python sender_gui.py
echo   b) In the "Receiver IPv4" FIELD, DELETE "127.0.0.1"
echo   c) TYPE the EXACT IPv4 address from RECEIVER laptop (from step 1)
echo      Example: if receiver ipconfig shows 10.29.140.181, type THAT
echo   d) Enter test message, click "Compress", then "Transmit"
echo.
echo STEP 4: FIREWALL CHECK (RUN AS ADMINISTRATOR IN CMD)
echo   On BOTH laptops, run these commands in Admin CMD:
echo   netsh advfirewall firewall add rule name="Huffman_RX" dir=in action=allow protocol=TCP localport=5000
echo   netsh advfirewall firewall add rule name="Huffman_TX" dir=out action=allow protocol=TCP remoteport=5000
echo.
echo STEP 5: TEST CONNECTIVITY
echo   On SENDER laptop, run: telnet <RECEIVER_IP> 5000
echo   (If telnet not recognized: Enable via Windows Features -> Telnet Client)
echo   SUCCESS: Blank screen with blinking cursor = connection accepted
echo   FAILURE: Check firewall/receiver status
echo.
echo STEP 6: ALTERNATIVE - USE HOTSPOT FOR TESTING
echo   If corporate/school network blocks device-to-device:
echo   1. Create mobile hotspot on one laptop
echo   2. Connect other laptop to that hotspot
echo   3. Use hotspot laptop's IP as receiver address
echo.
echo ============================================================
echo TROUBLESHOOTING TIPS:
echo   - NEVER use 127.0.0.1 between different devices
echo   - Disable VPNs (NordVPN, Cisco AnyConnect, etc.)
echo   - Antivirus may block - temporarily disable to test
echo   - Receiver MUST be started FIRST
echo   - Look for error popups in receiver GUI
echo ============================================================
pause
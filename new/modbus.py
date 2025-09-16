from pymodbus.client import ModbusTcpClient
import time

PLC_IP = "192.168.0.10"   # Change to your PLC IP
PLC_PORT = 502            # Default Modbus TCP port

# Create Modbus client (correct argument is 'port')
cli = ModbusTcpClient(PLC_IP, port=PLC_PORT)

if cli.connect():
    print("Connected to PLC successfully!")
    try:
        while True:
            # Read holding register (example: 40001 → address 0 in pymodbus)
            result = cli.read_holding_registers(0, 1)

            if not result.isError():
                raw_value = result.registers[0]
                temperature = raw_value / 10.0
                print(f"Temperature: {temperature} °C")
            else:
                print("Error reading register")

            time.sleep(2)

    except KeyboardInterrupt:
        print(" Stopping data read...")

    finally:
        cli.close()
        print(" Disconnected from PLC")

else:
    print(" Could not connect to PLC. Check IP and port.")

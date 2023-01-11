# selec
MODBUS wrapper for Selec EM2M series energy meters.  

Currently supporting EM2M-1P-C-100A, a single phase DIN RAIL device. Datasheet available at https://www.selec.com/product-details/energy-meter-direct-operated-em2m

## Reading the measurements from the device

```python
from selec.em2m_1p_c_100a import EnergyMeter

# device is the path to the USB device
# address is the address configuration of the device (default is 1)
# identifier is some string name given to the device for easy nomenculature.
dev = EnergyMeter(device='/dev/ttyUSB1', address=1, identifier="Grid")

# unit is returned with the measurement for easy understanding of the scale.
# read the voltage
v, unit = dev.voltage

# read the current
c, unit = dev.current

# read the frequency
f, unit = dev.frequency

# read the active power in kW
p, unit = dev.active_power

# read the reactive energy in kVAr
e, unit = dev.reactive_energy
```

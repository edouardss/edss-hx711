# Module hx711-loadcell 

Module for supporting the HX711 ADC for use with a load cell to measure weight.

intially as kodama;hx711-loadcell:loadcell
Expanded to include tare and wider reading payload. 

Loadcell model uses the hx711 Python library and currently is set to take the specified number of readings and return the average value of those readings.

### Configuration
The following attribute template can be used to configure this model:

```json
{
  "gain": 64,
  "doutPin": 5,
  "sckPin":6,
  "numberOfReadings":3
}
```

#### Attributes

The following attributes are available for this model:

| Name          | Type   | Inclusion | Description                |
|---------------|--------|-----------|----------------------------|
| `gain` | float  | Optional  | gain for hx711 readings |
| `doutPin` | int | Optional  | pin for data out |
| `sckPin` | int | Optional  | pin for clock |
| `numberOfReadings` | int | Optional  | number of readings to take each time |

#### Example Configuration

```json
{
  "gain": 64,
  "doutPin": 5,
  "sckPin":6,
  "numberOfReadings":3
}
```

The `tare` function is a DoCommand. Call it with `"tare": {}`, the return value is the value (in kgs) of the weight that will be systematically subtracted from the readings. 

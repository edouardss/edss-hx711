# Module hx711-loadcell 

Provide a description of the purpose of the module and any relevant information.

## Model kodama:hx711-loadcell:loadcell

Provide a description of the model and any relevant information.

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


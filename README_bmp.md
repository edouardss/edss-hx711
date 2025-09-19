### Configuration for BMP
The following attribute template can be used to configure this model:

```json
{
  "sea_level_pressure": 101325
}
```
pressure is measured in Pa (Pascals)
This is optional. 

The `tare` function is a DoCommand. Call it with `"tare": {}`, the return value is the value (in Pa and m) of the current pressure and altitude readings. They will be subtracted from future readings. The `reset_tare` function is another DoCommand which resets the offset values to 0. 


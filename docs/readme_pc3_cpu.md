# PC3 CPU 
Simple viewer that can display 3-array in real-time.
The input arrays are decoupled from any device and view can be rotated with mouse.

## App Usage
right mouse - rotate
left mouse - select

## Devices
| Data Source | Description |
| ----------- | ----------- |
| Device      | data source is directly from attached sensor device |
| SwDevice    | data source is from sw host app |

## Example API usage,
```
import pc3
dev = pc3.DeviceSw()
v = pc3.Viewer(dev)
v.start()

```
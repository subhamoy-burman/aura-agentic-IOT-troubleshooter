# Troubleshooting Guide: Error E-101 - WiFi Connectivity Issue

## Error Code
**E-101**: WiFi Connection Failure

## Symptom
The device status light is blinking amber, and it appears as "Offline" in the companion app.

**Additional Indicators:**
- Device may emit a single beep every 30 seconds
- LED pattern: Amber blink (1 second on, 1 second off)
- Unable to receive commands from the mobile app
- Scheduled cleaning cycles do not start
- Voice assistant integration is unavailable

## Root Cause
This error indicates the device cannot connect to the user's WiFi network. This can be due to:
- Incorrect WiFi password entry
- Router configuration issues (firewall, MAC filtering)
- Signal strength too weak (distance/obstacles)
- Incompatible WiFi band (device only supports 2.4GHz, not 5GHz)
- Router firmware issues or temporary network outage
- Too many devices connected to the router
- Changed WiFi network name (SSID) or password

## Prerequisites to Check
Before troubleshooting, verify:
- The WiFi router is powered on and functioning
- Other devices can connect to the same WiFi network
- The user knows the correct WiFi password
- The WiFi network is 2.4GHz (not 5GHz only)
- The device is charged (at least 20% battery)

## Resolution Steps

### Step 1: Basic Proximity Check
1.  Ask the user to confirm they are within 30 feet of their WiFi router
2.  Ensure there are no major obstacles (metal walls, thick concrete) between the device and router
3.  Temporarily move the device closer to the router (within 10 feet) for testing

### Step 2: App-Based Reconnection
1.  Instruct the user to open their companion app
2.  Navigate to: **Settings > WiFi > Reconnect**
3.  Guide them to re-enter their WiFi password carefully
4.  **Important**: Emphasize case sensitivity and special characters
5.  Verify they are selecting the 2.4GHz network (not 5GHz if dual-band router)
6.  Wait 60 seconds for the device to attempt connection

### Step 3: Router Reboot
If the issue persists:
1.  Recommend they reboot their home WiFi router
2.  Unplug the router's power cable for 30 seconds
3.  Plug it back in and wait 2-3 minutes for full startup
4.  Retry the connection process from Step 2

### Step 4: Factory Reset WiFi Settings (If Steps 1-3 Fail)
1.  On the device, locate the WiFi reset button (small recessed button near charging contacts)
2.  Using a paperclip, press and hold for 5 seconds until you hear two beeps
3.  The device will clear stored WiFi credentials
4.  Follow the initial setup process in the app as if setting up a new device
5.  Complete the WiFi pairing procedure

## Advanced Troubleshooting

### Router Configuration Check
If factory reset doesn't work, guide the user to check router settings:
- **DHCP**: Ensure DHCP is enabled on the router
- **MAC Filtering**: If enabled, add the device's MAC address to the allowed list
- **Firewall**: Temporarily disable strict firewall rules to test
- **Guest Network**: Try connecting to a different SSID if available

### Device Information to Collect
For escalation to support, gather:
- Device model and serial number
- Router make and model
- WiFi network name (SSID)
- Error code duration (how long the issue persists)
- Recent changes to home network

## Success Indicators
Connection is successful when:
- Status light changes from blinking amber to solid green
- Device appears as "Online" in the companion app
- Device responds to a test command (e.g., "Start cleaning")
- App displays current battery level and status

## Estimated Resolution Time
- Standard cases: 3-5 minutes
- With router reboot: 5-10 minutes
- With factory reset: 10-15 minutes

## Related Error Codes
- **E-102**: WiFi signal too weak
- **E-103**: WiFi authentication failure
- **E-104**: DHCP assignment failure

## Prevention Tips
Advise the user to:
- Keep the device firmware up to date via the app
- Position the charging dock within good WiFi range
- Avoid changing router passwords without updating the device
- Restart the device monthly for optimal performance

## Escalation Criteria
Escalate to Tier 2 support if:
- Issue persists after factory reset
- Multiple devices in the home have the same issue
- User cannot access router settings
- Device never successfully connected since purchase
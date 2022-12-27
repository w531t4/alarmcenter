# Example event received from Dahua NVR
```
i\u0000\u0000hh\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0001\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000Channel:0\r\nVideoAnalyseRule:CrossLineDetection\r\nAlarmState:2\r\nDomain name:\r\nTime:2018-07-24 02:20:34\r\n\r\n
```

# Observations
These first 31 characters (once utf-8 decoded) `i\u0000\u0000hh\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0001\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000` appear to remain static across all events. Henceforth referenced as `preamble`.


# alarmcenter.py process
1. Extract `preamble` (see above), assign to key `preamble` in a new dictionary `obj`
2. Assign remainder of data to key `msg` in `obj`
3. Create new dictionary `nicemsg` inside `obj` by splitting `msg` by `\r\n` and using `:` as a k/v delimiter
4. Add "dahua_alarm" as `type` to `nicemsg`
5. Add current time as `time` to `obj`
6. If `nicemsg` contains the key `Channel`:
    1. Lookup value of `Channel` against static list (within script `camera_names`), and assign value as `camera_name` inside `obj`
    2. Add "dahua" as `vendor` inside `obj`
    3. Lookup value of `Channel` against static list (within script `camera_ips`), and assign value as `ip` inside `obj`
    4. Copy key `VideoAnalyseRule` to key `category` within `obj`
    5. Copy key `camera_name` as key `message` within `obj`
    6. Publish `obj` to `notification` channel at redis target
7. Write `obj` to logfile

# object created by process
```
{
    "preamble": "i\u0000\u0000hh\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0001\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000",
    "msg": "Channel:0\r\nVideoAnalyseRule:CrossLineDetection\r\nAlarmState:2\r\nDomain name:\r\nTime:2018-07-24 02:20:34\r\n\r\n",
    "nicemsg": {
        "Channel": "0",
        "VideoAnalyseRule": "CrossLineDetection",
        "AlarmState": "2",
        "Domain name": "",
        "Time": "2018-07-27 001956",
        "type": "dahua_alarm",
        "camera_name": "camera_name_1"
    },
    "time": "2018-07-27T00:19:31.428172",
    "message": "camera_name_1",
    "ip": "10.9.0.2",
    "category": "CrossLineDetection",
    "vendor": "dahua"
}

note: preamble is currently omitted in actual code

Raw Examples from notes:
# there may be a missing 'i' here preceeding the 'i'?
{"msg": "i\u0000\u0000hh\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0001\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000Channel:0\r\nVideoAnalyseRule:CrossLineDetection\r\nAlarmState:2\r\nDomain name:\r\nTime:2018-07-24 02:20:34\r\n\r\n", "time": "2018-07-24T02:20:14.198100"}

'{"msg": "Channel:0\r\nVideoAnalyseRule:CrossLineDetection\r\nAlarmState:2\r\nDomain name:\r\nTime:2018-07-27 00:19:56\r\n\r\n", "nicemsg": {"Channel": "0", "VideoAnalyseRule": "CrossLineDetection", "AlarmState": "2", "Domain name": "", "Time": "2018-07-27 001956", "type": "dahua_alarm", "camera_name": "camera_name_1"}, "time": "2018-07-27T00:19:31.428172", "message": "ptz", "category": "CrossLineDetection", "vendor": "dahua"}'

```

# Example of manually pushing event to redis
`redis-cli -h 10.0.0.1 -p 6379`

PUBLISH notifications '{"msg": "Channel:8\r\nVideoAnalyseRule:CrossLineDetection\r\nAlarmState:2\r\nDomain name:\r\nTime:2018-07-27 00:19:56\r\n\r\n", "nicemsg": {"Channel": "8", "VideoAnalyseRule": "CrossLineDetection", "AlarmState": "2", "Domain name": "", "Time": "2018-07-27 001956", "type": "dahua_alarm", "camera_name": "camera_name_1"}, "time": "2018-07-27T00:19:31.428172", "message": "camera_name_1", "category": "CrossLineDetection", "ip": "10.9.0.2", "vendor": "dahua"}'

# Example of manually pushing event to alarmcenter
`printf "ii\u0000\u0000hh\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0001\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000Channel:0\r\nVideoAnalyseRule:CrossLineDetection\r\nAlarmState:2\r\nDomain name:\r\nTime:2018-07-24 02:20:34\r\n\r\n" | nc localhost 40000`
Open Source Lab: Simple Mirror Syncing API
------------------------------------------

The following functionality is being built at the moment:

* Adding projects

### Adding a project

Projects are added via the api. The following parameters are specified:

* Project name
* Host IP
* Source (Absolute path on the host used to pull content)
* Destination (Path on the master where the
* interval_unit: {minutes, hours or days}
* interval_value: an integer
* start_date in posix format Eg: "2014-03-10 09:30"

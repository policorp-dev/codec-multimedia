#
# Regular cron jobs for the codec-multimedia package.
#
0 4	* * *	root	[ -x /usr/bin/codec-multimedia_maintenance ] && /usr/bin/codec-multimedia_maintenance

#!/usr/bin/python

import boto
import time
import datetime
import logging

'''
This script starts up our dev server every morning at 7am and shuts
it down again at 7pm. Here is an example cron entry that runs the
script on weekdays at 7am and 7pm:

00 07,19 * * 1,2,3,4,5 /usr/bin/python /path/to/startstop.py
'''

# Set AWS Instance ID for our server
dev_id = 'i-5a18ab20'
# Set AWS Elestic IP for our server
dev_ip = '23.21.175.158'

# Setup logging
logging.basicConfig(filename='/var/root/cloud-scripts/startstop.log',level=logging.INFO)

# Make our connection to the EC2 API. boto looks for our API
# key pair in ~/.boto
ec2 = boto.connect_ec2()

# Datetim object
now = datetime.datetime.now()

logging.info('Start run: ' + now.strftime("%Y-%m-%d %H:%M"))

# If it is 7am we need to bring the instance up
if now.hour == 7:
	logging.info('Starting Dev')

	# This starts the instance
	ec2.start_instances(instance_ids=[dev_id])

	# Now we need to create an ofject for the instance so we can
	# check its status.
	reservations = ec2.get_all_instances()

	instances = [i for r in reservations for i in r.instances]
	
	# When the instance starts, the status will be 'pending'.
	# We can't attache the elastic IP until the status is 'running'.
	for i in instances:
		if i.id == dev_id:
			status = i.update()
			while status == 'pending':
				logging.info('Waiting for instance to start')
				time.sleep(10)
				status = i.update()
			if i.state == 'running':
				# Now that it is running, we can attach the IP.
				logging.info('Setting IP')
				ec2.associate_address(dev_id, dev_ip)

# If it is 7pm, we need to stop to server.
elif now.hour == 19:
	logging.info('Stopping Dev')
	ec2.stop_instances(instance_ids=[dev_id])

# If for some reason we run this when we shouldn't will just do nothing.
else:
	logging.info('Nothing to do')

logging.info('Stop run: ' + now.strftime("%Y-%m-%d %H:%M"))

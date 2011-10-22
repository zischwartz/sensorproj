from fabric.api import *

from fabric.contrib.console import confirm
from contextlib import contextmanager as _contextmanager

env.hosts = ['ec2-user@ec2-107-22-54-148.compute-1.amazonaws.com']

env.path = '/home/ec2-user/sensorproj/'
env.prj_name = 'voices'
env.git_repo = 'git://github.com/zischwartz/owsvoices.git'
env.activate = 'source %sbin/activate' % env.path


def prepare_deploy():
    local("./manage.py test posts") #chmod -x manage.py ?
    local("git add . && git commit -m 'commit by fab, prepare_deploy' ")
    local("git push ")


def prepare_server():
	sudo('yum install git-core nginx -y mercurial python-devel')
	#for mongodb
	# sudo('yum -y install git tcsh scons gcc-c++ glibc-devel')
	# sudo('yum -y install boost-devel pcre-devel js-devel readline-devel')
	# sudo('yum -y install boost-devel-static readline-static ncurses-staticl')
	sudo('easy_install pip')
	sudo('pip install virtualenv')
	# sudo('pip install supervisor')


	#for 32 bit
	# sudo('yum install http://downloads-distro.mongodb.org/repo/redhat/os/i686/RPMS/mongo-10gen-2.0.0-mongodb_1.i686.rpm -y --nogpgcheck')
	# sudo('yum install http://downloads-distro.mongodb.org/repo/redhat/os/i686/RPMS/mongo-10gen-server-2.0.0-mongodb_1.i686.rpm -y --nogpgcheck')
	#64 bit at http://downloads-distro.mongodb.org/repo/redhat/os/

	# sudo('mkdir -p /data/db/')
	# sudo('sudo chown `id -u` /data/db')



# pip install supervisor, guicorn
# http://senko.net/en/django-nginx-gunicorn/
#http://gunicorn.org/run.html#gunicorn-django

@_contextmanager
def virtualenv():
	with cd(env.path):
		with prefix(env.activate):
			yield


def first_deploy():
	code_dir = env.path + env.prj_name
	with settings(warn_only=True):
		run('mkdir %s' % env.path)
		with cd(env.path):
			run("git clone %s %s" % (env.git_repo, code_dir))
			run("virtualenv --no-site-packages . ")
			with virtualenv():
				run("pip install -r  %s/requirements.txt" % env.prj_name )

code_dir = env.path + env.prj_name

def config_nginx():
	with cd(env.path):					
		# Put our django specific conf in the main dir
		run("""echo "%s" > django_nginx.conf""" % nginx_config)

		#link to it in nginx's conf
		sudo("ln -s  %sdjango_nginx.conf /etc/nginx/conf.d/django_nginx.conf" % env.path)
	

  
		# sudo chown nginx -R static/
		#sudo chown nginx:nginx -R static/

		# run("""echo "%s" > nginx.conf""" % gunicorn_nginx_config)
		# sudo("rm /etc/nginx/nginx.conf")		
		# sudo("ln -s  %snginx.conf /etc/nginx/nginx.conf" % env.path)		

# sudo chmod -R  777 sitestatic/
# /home/ec2-user/conversation


def start():
	#run nginx based on the conf in code/voices/
	# sudo nginx -c /home/ec2-user/conversation/voices/nginx.conf
	sudo("nginx -c %s/nginx.conf" % code_dir)
	
	with cd(code_dir):
		run('mongod')
		with virtualenv():
			run('gunicorn_django')	


def test():
	local("""echo '%s' > z.txt""" % nginx_config)


# chmod 0771 static/ -r ? 

# sudo /etc/init.d/nginx restart


  		# if run("test -d %s" % code_dir).failed:

# env.path = '/home/ec2-user/conversation/'
# env.prj_name = 'voices'
# code_dir = env.path + env.prj_name
# /home/ec2-user/conversation/lib/python2.6/site-packages/django/contrib



nginx_config = """
server {
    listen   80 default_server;
    server_name example.com;
    # no security problem here, since / is alway passed to upstream
    root %s;
    # serve directly - analogous for static/staticfiles
    location /static/ {

    }
    location /admin/media/ {
        # this changes depending on your python version
        root %slib/python2.6/site-packages/django/contrib;
    }
    location / {
        proxy_pass_header Server;
        proxy_set_header Host \$"http_host";
        proxy_redirect off;
        proxy_set_header X-Real-IP \$"remote_addr";
        proxy_set_header X-Scheme \$"scheme";
        proxy_connect_timeout 10;
        proxy_read_timeout 10;
        proxy_pass http://localhost:8000/;
    }
    # what to serve if upstream is not available or crashes
    error_page 500 502 503 504 /media/50x.html;
}""" % (code_dir, env.path)



# supervisor_config = """
# [program:hello]
# directory = %s
# user = ec2-user
# command = /path/to/test/hello/script.sh
# stdout_logfile = /var/log/gunicorn/logfileout.log
# stderr_logfile = /var/log/gunicorn/logfileerr.log
#   """ % (code_dir, env.path)




gunicorn_nginx_config = """
# This is example contains the bare mininum to get nginx going with
# Gunicornservers.  

worker_processes 1;


pid /tmp/nginx.pid;
error_log /tmp/nginx.error.log;

events {
  worker_connections 1024; # increase if you have lots of clients
  accept_mutex off; # on - if nginx worker_processes > 1
  # use epoll; # enable for Linux 2.6+
  # use kqueue; # enable for FreeBSD, OSX
}

http {
  # nginx will find this file in the config directory set at nginx build time
  include mime.types;

  # fallback in case we can't determine a type
  default_type application/octet-stream;

  # click tracking!
  access_log /tmp/nginx.access.log combined;

  # you generally want to serve static files with nginx since neither
  # Unicorn nor Rainbows! is optimized for it at the moment
  sendfile on;

  tcp_nopush on; # off may be better for *some* Comet/long-poll stuff
  tcp_nodelay off; # on may be better for some Comet/long-poll stuff

  # we haven't checked to see if Rack::Deflate on the app server is
  # faster or not than doing compression via nginx.  It's easier
  # to configure it all in one place here for static files and also
  # to disable gzip for clients who don't get gzip/deflate right.
  # There are other other gzip settings that may be needed used to deal with
  # bad clients out there, see http://wiki.nginx.org/NginxHttpGzipModule
  gzip on;
  gzip_http_version 1.0;
  gzip_proxied any;
  gzip_min_length 500;
  gzip_disable "MSIE [1-6]\.";
  gzip_types text/plain text/html text/xml text/css
             text/comma-separated-values
             text/javascript application/x-javascript
             application/atom+xml;

  # this can be any application server, not just Unicorn/Rainbows!
  upstream app_server {
    # fail_timeout=0 means we always retry an upstream even if it failed
    # to return a good HTTP response (in case the Unicorn master nukes a
    # single worker for timing out).

    # for UNIX domain socket setups:
    server unix:/tmp/gunicorn.sock fail_timeout=0;

    # for TCP setups, point these to your backend servers
    # server 192.168.0.7:8080 fail_timeout=0;
    # server 192.168.0.8:8080 fail_timeout=0;
    # server 192.168.0.9:8080 fail_timeout=0;
  }

  server {
    # listen 80 default deferred; # for Linux
    # listen 80 default accept_filter=httpready; # for FreeBSD
    listen 80 default_server;

    client_max_body_size 4G;
    server_name _;

    # ~2 seconds is often enough for most folks to parse HTML/CSS and
    # retrieve needed images/icons/frames, connections are cheap in
    # nginx so increasing this is generally safe...
    keepalive_timeout 5;

    # path for static files
    root %s;

    location / {
      # an HTTP header important enough to have its own Wikipedia entry:
      #   http://en.wikipedia.org/wiki/X-Forwarded-For
      # proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;


      # enable this if and only if you use HTTPS, this helps Rack
      # set the proper protocol for doing redirects:
      # proxy_set_header X-Forwarded-Proto https;

      # pass the Host: header from the client right along so redirects
      # can be set properly within the Rack application
      # proxy_set_header Host $http_host;
      # proxy_set_header X-Forwarded-Host $host;

      # we don't want nginx trying to do something clever with
      # redirects, we set the Host: header above already.
      proxy_redirect off;


      # Comet/long-poll stuff.  It's also safe to set if you're
      # using only serving fast clients with Unicorn + nginx.
      # Otherwise you _want_ nginx to buffer responses to slow
      # clients, really.
      # proxy_buffering off;

      # Try to serve static files from nginx, no point in making an
      # *application* server like Unicorn/Rainbows! serve static files.
      if (!-f $request_filename) {
        proxy_pass http://app_server;
        break;
      }
    }

    # Error pages
    error_page 500 502 503 504 /500.html;
    location = /500.html {
      root /path/to/app/current/public;
    }
  }
} """  % code_dir
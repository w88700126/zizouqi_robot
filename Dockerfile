from w88700126/python-docker-environment
ADD server /server/server
ADD log /server/log
RUN pip install pycrypto
RUN yum -y install rsync subversion openssh-clients psmisc

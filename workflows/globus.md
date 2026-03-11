[TAMU globus main page](https://www.it.tamu.edu/services/services-by-category/infrastructure/globus.html)

After setting up an account, it is neccessary to join [TAMU globus subscription](https://service.tamu.edu/TDClient/36/Portal/KB/ArticleDet?ID=498)

[globus connect to TAMU HPRC tutorial](https://hprc.tamu.edu/kb/Software/Globus/)

[globus tutorial for setting up endpoints and personal endpoint](https://docs.globus.org/guides/tutorials/manage-files/transfer-files/)

[globus tutorial for setting up personal endpoint in Linux, terminal command, and tutorials](https://docs.globus.org/globus-connect-personal/install/linux/)
```
#After untar the instllation file
cd globusconnectpersonal-x.y.z #x.y.z is the downloaded version

#Start local globus connect
./globusconnectpersonal

# follow th gui to connect to run below command
./globusconnectpersonal -start &

# shut down the connect
$ ./globusconnectpersonal -stop
```

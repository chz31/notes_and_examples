[TAMU globus main page](https://www.it.tamu.edu/services/services-by-category/infrastructure/globus.html)

After setting up an account, it is neccessary to join [TAMU globus subscription](https://service.tamu.edu/TDClient/36/Portal/KB/ArticleDet?ID=498)

[globus connect to TAMU HPRC tutorial](https://hprc.tamu.edu/kb/Software/Globus/)

[globus tutorial for setting up endpoints and personal endpoint](https://docs.globus.org/guides/tutorials/manage-files/transfer-files/)

[globus tutorial for setting up personal endpoint in Linux, terminal command, and tutorials](https://docs.globus.org/globus-connect-personal/install/linux/)
```
#After untar the instllation file
cd globusconnectpersonal-x.y.z #x.y.z is the downloaded version

cd globusconnectpersonal-3.2.8

#Start local globus connect
./globusconnectpersonal

# follow th gui to connect to run below command
./globusconnectpersonal -start &

# shut down the connect
$ ./globusconnectpersonal -stop
```

After connecting, log into the globus account here: [https://hprc.tamu.edu/kb/Software/Globus/](https://hprc.tamu.edu/kb/Software/Globus/)

Select a collection:<br>
<img width="800" alt="image" src="https://github.com/user-attachments/assets/8e796f18-31e8-4fb0-9b28-a8e989dfe040" />

If it showed no permission information, just click the link to authorize through TAMU NetID.

It appears that the endpoint of one collection can only access files at the same hardrive the globus folder is located.

To initiate transfor, in File Management tab, enter the directory, and select the file. Click **Transfer or Sync to...** <br>
<img width="800" alt="image" src="https://github.com/user-attachments/assets/2a0c8c8b-803f-42a8-b2fa-7acfece78c21" />

Select another collection at the right-sed tab and enter the directory to transfer to file to: <br>
<img width="800" alt="image" src="https://github.com/user-attachments/assets/c330d7d5-024c-479f-8582-b8d93365dec4" />

Then go back to the left-side tab, and click **Start** to initiate transfer
<img width="600" alt="image" src="https://github.com/user-attachments/assets/cb10082f-2664-41fa-b9e9-fdde8328189d" />

You should see that transfer has been initiated:<br>
<img width="350" alt="image" src="https://github.com/user-attachments/assets/98a68258-2fab-42fe-8cb5-9f78c87af33e" />

Go to **Activity** tab to see the progress:<br>
<img width="600" alt="image" src="https://github.com/user-attachments/assets/f994b873-13f7-429b-9173-8c648d3adeb4" />

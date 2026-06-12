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


## Set a local folder as a sharable collection
Use the globus gui, click `Preference`, locate the folder, and check `share`.<br>
<img width="400" alt="image" src="https://github.com/user-attachments/assets/3f54af8a-8d18-4e82-97cf-fb0df62aec7c" />

In the globus.org website, go to `Collections`, select the local endpoint.

Click `Add Guest Collection` under the Collection tab. Log in NetID if needed.<br>
<img width="400" alt="image" src="https://github.com/user-attachments/assets/f552acf7-8741-47fa-9e8a-5019c95ec8f4" />


Locate the shared folder. Enter a Display Name and create a guest collection:<br>
<img width="350" alt="image" src="https://github.com/user-attachments/assets/11a93a23-25ac-4a36-b24b-f83d5f0a9aab" />

After created, the collection can be founded under Collections tab in the main local collection:<br>
<img width="300" alt="image" src="https://github.com/user-attachments/assets/f6127dd0-3c94-40d6-b5d1-3450b5b4fa7c" />

**The collection can also be found by other users through globus collection search.**

Click `permissions` to add permission to specific TAMU users. Check `write` to enable uploding to the collection, i.e., the local shared folder.<br>
<img width="300" alt="image" src="https://github.com/user-attachments/assets/40fec2ea-66c1-4c16-a44c-c3e2b27f256a" />

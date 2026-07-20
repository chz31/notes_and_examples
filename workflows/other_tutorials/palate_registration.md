# Surface-based registration using raw models

## 1. In Extension Manager (upper right corner), search and install the SlicerMorph Extension, and restart Slicer afterwards.
<img width="300" alt="image" src="https://github.com/user-attachments/assets/1e5bebc5-292b-48d1-a8cc-ed7fbccdfedb" />
<img width="300" alt="image" src="https://github.com/user-attachments/assets/cf56d650-fb14-4f8a-a167-edfc475056a2" />


## 2. Load data
Drag-and-drop two models into Slicer window.<br>
<img width="300" alt="image" src="https://github.com/user-attachments/assets/4ee8e521-8b31-4705-9eb5-6a7ef9bb2d57" />

You can view the data in the Data Module.<br>
<img width="300" alt="image" src="https://github.com/user-attachments/assets/4b9442d1-ded4-4d1d-960c-e6881ed3d555" />
<img width="300" alt="image" src="https://github.com/user-attachments/assets/0ba0fd7a-66c9-4000-85dc-bb2889607c5f" />

You can change the color of two models by clicking the color box<br>
<img width="500" alt="image" src="https://github.com/user-attachments/assets/0d63816b-0719-4c54-917a-0af30b6f50e4" />


## 3. Load data in FastModelAlign module
Click "Moduel Finder"<br>
<img width="300" alt="image" src="https://github.com/user-attachments/assets/0734d9a2-0fae-4cdb-9dc0-c264282186f0" />

Search for FastModelAlign <br>
<img width="300" alt="image" src="https://github.com/user-attachments/assets/0664c032-d968-4669-9f95-1bc0bd4537e4" />

If it is first time, it may ask you to install dependencies, which may take a few minutes.

Populate `Source Model` and `Target Model`.The Target Model is the fixed one. The source model will move to align to the target.

In `Output registered model`, select `Create New Model as`, and enter a descriptive name<br>
<img width="286" alt="image" src="https://github.com/user-attachments/assets/173d4306-c210-472e-bc43-13207d189a70" />

Your final set up should look like:<br>
<img width="500" alt="image" src="https://github.com/user-attachments/assets/9b1db52d-b571-45e3-8bc8-c51bc259aff0" />

## 4. Run the registration
Click 'Test pointcloud subsampling`, wait for 1-2 minutes until point densities are printed out:<br>
<img width="400" alt="image" src="https://github.com/user-attachments/assets/b6a42d95-d85b-4fec-a7bd-290137078173" />

Click `Run rigid registration`, wait for one to a few minutes until a red model is shown. <br>
<img width="500" alt="image" src="https://github.com/user-attachments/assets/1f02abd3-16db-4449-86d7-476dcf7c9eb0" />


The red model is the `Source Model` registered to the `Target Model`

If you switch back to `Data module`, you can toggle the eyeball symbol to display the original model and see how they differ before/after registration:<br>
<img width="500" alt="image" src="https://github.com/user-attachments/assets/cd55efb4-dd49-48c2-80ea-e4b3325932c8" />

Right click the eyeball to play with the Opacity bar for better visualization.

## 5. Save the results.
At the upper left corner, click File --> Save data. Click "Create a Medical Record Bundle" to save the whole scene. Change file name and directory if needed.<br>
<img width="500" alt="image" src="https://github.com/user-attachments/assets/0015950e-6dc3-40e5-a3a0-a10dba61e196" />



# Surface-based registration using the teeth region
## 1. Clone the model
Switch to the `Data` Module. 

Hide the registered red model from the last step by toggle the eyeball.

Right click each original model, and click `Clone`. You should see:<br>
<img width="300" alt="image" src="https://github.com/user-attachments/assets/06c8b076-b647-43e0-921a-8682ccdc5326" />

Hide the original model and only enable one model you want to cut. Double click to change the name to something like "Final surgery cut"<br>
<img width="300" alt="image" src="https://github.com/user-attachments/assets/fa95b035-81da-459b-9a4a-0f7dc585c6e0" />

## 2. Create a closed curve for the model
Switch to the "Markup" module. Click `Closed Curve`<br>
<img width="300" alt="image" src="https://github.com/user-attachments/assets/e4f2d00d-b40f-4f34-98b3-360befb02a5c" />

You can double click the object to change the name to something like:<br>
<img width="300" alt="image" src="https://github.com/user-attachments/assets/d47c6533-90bb-4c35-b8b1-994d0f17a1be" />

Move your cursor to the model and left-click many times to draw a curve to enclose the region you want to cut. Once you are done, **right-click** to exit:<br>
<img width="500" alt="image" src="https://github.com/user-attachments/assets/9b49519a-5620-4287-85c0-54546b87b213" />

<img width="500" alt="image" src="https://github.com/user-attachments/assets/cef08724-0532-4bf4-bf87-498b351b662f" />

Expand `Curve Settings` tab, select the model you are cutting under `Constrain to Model`. You should see that the curves fitted to the model.<br>
<img width="600" alt="image" src="https://github.com/user-attachments/assets/e0e19870-90ce-434c-952d-831636b61550" />

Now click 'Point List` in the `Markups` module to create a fiducial markup list. Change the name if necessary: <br>
<img width="400" alt="image" src="https://github.com/user-attachments/assets/ab7f7bd9-83a2-4596-8d55-39c51d942ad5" />

Click a couple of points within the curve enclosed region. To do so, after every click, you need to enable the point placement button at the top again, and re-click to place another point<br>
<img width="300" alt="image" src="https://github.com/user-attachments/assets/8ef8ca87-1f56-4542-93b6-d0039f73d09c" />

Repeat it a few times, you should have <br>
<img width="500" alt="image" src="https://github.com/user-attachments/assets/5fae7ecf-8a72-4cb3-a500-bdaba0c591d6" />


## 3. Model cut
In Module Finder, switch to 'Dynamic Modeler`

<img width="300" alt="image" src="https://github.com/user-attachments/assets/d766ec82-7b61-48a1-9cde-e44315ccc7c3" />

Select `Curve Cut`<br>
<img width="300" alt="image" src="https://github.com/user-attachments/assets/0afa783d-d243-46ea-ae0f-52ec983b52a4" />

In `Input nodes`, select `Model` as the model you want to cut, and select `Curve` and `Inside point` accordingly<br>
<img width="300" alt="image" src="https://github.com/user-attachments/assets/d3a71708-3266-4c10-8363-e68ac010195e" />





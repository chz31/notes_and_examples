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
Click 'Test pointcloud subsampling`, wait for 1-2 minutes until point densities are printed out:

Adjust the `Point Density Adjustment` (increase value to increase point density) and re-do pointcloud subsampling until each pointcloud has around 5,000 points.S

<img width="600" alt="image" src="https://github.com/user-attachments/assets/aeaa7b80-8438-4cd6-ba43-ca42c1e97f58" />


Click `Run rigid registration`, wait for one to a few minutes until a red model is shown. <br>
<img width="500" alt="image" src="https://github.com/user-attachments/assets/1f02abd3-16db-4449-86d7-476dcf7c9eb0" />


The red model is the `Source Model` registered to the `Target Model`

If you switch back to `Data module`, you can toggle the eyeball symbol to display the original model and see how they differ before/after registration:<br>
<img width="500" alt="image" src="https://github.com/user-attachments/assets/cd55efb4-dd49-48c2-80ea-e4b3325932c8" />

Right click the eyeball to play with the Opacity bar for better visualization.

## 5. Save the results.
At the upper left corner, click File --> Save data. Click "Create a Medical Record Bundle" to save the whole scene. Change file name and directory if needed.<br>
<img width="500" alt="image" src="https://github.com/user-attachments/assets/0015950e-6dc3-40e5-a3a0-a10dba61e196" />

The saved results can be drag and drop into Slicer to reload the whole scene.

# [Skip] Surface-based registration using the teeth region
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

In `Output nodes`, simply select the `Oytside model` as the same model you want to cut. <br>
<img width="400" alt="image" src="https://github.com/user-attachments/assets/cced9875-cb40-44cd-bed7-c40d59c25eaa" />

Click `Apply`, you should see: <br>
<img width="400" alt="image" src="https://github.com/user-attachments/assets/863b8602-ee7c-4cf2-9c3b-9d0d583bb296" />

## 4. repeat 2-3 for another model
Go back to `Data` module and hide everything other than the model you want to cut. Generate another cut model:<br>
<img width="400" alt="image" src="https://github.com/user-attachments/assets/f118190c-5c77-4379-8787-c660373fc78d" />

## 5. Rigid registration in FastModelAlign
Now switch to `FastModelAlign` and do another registration using the cut model

In Output registered model, simply `Create a new model` without renaming it since we do not need it for comparison.

<img width="500" alt="image" src="https://github.com/user-attachments/assets/cdbcc18f-7373-4912-86e7-faf3f8c5ca5f" />

Repeat the process to registered the cut model like:<br>
<img width="600" alt="image" src="https://github.com/user-attachments/assets/149461ed-df63-4444-a0b1-2e5c54914ab0" />

## 6. Align the actual models based on the modified registration from step 5
Switch back to Data Module, you should see a new transform object created. This one recored the transform trajectory from step 5.
<img width="300" alt="image" src="https://github.com/user-attachments/assets/05ae1c29-bcf7-4955-8c4d-359bb65a3c0c" />

Now, hide everything by toggle the eyeball. Clone the `Source Model` again, visualize it, and name it to something like `final_surgery_cut_to_initial`. 

Right click the grid at the right side and select the transform you just created:<br>
<img width="300" lt="image" src="https://github.com/user-attachments/assets/ff2cb5cc-835b-4e00-a425-326d5c18586b" />

You should see that the gird is rotated. Display the Target model (initial in this case), you'll see they are aligned.

<img width="700" alt="image" src="https://github.com/user-attachments/assets/da0081a4-d9ef-48ef-9a22-d6862d69c109" />

Optionally, if you right click the transform grid symbol, you can `Harden transform` to finalize it.

You can then display the last registration results for a comparison. 

## 7. Save the results
Save the results as previously shown.



# Local refined registration
## 1. Use ROI cut to cut a local region in both the source and target models after a global rigid registration
In `Markup` module`, create a new ROI. Expand `Display` section, then expand`Interaction handles` to check all checkboxes. An interaction handle should appear. Adjust ROI position and size to cover adjacent regions at the same side, include surgery-disrupted region, and exclude the teeth as much as possible. <br>
<img width="700" alt="image" src="https://github.com/user-attachments/assets/4e8ce5bb-a4d0-4d1c-9cb2-922468743085" />

In `Dynamic Modeler`, create an `ROI cut` for one model. Create a new model and change name (e.g., `initial_local`) for `inside` in `Output nodes`.Click `Apply`. </br>

Use the same ROI cut to cut the another model, and create a new `inside` model with a new name, such as `final_surgery_local` </br>

<img width="500" alt="image" src="https://github.com/user-attachments/assets/b796e104-9d8b-4f5d-937c-f39d8bfde7d1" />
<img width="700" alt="image" src="https://github.com/user-attachments/assets/df1c5fc4-5e76-43a7-8f6c-fc1677cd74a2" />


## 2. Using curve cut to exclude the surgery region from rigidly-registered models.
Visualize only the ROI-cut target model (e.g., `final_surgery_cut`). Place a closed curve to enclose the surgery site. The region should be slightly larger than the surgery site <br>

<img width="500" alt="image" src="https://github.com/user-attachments/assets/15df3690-c727-4b80-a7f5-05204468b711" />

In 'Dynmic Modeler`, choose 'curve cut` again. Save both 'Inside model`Outside model as a new model, such as `final_surgery_site` and `final_surgery_annulus` <br>
<img width="500" alt="image" src="https://github.com/user-attachments/assets/1e0c42be-bacc-4777-a132-89f21b8ce322" />
<img width="400" alt="image" src="https://github.com/user-attachments/assets/d858a441-6830-4ce0-b4b5-05b6c3b32e64" />


Use the script [slicer_project_curves_between_models.py](https://github.com/chz31/notes_and_examples/blob/main/workflows/other_tutorials/slicer_project_curve_between_models.py) to prooject curve to the source model.

**You can download the file by clicking the download button at the upper right corner and open it in a text editor to edit it**
<img width="300" alt="image" src="https://github.com/user-attachments/assets/e403f658-42bf-4d1e-b39b-a1a99ec94a74" />

First, copy-paste the entire script into the Slicer Python console.<br>
<img width="300" alt="image" src="https://github.com/user-attachments/assets/ec11e78b-dab7-44a2-ab78-0f12e30429d8" />


Open the script in the **text editor**, and change the node names to the existing model names in these lines, then copy-paste them in Slicer's Python console and hit Enter:
```
source_points_name = "final_annulus_cut_curve" # the curve you have already placed on a model
source_model_name = "final_surgery_local" # the ROI-cut model's name where the curve has been placed
target_model_name = "initial_local" # The model you will project the curve onto.
output_curve_name = source_points_name + "projected"
```

Afterwards copy-paste these lines below in Slicer Python console, and hit enter to run the script:
```
projected_curve = project_curve_between_models(
    source_curve_name=source_points_name,
    source_model_name=source_model_name,
    target_model_name=target_model_name,
    output_curve_name=output_curve_name,
)
```

You should be able to see a curve with `projected` postfix in its name is generated and the curve should be projected onto another model <br>
<img width="600" alt="image" src="https://github.com/user-attachments/assets/cf62ad07-6544-4ba9-88ed-c6c181ec2c30" />

Afterwards, do another `curve cut` for another model in `Dyanmic Modeler` and save the both the `Inside model` and the `Outside model` and name them to something like `initial_surgery_site` and `initial annulus`. <br>
<img width="400" halt="image" src="https://github.com/user-attachments/assets/a6e9b755-7586-4f70-aa27-ac8bc1bfbd64" />
<img width="400" alt="image" src="https://github.com/user-attachments/assets/dd8bbb45-0683-47ec-8387-561521c9c0ae" />


## 3. Do a refined rigid registration using the annulus models just created and transform the ROI-cut source model
In `FastModelAlign`, do a refined rigid registration for the curve-cut annulus models.Set up output model as something like `initial_to_final_annulus_rigid` <br>
<img width="700" alt="image" src="https://github.com/user-attachments/assets/d009fa53-23ae-495f-a12e-192a739544c2" />


## 4.Warp the source model onto the target model
This step will preform a warping of the locally registered source annulus model (`initial_to_final_annulus_rigid`) onto the target annulus model (`final_surgery_annulus`), then warp the full locally registered ROI-cut source model along with it to better fit to the surgery site.

Clone the ROI-cut global-registered source model before local refined registration (`initial_local` in the tutorial video) created from step 1, put it under the newly generated transform from the last step, and **harden the transform**.<br>
<img width="600" alt="image" src="https://github.com/user-attachments/assets/b26865d7-af4d-4d28-830e-ac036203feba" />

Download the script [cpd_annulus_extrapolation_test.py](https://github.com/chz31/notes_and_examples/blob/main/workflows/other_tutorials/cpd_annulus_extrapolation_test.py).

Open the script in a text editor and update these lines at the top:
```
preAnnulusNode  = slicer.util.getNode('initial_to_final_annulus_rigid') # the annulus of the local source model after local refined rigid registration, i.e., the output of the last FastModelAlign annulus-based registration.
postAnnulusNode = slicer.util.getNode('final_surgery_annulus') # the annulus of the target model
preFullNode     = slicer.util.getNode('initial_local_refined_by_annulus_registration') # full local source model after local refined rigid registration (annulus + surgical site) 
```

After, copy-paste **the entire script** in Slicer's Python console.

The script will run automatically. Wait a minute. You should be see a model with name `Pre_FullPatch_CPDWarped` created. This is the warped locally registered, ROI-cut source model.<br>
<img width="700" alt="image" src="https://github.com/user-attachments/assets/55dd5110-93ec-461c-a5df-e88f207efe7b" />



